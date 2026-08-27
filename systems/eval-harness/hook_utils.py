#!/usr/bin/env python3
"""
Shared helpers for .claude/hooks/*.py eval-harness hooks.

Extracted so the turn-level lifecycle hooks (eval-turn-start.py, eval-turn-stop.py)
and the existing subagent-level hooks (eval-agent-start.py, eval-agent-stop.py,
post-tool-use.py, step-complete.py) don't each carry their own copy of the same
atomic-write / session-id / eval-record-lookup logic. Existing hooks keep their
own inlined copies (they predate this module and work) — new hooks import from
here.
"""

import json
import sys
import secrets
import string
import fcntl
from pathlib import Path
from datetime import datetime, timezone

# systems/eval-harness/hook_utils.py -> parents[2] is IES root
IES_ROOT = Path(__file__).resolve().parents[2]
EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"
SESSION_INDEX_PATH = IES_ROOT / "memory" / "sessions" / "index.json"
ERROR_LOG = Path("/tmp/ies-hook-errors.log")
ALPHABET = string.ascii_uppercase + string.digits


def log_error(msg: str, tag: str = "HOOK"):
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] [{tag}] [ERROR] {msg}\n")
    except Exception:
        pass


def log_info(msg: str, tag: str = "HOOK"):
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] [{tag}] [INFO] {msg}\n")
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
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError as e:
        log_error(f"Failed to parse stdin JSON: {e}")
        return {}


def new_eval_id() -> str:
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%dT%H%M%S")
    suffix = "".join(secrets.choice(ALPHABET) for _ in range(6))
    return f"eval-{ts}-{suffix}"


def infer_session_id() -> str:
    """Read current session ID from memory/sessions/index.json, creating a
    session record if none exists yet so no eval record is ever orphaned.
    Mirrors eval-agent-start.py's infer_session_id — kept in sync by hand
    since that hook predates this module."""
    try:
        index = []
        if SESSION_INDEX_PATH.exists():
            with open(SESSION_INDEX_PATH, "r") as f:
                index = json.load(f)

        if index:
            # memory/sessions/index.json's real schema is
            # {started, closed, current_topic, topics} — there has never
            # been an "id" field (42 real records on disk, none have one).
            # "started" is already a unique-enough key per session record;
            # do not add an "id" field just to work around this.
            last = index[-1].get("started", "")
            if last:
                return last

        now = datetime.now(timezone.utc)
        session_id = now.isoformat().replace("+00:00", "Z")
        new_session = {
            "started": session_id,
            "closed": None,
            "current_topic": None,
            "topics": []
        }
        index.append(new_session)
        SESSION_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_json(SESSION_INDEX_PATH, index)
        log_info(f"Created session {session_id} for eval tracking")
        return session_id
    except Exception as e:
        log_error(f"Failed to infer or create session ID: {e}")
        now = datetime.now(timezone.utc)
        return f"session-{now.strftime('%Y-%m-%dT%H%M%S')}"


def find_records_for_session(session_id: str) -> list[Path]:
    """All eval-*.json files whose session_id matches, newest first."""
    if not session_id or not EVAL_RUNS_DIR.exists():
        return []
    records = []
    for f in EVAL_RUNS_DIR.glob("eval-*.json"):
        try:
            with open(f, "r") as file:
                data = json.load(file)
            if data.get("session_id") == session_id:
                records.append((f, data.get("started", "")))
        except Exception:
            continue
    records.sort(key=lambda x: x[1], reverse=True)
    return [r[0] for r in records]


def find_open_turn_record(session_id: str) -> Path | None:
    """Find the in-progress eval record opened by eval-turn-start.py for this
    session — identified by monitoring.active being true, not just by
    session_id + status (a subagent-level stub from eval-agent-start.py can
    also be in-progress under the same session_id)."""
    for f in find_records_for_session(session_id):
        try:
            with open(f, "r") as file:
                data = json.load(file)
            if data.get("status") == "in-progress" and data.get("monitoring", {}).get("active"):
                return f
        except Exception:
            continue
    return None
