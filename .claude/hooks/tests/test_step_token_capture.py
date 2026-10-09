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
from contextlib import redirect_stdout
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
    """post-tool-use.py fills windowed tokens for a main-session step."""
    runs, step_file, transcript = build_temp_ies(tmp / "a")
    sid = "sid-post-tool-use"
    rec_path = write_record(runs, make_record("eval-TESTPOSTTOOL01", sid))

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


def main():
    tmp = Path(tempfile.mkdtemp(prefix="ies-step-token-test-"))
    test_post_tool_use_inline_extraction(tmp)
    test_step_complete_updates_same_key(tmp)
    test_agent_stop_wiring_end_to_end(tmp)
    test_close_merge_does_not_shadow_captured_step(tmp)
    print("test_step_token_capture: all cases passed")


if __name__ == "__main__":
    main()
