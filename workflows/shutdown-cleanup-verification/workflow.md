---
name: shutdown-cleanup-verification
description: Adversarial verification of a session cleanup. Ralph cross-checks the cleanup claims against the actual commit, the git audit trail, and the purge outputs before the session is declared closed.
agent: ralph
model: sonnet
---

<!-- system:start -->
# Shutdown Cleanup Verification Workflow

**Goal:** Confirm that the cleanup's claims match what actually happened: nothing temp got committed, no deliverable or media file was deleted rather than preserved, the commit ran through the authorized wrapper (audit trail proves it), and the summary given to the controller is true.

**Agent:** Ralph, Verification Agent

**Architecture:** Single-step adversarial pass. Ralph receives the cleanup manifest (step outputs, state, audit log, commit sha) and returns a verdict table. The caller acts on the results; Ralph never fixes anything.

**Adversarial lens (shutdown-cleanup):** Cleanup claims vs commit and audit trail. The producing agent (Rigby) summarizes what it believes it cleaned and committed; Ralph re-derives each claim from recorded evidence: the commit itself (`git show --stat <sha>`, read-only), the wrapper's audit trail (`systems/eval-harness/git-ops.jsonl`), the step frontmatter outputs, and the purge patterns. This is the shutdown-cleanup lens in `agents/adversarial-isolation.md`.

## Lens checklist (what Ralph checks that the producer structurally cannot)

1. **Nothing temp committed:** the commit's file list contains no purge-pattern files (`.DS_Store`, `.fuse_hidden*`, `__pycache__`, `*.tmp`, root one-off scripts, `meetings/**/*.html`).
2. **Nothing precious deleted:** no image, media, PDF, or deliverable file removed by the purge step or absent from the commit when it should have been staged (standing rule: never remove screenshots/media from project folders).
3. **Commit ran through the wrapper:** the commit sha's operation has a matching entry in `systems/eval-harness/git-ops.jsonl` (`verb: commit`, executed, not refused). A commit with no audit entry bypassed the authorized path.
4. **Counts are true:** purged/organized/committed counts in the controller summary match the step outputs and the commit stat.
5. **"Workspace clean" claims are real:** a nothing-to-commit claim is checked against the lock-free change lists, not taken on faith.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|--------------|
| Cleanup manifest | Step output paths + commit sha + run-date | Passed from Rigby as accumulated-context |
| Step outputs | `workflows/shutdown-cleanup/steps/step-0{1..5}-*.md` frontmatter `outputs` | File system read |
| Workflow state | `workflows/shutdown-cleanup/state.yaml` | File system read |
| Git audit trail | `systems/eval-harness/git-ops.jsonl` | File system read |
| The commit itself | `git show --stat <sha>` (read-only; `git status` forbidden) | Lock-free git read |
| Controller summary | The summary text produced by step-04 | Passed in the manifest |

### Verdict table format

| Item | Cleanup claim | Recorded evidence | Verdict |
|------|---------------|-------------------|---------|
| (one row per claim) | (what the summary asserts) | (what the record shows) | ✅ Verified / ⚠️ Unverified |

### Output

- Verdict table + one-line summary
- Mark ⚠️ on any claim the record does not support
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Single step: `steps/step-01-verify.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
