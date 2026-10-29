#!/usr/bin/env python3
"""Regression suite for spawn-prompt agent attribution (2026-10-29).

The knox mislabel: eval-20261029T143236-FU0JH4 is a boot-token-analysis agent
whose prompt merely mentioned "Knox plaud-ingest runs". The old resolver
counted any whole-word mention of an unambiguous agent name, so the record was
stamped `agent: knox, owning_agent: knox`. Attribution must key on what the
spawn IS — an explicit identity declaration, an acting-as instruction, a
persona file actually read, a direct address, a skill-owner path — never on an
incidental filename/persona mention in prose.

Plain asserts, runnable directly: `python3 test_attribution_heuristics.py`.
"""

import importlib.util
import sys
from pathlib import Path

EVAL_HARNESS_DIR = Path(__file__).resolve().parents[3] / "systems" / "eval-harness"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sys.path.insert(0, str(EVAL_HARNESS_DIR))
hu = load_module("hook_utils_attr_test", EVAL_HARNESS_DIR / "hook_utils.py")
resolve = hu.resolve_spawn_agent_from_prompt

CASES = [
    # (text, expected)
    # --- the bug: bare mentions are not identities ---
    ("Analysis task: boot workflow token usage ... and Knox plaud-ingest "
     "runs spawned from boot step-01 if separately attributable.", None),
    ("Read the notes Knox wrote about the plaud-ingest pipeline.", None),
    ("Please chase down the invoice and the master file.", None),
    ("Single-purpose data pull. You are NOT loading any persona file or "
     "SYSTEM.md — execute six bounded tasks then exit.", None),
    # --- explicit identity declarations ---
    ("You are Chief, executing `workflows/morning-briefing/steps/"
     "step-04-synthesize-briefing.md` for the boot run.", "chief"),
    ("You are **Master**, the coordinator.", "master"),
    ("You are acting as Rigby, the IES System Operator agent "
     "(persona at agents/rigby.md — read it first).", "rigby"),
    ("You are acting as Chief (Daily Operations & Execution) for the morning "
     "boot.", "chief"),
    # --- persona-attributed persona file references ---
    ("You are the boot executor sub-agent. Your persona is defined in "
     "/ies/agents/master.md — read it first.", "master"),
    ("Load persona `agents/master.md` before starting.", "master"),
    # --- direct address ---
    ("Knox — run `workflows/plaud-ingest/workflow.md` in full.", "knox"),
    ("Rigby: build the capability package.", "rigby"),
    ("Shep — build a prep sheet for David's call today.", "shep"),
    # --- skill-owner path (single) ---
    ("You are a Grader agent (per .claude/skills/rigby-capability-build/"
     "subagents/grader.md — read it first, then follow it exactly).", "rigby"),
    # --- short dispatch cue ---
    ("Master here. Please spawn Ralph with the following task.", "ralph"),
    ("Agent: Shep. Do the thing.", "shep"),
    # --- long briefs: cue/mention mining must stay off ---
    ("You are executing Phase C of an approved plan. " + "x " * 400 +
     "spawning knox and agent: master are described in the architecture.",
     None),
]


def test_cases():
    for text, expected in CASES:
        got = resolve(text)
        assert got == expected, (
            f"resolve_spawn_agent_from_prompt({text[:60]!r}...) "
            f"-> {got!r}, expected {expected!r}")
    print(f"test_cases: {len(CASES)} attribution cases passed")


def test_persona_reads_beat_prompt():
    """A subagent that actually reads agents/<name>.md resolves to that agent
    even when the prompt carries no opener."""
    import json
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "agent-x.jsonl"
        rows = [
            {"type": "user", "message": {"content": "Do the analysis."}},
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Read",
                 "input": {"file_path": "/ies/agents/knox.md"}}]}},
        ]
        p.write_text("\n".join(json.dumps(r) for r in rows))
        assert hu.agent_from_transcript(p) == "knox", hu.agent_from_transcript(p)
    print("test_persona_reads_beat_prompt: passed")


def test_ambiguous_persona_reads():
    """Two different personas read -> ambiguous -> falls through to None."""
    import json
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "agent-y.jsonl"
        rows = [
            {"type": "user", "message": {"content": "Do the cleanup."}},
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Read",
                 "input": {"file_path": "/ies/agents/chase.md"}},
                {"type": "tool_use", "name": "Read",
                 "input": {"file_path": "/ies/agents/harper.md"}}]}},
        ]
        p.write_text("\n".join(json.dumps(r) for r in rows))
        assert hu.agent_from_transcript(p) is None, hu.agent_from_transcript(p)
    print("test_ambiguous_persona_reads: passed")


if __name__ == "__main__":
    test_cases()
    test_persona_reads_beat_prompt()
    test_ambiguous_persona_reads()
    print("\nAll attribution regression tests pass.")
