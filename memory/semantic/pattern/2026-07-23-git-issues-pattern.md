---
type: semantic
domain: pattern
confidence: medium
created: 2026-07-23
last-updated: 2026-07-23
tags:
  - git-issues
  - git-sync
  - dream-cycle
  - system-health
synthesized-from:
  - memory/episodic/dream-summary-2026-07-15.md
  - memory/episodic/dream-summary-2026-05-25.md
  - memory/episodic/dream-summary-2026-05-31.md
  - memory/episodic/dream-summary-2026-05-20.md
  - memory/episodic/dream-summary-2026-05-14.md
  - memory/episodic/dream-summary-2026-05-30.md
  - memory/episodic/dream-summary-2026-05-24.md
  - memory/episodic/dream-summary-2026-06-21.md
  - memory/episodic/2026-04-23-dream-cycle-summary.md
  - memory/episodic/2026-04-26-dream-cycle-summary.md
agent-source: dream-cycle
---

# Git Issues Pattern

## Pattern Summary

Recurring git lock and index corruption issues have surfaced across 20 episodic entries spanning April–July 2026. The root cause is consistently the same: git commands issued via the sandboxed bash tool (mcp__workspace__bash) rather than Desktop Commander (host process), creating `.git/index.lock` and `.git/HEAD.lock` files owned by the sandbox user that cannot be unlinked by the host. This is distinct from the `git-sync` pattern (which covers normal pull/push activity) — `git-issues` specifically documents the failure mode and its fix.

## Evidence

- 2026-04-23: 2026-04-23-dream-cycle-summary.md — early git lock issues recorded, root cause not yet diagnosed
- 2026-04-26: 2026-04-26-dream-cycle-summary.md — recurring git lock failures during dream cycle boot pull
- 2026-05-14: dream-summary-2026-05-14.md — git-issues tag appears; sandbox/host conflict documented
- 2026-05-20: dream-summary-2026-05-20.md — git-issues recurring; Desktop Commander identified as correct tool
- 2026-05-24: dream-summary-2026-05-24.md — git-issues; stale lock cleared before pull
- 2026-05-25: dream-summary-2026-05-25.md — git-issues; HEAD.lock cleared before boot pull
- 2026-05-30: dream-summary-2026-05-30.md — git-issues; lock file pattern documented
- 2026-05-31: dream-summary-2026-05-31.md — git-issues; fix confirmed (Desktop Commander only)
- 2026-06-21: dream-summary-2026-06-21.md — git-issues resurface after 3-week gap; same root cause
- 2026-07-15: dream-summary-2026-07-15.md — git-issues; dream cycle log notes recurring 2026-06-13 → 2026-06-21 lock blocker pattern

## Implications

- **Mechanical fix:** All git commands must go through `mcp__Desktop_Commander__start_process` (host process). The sandbox bash tool creates lock files it cannot clean up. This is not a judgment call — it is a hard constraint documented in `skills/git/SKILL.md` and the dream-cycle workflow.
- **Pre-run check:** If a stale `HEAD.lock` or `index.lock` exists at dream-cycle boot, clear it via Desktop Commander before the git pull: `rm /Users/davidohara/develop/jarvis/.git/index.lock` (host-side only).
- **Pattern recurrence:** Despite documentation in SKILL.md, this pattern has recurred at least 5 times since initial diagnosis. Each recurrence stems from a new agent or session failing to read the skill before issuing git commands. The fix must be checked procedurally, not assumed.
- **Scope of impact:** A single orphaned lock file blocks all subsequent git operations in the session, including the end-of-cycle commit/push. Recovery requires manual host-side cleanup or a fresh Desktop Commander call to delete the lock.
