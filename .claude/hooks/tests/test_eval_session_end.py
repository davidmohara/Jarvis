#!/usr/bin/env python3
"""
Regression suite for the detached SessionEnd sweep (2026-10-10 "Hook
cancelled" incident). Plain asserts, runnable directly:
`python3 test_eval_session_end.py`.

Runs against a THROWAWAY IES_ROOT in a temp directory: the live harness
under systems/eval-harness/runs/ is never touched. The hook honors the
IES_ROOT env override (same convention as skill_capture.py), and the
canonical closer (close-open-evals.py) is copied into the temp root so
the hook's detached spawn exercises the real delegation path.

Chain under test: .claude/hooks/eval-session-end.py spawns
systems/eval-harness/close-open-evals.py detached
(start_new_session=True), so the sweep completes even when the CLI
cancels the hook process at session teardown — the exact failure mode
of 2026-10-10, where a standard /exit killed the old inline sweep
mid-run and left the session's eval records open.

Assertions, in order:
  1. Detached delegation: the hook exits 0 immediately, then (after a
     bounded wait) a seeded phantom record is DELETED and a seeded real
     record is marked incomplete / session-exit-normal — the canonical
     close-open-evals.py semantics, not the old aborted/session-ended
     ones.
  2. Idempotence: a second sweep (second hook run) is a no-op — the
     already-closed record is untouched.
  3. Last-resort fallback: with no close-open-evals.py in the temp
     root, the hook falls back to the inline abort sweep and still
     leaves no record in-progress.
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parents[1]
IES_ROOT = Path(__file__).resolve().parents[3]
EVAL_HARNESS_DIR = IES_ROOT / "systems" / "eval-harness"
HOOK = HOOKS_DIR / "eval-session-end.py"
CLOSE_SCRIPT = EVAL_HARNESS_DIR / "close-open-evals.py"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def seed_runs_dir(runs_dir: Path):
    """Two records: a phantom (no steps, no subagents) and a real one
    (steps + assessment.mechanical), both in-progress."""
    phantom = {
        "id": "eval-20260101T000000-PHANTM",
        "status": "in-progress",
        "session_id": "sess-test",
        "workflow": "boot",
        "steps": [],
        "subagents": [],
    }
    real = {
        "id": "eval-20260101T000000-REALREC",
        "status": "in-progress",
        "session_id": "sess-test",
        "workflow": "shutdown-cleanup",
        "steps": [{"step": "step-01", "status": "done"}],
        "subagents": [],
        "assessment": {"mechanical": {"completed": True}},
    }
    (runs_dir / f"{phantom['id']}.json").write_text(json.dumps(phantom, indent=2))
    (runs_dir / f"{real['id']}.json").write_text(json.dumps(real, indent=2))
    return phantom["id"], real["id"]


def run_hook(ies_root: Path):
    """Run the SessionEnd hook pointed at ies_root, empty stdin payload."""
    env = dict(os.environ, IES_ROOT=str(ies_root))
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input="{}",
        capture_output=True, text=True, env=env, timeout=60,
    )


def wait_for(predicate, timeout_s=15.0, interval=0.2):
    """Bounded poll: the detached sweep runs outside the hook's lifetime,
    so assertions on its effects must wait for it to land."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return False


def read_record(runs_dir: Path, eval_id: str):
    return json.loads((runs_dir / f"{eval_id}.json").read_text())


def test_detached_delegation_and_idempotence():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        harness = root / "systems" / "eval-harness"
        runs_dir = harness / "runs"
        runs_dir.mkdir(parents=True)
        (harness / "close-open-evals.py").write_text(CLOSE_SCRIPT.read_text())

        phantom_id, real_id = seed_runs_dir(runs_dir)

        result = run_hook(root)
        assert result.returncode == 0, f"hook should exit 0, got {result.returncode}: {result.stderr}"

        # The sweep is detached — wait for its effects, not the hook's exit.
        def sweep_landed():
            return (
                not (runs_dir / f"{phantom_id}.json").exists()
                and read_record(runs_dir, real_id).get("status") == "incomplete"
            )

        assert wait_for(sweep_landed), (
            "detached sweep did not land: phantom not deleted and/or real record "
            "not closed within timeout"
        )
        closed = read_record(runs_dir, real_id)
        assert closed["assessment"]["mechanical"]["abort_reason"] == "session-exit-normal", (
            f"expected canonical session-exit-normal semantics, got "
            f"{closed['assessment']['mechanical'].get('abort_reason')}"
        )
        assert closed["assessment"]["mechanical"]["completed"] is False
        print("PASS 1: detached delegation deletes phantom, closes real record canonically")

        # Idempotence: a second run must not touch the already-closed record.
        before = (runs_dir / f"{real_id}.json").read_text()
        result2 = run_hook(root)
        assert result2.returncode == 0
        assert wait_for(lambda: True, timeout_s=2), "unreachable"
        time.sleep(1.0)  # let any (wrongly spawned) second sweep finish
        after = (runs_dir / f"{real_id}.json").read_text()
        assert after == before, "second sweep mutated an already-closed record"
        assert not (runs_dir / f"{phantom_id}.json").exists()
        print("PASS 2: second sweep is a no-op on already-closed records")


def test_inline_fallback_without_canonical_script():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        runs_dir = root / "systems" / "eval-harness" / "runs"
        runs_dir.mkdir(parents=True)
        # No close-open-evals.py copied in: the hook must fall back inline.

        phantom_id, real_id = seed_runs_dir(runs_dir)

        result = run_hook(root)
        assert result.returncode == 0, f"hook should exit 0, got {result.returncode}: {result.stderr}"

        real = read_record(runs_dir, real_id)
        assert real["status"] == "aborted", (
            f"inline fallback should mark in-progress records aborted, got {real['status']}"
        )
        assert real["assessment"]["mechanical"]["abort_reason"] == "session-ended"
        phantom = read_record(runs_dir, phantom_id)
        assert phantom["status"] == "aborted", (
            f"inline fallback has no phantom-deletion (canonical script owns that); "
            f"phantom should still be aborted, got {phantom['status']}"
        )
        print("PASS 3: inline fallback still closes everything when the canonical script is absent")


if __name__ == "__main__":
    test_detached_delegation_and_idempotence()
    test_inline_fallback_without_canonical_script()
    print("ALL PASS: test_eval_session_end.py")
