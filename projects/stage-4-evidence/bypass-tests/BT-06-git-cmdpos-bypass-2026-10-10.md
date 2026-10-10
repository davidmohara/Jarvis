# BT-06: Command-Position Git Bypass of the Git Gate (found in the wild)

**Date:** 2026-10-10 · **Mechanism under test:** `.claude/hooks/pre-tool-use.sh` + `.claude/hooks/git-gate.py` · **Related:** BT-05 (verified the redirect for clean `git <verb>` shapes; this is the shape it did not cover)

Unlike BT-01..BT-05, this was not a controlled test. The bypass fired **in production** and was discovered post-hoc: while investigating a cancelled SessionEnd hook (2026-10-10), the audit spool (`.git/ies/git-ops.jsonl`) showed a session's `add`/`commit`/`push` calls had reached raw git with no audit entries. The git-ops audit log being load-bearing is exactly what caught it, which is the enforcement-honesty story in one sentence.

## The hole

Every git operation in that session was issued as:

```
cd "/Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES" && git <verb> ...
```

Both enforcement layers anchored their git detection to **position zero** of the command line:

1. `pre-tool-use.sh` only delegated to `git-gate.py` when the primary line matched `^(git |skills/git/...|python3 skills/git/...)`. A `cd`-prefixed command never invoked the gate at all.
2. `git-gate.py`'s `classify()` checked `first.startswith("git")`, so even when consulted it classified the command as not-a-git-command.

The gate already had correct behavior defined for this case: its metachar scan is supposed to block compound git writes with the Atomic Command Rule message. Detection never reached that code. Result: raw writes, no lint, no gated-dir refusal, no credential scan, no audit entries. BT-05's verification matrix used clean `git <verb>`-shaped probes, which is why this survived it.

## The fix (2026-10-10, same session)

- `git-gate.py`: `GIT_CMDPOS_RE` matches git at any command position (line start, or after `&&`, `||`, `;`, `|`), run against the **quote-stripped** first line so prose mentioning git cannot false-positive. Compound-position writes/status/unknown block with the instructive message (status gets the lock-free-alternatives text); compound-position reads pass silently; compounds are never rewritten.
- `pre-tool-use.sh`: the delegation trigger now also matches `[&|;]<space>*git<space>`, so cd-chained git reaches the gate at all.
- Regression suite: 13 new cases in `test_git_gate.py`, including end-to-end runs through `pre-tool-use.sh` itself (layer 1 is where the incident actually slipped through, so the shell hook is asserted directly, not just the Python classifier).

## Verification matrix (executed live this session)

| # | Attempt | Expected | Actual | Verdict |
|---|---------|----------|--------|---------|
| V1 | Pre-fix demo: `cd "/path" && git commit -m "test"` through pre-tool-use.sh | redirect or block | silent exit 0, raw command would run | **BYPASSED (pre-fix, reproduced)** |
| V2 | Same command post-fix | block with Atomic Command Rule message | blocked, exit 2, instructive wrapper syntax shown | **BLOCKED** |
| V3 | `cd "/path" && git log --oneline -3` post-fix | silent allow | exit 0, no output | **ALLOWED (no friction added)** |
| V4 | `echo "notes on && git push"` (quoted prose) post-fix | silent allow | exit 0, no output (quote-stripping prevents false positive) | **ALLOWED** |
| V5 | Clean `git commit -m "clean"` post-fix | rewritten to wrapper through the shell layer | stdout carries the `ies-git` rewrite | **REDIRECTED (BT-05 behavior preserved)** |
| V6 | `test_git_gate.py` + `test_ies_git.py` | all pass | all cases passed | **PASS** |

Full command/output transcript: `logs/BT-06-cmdpos-bypass.log`.

## Honest limits

- `sh -c "git commit"`, `bash -c`, or subprocess escapes still bypass the gate (it classifies Bash-tool command text only). Unchanged from BT-05's disclosure; the audit log and per-step verifiers remain the post-hoc net.
- Hook script edits can take a turn to propagate on this OneDrive/FUSE mount, so a live session immediately after this fix may briefly still run the stale gate. Probe after editing before relying on new gate behavior.
- Only the **first line** is classified (heredoc protection), so a git write on a later line of a multi-line command is still outside detection. Narrow, disclosed, same class as the residual escapes above.
- The audit spool catches misses only at the next `add` (untracked `.git/ies/` spool folds into the tracked log), so a raw-write session is detectable post-hoc but not in real time.

**Net effect for the Stage 5 submission:** the BT-05 technical enforcement now covers git at any command position, not just position zero, and the discovery itself demonstrates the audit trail is load-bearing: the git-ops log caught a real enforcement gap that the enforcement could not see itself.
