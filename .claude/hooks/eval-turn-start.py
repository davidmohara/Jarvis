#!/usr/bin/env python3
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
    open_turn_level_record_exists,
)

WORKFLOWS_DIR = IES_ROOT / "workflows"
TAG = "TURN-START"
SEEN_MARKER_DIR = Path("/tmp/ies-eval-session-seen")


def load_master_workflows() -> dict:
    """workflows/*/workflow.md with `agent: master` in frontmatter — the only
    workflows with no subagent lifecycle of their own to hang an eval on."""
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
            if fm.get("agent") == "master":
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
    return open_turn_level_record_exists(workflow_name)


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


def boot_is_fresh() -> bool:
    """True if workflows/boot/state.yaml shows a boot is about to start
    fresh (not already in-progress from a prior, still-live turn)."""
    state_path = WORKFLOWS_DIR / "boot" / "state.yaml"
    if not state_path.exists():
        return True
    try:
        content = state_path.read_text()
        lines = content.split("\n")
        body = content
        if lines and lines[0].strip() == "---":
            for i, line in enumerate(lines[1:], start=1):
                if line.strip() == "---":
                    body = "\n".join(lines[1:i])
                    break
        data = yaml.safe_load(body) or {}
        return data.get("status") in (None, "not-started", "complete", "aborted")
    except Exception as e:
        log_error(f"boot_is_fresh check failed: {e}", TAG)
        return True


def open_eval_record(workflow_name: str, fm: dict, session_id: str, trigger: str, evidence: str = ""):
    EVAL_RUNS_DIR.mkdir(parents=True, exist_ok=True)
    eval_id = new_eval_id()
    now = datetime.now(timezone.utc)
    state_yaml_path = str((WORKFLOWS_DIR / workflow_name / "state.yaml").relative_to(IES_ROOT))

    record = {
        "id": eval_id,
        "type": "workflow",
        "name": workflow_name,
        "agent": fm.get("agent", "master"),
        "session_id": session_id,
        "trigger": trigger,
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

    master_workflows = load_master_workflows()
    if not master_workflows:
        return

    session_id = infer_session_id(payload)

    workflow_name = detect_workflow(prompt, master_workflows)
    evidence = _first_clause(prompt.lower()) if workflow_name else ""

    # boot special-case: CLAUDE.md mandates it unconditionally on session
    # start, independent of what the first prompt says.
    if not workflow_name and "boot" in master_workflows and is_first_prompt_this_session(session_id) and boot_is_fresh():
        workflow_name = "boot"
        evidence = "boot-first-prompt-of-session"

    if not workflow_name:
        return

    if already_open_for_workflow(session_id, workflow_name):
        log_info(f"Eval already open for '{workflow_name}' this session, skipping (evidence={evidence[:120]!r})", TAG)
        return

    open_eval_record(workflow_name, master_workflows[workflow_name], session_id, trigger="boot" if workflow_name == "boot" else "manual", evidence=evidence)


if __name__ == "__main__":
    main()
