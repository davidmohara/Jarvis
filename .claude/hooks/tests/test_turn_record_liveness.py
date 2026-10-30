#!/usr/bin/env python3
"""Regression suite for turn-level record liveness + executor linkage
(2026-10-30 boot-token analysis).

Root causes fixed, all observed in the 2026-10-30 boot session (e826819b):

  1. eval-session-end.py fires close-open-evals.py on events that are not
     session exit (three times that day, twice mid-boot). The sweep closed the
     LIVE boot turn record at 14:08:17 — seven minutes before boot finished —
     and left monitoring.active true on it.
  2. Because that record's status was no longer "in-progress",
     find_open_turn_records returned nothing for the session, so
     find_unambiguous_open_turn_record returned None and the six executors
     spawned afterwards (steps 02/03/04, 05-08, knox check) were never written
     into the parent's subagents[]. With no link, eval-agent-stop.py's rollup
     AND its partition backfill had no parent: the per-step tokens stayed on
     the executors' own records and the boot record carried no totals.
  3. close-eval-record.py (boot's own closer, run at 14:16:42) wrote status,
     completed and duration but never aggregated total_tokens_* and never
     cleared monitoring.active — a "closed" record that still claimed to be
     live and reported no cost.
  4. A prompt the harness injects into the main session ("<agent-message
     from=...>", "<task-notification>") was treated as a user turn, and at
     14:24:03 opened a second, spurious 'boot' turn record for the session.

Fixes under test:
  - close-open-evals.py: leaves a turn record alone while its monitored
    state.yaml is non-terminal; clears monitoring.active when it does close.
  - hook_utils.find_unambiguous_open_turn_record: prefers an in-progress
    record, but a single live (monitoring.active) record the sweep closed
    mid-run still counts as the parent.
  - hook_utils.find_turn_record_for_workflow: stop-time re-attach of an
    executor whose start-time link was never written (same session, same
    workflow, window containment).
  - hook_utils.aggregate_record_totals: one aggregation used by both closers.
  - eval-turn-start.py: injected agent/task messages never open a record.

Plain asserts, runnable directly: `python3 test_turn_record_liveness.py`.
Runs against a THROWAWAY IES-shaped temp root; the live harness is untouched.
"""

import importlib.util
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parents[1]
IES_ROOT = Path(__file__).resolve().parents[3]
EVAL_HARNESS_DIR = IES_ROOT / "systems" / "eval-harness"


def load_module(mod_name, path):
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def iso(dt):
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def read(path):
    return json.loads(Path(path).read_text())


def write_record(runs_dir: Path, record: dict):
    path = runs_dir / f"{record['id']}.json"
    path.write_text(json.dumps(record, indent=2))
    return path


class Harness:
    """One throwaway IES-shaped root, shared by every module under test."""

    def __init__(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.runs = self.tmp / "systems" / "eval-harness" / "runs"
        self.runs.mkdir(parents=True)
        (self.tmp / "memory" / "sessions").mkdir(parents=True)
        (self.tmp / "memory" / "sessions" / "index.json").write_text("[]")
        self.workflows = self.tmp / "workflows"
        self.workflows.mkdir(parents=True)
        self._old_ies_root = os.environ.get("IES_ROOT")
        os.environ["IES_ROOT"] = str(self.tmp)

        self.hook_utils = load_module("hook_utils", EVAL_HARNESS_DIR / "hook_utils.py")
        self.hook_utils.EVAL_RUNS_DIR = self.runs
        self.hook_utils.IES_ROOT = self.tmp  # monitored state.yaml paths resolve here
        sys.modules["hook_utils"] = self.hook_utils

        self.session = "sess-liveness-test"

    def state_yaml(self, workflow: str, status: str, completed_at: str = None):
        wf_dir = self.workflows / workflow
        wf_dir.mkdir(parents=True, exist_ok=True)
        lines = ["---", f"status: {status}"]
        if completed_at:
            lines.append(f"completed-at: {completed_at}")
        lines.append("---")
        (wf_dir / "state.yaml").write_text("\n".join(lines) + "\n")
        return f"workflows/{workflow}/state.yaml"

    def turn_record(self, name="boot", started=None, status="in-progress",
                    steps=None, subagents=None, rid=None, session_id=None):
        started = started or datetime.now(timezone.utc)
        return {
            "id": rid or f"eval-{started.strftime('%Y%m%dT%H%M%S')}-TURN01",
            "type": "workflow",
            "name": name,
            "agent": "master",
            "session_id": session_id or self.session,
            "started": iso(started),
            "completed": None,
            "status": status,
            "steps": steps or [],
            "subagents": subagents or [],
            "monitoring": {
                "active": True,
                "state_yaml_path": f"workflows/{name}/state.yaml",
                "opened_by": "eval-turn-start.py",
            },
            "assessment": {"mechanical": {"completed": None, "all_steps_finished": None,
                                          "tool_failures": 0, "error_ids": []}},
        }

    def close(self):
        if self._old_ies_root is None:
            os.environ.pop("IES_ROOT", None)
        else:
            os.environ["IES_ROOT"] = self._old_ies_root
        shutil.rmtree(self.tmp, ignore_errors=True)


def run_close_open_evals(runs_dir: Path):
    """Run the canonical closer in-process against a redirected root."""
    mod = load_module("close_open_evals_test", EVAL_HARNESS_DIR / "close-open-evals.py")
    return mod.close_open_evals(runs_dir)


def test_live_record_survives_session_end_sweep():
    """Guard 1: a record whose workflow is still executing is not closed."""
    h = Harness()
    try:
        h.state_yaml("boot", "in-progress")
        rec = h.turn_record(steps=[{"name": "step-01", "status": "complete"}])
        path = write_record(h.runs, rec)

        run_close_open_evals(h.runs)

        after = read(path)
        assert after["status"] == "in-progress", after["status"]
        assert after["monitoring"]["active"] is True, "live record lost its monitoring flag"
        print("PASS: session-end sweep leaves a still-running workflow's record open")
    finally:
        h.close()


def test_closed_record_no_longer_claims_to_be_live():
    """Guard 2: closing clears monitoring.active."""
    h = Harness()
    try:
        h.state_yaml("boot", "complete", iso(datetime.now(timezone.utc)))
        rec = h.turn_record(steps=[{"name": "step-01", "status": "complete"}])
        path = write_record(h.runs, rec)

        run_close_open_evals(h.runs)

        after = read(path)
        assert after["status"] == "incomplete", after["status"]
        assert after["monitoring"]["active"] is False, "closed record still claims to be monitored"
        print("PASS: closing a record clears monitoring.active")
    finally:
        h.close()


def test_sweep_closed_parent_still_receives_links():
    """A record the sweep closed mid-run is still the parent of later spawns.

    This is the exact 2026-10-30 sequence: sweep closes the live boot record,
    then steps 02-08 spawn. Linking must not go dark.
    """
    h = Harness()
    try:
        started = datetime.now(timezone.utc)
        rec = h.turn_record(started=started, status="incomplete",
                            steps=[{"name": "step-01", "status": "complete"}])
        write_record(h.runs, rec)

        found = h.hook_utils.find_unambiguous_open_turn_record(h.session)
        assert found is not None, "sweep-closed live record was not linkable"

        # A genuinely open record still wins when one exists.
        open_rec = h.turn_record(started=started + timedelta(seconds=1),
                                 rid="eval-20260101T000000-OPEN01")
        write_record(h.runs, open_rec)
        found2 = h.hook_utils.find_unambiguous_open_turn_record(h.session)
        assert found2 is not None and found2.name == "eval-20260101T000000-OPEN01.json", found2

        # Two genuinely open records stay ambiguous -> no guess.
        write_record(h.runs, h.turn_record(started=started + timedelta(seconds=2),
                                           rid="eval-20260101T000000-OPEN02"))
        assert h.hook_utils.find_unambiguous_open_turn_record(h.session) is None

        # A finished (finalized) record is NOT linkable.
        h2 = Harness()
        try:
            done = h2.turn_record(status="success")
            done["monitoring"]["active"] = False
            write_record(h2.runs, done)
            assert h2.hook_utils.find_unambiguous_open_turn_record(h2.session) is None
        finally:
            h2.close()
        print("PASS: sweep-closed parent stays linkable; finalized records do not")
    finally:
        h.close()


def test_orphan_reattach_resolves_parent_by_workflow_and_window():
    h = Harness()
    try:
        boot_start = datetime.now(timezone.utc) - timedelta(minutes=10)
        boot = h.turn_record(started=boot_start, status="success")  # closed by its own closer
        boot["completed"] = iso(boot_start + timedelta(minutes=8))
        boot["monitoring"]["active"] = False
        boot_path = write_record(h.runs, boot)

        child_started = iso(boot_start + timedelta(minutes=3))
        found = h.hook_utils.find_turn_record_for_workflow(h.session, "boot", child_started)
        assert found == boot_path, f"expected {boot_path.name}, got {found}"

        # Outside the parent's window -> not this parent.
        late = iso(boot_start + timedelta(minutes=30))
        assert h.hook_utils.find_turn_record_for_workflow(h.session, "boot", late) is None

        # A different session never adopts this session's child.
        assert h.hook_utils.find_turn_record_for_workflow("other-session", "boot", child_started) is None

        # A different workflow never adopts it either.
        assert h.hook_utils.find_turn_record_for_workflow(h.session, "morning-briefing", child_started) is None
        print("PASS: orphan re-attach resolves by session + workflow + window")
    finally:
        h.close()


def test_totals_aggregation_and_double_count_guard():
    h = Harness()
    try:
        rec = h.turn_record(steps=[
            {"name": "step-01", "tokens_input": 100, "tokens_output": 10, "cost_usd": 0.1},
            # partitioned from agent A1 — A1's subagents[] entry carries the
            # same tokens, so this step must not be counted again
            {"name": "step-02", "tokens_input": 200, "tokens_output": 20,
             "cost_usd": 0.2, "executed_by_agent_id": "A1"},
            # partitioned from A2, whose stop hook was lost (no tokens)
            {"name": "step-03", "tokens_input": 300, "tokens_output": 30,
             "cost_usd": 0.3, "executed_by_agent_id": "A2"},
        ], subagents=[
            {"agent_id": "A1", "tokens_input": 200, "tokens_output": 20, "cost_usd": 0.2},
            {"agent_id": "A2", "tokens_input": None, "tokens_output": None, "cost_usd": None},
        ])
        h.hook_utils.aggregate_record_totals(rec)
        assert rec["total_tokens_input"] == 100 + 200 + 300, rec["total_tokens_input"]
        assert rec["total_tokens_output"] == 10 + 20 + 30, rec["total_tokens_output"]
        assert abs(rec["total_cost_usd"] - 0.6) < 1e-9, rec["total_cost_usd"]
        print("PASS: totals aggregate steps + subagents without double counting")
    finally:
        h.close()


def test_injected_prompts_do_not_open_records():
    h = Harness()
    try:
        (h.workflows / "boot").mkdir(parents=True, exist_ok=True)
        (h.workflows / "boot" / "workflow.md").write_text(
            "---\nagent: master\n---\n\n# Boot\n")
        (h.workflows / "boot" / "state.yaml").write_text(
            "---\nstatus: complete\ncompleted-at: 2026-01-01T00:00:00Z\n---\n")

        ts = load_module("eval_turn_start_test", HOOKS_DIR / "eval-turn-start.py")
        ts.EVAL_RUNS_DIR = h.runs
        ts.WORKFLOWS_DIR = h.workflows
        ts.IES_ROOT = h.tmp
        ts.log_error = lambda *a, **k: None
        ts.log_info = lambda *a, **k: None

        def fire(prompt):
            ts.read_stdin = lambda: {"session_id": h.session, "prompt": prompt,
                                     "transcript_path": None}
            ts.main()

        fire('<agent-message from="ac26dd7e172dbc3b8">run the boot workflow again</agent-message>')
        fire('<task-notification>\n<status>completed</status>\n</task-notification>\nrun boot')
        assert not list(h.runs.glob("eval-*.json")), \
            f"injected prompt opened a record: {[p.name for p in h.runs.glob('eval-*.json')]}"
        print("PASS: injected agent-message / task-notification prompts never open a record")
    finally:
        h.close()


def test_cross_session_dedupe_respects_a_dead_session():
    """A dead session's record must not block a new session's record forever.

    An interrupted boot leaves workflows/boot/state.yaml non-terminal, and
    close-open-evals.py now refuses to close a record whose workflow looks
    live. Without the state.yaml-mtime bound, that leftover would suppress
    every new session's boot record for ABANDONED_RECORD_AFTER_HOURS.
    """
    h = Harness()
    try:
        h.state_yaml("boot", "in-progress")
        rec = h.turn_record(session_id="old-session")
        write_record(h.runs, rec)

        # Same session: always blocking.
        assert h.hook_utils.open_turn_level_record_exists("boot", session_id="old-session") is True
        # Different session, fresh state.yaml: still blocking (workflow is live).
        assert h.hook_utils.open_turn_level_record_exists("boot", session_id="new-session") is True
        # Different session, state.yaml untouched for hours: not blocking.
        old = (datetime.now(timezone.utc) - timedelta(hours=3)).timestamp()
        os.utime(h.tmp / "workflows" / "boot" / "state.yaml", (old, old))
        assert h.hook_utils.open_turn_level_record_exists("boot", session_id="new-session") is False
        print("PASS: a dead session's open record stops blocking after the state.yaml goes cold")
    finally:
        h.close()


if __name__ == "__main__":
    test_live_record_survives_session_end_sweep()
    test_closed_record_no_longer_claims_to_be_live()
    test_sweep_closed_parent_still_receives_links()
    test_orphan_reattach_resolves_parent_by_workflow_and_window()
    test_totals_aggregation_and_double_count_guard()
    test_injected_prompts_do_not_open_records()
    test_cross_session_dedupe_respects_a_dead_session()
    print("\nAll turn-record liveness regression tests pass.")
