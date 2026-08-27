#!/usr/bin/env python3
"""
Regression suite for eval-turn-start.py's detect_workflow(). No framework
dependency — plain asserts, runnable directly: `python3 test_detect_workflow.py`.

This exists because detect_workflow() has been tightened three times in one
session, each time after a real false-positive incident:
  1. Bare workflow-name mentions ("what does boot even do") — fixed with
     run-verb-adjacency requirement.
  2. shutdown-cleanup's real natural-language trigger ("exit"/"log off")
     never containing the workflow's own name/slug — fixed with
     WORKFLOW_TRIGGER_PHRASES / _ANCHORED.
  3. A run-verb-adjacent match anywhere in a long message firing on a LATER,
     unrelated clause that happened to mention a workflow name near an
     unrelated verb — fixed by restricting all non-path/non-slash matching
     to the prompt's first clause (see _first_clause()).

Every incident's actual failing prompt is preserved here as a permanent
regression case so it can never silently reappear.
"""

import importlib.util
import sys
from pathlib import Path

HOOK_PATH = Path(__file__).resolve().parents[1] / "eval-turn-start.py"


def load_module():
    spec = importlib.util.spec_from_file_location("eval_turn_start", HOOK_PATH)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


CASES = [
    # (prompt, expected_workflow_or_None, short description)
    ("run boot", "boot", "explicit run-verb + name"),
    ("/boot", "boot", "slash command"),
    ("workflows/boot/workflow.md", "boot", "explicit path reference"),
    ("start the boot workflow", "boot", "run-verb + phrase form of name"),
    ("boot, go ahead and run it", None, "name first, verb refers to pronoun not name"),
    ("we discussed boot instrumentation earlier tonight, the eval record for boot never fired", None, "bare mention, no run-verb adjacency"),
    ("kick off shutdown cleanup", "shutdown-cleanup", "run-verb + phrase form of name"),
    ("please run the weekly review workflow now", "weekly-review", "run-verb + phrase form of name"),
    ("what does boot even do", None, "'do' is not a run-verb (regression case: 'do' was mistakenly included once)"),
    ("fix boot's eval blind spot", None, "bare mention in a work request about boot itself"),
    ("good morning", None, "no workflow mentioned at all"),
    ("I want to exit", "shutdown-cleanup", "anchored single-word trigger, whole message"),
    ("exit", "shutdown-cleanup", "anchored single-word trigger, bare"),
    ("ok, lets exit", "shutdown-cleanup", "anchored single-word trigger, trailing"),
    ("log off please", "shutdown-cleanup", "multi-word trigger phrase, anywhere in first clause"),
    ("let's end the session", "shutdown-cleanup", "multi-word trigger phrase"),
    ("did you exit the meeting early", None, "'exit' not anchored to end of clause"),
    ("the client wants to exit their contract early, can you draft language for that", None, "'exit' mid-clause, unrelated domain"),
    ("time to shut down", "shutdown-cleanup", "anchored single-word trigger variant"),
    (
        "Master was relaying the persona-fix dispatch work. Separately, can you check why "
        "boot keeps opening spurious eval records when we run other things",
        None,
        "REAL INCIDENT: 'boot' + 'run' both present but in a later clause, not the first",
    ),
    (
        "I finished the capability-build task. Now let's discuss what happened with boot's "
        "eval record from the run at 16:22",
        None,
        "REAL INCIDENT: discussion of a completed boot run, mid-message",
    ),
    (
        "Rigby, dispatch the persona fix now. By the way, remember to check on the boot "
        "workflow later",
        None,
        "REAL INCIDENT: unrelated dispatch instruction, boot mentioned as an aside",
    ),
    (
        "here is a long message about several things. First, the report is ready. Second, "
        "please log off my old account from the portal. Third, run the numbers on Q3",
        None,
        "'log off' present but not in the first clause, and refers to an unrelated account",
    ),
    (
        "quick heads up before you continue: run the report generator, and separately I "
        "was thinking about whether we should exit the McKesson deal",
        None,
        "'run' and 'exit' both present but neither in the first clause, neither about a workflow",
    ),
    ("run boot now, and after that pull my calendar for tomorrow", "boot", "real invocation leading a longer message — must still fire"),
    ("exit. also remind me to call Sarah tomorrow", "shutdown-cleanup", "real invocation as first clause of a longer message — must still fire"),
]


def main():
    m = load_module()
    workflows = m.load_master_workflows()
    if not workflows:
        print("FATAL: load_master_workflows() found no agent: master workflows — "
              "cannot run test suite (are you running this from a checkout with "
              "workflows/boot, workflows/shutdown-cleanup, workflows/weekly-review present?)")
        sys.exit(2)

    failures = []
    for prompt, expected, desc in CASES:
        got = m.detect_workflow(prompt, workflows)
        ok = got == expected
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] expected={expected!r:20} got={got!r:20} — {desc}")
        if not ok:
            failures.append((prompt, expected, got, desc))

    print()
    print(f"{len(CASES) - len(failures)}/{len(CASES)} passed")
    if failures:
        print("\nFAILURES:")
        for prompt, expected, got, desc in failures:
            print(f"  - {desc}\n    prompt={prompt!r}\n    expected={expected!r} got={got!r}")
        sys.exit(1)


if __name__ == "__main__":
    main()
