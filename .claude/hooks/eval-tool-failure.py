#!/usr/bin/env python3
"""
PostToolUseFailure Hook: Tool Failure Logging
Triggered when a tool call fails.
Logs tool failures to the active eval record for Tier 1 mechanical assessment.
"""

import json
import sys
import fcntl
from pathlib import Path
from datetime import datetime

# Configuration — IES_ROOT from env var, fallback to default
IES_ROOT = Path(__file__).resolve().parents[2]
EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"
ERROR_LOG = Path("/tmp/ies-hook-errors.log")

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

def classify_tool_failure(tool_name, error) -> str:
    """Classify a failed tool call: a benign existence probe or a real failure.

    Root cause (reviews/boot-root-cause-2026-11-05.md, fix 5): the finalize
    rules turn `tool_failures > 0` into `partial`, but the counter counted
    EVERY failed call — including the routine check-then-create probes the
    workflows themselves treat as expected. Four genuinely complete boots
    (2026-10-30, 11-02, 11-03, 11-04) closed `partial` on exactly these:

      - Read on a file that doesn't exist yet (the standard probe before
        creating/checking a file) — error text "File does not exist."
      - Outlook MCP folder lookup against a deliberately non-existent
        folder name (auth capability probe) — error carries
        "code": "NOT_FOUND".

    Benign classes return a classification label and are still logged in
    tool_failure_log (audit trail intact) but do NOT increment
    tool_failures, so `partial` keeps signal: it now means a real failure
    happened, not that a workflow probed the filesystem. Anything that
    doesn't match a benign class is "real" and counts as before.
    """
    err = str(error)
    lowered = err.lower()
    if tool_name == "Read" and (
            "file does not exist" in lowered
            or "no such file or directory" in lowered
            or "enoent" in lowered
            or "not found" in lowered):
        return "file-not-found-probe"
    if str(tool_name).startswith("mcp__") and "not_found" in lowered:
        # MCP existence probes surface the connector's NOT_FOUND error code
        # (e.g. outlook_email_search against a deliberately fake folder).
        return "existence-probe"
    return "real"


def main():
    """Main hook logic."""
    payload = read_stdin()

    # Extract tool failure info from PostToolUseFailure hook
    tool_name = payload.get("tool_name")
    error = payload.get("error")
    duration_ms = payload.get("duration_ms")

    if not tool_name or not error:
        log_error("PostToolUseFailure hook missing tool_name or error")
        return

    # PostToolUseFailure carries `session_id` on its payload just like every
    # other Claude Code hook event does — this used to be assumed absent
    # ("this hook doesn't provide it directly") and fell straight to a
    # global "most recent in-progress record" scan, which can misattribute
    # a tool failure to an unrelated in-progress record (e.g. another
    # session's still-open turn-level record) when more than one is open
    # at once. Scope to this session first; only fall back to the old
    # global scan if the payload has no session_id for some reason.
    session_id = payload.get("session_id")

    eval_path = None
    try:
        if EVAL_RUNS_DIR.exists():
            records = []
            session_records = []
            for f in EVAL_RUNS_DIR.glob("eval-*.json"):
                try:
                    with open(f, "r") as file:
                        data = json.load(file)
                    if data.get("status") == "in-progress":
                        records.append((f, data.get("started", "")))
                        if session_id and data.get("session_id") == session_id:
                            session_records.append((f, data.get("started", "")))
                except Exception:
                    continue

            preferred = session_records if session_records else records
            if preferred:
                preferred.sort(key=lambda x: x[1], reverse=True)
                eval_path = preferred[0][0]
    except Exception as e:
        log_error(f"Failed to find eval record: {e}")
        return

    if not eval_path:
        return  # No active eval record, silent exit

    # Read and update eval record
    try:
        with open(eval_path, "r") as f:
            eval_record = json.load(f)

        # Classify before counting (see classify_tool_failure): benign
        # existence probes are logged for audit but do not increment
        # tool_failures, so the finalize rule `tool_failures > 0 -> partial`
        # stops firing on routine probes.
        classification = classify_tool_failure(tool_name, error)
        mech = eval_record["assessment"]["mechanical"]
        if classification == "real":
            mech["tool_failures"] = mech.get("tool_failures", 0) + 1
        else:
            mech["benign_tool_failures"] = mech.get("benign_tool_failures", 0) + 1

        # Build failure entry and attach to eval record
        failure_entry = {
            "tool": tool_name,
            "error": str(error),
            "duration_ms": duration_ms,
            "timestamp": datetime.now().isoformat(),
            "classification": classification,
        }
        if "tool_failure_log" not in mech:
            mech["tool_failure_log"] = []
        mech["tool_failure_log"].append(failure_entry)

        # Write updated eval record atomically
        atomic_write_json(eval_path, eval_record)
    except Exception as e:
        log_error(f"Failed to update eval record with tool failure: {e}")

if __name__ == "__main__":
    main()
