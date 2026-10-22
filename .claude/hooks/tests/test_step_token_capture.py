#!/usr/bin/env python3
"""
Regression suite for the per-step token/cost capture chain (Stage 5 Phase 2).
Plain asserts, runnable directly: `python3 test_step_token_capture.py`.

Runs against a THROWAWAY runs dir, workflow dir, and transcript in a temp
directory: nothing under systems/eval-harness/runs/ (the live harness) is
read or written, and no real session index is touched.

Chain under test (each link is a real hook in this build):
  - .claude/hooks/post-tool-use.py  -> writes the step skeleton AND fills
    windowed tokens for a step that ran inline in the main session (it
    already receives transcript_path on its own PostToolUse payload).
  - .claude/hooks/step-complete.py  -> updates that SAME skeleton entry.
    It must key on the name post-tool-use.py wrote (Path(file_path).name,
    ".md" included), not Path(...).stem, or it appends a duplicate and the
    skeleton the audit trail reads stays null.
  - .claude/hooks/eval-agent-stop.py -> resolves the workflow from the
    record's `workflow` field (set from the step path by post-tool-use.py)
    rather than the subagent-type `name` ("general-purpose"), and reaches
    step-complete.py for a subagent-run workflow.

The end-to-end case drives eval-agent-stop.py's main() with a real
SubagentStop payload shape, which spawns the real step-complete.py as a
subprocess against the temp runs dir (via the IES_ROOT env override).
"""

import importlib.util
import io
import json
import os
import sys
import tempfile
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime, timezone, timedelta
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parents[1]
IES_ROOT = Path(__file__).resolve().parents[3]
EVAL_HARNESS_DIR = IES_ROOT / "systems" / "eval-harness"

STEP_STARTED = "2026-10-09T10:00:00Z"
STEP_COMPLETED = "2026-10-09T10:10:00Z"
# Timestamps are quoted, matching every real IES step file -- an unquoted
# ISO timestamp is parsed by YAML into a datetime and json.dump() then fails.
STEP_FRONTMATTER = (
    "---\n"
    "status: complete\n"
    f"started-at: '{STEP_STARTED}'\n"
    f"completed-at: '{STEP_COMPLETED}'\n"
    "outputs:\n"
    "  demo_field: demo_value\n"
    "agent: demo\n"
    "---\n\n"
    "# Demo step body\n"
)

# Two assistant turns inside the step window. Same message.id twice would be
# deduped (real transcripts repeat a turn across content-block lines), so use
# two distinct ids. Model alias resolves to "sonnet" in model-pricing.json.
TRANSCRIPT_LINES = [
    {
        "type": "assistant",
        "isSidechain": False,
        "timestamp": "2026-10-09T10:03:00.000Z",
        "message": {
            "id": "msg_demo_1",
            "model": "claude-sonnet-4-5",
            "usage": {
                "input_tokens": 1000,
                "output_tokens": 200,
                "cache_read_input_tokens": 5000,
                "cache_creation": {"ephemeral_5m_input_tokens": 300, "ephemeral_1h_input_tokens": 0},
            },
        },
    },
    {
        "type": "assistant",
        "isSidechain": False,
        "timestamp": "2026-10-09T10:07:00.000Z",
        "message": {
            "id": "msg_demo_2",
            "model": "claude-sonnet-4-5",
            "usage": {
                "input_tokens": 500,
                "output_tokens": 100,
                "cache_read_input_tokens": 0,
                "cache_creation": {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 0},
            },
        },
    },
]


def load_module(mod_name, filename):
    spec = importlib.util.spec_from_file_location(mod_name, HOOKS_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_harness_module(mod_name, filename):
    spec = importlib.util.spec_from_file_location(mod_name, EVAL_HARNESS_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_main(mod, payload):
    """Feed a hook payload through a module's main(); return captured stdout."""
    mod.sys.stdin = io.StringIO(json.dumps(payload))
    out = io.StringIO()
    with redirect_stdout(out):
        mod.main()
    return out.getvalue()


def build_temp_ies(tmp):
    """Minimal IES-shaped temp root: runs dir, one workflow with one step."""
    runs = tmp / "systems" / "eval-harness" / "runs"
    runs.mkdir(parents=True)
    steps = tmp / "workflows" / "demo-wf" / "steps"
    steps.mkdir(parents=True)
    step_file = steps / "step-01-demo.md"
    step_file.write_text(STEP_FRONTMATTER)

    transcript = tmp / "transcript.jsonl"
    with open(transcript, "w") as f:
        for line in TRANSCRIPT_LINES:
            f.write(json.dumps(line) + "\n")

    return runs, step_file, transcript


def make_record(record_id, session_id, **extra):
    record = {
        "id": record_id,
        "type": "agent",
        "name": "general-purpose",
        "agent": "general-purpose",
        "session_id": session_id,
        "status": "in-progress",
        "started": "2026-10-09T09:59:00Z",
        "steps": [],
        "assessment": {
            "mechanical": {"completed": None, "all_steps_finished": None, "tool_failures": 0, "error_ids": []},
            "structural": {},
            "grading": {},
            "controller_feedback": {"rating": None, "comment": None, "timestamp": None},
        },
    }
    record.update(extra)
    return record


def write_record(runs, record):
    path = runs / f"{record['id']}.json"
    path.write_text(json.dumps(record, indent=2))
    return path


def read_steps(path):
    return json.loads(path.read_text()).get("steps") or []


def steps_named(steps, name):
    return [s for s in steps if isinstance(s, dict) and s.get("name") == name]


def test_post_tool_use_inline_extraction(tmp):
    """post-tool-use.py fills windowed tokens for a main-session step.

    The target record must belong to the step's workflow (name or workflow
    field == "demo-wf"): since 2026-10-21 step writes route by workflow, not
    by "most recent in-progress record" (recency routed plaud-ingest steps
    onto the boot executor's stub, eval-20261021T151415-QZP2GE)."""
    runs, step_file, transcript = build_temp_ies(tmp / "a")
    sid = "sid-post-tool-use"
    rec_path = write_record(runs, make_record("eval-TESTPOSTTOOL01", sid, name="demo-wf", type="workflow"))

    mod = load_module("ptu", "post-tool-use.py")
    mod.EVAL_RUNS_DIR = runs
    mod.INDEX_PATH = tmp / "a" / "no-such-index.json"  # never touch the real index

    run_main(mod, {
        "tool_name": "Edit",
        "tool_input": {"file_path": str(step_file)},
        "session_id": sid,
        "transcript_path": str(transcript),
    })

    steps = read_steps(rec_path)
    # Skeleton key includes the ".md" (Path(file_path).name) -- the existing
    # shape on disk, and the key every later writer must match.
    entries = steps_named(steps, "step-01-demo.md")
    assert len(entries) == 1, f"expected one skeleton entry, got {[s.get('name') for s in steps]}"
    entry = entries[0]
    assert entry.get("tokens_input") == 6800, f"input tokens: {entry.get('tokens_input')}"
    assert entry.get("tokens_output") == 300, f"output tokens: {entry.get('tokens_output')}"
    assert entry.get("model") == "sonnet", f"model: {entry.get('model')}"
    assert entry.get("cost_usd") is not None, "cost_usd must be computed"
    assert entry.get("token_source") == "windowed", f"token_source: {entry.get('token_source')}"
    assert entry.get("owning_agent"), "owning_agent must be set"


def test_step_write_never_routes_to_other_workflow(tmp):
    """A step write for workflow B must NOT land on workflow A's record.

    Regression for 2026-10-21: Knox's plaud-ingest step writes landed on the
    boot executor's stub (most-recent-in-progress routing), corrupted its
    `workflow` stamp to "plaud-ingest", and diverted that subagent's entire
    stop-time step processing to the wrong workflow. New contract: no
    workflow-matched record means an honest skip, not a misattributed write.
    """
    runs, step_file, transcript = build_temp_ies(tmp / "a2")
    sid = "sid-routing-guard"
    # Only record open belongs to a DIFFERENT workflow (a subagent stub
    # stamped with workflow="boot").
    rec_path = write_record(runs, make_record("eval-TESTROUTEGUARD", sid,
                                              name="general-purpose", workflow="boot"))

    mod = load_module("ptu", "post-tool-use.py")
    mod.EVAL_RUNS_DIR = runs
    mod.INDEX_PATH = tmp / "a2" / "no-such-index.json"

    run_main(mod, {
        "tool_name": "Edit",
        "tool_input": {"file_path": str(step_file)},  # workflows/demo-wf/steps/...
        "session_id": sid,
        "transcript_path": str(transcript),
    })

    assert read_steps(rec_path) == [], (
        f"demo-wf step must not be written to a boot-stamped record: {read_steps(rec_path)}")
    # And the record's workflow stamp must survive untouched.
    rec = json.loads(rec_path.read_text())
    assert rec.get("workflow") == "boot", f"workflow stamp corrupted: {rec.get('workflow')}"


def test_step_write_lands_on_closed_record_within_grace(tmp):
    """Late step writes still land on the workflow's record after it closed.

    2026-10-21 boot: eval-turn-stop closed the boot record at 15:41:40 but
    steps 06-08 were written at 15:47-15:50 — under an in-progress-only rule
    those steps had nowhere to go."""
    runs, step_file, transcript = build_temp_ies(tmp / "a3")
    sid = "sid-closed-grace"
    rec_path = write_record(runs, make_record(
        "eval-TESTCLOSEDGRACE", sid, name="demo-wf", type="workflow",
        status="success",
        completed=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")))

    mod = load_module("ptu", "post-tool-use.py")
    mod.EVAL_RUNS_DIR = runs
    mod.INDEX_PATH = tmp / "a3" / "no-such-index.json"

    run_main(mod, {
        "tool_name": "Edit",
        "tool_input": {"file_path": str(step_file)},
        "session_id": sid,
        "transcript_path": str(transcript),
    })

    entries = steps_named(read_steps(rec_path), "step-01-demo.md")
    assert len(entries) == 1, f"step must land on the closed-within-grace record: {read_steps(rec_path)}"


def test_step_complete_updates_same_key(tmp):
    """step-complete.py updates the skeleton instead of appending a duplicate."""
    runs, step_file, transcript = build_temp_ies(tmp / "b")
    sid = "sid-step-complete"
    rec = make_record("eval-TESTSTEPCOMPL01", sid, name="demo-wf", workflow="demo-wf")
    rec_path = write_record(runs, rec)

    mod = load_module("sc", "step-complete.py")
    mod.EVAL_RUNS_DIR = runs

    run_main(mod, {
        "step_file_path": str(step_file),
        "step_content": STEP_FRONTMATTER,
        "transcript_path": str(transcript),
        "session_id": sid,
        "workflow_name": "demo-wf",
        "eval_record_id": rec["id"],
    })

    steps = read_steps(rec_path)
    # No duplicate un-suffixed entry may be created.
    assert not steps_named(steps, "step-01-demo"), \
        f"step-complete appended a duplicate key: {[s.get('name') for s in steps]}"
    entries = steps_named(steps, "step-01-demo.md")
    assert len(entries) == 1, f"expected one entry, got {[s.get('name') for s in steps]}"
    entry = entries[0]
    assert entry.get("tokens_input") == 6800, f"input tokens: {entry.get('tokens_input')}"
    assert entry.get("tokens_output") == 300, f"output tokens: {entry.get('tokens_output')}"
    assert entry.get("model") == "sonnet", f"model: {entry.get('model')}"
    assert entry.get("cost_usd") is not None, "cost_usd must be computed"
    assert entry.get("token_source") == "windowed", f"token_source: {entry.get('token_source')}"


def test_agent_stop_wiring_end_to_end(tmp):
    """eval-agent-stop.py resolves the workflow and reaches step-complete.py."""
    root = tmp / "c"
    runs, step_file, transcript = build_temp_ies(root)
    sid = "sid-agent-stop"
    rec = make_record(
        "eval-TESTAGENTSTOP01", sid,
        agent_id="AID_DEMO",
        name="general-purpose",   # the subagent-type label, NOT the workflow
        workflow="demo-wf",       # the workflow this subagent actually ran
    )
    rec_path = write_record(runs, rec)

    mod = load_module("eas", "eval-agent-stop.py")
    mod.EVAL_RUNS_DIR = runs
    mod.IES_ROOT = root  # workflows/demo-wf/steps lives under the temp root

    # Real SubagentStop payload shape: agent_id, agent_type, agent_transcript_path.
    run_main(mod, {
        "agent_id": "AID_DEMO",
        "agent_type": "general-purpose",
        "agent_transcript_path": str(transcript),
        "session_id": sid,
    })

    steps = read_steps(rec_path)
    entries = steps_named(steps, "step-01-demo.md")
    assert len(entries) == 1, f"expected one step entry, got {[s.get('name') for s in steps]}"
    entry = entries[0]
    assert entry.get("tokens_input") == 6800, f"input tokens: {entry.get('tokens_input')}"
    assert entry.get("tokens_output") == 300, f"output tokens: {entry.get('tokens_output')}"
    assert entry.get("cost_usd") is not None, "cost_usd must be computed"
    assert entry.get("token_source") in ("windowed", "lenient_fallback"), \
        f"token_source: {entry.get('token_source')}"


def test_close_merge_does_not_shadow_captured_step(tmp):
    """close-eval-record.py's --steps merge must not append a null skeleton
    next to a captured '.md' entry (the '.md' vs bare-name key mismatch)."""
    mod = load_harness_module("cer", "close-eval-record.py")
    captured = {"name": "step-01-demo.md", "tokens_input": 6800, "tokens_output": 300, "cost_usd": 0.01}
    skeleton = [{"name": "step-01-demo", "tokens_input": None, "tokens_output": None, "cost_usd": None}]
    merged = mod.merge_steps([captured], skeleton)
    assert len(merged) == 1, f"merge appended a duplicate: {[s.get('name') for s in merged]}"
    assert merged[0].get("name") == "step-01-demo.md", merged[0]
    assert merged[0].get("tokens_input") == 6800, merged[0]


def test_daily_review_subagent_capture(tmp):
    """daily-review is instrumented the same way as the other candidates:
    a daily-review-shaped subagent run whose step carries a real
    [started-at, completed-at] window yields a windowed per-step token entry
    on the record (Stage 5 finding #4 — before this, no daily-review step
    ever carried token_source)."""
    root = tmp / "d"
    runs, _demo_step, transcript = build_temp_ies(root)
    dr_steps = root / "workflows" / "daily-review" / "steps"
    dr_steps.mkdir(parents=True, exist_ok=True)
    (dr_steps / "step-01-capture.md").write_text(STEP_FRONTMATTER)

    sid = "sid-daily-review"
    rec = make_record(
        "eval-TESTDAILYREVIEW01", sid,
        agent_id="AID_DR",
        name="general-purpose",   # subagent-type label, not the workflow
        workflow="daily-review",
    )
    rec_path = write_record(runs, rec)

    mod = load_module("eas_dr", "eval-agent-stop.py")
    mod.EVAL_RUNS_DIR = runs
    mod.IES_ROOT = root

    run_main(mod, {
        "agent_id": "AID_DR",
        "agent_type": "general-purpose",
        "agent_transcript_path": str(transcript),
        "session_id": sid,
    })

    entries = steps_named(read_steps(rec_path), "step-01-capture.md")
    assert len(entries) == 1, f"expected one daily-review step entry, got {entries}"
    entry = entries[0]
    assert entry.get("tokens_input") == 6800, f"input tokens: {entry.get('tokens_input')}"
    assert entry.get("tokens_output") == 300, f"output tokens: {entry.get('tokens_output')}"
    assert entry.get("cost_usd") is not None, "cost_usd must be computed"
    assert entry.get("token_source") == "windowed", f"token_source: {entry.get('token_source')}"


def test_daily_review_step_files_conform():
    """Every real daily-review step file carries the frontmatter the capture
    chain reads (status/started-at/completed-at + model). The previous state
    was the only place in the whole library with `status: complete` alongside a
    null `started-at`, which made the window uncomputable and blocked every
    capture path (Stage 5 finding #4)."""
    steps_dir = IES_ROOT / "workflows" / "daily-review" / "steps"
    files = sorted(steps_dir.glob("step-*.md"))
    assert files, f"no daily-review step files found under {steps_dir}"
    for f in files:
        text = f.read_text()
        lines = text.split("\n")
        assert lines and lines[0].strip() == "---", f"{f.name}: no leading frontmatter"
        fm = {}
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip()
        for key in ("status", "started-at", "completed-at", "model"):
            assert key in fm, f"{f.name}: missing frontmatter key {key!r}"
        # A completed step must carry a real start; a not-started one must not
        # claim completion. (The invalid old state was complete + null start.)
        if fm["status"] in ("complete", "completed"):
            assert fm["started-at"] not in ("~", "null", ""), \
                f"{f.name}: complete step with null started-at (blocks windowed capture)"
        else:
            assert fm["completed-at"] in ("~", "null", ""), \
                f"{f.name}: un-run step should not carry a completed-at"


def test_provider_model_pricing_populates_cost(tmp):
    """The pricing fix (Stage 5 finding #4): the provider model ids the eval
    records actually carry (this instance routes Claude tiers to Fireworks —
    ~/.claude/settings.json ANTHROPIC_DEFAULT_*_MODEL) now resolve in
    model-pricing.json, so a capture over such a transcript yields a real
    cost_usd instead of null."""
    harness = load_harness_module("tu", "token_usage.py")
    from step_audit import compute_cost
    # Direct lookup: priced provider id -> cost; genuinely unknown id -> None.
    assert compute_cost("accounts/fireworks/models/kimi-k3", 1000, 500) is not None
    assert compute_cost("glm-5p3", 1000, 500) is not None
    assert compute_cost("accounts/fireworks/models/does-not-exist", 1000, 500) is None

    transcript = tmp / "fleet.jsonl"
    lines = []
    for i, ts in enumerate(("2026-10-09T10:03:00.000Z", "2026-10-09T10:07:00.000Z")):
        lines.append({
            "type": "assistant", "isSidechain": False, "timestamp": ts,
            "message": {"id": f"msg_fleet_{i}", "model": "accounts/fireworks/models/kimi-k3",
                        "usage": {"input_tokens": 1000, "output_tokens": 200,
                                  "cache_read_input_tokens": 0,
                                  "cache_creation": {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 0}}},
        })
    transcript.write_text("\n".join(json.dumps(x) for x in lines) + "\n")
    usage = harness.usage_between(str(transcript), STEP_STARTED, STEP_COMPLETED,
                                  exclude_sidechain=True, lenient_fallback=False)
    assert usage is not None, "usage_between returned nothing"
    assert usage.get("cost_usd") is not None, \
        f"provider model must now price, got cost_usd={usage.get('cost_usd')}"
    assert usage.get("model") == "accounts/fireworks/models/kimi-k3", usage.get("model")


def test_phantom_success_guard(tmp):
    """close-eval-record.py refuses to record success/partial with no execution
    window (Stage 3 remediation — chief C4/C2).

    The 16 phantom-success daily-review scheduled runs were closed as
    `status: success` with duration_seconds 0.0 and a stale session_id — the
    from-scratch (Cowork) path with no stub and no --started, so started_dt
    fell back to `now` (eval-20260711T021151-T7AGFP, eval-20260707T021251-KHEVMG,
    eval-20260704T021304-XNRG5T, eval-20260620T021321-T6V6WJ,
    eval-20260602T021149-SL6FJ9, …). A run with no execution window cannot
    claim success; a real run (a --started window) still can.
    """
    mod = load_harness_module("cer_guard", "close-eval-record.py")

    root = tmp / "g"
    idx = root / "memory" / "sessions" / "index.json"
    idx.parent.mkdir(parents=True)
    idx.write_text("[]")
    mod.IES_ROOT = root
    mod.SESSION_INDEX = idx
    mod.current_session_id = lambda: "sid-guard"

    base = ["--name", "daily-review", "--type", "workflow", "--agent", "chief",
            "--trigger", "scheduled", "--steps", "step-auto"]

    def run_close(argv):
        runs = Path(tempfile.mkdtemp(prefix="ies-cer-guard-", dir=str(root)))
        mod.EVAL_RUNS_DIR = runs
        mod.sys.argv = ["close-eval-record.py"] + argv
        err = io.StringIO()
        with redirect_stdout(io.StringIO()), redirect_stderr(err):
            mod.main()
        recs = list(runs.glob("eval-*.json"))
        assert len(recs) == 1, f"expected one record, got {recs}"
        return json.loads(recs[0].read_text()), err.getvalue()

    # (1) Phantom: success, no stub, no --started -> downgraded to failure.
    rec, err = run_close(base + ["--status", "success"])
    assert rec["status"] == "failure", f"phantom not downgraded: {rec['status']}"
    assert rec["duration_seconds"] == 0.0, rec["duration_seconds"]
    assert rec["assessment"]["mechanical"]["abort_reason"] == "zero-duration-no-execution", rec
    assert "PHANTOM-SUCCESS GUARD" in err, err

    # (2) Legit: success WITH a real --started window -> stays success.
    start = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat().replace("+00:00", "Z")
    rec, err = run_close(base + ["--status", "success", "--started", start])
    assert rec["status"] == "success", f"legit run downgraded: {rec['status']}"
    assert rec["duration_seconds"] >= 500, rec["duration_seconds"]
    assert "PHANTOM-SUCCESS GUARD" not in err, err


def main():
    tmp = Path(tempfile.mkdtemp(prefix="ies-step-token-test-"))
    test_post_tool_use_inline_extraction(tmp)
    test_step_complete_updates_same_key(tmp)
    test_agent_stop_wiring_end_to_end(tmp)
    test_close_merge_does_not_shadow_captured_step(tmp)
    test_daily_review_subagent_capture(tmp)
    test_daily_review_step_files_conform()
    test_provider_model_pricing_populates_cost(tmp)
    test_phantom_success_guard(tmp)
    print("test_step_token_capture: all cases passed")


if __name__ == "__main__":
    main()
