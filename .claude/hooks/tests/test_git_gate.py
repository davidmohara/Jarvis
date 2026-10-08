#!/usr/bin/env python3
"""
Regression suite for git-gate.py classification and rewrite output.
Plain asserts, runnable directly: `python3 test_git_gate.py`.

Every case is a real shape seen in this session's Bash calls or a
near-miss that must never misroute:
  - classification must match the VERB position, never substrings
    (`cat skills/git/SKILL.md`, `git log --grep=commit` are reads/no-op)
  - wrapper invocations pass through untouched (no double-rewrite)
  - clean single git writes produce PreToolUse updatedInput JSON with
    permissionDecision allow
  - compound git writes block (Atomic Command Rule), but quoted -m
    content containing && or | must NOT trip the metachar block
  - `git status` blocks with lock-free alternatives
  - unclassified verbs block rather than guess (safe default)

Companion wrapper-policy tests (status refusal, commit lint, gated dirs,
secrets, force-to-main) live in test_ies_git.py.
"""

import importlib.util
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

HOOK_PATH = Path(__file__).resolve().parents[1] / "git-gate.py"


def load_module():
    spec = importlib.util.spec_from_file_location("git_gate", HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_hook(mod, command, tool="Bash"):
    """Feed one tool call through main(); return (exit_code, stdout, stderr)."""
    payload = json.dumps({"tool_name": tool, "tool_input": {"command": command, "description": "test"}})
    mod.sys.stdin = io.StringIO(payload)
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with redirect_stdout(out):
        old_err, mod.sys.stderr = sys.stderr, err
        try:
            mod.main()
        except SystemExit as e:
            code = e.code or 0
        finally:
            mod.sys.stderr = old_err
    return code, out.getvalue(), err.getvalue()


def main():
    mod = load_module()

    # --- classification: verb position, never substrings ---
    cases = [
        ("git log --oneline -5", "read"),
        ("git diff --name-only HEAD", "read"),
        ("git log --grep=commit", "read"),  # 'commit' as text, not verb
        ("git branch", "read"),
        ("git branch --show-current", "read"),
        ("git remote -v", "read"),
        ("cat skills/git/SKILL.md", None),  # not a git command at all
        ("echo 'git commit would go here'", None),
        ("git add -A", "write"),
        ("git commit -m 'feat(rigby): add gate'", "write"),
        ("git push origin main", "write"),
        ("git branch -d feat/old", "write"),
        ("git remote add upstream x", "write"),
        ("git status", "status"),
        ("git frobnicate", "unknown"),
    ]
    for command, expected in cases:
        kind, _ = mod.classify(command)
        assert kind == expected, f"classify({command!r}) = {kind!r}, expected {expected!r}"

    # wrapper invocations are recognized by classify (wrap) and pass through
    kind, _ = mod.classify("python3 skills/git/scripts/ies-git add -A")
    assert kind == "wrap", f"wrapper invocation classified {kind!r}"
    code, out, err = run_hook(mod, "python3 skills/git/scripts/ies-git add -A")
    assert code == 0 and out == "" and err == "", "wrapper invocation must pass through silently"

    # --- passthrough: reads, non-Bash tools, non-git commands ---
    for command in ["git log --oneline -5", "ls -la", "python3 unrelated.py git-ish"]:
        code, out, err = run_hook(mod, command)
        assert code == 0 and out == "" and err == "", f"read/passthrough {command!r} must be silent allow"

    code, out, err = run_hook(mod, "git commit -m 'x'", tool="Read")
    assert code == 0 and out == "", "non-Bash tools must be ignored"

    # --- rewrite: clean single git write -> updatedInput allow JSON ---
    # updatedInput must carry ONLY the changed field (empirically verified
    # 2026-10-08: a full tool_input copy is silently ignored by this build).
    code, out, err = run_hook(mod, 'git commit -m "feat(rigby): add gate"')
    assert code == 0, f"clean write must allow (exit 0), got {code}: {err}"
    payload = json.loads(out)
    hs = payload["hookSpecificOutput"]
    assert hs["hookEventName"] == "PreToolUse", hs
    assert hs["permissionDecision"] == "allow", hs
    assert hs["updatedInput"] == {"command": 'python3 skills/git/scripts/ies-git commit -m "feat(rigby): add gate"'}, hs

    code, out, err = run_hook(mod, "git add CHANGELOG.md projects/")
    assert code == 0 and "git-ops.jsonl" not in out
    assert json.loads(out)["hookSpecificOutput"]["updatedInput"] == {
        "command": "python3 skills/git/scripts/ies-git add CHANGELOG.md projects/"
    }

    # --- block: compound writes (Atomic Command Rule) ---
    for command in [
        "git add -A && git commit -m 'x'",
        "git commit -m 'a' | tee log",
        "git push origin main; echo done",
        "git add $(find . -name '*.tmp')",
        "git checkout -b newbranch && git push -u origin newbranch",
    ]:
        code, out, err = run_hook(mod, command)
        assert code == 2 and out == "", f"compound {command!r} must block with exit 2, got {code}"
        assert "Atomic Command Rule" in err or "cannot be safely redirected" in err, err

    # --- the incident case: quoted -m content containing metachars must NOT block ---
    code, out, err = run_hook(mod, 'git commit -m "feat: support a && b and pipe | char"')
    assert code == 0 and json.loads(out)["hookSpecificOutput"]["updatedInput"]["command"].endswith(
        'ies-git commit -m "feat: support a && b and pipe | char"'
    ), f"quoted metachar message misrouted: code={code} err={err}"

    # --- block: git status, with alternatives ---
    code, out, err = run_hook(mod, "git status")
    assert code == 2 and "git diff --name-only HEAD" in err, err

    # --- block: unclassified verb (safe default) ---
    code, out, err = run_hook(mod, "git frobnicate --all")
    assert code == 2 and "not a classified git verb" in err, err

    # --- multiline: first line is a git write -> block, never partial rewrite ---
    code, out, err = run_hook(mod, "git add -A\nrm -rf /")
    assert code == 2 and out == "", "multiline git write must block, not rewrite the first line"

    print("test_git_gate: all cases passed")


if __name__ == "__main__":
    main()
