#!/usr/bin/env python3
"""
Git gate: transparent redirection of raw git write commands onto the
authorized wrapper (skills/git/scripts/ies-git), enforced at PreToolUse.

Behavior, for Bash commands only:
  - git READ verbs (log, diff, show, ...) and existing wrapper invocations:
    allowed untouched (silent, exit 0)
  - `git status`: blocked (skill rule; lock-file hazard), with lock-free
    alternatives in the refusal message
  - a clean, single git WRITE verb (add, commit, push, ...): REWRITTEN via
    PreToolUse updatedInput to `python3 skills/git/scripts/ies-git <args>`
    with permissionDecision allow. The model's command executes through the
    wrapper, which enforces the git skill's rules and appends the audit entry.
  - a compound or unparseable git write (chained with &&, |, ;, newlines,
    command substitution, or git at any command position beyond the start,
    e.g. `cd dir && git push`): blocked with an instructive message. A safe
    rewrite of a compound command is impossible, and refusing it mechanically
    enforces the skill's Atomic Command Rule.

Design notes:
  - Classification matches the git VERB position (^git <verb>), never
    substrings, so `cat skills/git/SKILL.md` or `git log --grep=commit`
    can never false-positive.
  - Only the first line of a command is classified (same heredoc protection
    as pre-tool-use.sh); a multi-line command whose first line is a git write
    is blocked rather than rewritten.
  - This hook never both blocks and rewrites: one decision per call.
  - Exit codes: 0 = allow (possibly rewritten via stdout JSON), 2 = block
    (stderr is fed back to the model as feedback).
"""

import json
import re
import sys

WRAPPER = "python3 skills/git/scripts/ies-git"
WRAPPER_RE = re.compile(r"^(\./)?skills/git/scripts/ies-git\b|^python3\s+skills/git/scripts/ies-git\b")

GIT_WRITE_VERBS = {
    "add", "commit", "push", "pull", "fetch", "merge", "rebase",
    "cherry-pick", "reset", "restore", "checkout", "switch", "stash",
    "tag", "apply", "revert", "mv", "rm", "init", "clone", "worktree",
    "bisect", "notes", "update-index", "gc", "prune", "clean", "config",
}

GIT_READ_VERBS = {
    "log", "diff", "show", "ls-files", "remote", "describe", "rev-parse",
    "blame", "shortlog", "cat-file", "reflog", "var", "help", "version",
}

# Git at ANY command position (line start or after && / || / ; / |), used
# on the quote-stripped first line. The 2026-10-10 incident: every git op
# in that session ran as `cd "<repo>" && git <verb> ...` and sailed through
# both this gate and pre-tool-use.sh's delegation trigger, because both
# only looked at position zero — the raw writes reached git untouched and
# the audit spool never saw them. Detection must match command position,
# never bare substrings, so `cat skills/git/SKILL.md` or prose mentioning
# git still can't false-positive.
GIT_CMDPOS_RE = re.compile(r"(?:^|&&|\|\||;|\|)\s*git\s+([a-z][a-z0-9-]*)\b")

# A write is only safely rewritable when the command is a single, simple
# invocation: no shell metachars anywhere in the command string.
UNSAFE_METACHARS = re.compile(r"&&|\|\||;|\||\n|`|\$\(|>|<")

BLOCK_TEMPLATE = (
    "IES git gate: raw `{verb}` is a compound or unparseable command, so it "
    "cannot be safely redirected to the authorized wrapper.\n"
    "Run ONE git operation per call (Atomic Command Rule, skills/git/SKILL.md), "
    "or invoke the wrapper directly:\n"
    "  {wrapper} {verb} ..."
)

STATUS_BLOCK = (
    "IES git gate: `git status` is forbidden (it writes .git/index.lock; on "
    "FUSE mounts that lock orphans and blocks all git operations). "
    "Lock-free alternatives:\n"
    "  git diff --name-only HEAD | git diff --name-only | git diff --staged "
    "--name-only | git ls-files --modified --others --exclude-standard"
)


def classify(command):
    """Return one of: ("read", None) ("wrap", None) ("status", None)
    ("write", verb) ("unknown", verb) ("compound-read", verb)
    ("compound-block", verb) (None, None) for not-a-git-command."""
    first = command.split("\n", 1)[0].strip()
    if not first.startswith("git"):
        if WRAPPER_RE.match(first):
            return ("wrap", None)
        # Git at a command position beyond the start (e.g. `cd dir && git
        # push`): a compound by definition, so never rewritable — reads are
        # allowed through, writes/status/unknown block with the Atomic
        # Command Rule message. Quoted segments are stripped first so prose
        # mentioning git (`echo "run && git push"`) can't false-positive.
        unquoted = re.sub(r'"[^"]*"|\'[^\']*\'', "", first)
        m = GIT_CMDPOS_RE.search(unquoted)
        if not m:
            return (None, None)
        verb = m.group(1)
        if verb in ("branch", "remote"):
            nonflag = [a for a in unquoted[m.end():].split() if not a.startswith("-")]
            if not nonflag:
                return ("compound-read", verb)
            return ("compound-block", verb)
        if verb in GIT_READ_VERBS:
            return ("compound-read", verb)
        return ("compound-block", verb)
    m = re.match(r"^git\s+([a-z][a-z0-9-]*)\b(.*)$", first)
    if not m:
        return ("unknown", None)
    verb, rest = m.group(1), m.group(2)
    if verb == "branch":
        # `git branch` (list) and read-only flag forms are reads; anything
        # with a non-flag argument creates or deletes a branch (write).
        nonflag = [a for a in rest.split() if not a.startswith("-")]
        return ("read" if not nonflag else "write", verb)
    if verb == "remote":
        # `git remote` / `git remote -v` lists; `git remote add ...` writes.
        nonflag = [a for a in rest.split() if not a.startswith("-")]
        return ("read" if not nonflag else "write", verb)
    if verb == "status":
        return ("status", verb)  # classified, then refused with alternatives
    if verb in GIT_READ_VERBS:
        return ("read", verb)
    if verb in GIT_WRITE_VERBS:
        return ("write", verb)
    return ("unknown", verb)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # not our problem; pre-tool-use.sh handles malformed input

    if data.get("tool_name") != "Bash":
        sys.exit(0)

    tool_input = data.get("tool_input") or {}
    command = tool_input.get("command", "")
    if not command:
        sys.exit(0)

    kind, verb = classify(command)

    if kind is None or kind in ("read", "wrap", "compound-read"):
        sys.exit(0)

    if kind == "compound-block":
        # Compound-position git (e.g. `cd dir && git push`): never safe to
        # rewrite, so block. Status gets its lock-free-alternatives message.
        if verb == "status":
            print(STATUS_BLOCK, file=sys.stderr)
        else:
            print(BLOCK_TEMPLATE.format(verb=verb, wrapper=WRAPPER), file=sys.stderr)
        sys.exit(2)

    if kind == "status":
        print(STATUS_BLOCK, file=sys.stderr)
        sys.exit(2)

    if kind == "unknown":
        # A verb neither list knows: block rather than guess (safe default).
        print(
            f"IES git gate: `git {verb}` is not a classified git verb. "
            "If it is a read-only verb, add it to GIT_READ_VERBS in "
            ".claude/hooks/git-gate.py. Otherwise route through the wrapper: "
            f"{WRAPPER} {verb} ...",
            file=sys.stderr,
        )
        sys.exit(2)

    # kind == "write": rewrite only clean single commands. Quoted segments
    # (commit messages legitimately contain && or |) are stripped before the
    # metachar scan; a message that defeats the strip worst-case blocks,
    # which errs safe.
    unquoted = re.sub(r'"[^"]*"|\'[^\']*\'', "", command)
    if UNSAFE_METACHARS.search(unquoted):
        print(BLOCK_TEMPLATE.format(verb=verb, wrapper=WRAPPER), file=sys.stderr)
        sys.exit(2)

    rewritten = re.sub(r"^git\s+", WRAPPER + " ", command.split("\n", 1)[0].strip(), count=1)
    # Empirical (2026-10-08, this build): updatedInput must carry ONLY the
    # changed fields ({"command": ...}), exactly matching the documented
    # example shape. A full tool_input copy (with description, etc.) is
    # silently ignored and the original command runs instead — verified both
    # ways live via the git-version probe before this line was finalized.
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "updatedInput": {"command": rewritten},
        }
    }
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
