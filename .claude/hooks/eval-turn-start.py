#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""
UserPromptSubmit Hook: Eval Record Opener + state.yaml Monitoring Start

Fires on every raw user prompt, before any expansion — this is deliberate:
it also catches natural-language workflow triggers that never go through a
slash-command expansion step (a UserPromptExpansion-based hook would miss
those). Detects whether this prompt is asking Master to run a workflow that
never gets a SubagentStart/SubagentStop pair of its own — i.e. any workflow
whose frontmatter names `agent: master` (boot, shutdown-cleanup,
weekly-review as of this writing) and therefore executes inline in the main
session. For workflows spawned as a subagent under a different agent's
persona (Knox for plaud-ingest, Chief for morning-briefing, etc.),
eval-agent-start.py already opens the record on SubagentStart — this hook
backs off and does nothing for those, so no duplicate record is created.

Skills are explicitly out of scope here: a skill's own SKILL COMPLETE write
already creates its eval record via post-tool-use.py's
create_eval_record_from_skill_run. Opening a stub here too would double it.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

_IES_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_IES_ROOT / "systems" / "eval-harness" / "vendor"))
sys.path.insert(0, str(_IES_ROOT / "systems" / "eval-harness"))
import yaml
from hook_utils import (
    IES_ROOT, EVAL_RUNS_DIR, log_error, log_info, atomic_write_json,
    read_stdin, new_eval_id, infer_session_id, extract_workflow_path_reference,
    open_turn_level_record_exists, SESSION_EXIT_ABORT_REASONS,
)
try:
    from token_usage import latest_turn_model
except Exception:
    latest_turn_model = None

WORKFLOWS_DIR = IES_ROOT / "workflows"
TAG = "TURN-START"
SEEN_MARKER_DIR = Path("/tmp/ies-eval-session-seen")


# Workflows whose trigger phrase lands in Master's main session on
# UserPromptSubmit even though their execution was reconciled to a different
# owner. Two cases live here:
#   - shutdown-cleanup became Rigby-owned 2026-10-09 per agents/manifest.md,
#     but "exit" / "log off" still arrives as a main-session prompt, so
#     turn-level detection must keep firing for it.
#   - daily-review is Chief-owned (workflows/daily-review/workflow.md
#     `agent: chief`) and runs as a Chief subagent, so `load_master_workflows`
#     below never picks it up from frontmatter. But its real trigger ("run
#     daily review", "wrap up the day") still lands in Master's main session,
#     and without a turn-level record open for the run the guardrail
#     checkpoint finds no in-progress record and the run falls back to the
#     manual close-eval-record.py Cowork path — which writes skeleton steps
#     with no per-step model/tokens/cost/token_source (the exact daily-review
#     instrumentation gap: no daily-review step ever carried token_source).
#     Listing it here gives daily-review the same turn-level eval-record path
#     boot has.
# Without this set, an ownership reconciliation silently deletes the
# workflow's exit-trigger detection (the exact regression
# test_detect_workflow.py's shutdown-cleanup cases were preserved to catch).
MAIN_SESSION_TRIGGER_WORKFLOWS = {"shutdown-cleanup", "daily-review"}


# Prompts the harness injects into the main session that are NOT user turns:
# a subagent's message to its parent ("<agent-message from=\"a1b2c3\">...")
# and a background task's completion notice ("<task-notification>..."). These
# arrive as UserPromptSubmit payloads and must never open a turn-level eval
# record: on 2026-10-30 an <agent-message> 8 minutes after boot finished
# matched "boot" + a run-verb and opened eval-20261030T142403-YWDWF6 — a
# spurious second boot record for a session whose boot was already closed
# (trigger_evidence '<agent-message from="ac26dd7e172dbc3b8">'). The same
# class produced eval-20261022T194016-5C4OEY ('<task-notification>', 3.9M
# tokens of unrelated work). A real user prompt never starts with one of
# these tags.
INJECTED_PROMPT_PREFIXES = ("<agent-message", "<task-notification")


def is_injected_prompt(prompt: str) -> bool:
    return (prompt or "").lstrip().lower().startswith(INJECTED_PROMPT_PREFIXES)


def load_master_workflows() -> dict:
    """workflows/*/workflow.md with `agent: master` in frontmatter (the only
    workflows with no subagent lifecycle of their own to hang an eval on),
    plus MAIN_SESSION_TRIGGER_WORKFLOWS above."""
    out = {}
    if not WORKFLOWS_DIR.exists():
        return out
    for wf_dir in WORKFLOWS_DIR.iterdir():
        wf_file = wf_dir / "workflow.md"
        if not wf_file.is_file():
            continue
        try:
            content = wf_file.read_text()
            if not content.startswith("---"):
                continue
            end_idx = content.index("---", 3)
            fm = yaml.safe_load(content[3:end_idx]) or {}
            if fm.get("agent") == "master" or wf_dir.name in MAIN_SESSION_TRIGGER_WORKFLOWS:
                out[wf_dir.name] = fm
        except Exception as e:
            log_error(f"Failed to read {wf_file}: {e}", TAG)
    return out


# already_open_for_workflow moved to hook_utils.open_turn_level_record_exists
# (shared with post-tool-use.py's create_eval_record_from_state, which needs
# the identical check — see that function's docstring for why). Kept as a
# thin local alias so this file's existing call sites/tests don't need to
# change.
def already_open_for_workflow(session_id: str, workflow_name: str) -> bool:
    return open_turn_level_record_exists(workflow_name, session_id=session_id)


RUN_VERBS = r"(?:run|start|kick off|kick-off|execute|launch|invoke|fire off|fire up|begin)"

# Some master-owned workflows are invoked through a natural-language phrase
# that never contains the workflow's own name/slug at all — sourced from
# agents/master.md's routing table, the authoritative list of real trigger
# phrases David actually uses. shutdown-cleanup is the case in point: its
# real trigger is "exit" / "log off" / "end session" (agents/master.md line
# ~82), never the words "shutdown" or "cleanup". Without this, shutdown-
# cleanup's turn-level eval record would never fire in practice — the
# name-based matching below would just never see its real invocation.
# Kept short and literal (not fuzzy) for the same reason the name-matching
# above requires a run-verb: these phrases are still specific enough that
# they're unlikely to appear in unrelated conversation, unlike a bare
# workflow name/slug (e.g. "boot") which gets discussed constantly.
# Two confidence tiers: "log off" / "end session" are specific enough to
# match anywhere in the prompt. Bare "exit" / "shut down" are common words
# in unrelated sentences ("did you exit the meeting early?"), so those only
# count when they essentially ARE the message — anchored to the whole
# (punctuation-stripped) prompt or a short leading/trailing clause of it —
# same reasoning as requiring a run-verb next to a workflow's name above.
WORKFLOW_TRIGGER_PHRASES = {
    "shutdown-cleanup": [
        r"\blog(?:ging)? off\b",
        r"\bend(?:ing)? (?:the |this )?session\b",
    ],
    # daily-review's real invocation is often the name-less "wrap up the day"
    # (see workflows/daily-review/state.yaml original-request) rather than the
    # workflow's own name/slug. Kept as literal, specific phrases (not fuzzy)
    # for the same reason the name-based match requires a run-verb: these are
    # unlikely to appear in an unrelated first clause.
    "daily-review": [
        r"\bwrap up (?:the|my|our) day\b",
        r"\bend.of.day (?:review|shutdown)\b",
    ],
}
WORKFLOW_TRIGGER_PHRASES_ANCHORED = {
    "shutdown-cleanup": [r"\bexit\b", r"\bshut(?:ting)? down\b"],
}


def _first_clause(text: str) -> str:
    """The first sentence/clause of a prompt, lowercased. Real invocations
    ('run boot', 'exit') are short and lead with the request. Discussion or
    dispatch text that happens to mention a workflow name is usually a
    later clause in a longer message ('...the persona-fix dispatch work,
    and separately, can you check why boot's eval record...') — restricting
    matching to the first clause is what actually closes this failure
    class, not just word-proximity within an unbounded window (proximity
    alone still matched an unrelated 'run'/'start' elsewhere in the same
    long message near a later, unrelated mention of 'boot'). Found via a
    live incident: 3 spurious boot/shutdown-cleanup records opened this
    session while 'boot' was discussed mid-message during unrelated
    dispatch/analysis turns, none of which were anywhere close to the
    start of those messages."""
    # Split on sentence enders and newlines; keep it simple and conservative
    # (a false split just makes the check stricter, never looser).
    parts = re.split(r"[.!?;\n]", text, maxsplit=1)
    return parts[0].strip()


def detect_workflow(prompt: str, master_workflows: dict) -> str | None:
    """Return the workflow name this prompt is asking Master to actually
    RUN, or None. Deliberately narrow: a bare mention of a workflow's name
    anywhere in the prompt is not run-intent — boot in particular gets
    discussed constantly (it's the subject of its own instrumentation work),
    so matching on the word alone opens a spurious eval record every time
    someone just talks about it. Require one of: an explicit path reference,
    a slash command, an imperative run-verb directly next to the name, or
    (for workflows whose real trigger doesn't contain their own name, per
    WORKFLOW_TRIGGER_PHRASES above) one of their documented trigger phrases —
    AND, for everything except the path/slash-command checks, the match must
    land in the prompt's first clause. A path reference or slash command is
    unambiguous wherever it appears in the message, so those two checks are
    exempt from the first-clause restriction."""
    if not prompt:
        return None
    lowered = prompt.lower().strip()

    # Explicit path reference: "workflows/boot/workflow.md" — unambiguous
    # anywhere in the message, no first-clause restriction needed. Shared
    # with eval-agent-start.py's spawn-prompt detection (hook_utils.py) so
    # this one regex isn't maintained in two places.
    path_match = extract_workflow_path_reference(lowered)
    if path_match and path_match in master_workflows:
        return path_match

    # Slash command: "/boot", "/shutdown-cleanup" — only valid as the literal
    # start of the message anyway, so it's already first-clause by construction.
    if lowered.startswith("/"):
        token = lowered[1:].split()[0] if len(lowered) > 1 else ""
        token = token.strip()
        if token in master_workflows:
            return token

    clause = _first_clause(lowered)

    # Documented natural-language trigger phrase (no run-verb needed — the
    # phrase itself IS the invocation, per agents/master.md's routing table).
    for name, patterns in WORKFLOW_TRIGGER_PHRASES.items():
        if name in master_workflows and any(re.search(p, clause) for p in patterns):
            return name

    # Same, but for single common words that are only invocation-intent when
    # they land at the very end of the (first-clause) message — a closing
    # command ("exit", "ok, let's exit", "time to shut down") rather than
    # buried mid-sentence about something unrelated ("did you exit the
    # meeting early").
    stripped = clause.strip(" .!?…")
    for name, patterns in WORKFLOW_TRIGGER_PHRASES_ANCHORED.items():
        if name in master_workflows and any(re.search(p + r"\s*$", stripped) for p in patterns):
            return name

    # Clear imperative: a run-verb within a few words of the name/slug,
    # either order ("run boot", "start the boot workflow"), restricted to
    # the first clause only.
    for name in master_workflows:
        phrase = re.escape(name.replace("-", " "))
        name_re = rf"(?:{re.escape(name)}|{phrase})"
        if re.search(rf"\b{RUN_VERBS}\b(?:\s+\w+){{0,3}}\s+\b{name_re}\b", clause):
            return name
        if re.search(rf"\b{name_re}\b(?:\s+\w+){{0,3}}\s+\b{RUN_VERBS}\b", clause):
            return name

    return None


def is_first_prompt_this_session(session_id: str) -> bool:
    """Best-effort marker: has this session_id already had a UserPromptSubmit
    pass through this hook? Used only to auto-attribute boot, since CLAUDE.md
    mandates boot unconditionally on session start regardless of what the
    first message says — text matching alone would miss that."""
    try:
        SEEN_MARKER_DIR.mkdir(parents=True, exist_ok=True)
        marker = SEEN_MARKER_DIR / session_id
        if marker.exists():
            return False
        marker.touch()
        return True
    except Exception as e:
        log_error(f"is_first_prompt_this_session failed: {e}", TAG)
        return False


BOOT_STALE_COMPLETION_AFTER_HOURS = 12


def _read_state_yaml(state_path: Path) -> dict:
    """Parsed body (frontmatter markers stripped) of a workflow state.yaml,
    or {} when unreadable."""
    if not state_path.exists():
        return {}
    try:
        content = state_path.read_text()
        lines = content.split("\n")
        body = content
        if lines and lines[0].strip() == "---":
            for i, line in enumerate(lines[1:], start=1):
                if line.strip() == "---":
                    body = "\n".join(lines[1:i])
                    break
        return yaml.safe_load(body) or {}
    except Exception as e:
        log_error(f"failed reading {state_path}: {e}", TAG)
        return {}


def boot_is_fresh() -> bool:
    """True if workflows/boot/state.yaml shows a boot is about to start
    fresh (not already in-progress from a prior, still-live turn).

    A terminal status (complete/aborted) is necessary but not sufficient:
    a `status: complete` left over from a PRIOR session — days old — used
    to count as "fresh" here, which is exactly what let eval-turn-start.py
    open a speculative 'boot' eval record for a session that never actually
    ran boot at all (the phantom record incident, err-20260829T161711-3IPMKR).
    Requiring the completion timestamp to be recent doesn't make this check
    perfect (it can't prove THIS session will run boot), but it stops the
    common case: a stale multi-day-old 'complete' status being read as
    permission to open a new record every single session thereafter."""
    data = _read_state_yaml(WORKFLOWS_DIR / "boot" / "state.yaml")
    if not data:
        return True
    status = data.get("status")
    if status in (None, "not-started"):
        return True
    if status not in ("complete", "aborted"):
        return False

    completed_at = data.get("completed-at")
    if not completed_at:
        return True  # no timestamp to judge staleness by — don't block on it
    try:
        ts = str(completed_at).replace("Z", "+00:00")
        completed_dt = datetime.fromisoformat(ts)
        if completed_dt.tzinfo is None:
            completed_dt = completed_dt.replace(tzinfo=timezone.utc)
    except Exception:
        return True  # unparseable — don't block on it either

    age_hours = (datetime.now(timezone.utc) - completed_dt).total_seconds() / 3600
    return age_hours < BOOT_STALE_COMPLETION_AFTER_HOURS


# ---------------------------------------------------------------------------
# Cross-session continuation policy (root-cause fix 9,
# reviews/boot-root-cause-2026-11-05.md)
#
# POLICY: one eval record per logical workflow run, across sessions. IES
# workflows already have continuation semantics at the workflow layer —
# state.yaml persists current-step and a resumed session picks up where the
# dead one left off — so the eval layer now mirrors that instead of minting
# a fresh record per session attempt. The retry-stack evidence: 27 records
# across 13 boot days, 2-4 records per real boot, each with its own verdict,
# because a session that died mid-boot got its record closed by a
# session-lifecycle sweep and the next session's boot opened a brand-new one.
#
# Mechanism: when this hook is about to open a turn-level record for
# workflow W, and a prior record for W was closed by a session-lifecycle
# sweep (abort_reason in SESSION_EXIT_ABORT_REASONS) within
# CONTINUATION_WINDOW_HOURS, and W's state.yaml is still in-progress (the
# run genuinely never finished), REOPEN that record under this session
# instead of opening a new one: status back to in-progress, session_id
# re-keyed to this session, monitoring reactivated, with a `continuations`
# audit list recording every session that carried the run. The record's
# original `started` is kept, so the final duration honestly spans the whole
# logical run (sessions included).
#
# Deliberate non-goals / residual choices:
#   - A prior record closed as success/failure/partial is never adopted:
#     that run reached a real verdict; a re-run is a new run.
#   - A graded record (grading.last_graded set) is never adopted.
#   - A NEW run started from step-01 in a later session (David re-runs boot
#     from the top rather than resuming) still adopts if the prior record
#     died mid-run within the window: it is the same boot-day attempt chain,
#     the continuations list makes the merge visible, and steps re-run under
#     their own names simply overwrite their prior entries.
#   - Old-session subagent records keep their old session_id; late stops of
#     those agents resolve their parent by subagents[] membership or the
#     orphan re-attach path (session + workflow + window), which does not
#     match the re-keyed session — a residual known gap, mitigated by the
#     fact that a dead session's subagents almost always stop before its
#     SessionEnd sweep runs.
# ---------------------------------------------------------------------------
CONTINUATION_WINDOW_HOURS = 24


def find_continuable_record(workflow_name: str) -> "Path | None":
    """Most recent prior turn-level record for this workflow that was closed
    by a session-lifecycle sweep within the continuation window, while the
    workflow's own state.yaml is still in-progress. None when no such record
    exists (the normal case: finished runs, stale closures, fresh days)."""
    if not EVAL_RUNS_DIR.exists():
        return None
    # The workflow must be genuinely unfinished — a terminal state.yaml
    # means the prior run completed and this is a new run, not a continuation.
    state = _read_state_yaml(WORKFLOWS_DIR / workflow_name / "state.yaml")
    if state.get("status") != "in-progress":
        return None

    candidates = []
    now = datetime.now(timezone.utc)
    for f in EVAL_RUNS_DIR.glob("eval-*.json"):
        try:
            data = json.load(open(f))
        except Exception:
            continue
        if data.get("type") != "workflow":
            continue
        if data.get("name") != workflow_name and data.get("workflow") != workflow_name:
            continue
        if data.get("status") not in ("aborted", "incomplete"):
            continue
        mech = (data.get("assessment") or {}).get("mechanical") or {}
        if mech.get("abort_reason") not in SESSION_EXIT_ABORT_REASONS:
            continue
        if (data.get("assessment", {}).get("grading") or {}).get("last_graded"):
            continue  # already graded — never reopen a graded record
        started = data.get("started")
        try:
            started_dt = datetime.fromisoformat(str(started).replace("Z", "+00:00"))
            if started_dt.tzinfo is None:
                started_dt = started_dt.replace(tzinfo=timezone.utc)
        except Exception:
            continue
        if (now - started_dt).total_seconds() > CONTINUATION_WINDOW_HOURS * 3600:
            continue
        candidates.append((started, f))
    if not candidates:
        return None
    candidates.sort(key=lambda x: str(x[0]), reverse=True)
    return candidates[0][1]


def adopt_continuation_record(prior_path: Path, session_id: str, trigger: str,
                              evidence: str) -> bool:
    """Reopen a session-lifecycle-closed record under the new session
    (see the continuation policy block above). Returns True when the record
    was reopened and is now the run's live record; False on any failure
    (the caller then falls back to opening a fresh record)."""
    try:
        with open(prior_path, "r") as f:
            record = json.load(f)
        prior_status = record.get("status")
        prior_reason = (record.get("assessment") or {}).get("mechanical", {}).get("abort_reason")
        now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        record["status"] = "in-progress"
        record["session_id"] = session_id
        record["completed"] = None
        record["duration_seconds"] = None
        mech = record.setdefault("assessment", {}).setdefault("mechanical", {})
        mech.pop("abort_reason", None)
        mech["completed"] = None
        mech["all_steps_finished"] = None
        monitoring = record.setdefault("monitoring", {})
        monitoring["active"] = True
        continuations = monitoring.setdefault("continuations", [])
        continuations.append({
            "resumed_in_session": session_id,
            "resumed_at": now_iso,
            "prior_status": prior_status,
            "prior_abort_reason": prior_reason,
            "trigger_evidence": (evidence or "")[:200],
        })
        atomic_write_json(prior_path, record)
        log_info(
            f"Adopted continuation record {record.get('id')} for '{record.get('name')}' "
            f"(closed {prior_status}/{prior_reason}, reopened under session {session_id}) "
            f"— same logical run, no new record", TAG)
        return True
    except Exception as e:
        log_error(f"continuation adoption failed for {prior_path.name}: {e}", TAG)
        return False


def open_eval_record(workflow_name: str, fm: dict, session_id: str, trigger: str, evidence: str = "",
                     transcript_path: str | None = None):
    EVAL_RUNS_DIR.mkdir(parents=True, exist_ok=True)
    eval_id = new_eval_id()
    now = datetime.now(timezone.utc)
    state_yaml_path = str((WORKFLOWS_DIR / workflow_name / "state.yaml").relative_to(IES_ROOT))

    # Model capture at creation (2026-10-23): a master-owned workflow runs
    # inline in the parent session, so the session transcript's latest
    # assistant turn is the model currently serving the run. This is the
    # model at OPEN time; eval-turn-stop.py's finalize re-derives the
    # window's dominant model into parent_window.model and backstops this
    # field from it, so a mid-run /model switch is still reflected.
    model = None
    model_source = None
    if latest_turn_model and transcript_path:
        try:
            model = latest_turn_model(transcript_path)
            if model:
                model_source = "session-transcript-latest"
        except Exception:
            model = None

    record = {
        "id": eval_id,
        "type": "workflow",
        "name": workflow_name,
        "agent": fm.get("agent", "master"),
        "session_id": session_id,
        "trigger": trigger,
        "model": model,
        "model_source": model_source,
        "started": now.isoformat().replace("+00:00", "Z"),
        "completed": None,
        "duration_seconds": None,
        "status": "in-progress",
        "steps": [],
        "subagents": [],
        "monitoring": {
            "active": True,
            "state_yaml_path": state_yaml_path,
            "opened_by": "eval-turn-start.py",
            # Truncated diagnostic (never the full prompt) of what actually
            # matched — added after a live incident where 3 spurious records
            # opened this session with no way to tell what text triggered
            # them after the fact. "boot-first-prompt" for the CLAUDE.md
            # special case; otherwise the matched first-clause text, capped
            # to keep this from becoming a prompt-logging concern.
            "trigger_evidence": (evidence or "")[:200],
        },
        "assessment": {
            "mechanical": {"completed": None, "all_steps_finished": None, "tool_failures": 0, "error_ids": []},
            "structural": {"expected_outputs_written": None, "outputs_non_empty": None, "assertions_checked": 0, "assertions_passed": 0, "assertion_results": []},
            "grading": {"last_graded": None, "grade": None, "safety_grade": None, "grader_notes": None},
            "controller_feedback": {"rating": None, "comment": None, "timestamp": None},
            "bias_assessment": {
                "applicable": False, "protected_attributes": [], "fairness_metric": None,
                "demographic_coverage_verified": False, "adversarial_inputs_tested": False,
                "bias_detected": False, "bias_flags": [], "remediation_status": "none",
            },
        },
        "version_hash": None,
        "prior_baseline_id": None,
        "tags": ["turn-level"],
    }
    path = EVAL_RUNS_DIR / f"{eval_id}.json"
    atomic_write_json(path, record)
    if path.exists():
        log_info(f"Opened turn-level eval record {eval_id} for workflow '{workflow_name}' (session={session_id}, trigger={trigger}, evidence={evidence[:120]!r})", TAG)
    else:
        log_error(f"Failed to write turn-level eval record for '{workflow_name}'", TAG)


def main():
    payload = read_stdin()
    prompt = payload.get("prompt") or payload.get("user_prompt") or payload.get("message") or ""

    # Only a real user prompt can start a workflow run. Injected agent/task
    # messages are a subagent's traffic, not an invocation (see
    # INJECTED_PROMPT_PREFIXES).
    if is_injected_prompt(prompt):
        log_info(f"Ignoring injected non-user prompt as a turn start (evidence={prompt.lstrip()[:80]!r})", TAG)
        return

    master_workflows = load_master_workflows()
    if not master_workflows:
        return

    session_id = infer_session_id(payload)

    workflow_name = detect_workflow(prompt, master_workflows)
    evidence = _first_clause(prompt.lower()) if workflow_name else ""

    # boot special-case: CLAUDE.md mandates it unconditionally on session
    # start, independent of what the first prompt says.
    if not workflow_name and "boot" in master_workflows and is_first_prompt_this_session(session_id):
        if boot_is_fresh():
            workflow_name = "boot"
            evidence = "boot-first-prompt-of-session"
        elif _read_state_yaml(WORKFLOWS_DIR / "boot" / "state.yaml").get("status") == "in-progress":
            # A prior session's boot never finished (state.yaml still
            # in-progress) and CLAUDE.md mandates boot on every session —
            # this session is resuming that run. The first-prompt heuristic
            # previously skipped this case entirely (boot_is_fresh() is
            # False for an in-progress state), so a resumed boot opened no
            # turn-level record at all unless the prompt text happened to
            # match. Continuation policy (root-cause fix 9): open/adopt a
            # record for the SAME logical run.
            workflow_name = "boot"
            evidence = "boot-resumed-mid-run"

    if not workflow_name:
        return

    if already_open_for_workflow(session_id, workflow_name):
        log_info(f"Eval already open for '{workflow_name}' this session, skipping (evidence={evidence[:120]!r})", TAG)
        return

    # Cross-session continuation (root-cause fix 9): if this workflow's
    # prior run died with its session (record closed by a session-lifecycle
    # sweep) and the workflow is still in-progress, continue THAT record
    # instead of minting a new one. See the policy block above
    # find_continuable_record.
    trigger = "boot" if workflow_name == "boot" else "manual"
    prior = find_continuable_record(workflow_name)
    if prior is not None and adopt_continuation_record(prior, session_id, trigger, evidence):
        return

    open_eval_record(workflow_name, master_workflows[workflow_name], session_id, trigger=trigger, evidence=evidence,
                     transcript_path=payload.get("transcript_path"))


if __name__ == "__main__":
    main()
