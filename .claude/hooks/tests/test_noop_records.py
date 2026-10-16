#!/usr/bin/env python3
"""Regression suite for deliberate no-op eval records (2026-10-16).

A workflow that runs and correctly determines there is nothing to do (e.g.
plaud-ingest's daily `outcome: no-new-recordings` pass) must leave a real,
audit-visible record in runs/ — NOT be quarantined as a phantom. A zero-step
record with NO documented disposition is still a phantom and must be
quarantined exactly as before.

Plain asserts, runnable directly: `python3 test_noop_records.py`.
Runs against a THROWAWAY IES-shaped temp root; the live harness is untouched.
"""

import importlib.util
import json
import tempfile
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parents[1]
IES_ROOT = Path(__file__).resolve().parents[3]
EVAL_HARNESS_DIR = IES_ROOT / "systems" / "eval-harness"


def load_module(mod_name, path):
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_root(tmp):
    runs = tmp / "systems" / "eval-harness" / "runs"
    runs.mkdir(parents=True)
    (tmp / "memory" / "sessions").mkdir(parents=True)
    (tmp / "memory" / "sessions" / "index.json").write_text("[]")
    (tmp / "workflows" / "plaud-ingest").mkdir(parents=True)
    return runs


def load_ptu(tmp, runs):
    mod = load_module("ptu_noop", HOOKS_DIR / "post-tool-use.py")
    mod.IES_ROOT = tmp
    mod.EVAL_RUNS_DIR = runs
    mod.EVAL_PHANTOMS_DIR = runs / "_phantoms"
    mod.INDEX_PATH = tmp / "memory" / "sessions" / "index.json"
    mod.ASSERTIONS_DIR = tmp / "no-assertions"  # skip assertion globbing
    mod.log_error = lambda *a, **k: None
    return mod


def drive(mod, tmp, state_yaml, session_id="sess-noop"):
    """Write state.yaml and push it through the real PostToolUse path."""
    state_file = tmp / "workflows" / "plaud-ingest" / "state.yaml"
    state_file.write_text(state_yaml)
    mod.process_eval_harness(
        "workflows/plaud-ingest/state.yaml", str(state_file), session_id)


NOOP_STATE = """---
workflow: plaud-ingest
agent: knox
status: complete
outcome: no-new-recordings
session-id: pi-20261015-001
session-started: '2026-10-15T00:00:00Z'
completed-at: '2026-10-15T00:00:00Z'
current-step: step-01
accumulated-context:
  new-recordings: []
---
"""

# status: complete but NO no-op disposition — an undispositioned completion
# (stale state.yaml re-read, or a workflow that never recorded an outcome).
COMPLETE_NO_DISPOSITION = """---
workflow: plaud-ingest
agent: knox
status: complete
session-id: pi-20261015-002
session-started: '2026-10-15T00:00:00Z'
---
"""

IN_PROGRESS_STATE = """---
workflow: plaud-ingest
agent: knox
status: in-progress
current-step: step-01
---
"""


def test_deliberate_noop_kept(tmp):
    runs = build_root(tmp / "noop")
    mod = load_ptu(tmp / "noop", runs)
    drive(mod, tmp / "noop", NOOP_STATE)

    in_runs = list(runs.glob("eval-*.json"))
    in_phantom = list((runs / "_phantoms").glob("eval-*.json")) if (runs / "_phantoms").exists() else []
    assert len(in_runs) == 1, f"no-op record must land in runs/, got {in_runs} / {in_phantom}"
    assert not in_phantom, f"no-op must NOT be quarantined, got {in_phantom}"
    rec = json.loads(in_runs[0].read_text())
    assert rec["name"] == "plaud-ingest", rec["name"]
    assert rec["status"] == "no-op", f"status must be no-op, got {rec['status']}"
    assert rec["no_op"] is True, "no_op marker missing"
    assert "no-op" in rec["tags"], f"no-op tag missing: {rec['tags']}"
    assert rec["status"] != "success", "a no-op must never read as a substantive success"


def test_true_phantom_still_quarantined(tmp):
    runs = build_root(tmp / "phantom")
    mod = load_ptu(tmp / "phantom", runs)
    drive(mod, tmp / "phantom", COMPLETE_NO_DISPOSITION)

    in_runs = list(runs.glob("eval-*.json"))
    in_phantom = list((runs / "_phantoms").glob("eval-*.json"))
    assert not in_runs, f"undispositioned zero-step record must not sit in runs/, got {in_runs}"
    assert len(in_phantom) == 1, f"phantom must be quarantined, got {in_phantom}"
    rec = json.loads(in_phantom[0].read_text())
    assert "phantom-candidate" in rec["tags"], rec["tags"]
    assert not rec.get("no_op"), "a phantom must not be marked no_op"


def test_in_progress_creates_nothing(tmp):
    runs = build_root(tmp / "inprog")
    mod = load_ptu(tmp / "inprog", runs)
    drive(mod, tmp / "inprog", IN_PROGRESS_STATE)
    assert not list(runs.glob("eval-*.json")), "an un-run workflow must produce no record"
    ph = runs / "_phantoms"
    assert not (ph.exists() and list(ph.glob("eval-*.json"))), "no phantom for an un-run workflow"


def _seed_metrics_dir(tmp, label):
    runs = build_root(tmp / label)
    noop = {
        "id": "eval-METRIC-NOOP", "type": "workflow", "name": "plaud-ingest",
        "agent": "knox", "status": "no-op", "no_op": True, "tags": ["cowork-hook", "no-op"],
        "started": "2026-10-15T00:00:00Z", "duration_seconds": 1.0,
        "steps": [], "assessment": {"mechanical": {"completed": True, "tool_failures": 0,
                                                   "error_ids": [], "all_steps_finished": True},
                                    "structural": {}, "grading": {}, "controller_feedback": {}},
    }
    real = {
        "id": "eval-METRIC-REAL", "type": "workflow", "name": "boot",
        "agent": "master", "status": "success", "tags": [],
        "started": "2026-10-15T00:00:00Z", "duration_seconds": 2.0,
        "steps": [], "assessment": {"mechanical": {"completed": True, "tool_failures": 0,
                                                   "error_ids": [], "all_steps_finished": True},
                                    "structural": {}, "grading": {}, "controller_feedback": {}},
    }
    (runs / f"{noop['id']}.json").write_text(json.dumps(noop))
    (runs / f"{real['id']}.json").write_text(json.dumps(real))
    return runs


def test_noop_excluded_from_dashboard_metrics(tmp):
    runs = _seed_metrics_dir(tmp, "metrics-dash")
    dash = load_module("dash_noop", EVAL_HARNESS_DIR / "generate-dashboard.py")
    records = dash.load_eval_records(str(runs), recent=100, period=3650,
                                     workflow=None, skill=None, agent=None)
    ids = {r["id"] for r in records}
    assert "eval-METRIC-REAL" in ids, "real run must survive the filter"
    assert "eval-METRIC-NOOP" not in ids, "no-op must be excluded from dashboard metrics"
    metrics = dash.calculate_metrics(records)
    assert metrics["success"] == 1, f"only the real run counts as success: {metrics['success']}"
    assert metrics["total"] == 1, f"no-op must not inflate total: {metrics['total']}"
    assert metrics["success_rate"] == 100.0, metrics["success_rate"]


def test_noop_excluded_from_version_trend(tmp):
    runs = _seed_metrics_dir(tmp, "metrics-vt")
    vt = load_module("vt_noop", EVAL_HARNESS_DIR / "version-trend.py")
    vt.EVAL_RUNS_DIR = runs
    plaud = vt.load_records("plaud-ingest")
    assert plaud == [], f"no-op must be excluded from version-trend math, got {plaud}"
    boot = vt.load_records("boot")
    assert len(boot) == 1, f"real run must remain, got {boot}"


def main():
    tmp = Path(tempfile.mkdtemp(prefix="ies-noop-test-"))
    test_deliberate_noop_kept(tmp)
    test_true_phantom_still_quarantined(tmp)
    test_in_progress_creates_nothing(tmp)
    test_noop_excluded_from_dashboard_metrics(tmp)
    test_noop_excluded_from_version_trend(tmp)
    print("test_noop_records: all cases passed")


if __name__ == "__main__":
    main()
