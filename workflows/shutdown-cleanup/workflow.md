---
name: shutdown-cleanup
description: Session exit cleanup — purge temp artifacts, organize deliverables, verify naming, commit clean
agent: master
model: sonnet
---

<!-- system:start -->
# Shutdown Cleanup Workflow

**Goal:** Leave the workspace clean after every session. No temp artifacts committed, all deliverables properly named and placed, gitignore patterns up to date, and a clean commit.

**Agent:** Master — Orchestrator

**Architecture:** Automated 4-step workflow. Master runs this without controller interaction when exit is signaled. Report a summary of actions taken at the end.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Trigger

This workflow runs automatically when the controller signals exit, log off, or end of session. It executes before the final commit.

### Artifact Categories

| Category | Examples | Action |
|----------|---------|--------|
| Intermediate build files | `.html` from PDF pipelines, temp scripts (`.js`, `.py`, `.sh`) | Delete |
| System artifacts | `.DS_Store`, `.fuse_hidden*`, `__pycache__`, `.tmp` | Delete |
| Deliverables | PDF, Word, PPTX, EPUB — generated for reading or distribution | Verify naming and location |
| Source files | Markdown files created or modified during the session | Verify naming convention |

### Output

- Clean workspace with no temp artifacts
- All deliverables properly named and located
- Updated `.gitignore` if new patterns discovered
- Summary of cleanup actions for the controller
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.

2. If `status: in-progress`:
   - You are resuming a previous run. Do NOT start over.
   - Read `current-step` to find where to continue.
   - Load `accumulated-context` — this is the data already gathered. Do not re-gather it.
   - Check that step's frontmatter:
     - If `status: in-progress`: the step was interrupted mid-execution — re-execute it.
     - If `status: not-started`: begin it fresh.
   - Notify the controller: "[Agent]: Resuming [workflow-name] from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

4. If `status: aborted`:
   - Do not resume automatically. Surface to controller:
     "[Agent]: [workflow-name] was previously aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.

## EXECUTION

**Dispatch model:** every step runs as a spawned sub-agent — no inline exception here at all. Checked step-01 (`step-01-purge-artifacts.md`) specifically against boot's constraint (does it load `agents/master.md`/`SYSTEM.md`/identity files into Master's *own* live session?): no — it purges temp-file patterns and runs the IES root-check, neither of which requires anything to land in Master's live context. By the time shutdown-cleanup runs, Master's own identity was already loaded once, earlier in the session, at boot. None of the 4 steps here have that constraint, so unlike boot there is no reason for any of them to run inline.

1. Spawn one subagent (general-purpose, persona `agents/master.md`) with instructions to run STATE CHECK, then execute steps 01 through 04 in order, following each step's own frontmatter/state.yaml update protocol exactly as written.
2. Wait for it (block on the result) — the controller needs the cleanup summary this turn.
3. The subagent's final message must contain the complete summary produced in step-04 ("Shutdown cleanup complete: ..."), verbatim. Master relays that to the controller as its own next message.
4. If step-01's root-check finds a genuinely uncertain non-canonical entry, the subagent should pause and surface it in its response rather than guess; Master relays the question to the controller and, once answered, resumes the same subagent via SendMessage — this preserves `state.yaml`'s `current-step` and `accumulated-context`.

This gives shutdown-cleanup a real `SubagentStart`/`SubagentStop` pair, same as boot. `.claude/hooks/eval-turn-start.py` opens the eval record independently of this (on `UserPromptSubmit`, matched against `agents/master.md`'s real trigger phrases — "exit", "log off", "end session" — not the words "shutdown" or "cleanup", which never actually appear in how this workflow gets invoked); `.claude/hooks/eval-turn-stop.py` closes it once `state.yaml` reaches `status: complete`.

### Steps

| # | File | Executed by |
|---|------|-------------|
| 1 | `step-01-purge-artifacts.md` | spawned subagent |
| 2 | `step-02-organize-deliverables.md` | spawned subagent |
| 3 | `step-03-gitignore-check.md` | spawned subagent |
| 4 | `step-04-commit.md` | spawned subagent |

Begin: `steps/step-01-purge-artifacts.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
