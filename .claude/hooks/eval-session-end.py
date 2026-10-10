#!/usr/bin/env python3
"""
SessionEnd Hook: Eval Record Finalization
Triggered when a Claude Code session ends. Hands the open-eval-record
sweep to systems/eval-harness/close-open-evals.py — the canonical closer,
the same script CLAUDE.md's Exit Behavior step 1 runs interactively — so
hook-driven and interactive exits converge on one semantics: phantom
records (zero steps, zero subagents) deleted, real ones marked
incomplete with abort_reason "session-exit-normal". This hook's previous
inline sweep marked everything "aborted"/"session-ended", a divergent
second truth that predated the canonical script (2026-05-25).

DETACHED EXECUTION — the fix for the 2026-10-10 "Hook cancelled"
incident. The old hook read every eval-*.json in runs/ (900+ records on
OneDrive-synced storage) synchronously inside its own process lifetime.
A standard /exit still cancelled the hook mid-sweep — teardown is
impatient with SessionEnd hooks — and the session's records stayed open
(the exact failure this hook exists to prevent). The sweep now runs in a
DETACHED process (start_new_session=True): this hook only spawns it and
exits 0 immediately, so the sweep's completion no longer depends on the
hook process surviving session teardown. Fallbacks, in order: a
synchronous bounded subprocess.run if the detached spawn fails, then the
old inline abort-sweep if the canonical script is missing entirely.

Known and accepted: the detached sweep is not scoped to this session's
records (neither was the old inline sweep, nor close-open-evals.py
itself), so a SessionEnd firing while a separate live session has a
record legitimately in-progress would close that record too. Single-
controller usage makes this a non-issue in practice, and the phantom-
deletion guard in close-open-evals.py keeps false closes cheap.

Honors the IES_ROOT env var (same convention as skill_capture.py and
step-complete.py) so tests can point at a throwaway root without
touching the live harness.
"""

import json
import os
import subprocess
import sys
import fcntl
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parents[2]
IES_ROOT = Path(os.environ.get("IES_ROOT", REPO_ROOT))
EVAL_HARNESS_DIR = IES_ROOT / "systems" / "eval-harness"
EVAL_RUNS_DIR = EVAL_HARNESS_DIR / "runs"
CLOSE_SCRIPT = EVAL_HARNESS_DIR / "close-open-evals.py"
ERROR_LOG = Path("/tmp/ies-hook-errors.log")

TAG = "SESSION-END"


def log_error(msg: str):
    """Log error to /tmp/ies-hook-errors.log without blocking."""
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] [{TAG}] [ERROR] {msg}\n")
    except Exception:
        pass


def log_info(msg: str):
    """Log informational message to /tmp/ies-hook-errors.log."""
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] [{TAG}] [INFO] {msg}\n")
    except Exception:
        pass


def canonical_closer_available() -> bool:
    return CLOSE_SCRIPT.is_file() and EVAL_RUNS_DIR.is_dir()


def spawn_detached() -> bool:
    """Spawn close-open-evals.py detached (own session/process group) and
    return immediately. start_new_session=True is the whole point: the
    sweep survives the CLI cancelling or timing out this hook, because it
    is no longer in the hook's (or the CLI's) process group."""
    try:
        with open(ERROR_LOG, "a") as errf:
            subprocess.Popen(
                [sys.executable, str(CLOSE_SCRIPT), str(EVAL_RUNS_DIR)],
                stdin=subprocess.DEVNULL,
                stdout=errf,
                stderr=errf,
                start_new_session=True,
            )
        log_info("SessionEnd: spawned detached close-open-evals.py sweep")
        return True
    except Exception as e:
        log_error(f"detached spawn of close-open-evals.py failed: {e}")
        return False


def run_synchronous() -> bool:
    """Fallback when the detached spawn failed: run the canonical closer
    in the foreground with a bounded timeout. Same completion guarantee
    as the old hook at best (dies if cancelled) — strictly worse than
    detached, strictly better than nothing."""
    try:
        result = subprocess.run(
            [sys.executable, str(CLOSE_SCRIPT), str(EVAL_RUNS_DIR)],
            capture_output=True, text=True, timeout=120)
        if result.stdout.strip():
            log_info(f"SessionEnd sync sweep: {result.stdout.strip()}")
        return True
    except Exception as e:
        log_error(f"synchronous close-open-evals.py run failed: {e}")
        return False


def sweep_inline():
    """Last resort (canonical script missing): the pre-2026-10-10 inline
    behavior — mark every in-progress record aborted so nothing is left
    looking live. Kept atomically written as before."""
    aborted_count = 0
    for f in EVAL_RUNS_DIR.glob("eval-*.json"):
        try:
            with open(f, "r") as file:
                data = json.load(file)

            if data.get("status") == "in-progress":
                data["status"] = "aborted"
                data["completed"] = datetime.now().isoformat().replace("+00:00", "Z")
                if "assessment" not in data:
                    data["assessment"] = {}
                if "mechanical" not in data["assessment"]:
                    data["assessment"]["mechanical"] = {}
                data["assessment"]["mechanical"]["completed"] = False
                data["assessment"]["mechanical"]["abort_reason"] = "session-ended"

                tmp_path = f.with_suffix(".tmp")
                try:
                    with open(tmp_path, "w") as tf:
                        fcntl.flock(tf, fcntl.LOCK_EX)
                        json.dump(data, tf, indent=2)
                        fcntl.flock(tf, fcntl.LOCK_UN)
                    tmp_path.replace(f)
                except Exception as e:
                    log_error(f"atomic write failed for {f}: {e}")
                    if tmp_path.exists():
                        tmp_path.unlink(missing_ok=True)
                aborted_count += 1
        except Exception as e:
            log_error(f"Failed to finalize eval record {f}: {e}")

    if aborted_count > 0:
        log_info(f"SessionEnd inline sweep: marked {aborted_count} eval record(s) aborted")


def main():
    """Main hook logic: detached spawn -> sync run -> inline sweep."""
    if not EVAL_RUNS_DIR.exists():
        return

    if canonical_closer_available():
        if spawn_detached():
            return
        if run_synchronous():
            return
    sweep_inline()


if __name__ == "__main__":
    main()
