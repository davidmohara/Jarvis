#!/usr/bin/env python3
"""
Regression suite for the fully-loaded workflow cost attribution (2026-10-21,
David's ruling that a workflow's recorded cost must include the parent
session's own turns during the run window, reconciling across the day).

Plain asserts, runnable directly: `python3 test_fully_loaded_cost.py`.
Everything runs against temp directories — no live runs dir, no real
~/.claude/projects.

Chain under test:
  - token_usage.parent_window_usage      (strict window, sidechain exclusion,
                                          per-turn mixed-model pricing,
                                          honest zero on an empty window)
  - fully_loaded_cost.apply_to_record    (component model: parent window +
                                          subagent components, inline steps
                                          never double counted; agent-type
                                          records add their own run cost)
  - reconcile-workflows.reconcile_day    (day invariant: attributed +
                                          remainder == metered, overlapping
                                          record windows unioned, unlinked
                                          subagent transcripts land in the
                                          remainder)
  - eval-turn-stop finalize              (writes parent_window/fully_loaded_*
                                          fields at record close)
"""

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parents[1]
IES_ROOT = Path(__file__).resolve().parents[3]
EVAL_HARNESS_DIR = IES_ROOT / "systems" / "eval-harness"
COST_ATTR_DIR = IES_ROOT / "systems" / "cost-attribution"

sys.path.insert(0, str(EVAL_HARNESS_DIR))

import token_usage
import fully_loaded_cost as flc


def load_module(mod_name, path):
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


def turn(mid, ts, model, input_tokens=0, output_tokens=0, cache_read=0,
         sidechain=False):
    return {
        "type": "assistant",
        "isSidechain": sidechain,
        "timestamp": ts,
        "message": {
            "id": mid,
            "model": model,
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cache_read_input_tokens": cache_read,
                "cache_creation": {"ephemeral_5m_input_tokens": 0,
                                   "ephemeral_1h_input_tokens": 0},
            },
        },
    }


def write_transcript(path: Path, turns: list):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for t in turns:
            f.write(json.dumps(t) + "\n")
    return str(path)


WINDOW_START = "2026-10-21T10:00:00Z"
WINDOW_END = "2026-10-21T10:30:00Z"

KIMI = "accounts/fireworks/models/kimi-k3"   # $3/$15 per Mtok
FLASH = "glm-5p3-flash"                       # $0.15/$0.5 per Mtok


def test_parent_window_strict_window_and_sidechain_exclusion(tmp):
    """Only non-sidechain turns inside the window count; duplicate message.id
    lines (one turn written as several JSONL lines) are deduped; mixed models
    price per-turn."""
    transcript = write_transcript(tmp / "main.jsonl", [
        turn("m_before", "2026-10-21T09:00:00Z", KIMI, input_tokens=999999),  # before window
        turn("m_1", "2026-10-21T10:05:00Z", KIMI, input_tokens=1000, output_tokens=100),
        turn("m_1", "2026-10-21T10:05:01Z", KIMI, input_tokens=1000, output_tokens=100),  # dup id
        turn("m_2", "2026-10-21T10:10:00Z", FLASH, input_tokens=10000),
        turn("m_side", "2026-10-21T10:15:00Z", KIMI, input_tokens=999999, sidechain=True),
        turn("m_after", "2026-10-21T11:00:00Z", KIMI, input_tokens=999999),  # after window
    ])
    pw = token_usage.parent_window_usage(transcript, WINDOW_START, WINDOW_END)
    assert pw is not None
    assert pw["turns_matched"] == 2, pw
    assert pw["tokens_input"] == 11000, pw
    assert pw["tokens_output"] == 100, pw
    # per-turn pricing: kimi 1000*3e-6 + 100*15e-6 = 0.0045; flash 10000*0.15e-6 = 0.0015
    assert pw["cost_usd"] == 0.006, pw
    assert pw["token_source"] == "parent-window"


def test_parent_window_empty_window_is_honest_zero(tmp):
    """A real transcript with no turns in the window is a true $0.00 (not
    None, not the lenient whole-transcript fabrication); a missing transcript
    is None."""
    transcript = write_transcript(tmp / "main.jsonl", [
        turn("m_1", "2026-10-21T09:00:00Z", KIMI, input_tokens=5000),
    ])
    pw = token_usage.parent_window_usage(transcript, WINDOW_START, WINDOW_END)
    assert pw is not None and pw["turns_matched"] == 0
    assert pw["tokens_input"] == 0 and pw["cost_usd"] == 0.0, pw
    assert token_usage.parent_window_usage(str(tmp / "nope.jsonl"),
                                           WINDOW_START, WINDOW_END) is None
    assert token_usage.parent_window_usage(None, WINDOW_START, WINDOW_END) is None


def _workflow_record(**extra):
    rec = {
        "id": "eval-TESTFL001",
        "type": "workflow",
        "name": "demo-wf",
        "session_id": "sid-fl",
        "started": WINDOW_START,
        "completed": WINDOW_END,
        "steps": [],
        "subagents": [],
    }
    rec.update(extra)
    return rec


def test_apply_workflow_record_no_double_count(tmp):
    """fully_loaded = parent_window + subagent components. Inline steps are
    inside the parent window and must not be added; a step executed by a
    subagent whose rollup has tokens must not be added either; the same step
    counts (on the subagent side) only when the rollup lost its tokens."""
    transcript = write_transcript(tmp / "main.jsonl", [
        turn("m_1", "2026-10-21T10:05:00Z", KIMI, input_tokens=1000000),  # $3.00 parent
    ])
    steps = [
        {"name": "step-01.md", "tokens_input": 100, "tokens_output": 10, "cost_usd": 0.10},
        {"name": "step-02.md", "tokens_input": 200, "tokens_output": 20, "cost_usd": 0.20,
         "executed_by_agent_id": "sub1"},
    ]
    subs_with = [{"agent_id": "sub1", "tokens_input": 5000, "tokens_output": 50,
                  "cost_usd": 0.50}]
    rec = _workflow_record(steps=[dict(s) for s in steps],
                           subagents=[dict(s) for s in subs_with])
    block = flc.apply_to_record(rec, transcript_path=transcript)
    assert block["cost_usd"] == 3.0, block
    # sub component = rollup only (step-02 skipped): 3.00 + 0.50
    assert rec["fully_loaded_cost_usd"] == 3.5, rec["fully_loaded_cost_usd"]

    subs_without = [{"agent_id": "sub1", "tokens_input": None, "tokens_output": None,
                     "cost_usd": None}]
    rec2 = _workflow_record(steps=[dict(s) for s in steps],
                            subagents=[dict(s) for s in subs_without])
    flc.apply_to_record(rec2, transcript_path=transcript)
    # rollup lost its tokens -> step-02's $0.20 counts on the subagent side
    assert rec2["fully_loaded_cost_usd"] == 3.2, rec2["fully_loaded_cost_usd"]


def test_apply_agent_record_adds_own_run_cost(tmp):
    """A type:agent record (a subagent's own record) fully-loads as parent
    window + its own whole-run cost."""
    transcript = write_transcript(tmp / "main.jsonl", [
        turn("m_1", "2026-10-21T10:05:00Z", KIMI, input_tokens=1000000),  # $3.00
    ])
    rec = {
        "id": "eval-TESTFL002", "type": "agent", "name": "general-purpose",
        "agent_id": "sub9", "session_id": "sid-fl",
        "started": WINDOW_START, "completed": WINDOW_END,
        "steps": [], "subagents": [],
        "total_cost_usd": 0.68, "total_tokens_input": 1654697,
        "total_tokens_output": 3218,
    }
    block = flc.apply_to_record(rec, transcript_path=transcript)
    assert block["cost_usd"] == 3.0
    assert rec["fully_loaded_cost_usd"] == 3.68, rec["fully_loaded_cost_usd"]
    assert rec["fully_loaded_tokens_input"] == 1000000 + 1654697


def test_apply_no_session_transcript_is_honest(tmp):
    """No local transcript -> labeled nulls, fully_loaded falls back to the
    subagent component with an explanatory note (never a fabricated zero)."""
    empty_projects = tmp / "projects"
    empty_projects.mkdir(parents=True)
    rec = _workflow_record(
        steps=[{"name": "step-01.md", "tokens_input": 100, "tokens_output": 10,
                "cost_usd": 0.10, "executed_by_agent_id": "sub1"}],
        subagents=[])
    block = flc.apply_to_record(rec, projects_dir=empty_projects)
    assert block["token_source"] == "no-session-transcript", block
    assert block["cost_usd"] is None
    assert rec["fully_loaded_cost_usd"] == 0.10, rec["fully_loaded_cost_usd"]
    assert rec.get("fully_loaded_note"), rec


def test_apply_skips_open_and_invalid_windows(tmp):
    rec = _workflow_record(completed=None)
    assert flc.apply_to_record(rec, transcript_path=str(tmp / "x.jsonl")) is None
    assert "parent_window" not in rec
    rec2 = _workflow_record(started="2026-10-21T10:30:00Z",
                            completed="2026-10-21T10:00:00Z")
    block = flc.apply_to_record(rec2, transcript_path=str(tmp / "x.jsonl"))
    assert block["token_source"] == "invalid-window"
    assert rec2["fully_loaded_cost_usd"] is None


def _build_session(tmp, sid="sid-recon"):
    """One session: main transcript + two subagent transcripts."""
    proj = tmp / "projects" / "proj-a"
    main = write_transcript(proj / f"{sid}.jsonl", [
        # inside workflow window (10:00-10:30)
        turn("m_in1", "2026-10-21T10:05:00Z", KIMI, input_tokens=1000000),   # $3.00
        turn("m_in2", "2026-10-21T10:20:00Z", KIMI, input_tokens=1000000),   # $3.00
        # outside every window
        turn("m_out", "2026-10-21T15:00:00Z", KIMI, input_tokens=500000),    # $1.50
        # previous day (never counted)
        turn("m_prev", "2026-10-20T23:00:00Z", KIMI, input_tokens=999999),
    ])
    subA = write_transcript(proj / sid / "subagents" / "agent-aaa.jsonl", [
        turn("s_a", "2026-10-21T10:10:00Z", FLASH, input_tokens=1000000),    # $0.15
    ])
    subB = write_transcript(proj / sid / "subagents" / "agent-bbb.jsonl", [
        turn("s_b", "2026-10-21T12:00:00Z", FLASH, input_tokens=2000000),    # $0.30 unlinked
    ])
    runs = tmp / "runs"
    runs.mkdir(parents=True)
    return tmp / "projects", runs, main, subA, subB


def test_reconcile_day_invariant_and_overlap(tmp):
    """attributed(union windows + linked subagents) + remainder == metered,
    exactly; overlapping record windows count once; the unlinked subagent
    transcript is remainder, not attribution."""
    projects, runs, _m, _a, _b = _build_session(tmp)
    wf = _workflow_record(
        id="eval-RECONWF001", session_id="sid-recon",
        subagents=[{"agent_id": "aaa", "tokens_input": 1000000,
                    "tokens_output": 0, "cost_usd": 0.15}],
    )
    # nested/overlapping agent record (like the boot executor's own record)
    ag = {
        "id": "eval-RECONAG001", "type": "agent", "name": "general-purpose",
        "agent_id": "aaa", "session_id": "sid-recon",
        "started": "2026-10-21T10:10:00Z", "completed": "2026-10-21T10:25:00Z",
        "steps": [], "subagents": [], "total_cost_usd": 0.15,
    }
    (runs / f"{wf['id']}.json").write_text(json.dumps(wf))
    (runs / f"{ag['id']}.json").write_text(json.dumps(ag))

    rw = load_module("reconcile_workflows_test",
                     COST_ATTR_DIR / "reconcile-workflows.py")
    result = rw.reconcile_day("2026-10-21", projects_dir=projects, runs_dir=runs)
    s = result["sessions"]["sid-recon"]
    assert s["session_total_cost_usd"] == round(3.0 + 3.0 + 1.5 + 0.15 + 0.30, 6), s
    assert s["attributed_parent_usd"] == 6.0, s          # both windows' union: m_in1+m_in2 once
    assert s["attributed_subagents_usd"] == 0.15, s      # agent-aaa linked (deduped across records)
    assert s["remainder_main_outside_windows_usd"] == 1.5, s
    assert s["remainder_unlinked_subagents_usd"] == 0.30, s
    assert s["remainder_usd"] == 1.8, s
    assert s["passed"], s
    assert result["day"]["passed"] and result["day"]["invariant_diff_usd"] == 0
    # per-record fully-loaded figures still printed per record (overlap is
    # only de-duplicated in the union accounting)
    wf_row = [r for r in s["records"] if r["id"] == "eval-RECONWF001"][0]
    assert wf_row["parent_window_cost_usd"] == 6.0 and wf_row["fully_loaded_cost_usd"] == 6.15


def test_reconcile_unmatched_record_listed(tmp):
    """A record whose session has no local transcript is reported, not
    silently folded into the invariant."""
    projects, runs, _m, _a, _b = _build_session(tmp)
    ghost = _workflow_record(id="eval-RECONGHOST", session_id="sid-nope")
    (runs / f"{ghost['id']}.json").write_text(json.dumps(ghost))
    rw = load_module("reconcile_workflows_test2",
                     COST_ATTR_DIR / "reconcile-workflows.py")
    result = rw.reconcile_day("2026-10-21", projects_dir=projects, runs_dir=runs)
    ids = [r["id"] for r in result["records_without_local_transcript"]]
    assert "eval-RECONGHOST" in ids, ids


def test_turn_stop_finalize_writes_parent_window(tmp):
    """eval-turn-stop.py finalize() stamps parent_window + fully_loaded_* at
    record close, using the Stop payload's transcript_path."""
    transcript = write_transcript(tmp / "main.jsonl", [
        turn("m_1", "2026-10-21T10:05:00Z", KIMI, input_tokens=1000000),  # $3.00
    ])
    runs = tmp / "runs"
    runs.mkdir(parents=True)
    rec = _workflow_record(
        status="in-progress",
        monitoring={"active": True, "state_yaml_path": "workflows/demo-wf/state.yaml"},
        subagents=[{"agent_id": "sub1", "tokens_input": 1000, "tokens_output": 10,
                    "cost_usd": 0.01}],
        assessment={"mechanical": {"tool_failures": 0, "error_ids": []},
                    "structural": {}, "grading": {},
                    "controller_feedback": {"rating": None, "comment": None,
                                            "timestamp": None}},
    )
    eval_path = runs / f"{rec['id']}.json"
    eval_path.write_text(json.dumps(rec))

    mod = load_module("ets_flc", HOOKS_DIR / "eval-turn-stop.py")
    mod.finalize(eval_path, rec, {"status": "complete"},
                 transcript_path=transcript)

    saved = json.loads(eval_path.read_text())
    pw = saved.get("parent_window")
    assert pw and pw["token_source"] == "parent-window", saved.get("parent_window")
    assert pw["cost_usd"] == 3.0, pw
    # subagent rollup $0.01 + parent window $3.00
    assert saved["fully_loaded_cost_usd"] == 3.01, saved.get("fully_loaded_cost_usd")
    assert saved["status"] == "success", saved.get("status")


def main():
    tmp = Path(tempfile.mkdtemp(prefix="ies-fully-loaded-test-"))
    test_parent_window_strict_window_and_sidechain_exclusion(tmp / "a")
    test_parent_window_empty_window_is_honest_zero(tmp / "b")
    test_apply_workflow_record_no_double_count(tmp / "c")
    test_apply_agent_record_adds_own_run_cost(tmp / "d")
    test_apply_no_session_transcript_is_honest(tmp / "e")
    test_apply_skips_open_and_invalid_windows(tmp / "f")
    test_reconcile_day_invariant_and_overlap(tmp / "g")
    test_reconcile_unmatched_record_listed(tmp / "h")
    test_turn_stop_finalize_writes_parent_window(tmp / "i")
    print("test_fully_loaded_cost: all cases passed")


if __name__ == "__main__":
    main()
