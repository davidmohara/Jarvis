#!/usr/bin/env python3
"""
PostToolUse Hook: Session Index Capture + Eval Harness Integration
Triggered after every Write or Edit tool call.

Two independent concerns:
1. Session Index: Reads current session's topic and appends file path to active topic
2. Eval Harness: Detects state.yaml and step frontmatter writes to update eval records

Since Cowork doesn't support multiple hooks on the same event, both concerns
are handled in this single file but are logically separated.
"""

import json
import sys
import fcntl
import hashlib
import re
import secrets
import string
from pathlib import Path
from datetime import datetime, timezone

# Derive IES_ROOT from this file's location: .claude/hooks/post-tool-use.py → project root
IES_ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = IES_ROOT / "memory" / "sessions" / "index.json"
EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"
SKILL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "skill-runs"
ERROR_LOG = Path("/tmp/ies-hook-errors.log")
ALPHABET = string.ascii_uppercase + string.digits

# Vendored PyYAML (see systems/eval-harness/vendor/yaml/LICENSE) goes first on
# sys.path so this hook never depends on pip/pyyaml being installed on the
# host — checked in ahead of any environment copy of the real package.
sys.path.insert(0, str(IES_ROOT / "systems" / "eval-harness" / "vendor"))
sys.path.insert(0, str(IES_ROOT / "systems" / "eval-harness"))
import yaml
try:
    from token_usage import usage_between
except Exception:
    usage_between = None
try:
    from hook_utils import infer_session_id as _shared_infer_session_id
except Exception:
    _shared_infer_session_id = None
try:
    from hook_utils import open_turn_level_record_exists
except Exception:
    open_turn_level_record_exists = None
try:
    import assertion_checks as _assertion_checks
except Exception:
    _assertion_checks = None

# ============================================================================
# SHARED UTILITIES
# ============================================================================

def log_error(msg: str):
    """Log error to /tmp/ies-hook-errors.log without blocking."""
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] [ERROR] {msg}\n")
    except Exception:
        pass

def atomic_write_json(path: Path, data: dict):
    """Write JSON atomically using a temp file + rename, with exclusive lock."""
    tmp_path = path.with_suffix(".tmp")
    try:
        with open(tmp_path, "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(data, f, indent=2)
            fcntl.flock(f, fcntl.LOCK_UN)
        tmp_path.replace(path)
    except Exception as e:
        log_error(f"atomic_write_json failed for {path}: {e}")
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)

def read_stdin() -> dict:
    """Read hook payload from stdin."""
    try:
        payload = json.load(sys.stdin)
        return payload
    except json.JSONDecodeError as e:
        log_error(f"Failed to parse stdin JSON: {e}")
        return {}

def normalize_path(abs_path: str) -> str:
    """Convert absolute path to relative path from IES root."""
    try:
        path_obj = Path(abs_path)
        return str(path_obj.relative_to(IES_ROOT))
    except ValueError:
        return abs_path


def extract_frontmatter_block(content: str) -> str:
    """Strip the leading/trailing `---` markers IES uses to wrap both step
    frontmatter and state.yaml files. Passing the raw file (with a trailing
    marker present) straight to yaml.safe_load() parses as two YAML
    documents — a real one plus an empty one after the closing marker — and
    raises ComposerError. If there's no second marker, returns content as-is
    (single-document files parse fine unmodified)."""
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return content
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[1:i])
    return "\n".join(lines[1:])

# ============================================================================
# SESSION INDEX FUNCTIONS
# ============================================================================

def read_index() -> list:
    """Read the current session index."""
    if not INDEX_PATH.exists():
        return []
    try:
        with open(INDEX_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        log_error(f"Failed to read index: {e}")
        return []

def write_index(data: list):
    """Write the updated session index atomically."""
    atomic_write_json(INDEX_PATH, data)

def update_session_index(rel_path: str):
    """Update session index with the current file path."""
    index = read_index()
    if not index:
        log_error("Session index is empty or missing")
        return

    current_session = index[-1]
    current_topic = current_session.get("current_topic")
    topics = current_session.get("topics", [])

    updated = True
    if not current_topic:
        # Find or create unattributed bucket
        unattributed = None
        for t in topics:
            if t.get("topic") == "unattributed":
                unattributed = t
                break
        if not unattributed:
            unattributed = {"topic": "unattributed", "files": [], "loops": [], "flag": True}
            topics.append(unattributed)
        if rel_path not in unattributed.get("files", []):
            unattributed["files"].append(rel_path)
    else:
        matching_topic = None
        for t in topics:
            if t.get("topic") == current_topic or t.get("name") == current_topic:
                matching_topic = t
                break
        if matching_topic:
            if "files" not in matching_topic:
                matching_topic["files"] = []
            if rel_path not in matching_topic["files"]:
                matching_topic["files"].append(rel_path)
        else:
            log_error(f"Current topic '{current_topic}' not found in topics list")
            updated = False

    if updated:
        write_index(index)

# ============================================================================
# EVAL HARNESS FUNCTIONS
# ============================================================================

EVAL_PHANTOMS_DIR = EVAL_RUNS_DIR / "_phantoms"
_STATE_YAML_PATH_RE = re.compile(r"workflows/([a-z0-9_-]+)/state\.yaml$", re.IGNORECASE)

# How far before the current run's start an existing record may begin and
# still count as the same run for dedupe. Turn-level records open on the
# first prompt of the session, which can predate state.yaml's
# session-started by minutes (boot's record opened 2 min before its
# session-started on 2026-09-18) — but a genuinely separate rerun of the
# same workflow starts its own window much later, so a small tolerance
# distinguishes "same run, two id flavors" from "two real runs".
SAME_RUN_WINDOW_TOLERANCE_SECONDS = 15 * 60


def parse_ts_assume_utc(value) -> "datetime | None":
    """Parse an ISO-8601 timestamp; naive values are assumed UTC (the same
    convention eval-turn-stop.py's _parse_ts uses)."""
    if not value or not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def workflow_name_from_path(rel_path: str | None) -> str | None:
    """Derive the workflow name from a state.yaml path:
    `workflows/<name>/state.yaml` → `<name>`. Returns None if the path
    doesn't match. This is the authoritative source — several workflows
    (boot being the canonical case, err class of 2026-09-18) have a
    state.yaml schema with NO `workflow:` field at all, so relying on the
    YAML content alone resolved those runs to "unknown" and defeated both
    dedupe guards in create_eval_record_from_state (they keyed on a name
    that never matched the real record), producing one phantom eval record
    per boot completion."""
    if not rel_path:
        return None
    m = _STATE_YAML_PATH_RE.search(rel_path.replace("\\", "/"))
    return m.group(1) if m else None


def resolve_workflow_name(state_data: dict, rel_path: str | None = None) -> str | None:
    """Resolve the workflow name for a state.yaml write. Path first
    (authoritative — always present in the tool payload), YAML `workflow:`
    field as fallback. Returns None when neither yields a name; callers
    must treat None as unresolvable, not coerce it to "unknown" — a record
    the harness cannot identify has zero eval value."""
    name = workflow_name_from_path(rel_path)
    if name:
        return name
    name = state_data.get("workflow")
    if name and name != "unknown":
        return name
    return None


def find_active_eval_record(session_id: str) -> Path | None:
    """Find the most recent in-progress eval record for this session."""
    try:
        if not EVAL_RUNS_DIR.exists():
            return None

        records = []
        for f in EVAL_RUNS_DIR.glob("eval-*.json"):
            try:
                with open(f, "r") as file:
                    data = json.load(file)
                if data.get("session_id") == session_id and data.get("status") == "in-progress":
                    records.append((f, data.get("started", "")))
            except Exception:
                continue

        if records:
            records.sort(key=lambda x: x[1], reverse=True)
            return records[0][0]
    except Exception as e:
        log_error(f"Failed to find eval record: {e}")
    return None


def find_completed_eval_record(workflow_name: str, session_id: str,
                               run_started: "datetime | None" = None,
                               alt_session_id: str | None = None) -> Path | None:
    """Find any completed (non-in-progress) eval record for this workflow that
    belongs to the SAME RUN the caller is about to record.

    A record counts as the same run when ANY of these holds:
      - its session_id matches the caller's session_id (harness flavor), or
      - its session_id matches alt_session_id (the sessions-index flavor —
        close-eval-record.py historically resolved that flavor, so the
        authoritative record for this run may live under it), or
      - its `started` falls within the current run's window
        ([run_started - SAME_RUN_WINDOW_TOLERANCE, now]).

    The window clause is what catches same-run records written under a
    session-id flavor the caller has never seen; it deliberately does NOT
    extend to the whole UTC day, so a genuinely separate earlier run of the
    same workflow (its record started well before this run's window) still
    allows a second, legitimate record. Returns the most recent match, or
    None if none exists.
    """
    try:
        if not EVAL_RUNS_DIR.exists():
            return None

        window_start = None
        if run_started is not None:
            from datetime import timedelta
            window_start = run_started - timedelta(seconds=SAME_RUN_WINDOW_TOLERANCE_SECONDS)

        records = []
        for f in EVAL_RUNS_DIR.glob("eval-*.json"):
            try:
                with open(f, "r") as file:
                    data = json.load(file)
                if (data.get("name") != workflow_name
                        or data.get("status") == "in-progress"):
                    continue
                same_session = data.get("session_id") == session_id
                same_alt = bool(alt_session_id) and data.get("session_id") == alt_session_id
                in_window = False
                if window_start is not None and data.get("started"):
                    rec_started = parse_ts_assume_utc(data.get("started"))
                    if rec_started is not None and rec_started >= window_start:
                        in_window = True
                if same_session or same_alt or in_window:
                    records.append((f, data.get("started", "")))
            except Exception:
                continue

        if records:
            records.sort(key=lambda x: x[1], reverse=True)
            return records[0][0]
    except Exception as e:
        log_error(f"Failed to find completed eval record: {e}")
    return None

def infer_trigger(state_data: dict) -> str:
    """Infer trigger from state.yaml content."""
    # state.yaml may have an explicit trigger field
    trigger = state_data.get("trigger")
    if trigger in ("scheduled", "manual", "boot"):
        return trigger
    # Infer from original_request or session context
    # Use (... or "") to handle None values in the state_data
    original_request = (state_data.get("original-request") or "").lower()
    if "scheduled" in original_request or "auto" in original_request:
        return "scheduled"
    if "boot" in original_request:
        return "boot"
    return "manual"


def new_eval_id() -> str:
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%dT%H%M%S")
    suffix = "".join(secrets.choice(ALPHABET) for _ in range(6))
    return f"eval-{ts}-{suffix}"


def workflow_version_hash(workflow_name: str) -> str | None:
    """Compute a short SHA256 of the workflow.md at execution time."""
    candidate = IES_ROOT / "workflows" / workflow_name / "workflow.md"
    if candidate.exists():
        return hashlib.sha256(candidate.read_bytes()).hexdigest()[:16]
    return None


def skill_version_hash(skill_name: str) -> str | None:
    """Compute a short SHA256 of the skill's SKILL.md at execution time."""
    # Skills live in .claude/skills/ or skills/
    for candidate in [
        IES_ROOT / ".claude" / "skills" / skill_name / "SKILL.md",
        IES_ROOT / "skills" / skill_name / "SKILL.md",
    ]:
        if candidate.exists():
            return hashlib.sha256(candidate.read_bytes()).hexdigest()[:16]
    return None


ASSERTIONS_DIR = IES_ROOT / "systems" / "eval-harness" / "assertions"


def run_assertions(name: str, eval_record: dict) -> dict:
    """Load and evaluate assertions for a workflow or skill.

    Thin delegator to the canonical implementation in assertion_checks.py,
    shared with eval-agent-stop.py and grade_skill_run.py so all three
    callers evaluate identically. Returns the original structural dict
    unchanged if the shared module failed to import or no assertion file
    exists for the given name.
    """
    structural = eval_record.get("assessment", {}).get("structural", {
        "expected_outputs_written": None,
        "outputs_non_empty": None,
        "assertions_checked": 0,
        "assertions_passed": 0,
        "assertion_results": []
    })

    if _assertion_checks is None:
        log_error("run_assertions: assertion_checks module unavailable, skipping")
        return structural

    return _assertion_checks.run_assertions(
        assertions_dir=ASSERTIONS_DIR,
        name=name,
        eval_record=eval_record,
        ies_root=IES_ROOT,
        agent=eval_record.get("agent"),
        transcript_path=None,  # not available at PostToolUse hook time
        yaml_module=yaml,
        log_error=log_error,
    )


def create_eval_record_from_skill_run(skill_run_data: dict, session_id: str):
    """Create a complete eval record when a skill writes its skill-runs JSON signal file."""
    try:
        EVAL_RUNS_DIR.mkdir(parents=True, exist_ok=True)

        skill_name = skill_run_data.get("skill", "unknown")
        agent = skill_run_data.get("agent", "unknown")
        trigger = skill_run_data.get("trigger", "manual")
        status_raw = skill_run_data.get("status", "success")
        # Normalize status to eval harness values
        status = status_raw if status_raw in ("success", "partial", "failure", "aborted") else "success"

        now = datetime.now(timezone.utc)
        completed_iso = now.isoformat().replace("+00:00", "Z")

        started_raw = skill_run_data.get("started")
        if started_raw:
            try:
                started_dt = datetime.fromisoformat(str(started_raw).replace("Z", "+00:00"))
                if started_dt.tzinfo is None:
                    started_dt = started_dt.replace(tzinfo=timezone.utc)
                started_iso = started_dt.isoformat().replace("+00:00", "Z")
            except ValueError:
                from datetime import timedelta
                started_dt = now - timedelta(seconds=60)
                started_iso = started_dt.isoformat().replace("+00:00", "Z")
        else:
            from datetime import timedelta
            started_dt = now - timedelta(seconds=60)
            started_iso = started_dt.isoformat().replace("+00:00", "Z")

        duration = max(0, round((now - started_dt).total_seconds(), 1))
        eval_id = new_eval_id()
        vhash = skill_version_hash(skill_name)

        record = {
            "id": eval_id,
            "type": "skill",
            "name": skill_name,
            "agent": agent,
            "session_id": session_id,
            "trigger": trigger,
            "started": started_iso,
            "completed": completed_iso,
            "duration_seconds": duration,
            "status": status,
            "steps": [],
            "assessment": {
                "mechanical": {
                    "completed": status in ("success", "partial"),
                    "all_steps_finished": status == "success",
                    "tool_failures": skill_run_data.get("tool_failures", 0),
                    "error_ids": skill_run_data.get("error_ids", [])
                },
                "structural": {
                    "expected_outputs_written": None,
                    "outputs_non_empty": None,
                    "assertions_checked": 0,
                    "assertions_passed": 0,
                    "assertion_results": []
                },
                "grading": {
                    "last_graded": None,
                    "grade": None,
                    "grader_notes": None
                },
                "controller_feedback": {
                    "rating": None,
                    "comment": None,
                    "timestamp": None
                }
            },
            "version_hash": vhash,
            "prior_baseline_id": None,
            "tags": ["cowork-hook", "skill"]
        }

        # Run structural assertions and merge results
        record["assessment"]["structural"] = run_assertions(skill_name, record)

        path = EVAL_RUNS_DIR / f"{eval_id}.json"
        atomic_write_json(path, record)
    except Exception as e:
        log_error(f"Failed to create eval record from skill-run signal: {e}")


def create_eval_record_from_state(state_data: dict, session_id: str, rel_path: str | None = None):
    """Create a complete eval record when state.yaml reaches status: complete
    and no in-progress stub exists (Cowork path — SubagentStart hook never fired).

    Guard: if a completed record already exists for this workflow + session, or if
    steps would be empty and this appears to be a duplicate cowork-hook trigger,
    skip creation and log a warning instead of writing a phantom record.
    """
    try:
        EVAL_RUNS_DIR.mkdir(parents=True, exist_ok=True)

        # Name resolution: the state.yaml PATH is authoritative (boot's
        # state.yaml has no `workflow:` field at all — resolving from YAML
        # alone produced "unknown", which never matched the real record's
        # name in GUARD 1/2 below, so every boot completion wrote a phantom.
        # 2026-09-18: three phantom-candidates and one orphan in one day).
        workflow_name = resolve_workflow_name(state_data, rel_path)
        if workflow_name is None:
            # Never write a record named "unknown" — the harness cannot
            # identify it, it cannot be deduped, and its only observable
            # effect is polluting the grade distribution (two graded F by
            # the Tier 3 sweep on 2026-09-18).
            log_error(
                f"[GUARD] Refused to create workflow eval record for session='{session_id}' "
                f"— workflow name unresolvable from both state.yaml path ({rel_path!r}) "
                f"and YAML content. No record written."
            )
            return

        agent = state_data.get("agent", "unknown")
        trigger = infer_trigger(state_data)

        now = datetime.now(timezone.utc)
        completed_iso = now.isoformat().replace("+00:00", "Z")

        # Resolve this run's start BEFORE the dedupe guards — GUARD 1 uses it
        # as the same-run window. Use session-started time if available; fall
        # back to now-60s.
        session_started = state_data.get("session-started")
        started_dt = parse_ts_assume_utc(session_started) if session_started else None
        if started_dt is not None:
            started_iso = started_dt.isoformat().replace("+00:00", "Z")
        else:
            from datetime import timedelta
            started_dt = now - timedelta(seconds=60)
            started_iso = started_dt.isoformat().replace("+00:00", "Z")

        # The other session-id flavor this run's authoritative record might
        # live under: close-eval-record.py historically resolved the sessions
        # -index id (e.g. "session-2026-09-18-115915") while hooks carry the
        # harness id — the two-flavor split that let the 2026-09-18
        # daily-review phantom past GUARD 1.
        alt_session_id = None
        try:
            index = read_index()
            if index:
                candidate = index[-1].get("id")
                if candidate and candidate != session_id:
                    alt_session_id = candidate
        except Exception:
            pass

        # GUARD 1: Check for an existing completed record for this workflow + same run.
        # close-eval-record.py (invoked by workflow final steps) writes a proper record
        # with steps populated. If that already exists, this cowork-hook path would
        # produce a duplicate phantom with steps: [] — skip it. Matching is by session
        # id (either flavor) OR by same-run start window, never by bare same-day name,
        # so a genuine second run of the workflow later in the day still gets recorded.
        existing = find_completed_eval_record(
            workflow_name, session_id,
            run_started=started_dt, alt_session_id=alt_session_id)
        if existing is not None:
            log_error(
                f"[GUARD] Skipped phantom workflow eval creation for '{workflow_name}' "
                f"session='{session_id}': completed record already exists at {existing.name}. "
                f"This was a cowork-hook state.yaml trigger that would have produced steps: []."
            )
            return

        # GUARD 2: Check for a still-open (in-progress) turn-level record for
        # this workflow, regardless of session_id. GUARD 1 alone missed
        # exactly this case in a real incident (eval-20260828T160656-FE6XZW):
        # eval-turn-start.py had already opened a genuine turn-level record
        # for this workflow (eval-20260828T154249-UQX5N6), but it was still
        # in-progress at the moment this PostToolUse fired — its own Stop
        # hook (eval-turn-stop.py) didn't finalize it until 14 seconds later.
        # find_completed_eval_record only matches non-in-progress records, so
        # it saw nothing to dedupe against and this path went ahead and wrote
        # a second, phantom "completed" record for the same workflow run.
        # This is a genuine race between two independent hook triggers
        # (PostToolUse here vs. the Stop hook that owns finalization) — the
        # fix is to back off and let the real record finalize on its own
        # rather than racing it, not to guess/estimate anything here.
        if open_turn_level_record_exists and open_turn_level_record_exists(workflow_name):
            log_error(
                f"[GUARD] Skipped phantom workflow eval creation for '{workflow_name}' "
                f"session='{session_id}': a turn-level record for this workflow is still "
                f"in-progress (opened by eval-turn-start.py). Backing off so eval-turn-stop.py "
                f"can finalize the real record instead of racing it with a duplicate."
            )
            return

        # (started_dt / started_iso / now / completed_iso were resolved above
        # GUARD 1 — the guard needs this run's start as its same-run window.
        # Naive session-started values are assumed UTC by parse_ts_assume_utc;
        # previously a naive timestamp raised TypeError on the duration
        # subtraction and the outer try/except swallowed it — the record
        # silently never got written.)
        duration = max(0, round((now - started_dt).total_seconds(), 1))
        eval_id = new_eval_id()
        vhash = workflow_version_hash(workflow_name)

        record = {
            "id": eval_id,
            "type": "workflow",
            "name": workflow_name,
            "agent": agent,
            "session_id": session_id,
            "trigger": trigger,
            "started": started_iso,
            "completed": completed_iso,
            "duration_seconds": duration,
            "status": "success",  # state.yaml complete = mechanical success
            "steps": [],
            "assessment": {
                "mechanical": {
                    "completed": True,
                    "all_steps_finished": True,
                    "tool_failures": 0,
                    "error_ids": []
                },
                "structural": {
                    "expected_outputs_written": None,
                    "outputs_non_empty": None,
                    "assertions_checked": 0,
                    "assertions_passed": 0,
                    "assertion_results": []
                },
                "grading": {
                    "last_graded": None,
                    "grade": None,
                    "grader_notes": None
                },
                "controller_feedback": {
                    "rating": None,
                    "comment": None,
                    "timestamp": None
                }
            },
            "version_hash": vhash,
            "prior_baseline_id": None,
            "tags": ["cowork-hook"]
        }

        # Run structural assertions and merge results
        record["assessment"]["structural"] = run_assertions(workflow_name, record)

        # GUARD: steps are ALWAYS empty on this path (they only get populated
        # into an already-open in-progress record via the step-frontmatter
        # branch of process_eval_harness; this function creates the record at
        # completion time, after any such window). The old behavior tagged
        # these "phantom-candidate" but still wrote them into the main runs
        # dir — a label, not a guard — where they were picked up by the
        # Tier 3 grading sweep and the success-rate math and distorted both
        # (2026-09-18 incident). The legitimate Cowork coverage case (a
        # workflow that completes with no close-eval-record.py call and no
        # turn-level record) still depends on this record existing, so it is
        # not dropped — it is quarantined to runs/_phantoms/ instead, with
        # its correctly-resolved name, where every metrics/grading reader
        # (non-recursive globs + phantom-candidate tag filters) ignores it
        # but it remains on disk for diagnosis. The authoritative record for
        # a properly instrumented workflow arrives via close-eval-record.py
        # or eval-turn-stop.py into the main runs dir as before.
        if not record.get("steps"):
            record["tags"] = list(set(record.get("tags", [])) | {"phantom-candidate"})
            EVAL_PHANTOMS_DIR.mkdir(parents=True, exist_ok=True)
            path = EVAL_PHANTOMS_DIR / f"{eval_id}.json"
            log_error(
                f"[GUARD] Quarantined cowork-hook workflow eval for '{workflow_name}' "
                f"session='{session_id}' to _phantoms/{eval_id}.json — steps: [] means this "
                f"path cannot produce a verifiable record. If this workflow SHOULD have an "
                f"authoritative record in runs/, have its final step call close-eval-record.py."
            )
        else:
            path = EVAL_RUNS_DIR / f"{eval_id}.json"
        atomic_write_json(path, record)
    except Exception as e:
        log_error(f"Failed to create eval record from state.yaml: {e}")


def update_eval_record_state_yaml(eval_path: Path, file_path: str, content: str) -> bool:
    """Update eval record with workflow lifecycle info from state.yaml.

    Returns True if the record was updated, False if it declined to touch it
    (name conflict — see below) so the caller can fall through to creating a
    fresh record instead of silently overwriting an unrelated one.
    """
    try:
        with open(eval_path, "r") as f:
            eval_record = json.load(f)

        # Parse the state.yaml content (strip the --- wrapper first — see
        # extract_frontmatter_block docstring for why this is required)
        state_data = yaml.safe_load(extract_frontmatter_block(content))
        if not state_data:
            return True  # nothing to apply, but not a conflict — don't fall through

        # Path-derived name is authoritative (boot's state.yaml carries no
        # `workflow:` field); YAML field is the fallback. If neither resolves,
        # keep the record's existing name rather than stamping "unknown".
        workflow_name = (
            resolve_workflow_name(state_data, file_path)
            or eval_record.get("name")
            or "unknown"
        )

        # Guard: find_active_eval_record() matches on session_id alone, not
        # workflow name. If the global session index hasn't rotated (a stale
        # session_id shared across many unrelated real-world sessions — see
        # err-tracking for the boot staleness issue this correlates with),
        # this record may belong to a DIFFERENT workflow/agent that just
        # hasn't been marked complete yet. Overwriting its name/type here
        # would silently erase that record's identity. If the record already
        # has an established name that disagrees with this state.yaml's
        # workflow, decline and let the caller create a fresh record.
        existing_name = eval_record.get("name")
        existing_type = eval_record.get("type")
        name_disagrees = existing_name and existing_name not in (None, "unknown", workflow_name)
        # Decline whenever the found record is a `type: "agent"` stub too —
        # not just when it's a `type: "workflow"` record with a disagreeing
        # name. find_active_eval_record() picks the single most-recently-
        # started in-progress record for this session_id with no type
        # filter, so a subagent's own agent-type stub (e.g. Knox's
        # plaud-ingest fork, opened by eval-agent-start.py under the SAME
        # session_id as boot's turn-level record — now guaranteed true
        # session-wide since the session_id fix) can be "the most recent"
        # candidate at the moment boot's state.yaml write fires. Without
        # this, the block below would silently relabel that unrelated
        # agent's stub as `type: "workflow", name: "boot"`, corrupting it.
        if name_disagrees and existing_type == "workflow":
            log_error(
                f"[GUARD] update_eval_record_state_yaml declined to overwrite "
                f"{eval_path.name} — existing name={existing_name!r} disagrees with "
                f"state.yaml workflow={workflow_name!r}. Likely a stale/shared session_id. "
                f"Falling through to a fresh record for {workflow_name!r}."
            )
            return False
        if existing_type == "agent":
            log_error(
                f"[GUARD] update_eval_record_state_yaml declined to overwrite "
                f"{eval_path.name} — existing type='agent' (a subagent's own stub, "
                f"name={existing_name!r}), not a workflow turn-level record. "
                f"Falling through to a fresh/cowork record for {workflow_name!r}."
            )
            return False

        # Update eval record with workflow lifecycle info
        eval_record["type"] = "workflow"
        eval_record["name"] = workflow_name
        eval_record["trigger"] = infer_trigger(state_data)

        # Update mechanical assessment based on state
        status = state_data.get("status")
        if status == "complete":
            eval_record["assessment"]["mechanical"]["completed"] = True
        elif status in ["in-progress", "not-started"]:
            eval_record["assessment"]["mechanical"]["completed"] = False

        # Write updated eval record atomically
        atomic_write_json(eval_path, eval_record)
        return True
    except Exception as e:
        log_error(f"Failed to update eval record from state.yaml: {e}")
        return True  # don't trigger the fallback path on an unrelated error

def update_eval_record_step_frontmatter(eval_path: Path, file_path: str, content: str, transcript_path: str = None):
    """Update eval record with step timing from step frontmatter.

    NOTE: Token extraction happens in .claude/hooks/step-complete.py, NOT here.
    This hook runs during step execution when transcripts may not be complete.
    We only create the step skeleton with timing/status; step-complete.py
    populates tokens after the step fully completes.
    """
    try:
        with open(eval_path, "r") as f:
            eval_record = json.load(f)

        # Parse YAML frontmatter (between --- markers)
        lines = content.split("\n")
        frontmatter_lines = []
        in_frontmatter = False
        for line in lines:
            if line.strip() == "---":
                in_frontmatter = not in_frontmatter
                if not in_frontmatter:
                    break
                continue
            if in_frontmatter:
                frontmatter_lines.append(line)

        if not frontmatter_lines:
            return

        frontmatter = yaml.safe_load("\n".join(frontmatter_lines))
        if not frontmatter:
            return

        # Extract step name from file path
        step_name = Path(file_path).name

        # Create or update step entry (tokens left null for step-complete.py to populate)
        step_entry = {
            "name": step_name,
            "started": frontmatter.get("started-at"),
            "completed": frontmatter.get("completed-at"),
            "duration_seconds": None,
            "status": frontmatter.get("status"),
            "data_sources_used": frontmatter.get("data_sources_used", []),
            "data_source_failures": frontmatter.get("data_source_failures", []),
            "model": frontmatter.get("model"),
            "tokens_input": None,
            "tokens_output": None,
            "cost_usd": None
        }

        # Calculate duration if both timestamps exist
        if step_entry["started"] and step_entry["completed"]:
            try:
                start = datetime.fromisoformat(step_entry["started"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(step_entry["completed"].replace("Z", "+00:00"))
                step_entry["duration_seconds"] = round((end - start).total_seconds(), 2)
            except Exception:
                pass

        # Add or update step in eval record (no token extraction here)
        eval_record["steps"] = [s for s in eval_record.get("steps", []) if s["name"] != step_name]
        eval_record["steps"].append(step_entry)

        # Update mechanical assessment for step completion
        if frontmatter.get("status") == "complete":
            # Count completed steps vs total steps (simplified)
            eval_record["assessment"]["mechanical"]["all_steps_finished"] = True

        # Write updated eval record atomically
        atomic_write_json(eval_path, eval_record)
    except Exception as e:
        log_error(f"Failed to update eval record from step frontmatter: {e}")

def check_error_tracking_write(file_path: str, session_id: str):
    """Check if this write is to error-tracking and update eval record.

    Only correlates the error onto a record that shows genuine evidence of
    that workflow actually executing this session (non-empty steps[] or
    subagents[], or a Tier-1 mechanical assessment already recorded). A
    bare record with none of that — e.g. one opened speculatively by
    eval-turn-start.py's 'boot-first-prompt-of-session' heuristic, where
    the workflow it guessed at never actually ran — is not evidence the
    error has anything to do with that workflow. Blindly stamping
    status: failure onto whatever in-progress record happens to share this
    session_id previously turned an unrelated error (from a completely
    different task running in the same session) into a fabricated boot
    failure. See err-20260829T161711-3IPMKR."""
    try:
        if "error-tracking/entries" not in file_path:
            return

        eval_path = find_active_eval_record(session_id)
        if not eval_path:
            return

        # Extract error ID from filename
        error_id = Path(file_path).stem

        with open(eval_path, "r") as f:
            eval_record = json.load(f)

        mechanical = eval_record.get("assessment", {}).get("mechanical", {})
        has_real_activity = (
            bool(eval_record.get("steps"))
            or bool(eval_record.get("subagents"))
            or mechanical.get("completed") is not None
        )
        if not has_real_activity:
            log_error(
                f"[INFO] Skipping error correlation of {error_id} onto {eval_record.get('id')} "
                f"('{eval_record.get('name')}') — record has no steps/subagents/mechanical "
                "assessment yet, so this error can't be attributed to that workflow"
            )
            return

        # Add error ID to mechanical assessment
        if error_id not in eval_record["assessment"]["mechanical"]["error_ids"]:
            eval_record["assessment"]["mechanical"]["error_ids"].append(error_id)

        # Update status to failure if error was logged
        eval_record["status"] = "failure"

        # Write updated record atomically
        atomic_write_json(eval_path, eval_record)
    except Exception as e:
        log_error(f"Failed to check error tracking write: {e}")

def process_eval_harness(rel_path: str, file_path: str, session_id: str, transcript_path: str = None):
    """Process eval harness integration for this file write."""
    # Check if this is a state.yaml write
    if rel_path.endswith("state.yaml"):
        try:
            with open(file_path, "r") as f:
                content = f.read()
        except Exception as e:
            log_error(f"Failed to read state.yaml for eval: {e}")
            content = None

        if content:
            # Extract workflow name and status for logging
            try:
                state_data = yaml.safe_load(extract_frontmatter_block(content)) or {}
                workflow_name = resolve_workflow_name(state_data, rel_path) or "unknown"
                status = state_data.get("status", "unknown")
                log_error(f"[EVAL-HARNESS] Processing state.yaml write: workflow={workflow_name}, status={status}, session_id={session_id}")
            except Exception:
                pass

            eval_path = find_active_eval_record(session_id)
            updated = False
            if eval_path:
                # Claude Code path: close the existing stub — unless the stub
                # belongs to a different, already-named workflow (stale/shared
                # session_id), in which case fall through to the Cowork path
                # below rather than overwriting an unrelated record.
                log_error(f"[EVAL-HARNESS] Found active eval record: {eval_path.name}")
                updated = update_eval_record_state_yaml(eval_path, rel_path, content)
                log_error(f"[EVAL-HARNESS] Update result: {updated}")
            if not eval_path or not updated:
                # Cowork path: no SubagentStart hook fired — create record on complete
                try:
                    state_data = yaml.safe_load(extract_frontmatter_block(content)) or {}
                    if state_data.get("status") == "complete":
                        log_error(f"[EVAL-HARNESS] Creating new eval record (cowork path) for {workflow_name}")
                        create_eval_record_from_state(state_data, session_id, rel_path=rel_path)
                except Exception as e:
                    log_error(f"Failed to parse state.yaml for eval creation: {e}")

    # Check if this is a step frontmatter write
    elif "/steps/" in rel_path and rel_path.endswith(".md"):
        eval_path = find_active_eval_record(session_id)
        if eval_path:
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                update_eval_record_step_frontmatter(eval_path, rel_path, content, transcript_path)
            except Exception as e:
                log_error(f"Failed to read step frontmatter for eval: {e}")

    # Check if this is a skill-run signal write
    elif "eval-harness/skill-runs/" in rel_path and rel_path.endswith(".json"):
        try:
            with open(file_path, "r") as f:
                skill_run_data = json.load(f)
            create_eval_record_from_skill_run(skill_run_data, session_id)
        except Exception as e:
            log_error(f"Failed to create eval record from skill-run write: {e}")

    # Check if this is an error-tracking write
    check_error_tracking_write(rel_path, session_id)

def get_session_id(payload: dict | None = None) -> str:
    """Prefer the harness-native `session_id` off this hook's own stdin
    payload (PostToolUse carries it per Claude Code's documented hook
    schema — guaranteed present, stable for the whole session). Falls back
    to memory/sessions/index.json's `id` field only if the payload has none.

    Root-cause note: this function previously always read
    memory/sessions/index.json's `id` field, while eval-turn-start.py /
    eval-agent-start.py (via hook_utils.infer_session_id) read the
    `started` field instead — two independent implementations disagreeing
    on which field means "the session id" for the exact same session
    record. That's what produced eval-20260828T140308-WL89IY (opened here,
    via create_eval_record_from_state, under the `id`-format session_id)
    as an unlinked duplicate of eval-20260828T135817-P00Y9T (opened by
    eval-turn-start.py under the `started`-format session_id) for the same
    real boot run. Delegating to the same shared helper as the other hooks
    closes that gap."""
    if _shared_infer_session_id:
        try:
            return _shared_infer_session_id(payload)
        except Exception as e:
            log_error(f"shared infer_session_id failed in get_session_id: {e}")
    if payload:
        sid = payload.get("session_id")
        if sid:
            return sid
    index = read_index()
    if not index:
        log_error("Session index is empty or missing")
        return ""
    return index[-1].get("id", "")

# ============================================================================
# MAIN HOOK ENTRY POINT
# ============================================================================

def main():
    """Main hook logic - routes to session index or eval harness based on file type."""
    payload = read_stdin()

    # Extract tool info
    tool_name = payload.get("tool_name")
    tool_input = payload.get("tool_input", {})
    file_path = tool_input.get("file_path")
    transcript_path = payload.get("transcript_path")

    # Only process Write and Edit tools
    if tool_name not in ["Write", "Edit"] or not file_path:
        return  # Silent exit for non-matching tools

    # Normalize the file path
    rel_path = normalize_path(file_path)

    # Block 1: Session Index Update (best-effort, independent of eval harness)
    update_session_index(rel_path)

    # Block 2: Eval Harness Integration (independent of session index)
    session_id = get_session_id(payload)
    process_eval_harness(rel_path, file_path, session_id, transcript_path)

if __name__ == "__main__":
    main()
