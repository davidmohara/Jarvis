#!/usr/bin/env python3
"""Regression suite for async background subagent eval recording (2026-10-28).

Root causes fixed, all observed in the 2026-10-28 boot session (98fa4325):

  1. This harness fires SubagentStart once per RESUME SEGMENT of a
     background agent, not once per logical agent — one Knox plaud-ingest
     agent accrued five stub records (1SI5VG/Q4RJKA/S5588B/JYUC62/0XRNN0),
     splitting its cost across five records and double-listing agents in the
     parent boot record's subagents[].
  2. close-open-evals.py phantom-deleted in-progress stubs with zero
     steps/subagents — including stubs for agents STILL RUNNING at session
     end. The boot 05-08 briefing agent's stub (eval-...172711-WLE85H) was
     deleted at 17:30:51; its SubagentStop fired at 17:31:33 with nothing
     to land on, and a ~3M-token run left no record (same as 10-27).
  3. eval-agent-stop.py's agent_type fallback then hijacked an unrelated
     in-progress record (M92BI5) and stamped it with the orphaned agent's
     tail-slice tokens; that record's own stop hijacked the next one
     (0XRNN0) — a cascade. Six more stops with no stub and an empty
     agent_type recorded nothing at all.

Fixes under test:
  - eval-agent-start.py: one record per agent_id (reuse open, reopen closed),
    no duplicate subagents[] links.
  - eval-agent-stop.py: agent_id match accepts closed records; the
    agent_type fallback only applies when the payload has NO agent_id;
    a stop with an agent_id but no stub creates a stop-origin record from
    the subagent transcript.
  - close-open-evals.py: phantom deletion only for records with NO
    agent_id; agent stubs are marked incomplete, never deleted.

Plain asserts, runnable directly: `python3 test_async_agent_recording.py`.
Runs against a THROWAWAY IES-shaped temp root; the live harness is untouched.
"""

import importlib.util
import json
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


def write_turn(transcript: Path, ts, mid, inp=100, out=10):
    turn = {
        "type": "assistant",
        "timestamp": iso(ts),
        "message": {
            "id": mid,
            "model": "claude-sonnet-4-5",
            "usage": {"input_tokens": inp, "output_tokens": out,
                      "cache_read_input_tokens": 0, "cache_creation": {}},
        },
    }
    with open(transcript, "a") as f:
        f.write(json.dumps(turn) + "\n")


def records_for(runs_dir: Path, agent_id: str):
    out = []
    for f in runs_dir.glob("eval-*.json"):
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue
        if d.get("agent_id") == agent_id:
            out.append((f, d))
    return out


class Harness:
    """Loads the three modules under test against one throwaway root."""

    def __init__(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.runs = self.tmp / "systems" / "eval-harness" / "runs"
        self.runs.mkdir(parents=True)
        (self.tmp / "memory" / "sessions").mkdir(parents=True)
        (self.tmp / "memory" / "sessions" / "index.json").write_text("[]")
        (self.tmp / "workflows").mkdir(parents=True)
        self.assertions = self.tmp / "assertions"
        self.assertions.mkdir()
        self.errors = self.tmp / "no-errors"

        # Register under the real module name so the hooks' own
        # `from hook_utils import ...` resolves to THIS instance (with the
        # redirected runs dir), not a second copy Python imports fresh.
        self.hook_utils = load_module("hook_utils", EVAL_HARNESS_DIR / "hook_utils.py")
        self.hook_utils.EVAL_RUNS_DIR = self.runs
        sys.modules["hook_utils"] = self.hook_utils

        self.start = load_module("agent_start_async", HOOKS_DIR / "eval-agent-start.py")
        self.start.EVAL_RUNS_DIR = self.runs

        self.stop = load_module("agent_stop_async", HOOKS_DIR / "eval-agent-stop.py")
        self.stop.EVAL_RUNS_DIR = self.runs
        self.stop.IES_ROOT = self.tmp
        self.stop.EVAL_ASSERTIONS_DIR = self.assertions
        self.stop.ERROR_TRACKING_DIR = self.errors
        self.stop._flc = None  # parent-window cost is not under test here

        for mod in (self.start, self.stop):
            mod.log_error = lambda *a, **k: None
            mod.log_info = lambda *a, **k: None

        self.session = "sess-async-test"

    def fire_start(self, agent_id, agent_type="general-purpose"):
        self.start.read_stdin = lambda: {
            "session_id": self.session,
            "agent_id": agent_id,
            "agent_type": agent_type,
            "hook_event_name": "SubagentStart",
        }
        self.start.main()

    def fire_stop(self, agent_id, agent_type="general-purpose",
                  transcript=None, last_message="done"):
        self.stop.read_stdin = lambda: {
            "session_id": self.session,
            "agent_id": agent_id,
            "agent_type": agent_type,
            "agent_transcript_path": str(transcript) if transcript else None,
            "last_assistant_message": last_message,
            "hook_event_name": "SubagentStop",
        }
        self.stop.main()


def test_duplicate_starts_collapse():
    h = Harness()
    h.fire_start("agent-dup-1")
    h.fire_start("agent-dup-1")  # resume segment: same agent_id
    h.fire_start("agent-dup-1")
    recs = records_for(h.runs, "agent-dup-1")
    assert len(recs) == 1, f"expected 1 record for resumed agent, got {len(recs)}"
    assert recs[0][1]["status"] == "in-progress"
    print("PASS: duplicate SubagentStart segments collapse to one record")


def test_full_lifecycle_single_record_cumulative_tokens():
    h = Harness()
    transcript = h.tmp / "agent-lifecycle.jsonl"

    h.fire_start("agent-life-1")
    write_turn(transcript, datetime.now(timezone.utc), "m1")
    h.fire_stop("agent-life-1", transcript=transcript)

    recs = records_for(h.runs, "agent-life-1")
    assert len(recs) == 1 and recs[0][1]["status"] in ("success", "partial"), recs[0][1]["status"]
    assert recs[0][1]["total_tokens_input"] == 100

    # Resume: same agent_id, new segment, cumulative transcript.
    h.fire_start("agent-life-1")
    recs = records_for(h.runs, "agent-life-1")
    assert len(recs) == 1, "resume created a second record"
    assert recs[0][1]["status"] == "in-progress", "closed record was not reopened on resume"

    write_turn(transcript, datetime.now(timezone.utc), "m2")
    write_turn(transcript, datetime.now(timezone.utc), "m3")
    h.fire_stop("agent-life-1", transcript=transcript)

    recs = records_for(h.runs, "agent-life-1")
    assert len(recs) == 1
    d = recs[0][1]
    assert d["status"] in ("success", "partial"), d["status"]
    # Cumulative: the window spans the original start to the final stop, and
    # the transcript is the agent's whole history — all three turns count.
    assert d["total_tokens_input"] == 300, d["total_tokens_input"]
    assert d["total_tokens_output"] == 30, d["total_tokens_output"]
    print("PASS: start/stop/resume/stop yields one record with cumulative tokens")


def test_stop_origin_record_when_start_never_fired():
    h = Harness()
    transcript = h.tmp / "agent-ghost.jsonl"
    t0 = datetime.now(timezone.utc) - timedelta(minutes=4)
    write_turn(transcript, t0, "g1", inp=5000, out=200)
    write_turn(transcript, t0 + timedelta(minutes=3), "g2", inp=7000, out=300)

    h.fire_stop("agent-ghost-1", transcript=transcript)

    recs = records_for(h.runs, "agent-ghost-1")
    assert len(recs) == 1, "stop-origin record was not created"
    d = recs[0][1]
    assert "stop-origin" in d.get("tags", [])
    assert d["started"].startswith(iso(t0)[:19]), d["started"]
    assert d["status"] in ("success", "partial"), d["status"]
    assert d["total_tokens_input"] == 12000, d["total_tokens_input"]
    assert d["total_tokens_output"] == 500, d["total_tokens_output"]
    print("PASS: stop with no stub creates a stop-origin record with real window and tokens")


def test_no_fallback_hijack_when_agent_id_present():
    h = Harness()
    # Agent Z is mid-run with an open stub.
    h.fire_start("agent-zed-1")
    zed_before = records_for(h.runs, "agent-zed-1")[0][1]

    # Agent W's stop arrives: its stub is gone (swept) or never existed.
    # Old behavior: complete Z's record with W's data. New behavior: a
    # stop-origin record for W, Z untouched.
    h.fire_stop("agent-doubleu-1", transcript=None)

    zed_after = records_for(h.runs, "agent-zed-1")[0][1]
    assert zed_after["status"] == "in-progress", "sibling record was hijacked by an orphaned stop"
    assert zed_after.get("completed") == zed_before.get("completed")
    w = records_for(h.runs, "agent-doubleu-1")
    assert len(w) == 1 and "stop-origin" in w[0][1].get("tags", [])
    print("PASS: orphaned stop with agent_id does not hijack a sibling's record")


def test_sweep_never_deletes_agent_stubs():
    h = Harness()
    h.fire_start("agent-still-running")  # in-progress, zero steps/subagents, HAS agent_id
    phantom = {
        "id": "eval-20260101T000000-TURNPH",
        "status": "in-progress",
        "session_id": h.session,
        "workflow": "boot",
        "steps": [],
        "subagents": [],
        # no agent_id: a turn-level speculative record — the deletion case
        # from err-20260829T161711-3IPMKR, preserved.
    }
    (h.runs / f"{phantom['id']}.json").write_text(json.dumps(phantom, indent=2))

    closer = load_module("close_open_async", EVAL_HARNESS_DIR / "close-open-evals.py")
    closer.close_open_evals(h.runs)

    stub = records_for(h.runs, "agent-still-running")
    assert len(stub) == 1, "agent stub was deleted by the sweep"
    assert stub[0][1]["status"] == "incomplete", stub[0][1]["status"]
    assert stub[0][1]["assessment"]["mechanical"]["abort_reason"] == "session-exit-normal"
    assert not (h.runs / f"{phantom['id']}.json").exists(), "agent_id-less phantom was not deleted"
    print("PASS: sweep marks agent stubs incomplete (never deletes); turn-level phantoms still deleted")


def test_late_stop_adopts_swept_stub():
    """The 2026-10-28 WLE85H sequence: stub swept (marked incomplete) while
    the agent is still running; the real stop fires after and must land on
    the swept record, completing it with real tokens."""
    h = Harness()
    transcript = h.tmp / "agent-late.jsonl"

    h.fire_start("agent-late-1")
    write_turn(transcript, datetime.now(timezone.utc), "l1", inp=900, out=90)
    closer = load_module("close_open_async2", EVAL_HARNESS_DIR / "close-open-evals.py")
    closer.close_open_evals(h.runs)
    d = records_for(h.runs, "agent-late-1")[0][1]
    assert d["status"] == "incomplete"

    write_turn(transcript, datetime.now(timezone.utc), "l2", inp=100, out=10)
    h.fire_stop("agent-late-1", transcript=transcript)

    recs = records_for(h.runs, "agent-late-1")
    assert len(recs) == 1
    d = recs[0][1]
    assert d["status"] in ("success", "partial"), f"late stop did not complete the swept stub: {d['status']}"
    assert d["total_tokens_input"] == 1000, d["total_tokens_input"]
    print("PASS: late stop adopts the swept stub and completes it with real tokens")


def test_ghost_stop_no_sibling_transcript_substitution():
    """Ghost stop (agent_id present, agent's transcript never landed on disk —
    the six 2026-10-28 nested-background-agent stops): the stop-origin record
    must carry NO token data rather than usage_between's same-dir fallback
    substituting the newest sibling agent's transcript. Live instance:
    eval-20261028T220545-VFF726 picked up 10.9M tokens belonging to a
    different agent before this rule existed."""
    h = Harness()
    sibling = h.tmp / "subagents"
    sibling.mkdir()
    other = sibling / "agent-someoneelse.jsonl"
    write_turn(other, datetime.now(timezone.utc), "s1", inp=999999, out=1)

    h.fire_stop("agent-ghost-2", agent_type="",
                transcript=sibling / "agent-ghost-2.jsonl")  # never written

    recs = records_for(h.runs, "agent-ghost-2")
    assert len(recs) == 1
    d = recs[0][1]
    assert "stop-origin" in d.get("tags", [])
    assert d.get("total_tokens_input") is None, \
        f"ghost stop attributed sibling transcript tokens: {d.get('total_tokens_input')}"
    assert d.get("token_source") != "subagent-transcript"
    print("PASS: ghost stop with missing transcript records no tokens (no sibling substitution)")


def test_parent_link_dedup():
    h = Harness()
    parent = {
        "id": "eval-20260101T000000-PARENT",
        "status": "in-progress",
        "session_id": h.session,
        "type": "workflow",
        "name": "boot",
        "monitoring": {"active": True},
        "steps": [],
        "subagents": [],
    }
    (h.runs / f"{parent['id']}.json").write_text(json.dumps(parent, indent=2))

    h.fire_start("agent-linked-1")
    h.fire_start("agent-linked-1")  # resume re-fire

    d = json.loads((h.runs / f"{parent['id']}.json").read_text())
    links = [s for s in d["subagents"] if s.get("agent_id") == "agent-linked-1"]
    assert len(links) == 1, f"parent subagents[] has {len(links)} entries for one agent"
    print("PASS: parent subagents[] links an agent_id exactly once across resume re-fires")


if __name__ == "__main__":
    test_duplicate_starts_collapse()
    test_full_lifecycle_single_record_cumulative_tokens()
    test_stop_origin_record_when_start_never_fired()
    test_no_fallback_hijack_when_agent_id_present()
    test_sweep_never_deletes_agent_stubs()
    test_late_stop_adopts_swept_stub()
    test_ghost_stop_no_sibling_transcript_substitution()
    test_parent_link_dedup()
    print("\nAll async-agent recording regression tests pass.")
