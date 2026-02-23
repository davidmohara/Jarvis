---
name: shutdown-cleanup
description: Session exit cleanup — purge temp artifacts, organize deliverables, verify naming, commit clean
agent: master
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
## EXECUTION

Read fully and follow: `steps/step-01-purge-artifacts.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
