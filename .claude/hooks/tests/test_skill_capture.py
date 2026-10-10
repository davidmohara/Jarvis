#!/usr/bin/env python3
"""
Regression suite for the hook-based skill-run capture chain (Phase F2, 2026-10-10).
Plain asserts, runnable directly: `python3 test_skill_capture.py`.

Runs against a THROWAWAY IES_ROOT in a temp directory: nothing under
systems/eval-harness/runs/ (the live harness) is read or written, and the
deterministic grader is skipped in test mode (skill_capture honors the
IES_ROOT env override; grade_skill_run.py does not, so skill_capture skips
it whenever IES_ROOT differs from the repo root).

Chain under test (each link is a real hook/module in this build):
  - .claude/hooks/eval-skill-invoke.py -> PostToolUse(Skill) hook; appends a
    pending entry via systems/eval-harness/skill_capture.py record_invoke().
  - systems/eval-harness/skill_capture.py finalize() -> writes the
    skill-runs signal file, creates the eval record by reusing
    post-tool-use.py's create_eval_record_from_skill_run (with the imported
    module's root-derived paths rebound to the temp root), and clears the
    pending entries for the session.
  - sweep_stale() -> finalizes abandoned entries as status "aborted".

Replaced by this chain: the retired in-file "SKILL COMPLETE" / "GRADE THIS
RUN" sections. The companion validators (add-skill-signals.py,
add-step-tracking.py, now read-only guards) fail if any stamped section
reappears in a skill or step file.
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parents[1]
IES_ROOT = Path(__file__).resolve().parents[3]
EVAL_HARNESS_DIR = IES_ROOT / "systems" / "eval-harness"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_hook(hook_path, payload, ies_root):
    env = dict(os.environ, IES_ROOT=str(ies_root))
    return subprocess.run(
        [sys.executable, str(hook_path)],
        input=json.dumps(payload), capture_output=True, text=True, env=env, timeout=60,
    )


def make_temp_root(tmp):
    root = Path(tmp)
    (root / "systems" / "eval-harness" / "runs").mkdir(parents=True)
    (root / "systems" / "eval-harness" / "skill-runs").mkdir(parents=True)
    (root / "skills" / "demo-skill").mkdir(parents=True)
    (root / "skills" / "demo-skill" / "SKILL.md").write_text(
        "---\nname: demo-skill\nowning_agent: harper\n---\nDo the thing.\n"
    )
    return root


def test_record_via_hook(tmp):
    root = make_temp_root(tmp)
    hook = HOOKS_DIR / "eval-skill-invoke.py"
    proc = run_hook(hook, {"tool_name": "Skill", "tool_input": {"skill": "demo-skill"}, "session_id": "sess-1"}, root)
    assert proc.returncode == 0, f"hook exited {proc.returncode}: {proc.stderr}"
    pending = (root / "systems" / "eval-harness" / "runs" / "pending-skill-runs.jsonl").read_text().splitlines()
    assert len(pending) == 1, f"expected 1 pending entry, got {len(pending)}"
    entry = json.loads(pending[0])
    assert entry["skill"] == "demo-skill"
    assert entry["session_id"] == "sess-1"
    # A non-Skill tool use must not record anything.
    run_hook(hook, {"tool_name": "Edit", "tool_input": {}}, root)
    pending = (root / "systems" / "eval-harness" / "runs" / "pending-skill-runs.jsonl").read_text().splitlines()
    assert len(pending) == 1, "Edit tool use must not append a pending skill entry"
    print("ok: PostToolUse(Skill) hook records pending entries; non-Skill tools pass through")


def test_finalize(tmp):
    root = make_temp_root(tmp)
    hook = HOOKS_DIR / "eval-skill-invoke.py"
    run_hook(hook, {"tool_name": "Skill", "tool_input": {"skill": "demo-skill"}, "session_id": "sess-1"}, root)
    sc = load_module("skill_capture_test", EVAL_HARNESS_DIR / "skill_capture.py")
    sc.IES_ROOT = root
    sc.PENDING_PATH = root / "systems" / "eval-harness" / "runs" / "pending-skill-runs.jsonl"
    sc.SKILL_RUNS_DIR = root / "systems" / "eval-harness" / "skill-runs"
    sc.EVAL_RUNS_DIR = root / "systems" / "eval-harness" / "runs"
    sc.finalize("sess-1")
    signal = json.loads((sc.SKILL_RUNS_DIR / "demo-skill-latest.json").read_text())
    assert signal["skill"] == "demo-skill"
    assert signal["agent"] == "harper", f"owning agent not read from SKILL.md frontmatter: {signal['agent']}"
    assert signal["captured_via"] == "hook"
    records = list((sc.EVAL_RUNS_DIR).glob("eval-*.json"))
    assert len(records) == 1, f"expected 1 eval record, got {len(records)}"
    record = json.loads(records[0].read_text())
    assert record["name"] == "demo-skill" and record["type"] == "skill" and record["agent"] == "harper"
    assert not sc.PENDING_PATH.exists(), "pending entries must be cleared after finalize"
    # Second finalize is a no-op.
    sc.finalize("sess-1")
    assert len(list(sc.EVAL_RUNS_DIR.glob("eval-*.json"))) == 1, "duplicate finalize must not create a second record"
    print("ok: finalize writes signal + eval record, clears pending, idempotent")


def test_sweep_stale(tmp):
    root = make_temp_root(tmp)
    sc = load_module("skill_capture_sweep", EVAL_HARNESS_DIR / "skill_capture.py")
    sc.IES_ROOT = root
    sc.PENDING_PATH = root / "systems" / "eval-harness" / "runs" / "pending-skill-runs.jsonl"
    sc.SKILL_RUNS_DIR = root / "systems" / "eval-harness" / "skill-runs"
    sc.EVAL_RUNS_DIR = root / "systems" / "eval-harness" / "runs"
    sc.PENDING_PATH.parent.mkdir(parents=True, exist_ok=True)
    sc.PENDING_PATH.write_text(
        json.dumps({"skill": "old-skill", "session_id": "sess-old", "started": "2026-10-09T10:00:00Z"})
        + "\n"
    )
    swept = sc.sweep_stale()
    assert swept == 1, f"expected 1 swept entry, got {swept}"
    signal = json.loads((sc.SKILL_RUNS_DIR / "old-skill-latest.json").read_text())
    assert signal["status"] == "aborted", "stale entries must finalize as aborted"
    assert not sc.PENDING_PATH.exists(), "pending file must be empty after sweep"
    print("ok: sweep finalizes stale entries as aborted and clears pending")


def test_validators_guard():
    """The F1 validators must be read-only guards that exit nonzero on stamped files."""
    v1 = load_module("v_signals", EVAL_HARNESS_DIR / "add-skill-signals.py")
    v2 = load_module("v_steps", EVAL_HARNESS_DIR / "add-step-tracking.py")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        skill_dir = root / "skills" / "stamped-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("## SKILL COMPLETE\nwrite the signal file\n")
        v1.IES_ROOT = root
        v1.SKILLS_DIRS = [root / ".claude" / "skills", root / "skills"]
        rc = v1.main()
        assert rc == 1, "validator must fail (exit 1) when a stamped section exists"
        (skill_dir / "SKILL.md").write_text("Just instructions.\n")
        rc = v1.main()
        assert rc == 0, "validator must pass (exit 0) on clean skills"
        steps_dir = root / "workflows" / "wf" / "steps"
        steps_dir.mkdir(parents=True)
        (steps_dir / "step-01-x.md").write_text(
            "## STEP COMPLETION TRACKING\npython3 systems/eval-harness/record-step.py wf step-01-x complete\n"
        )
        v2.IES_ROOT = root
        v2.WORKFLOWS_DIR = root / "workflows"
        rc = v2.main()
        assert rc == 1, "step validator must fail when a stamped tracking block exists"
        (steps_dir / "step-01-x.md").write_text("Just instructions.\n")
        rc = v2.main()
        assert rc == 0, "step validator must pass on clean step files"
    print("ok: F1 validators are read-only guards (fail on stamped, pass on clean)")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        test_record_via_hook(tmp)
    with tempfile.TemporaryDirectory() as tmp:
        test_finalize(tmp)
    with tempfile.TemporaryDirectory() as tmp:
        test_sweep_stale(tmp)
    test_validators_guard()
    print("ALL SKILL-CAPTURE TESTS PASSED")


if __name__ == "__main__":
    main()
