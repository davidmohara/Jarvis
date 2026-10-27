---
name: plaud-ingest-verification
description: 'Adversarial verification of a Plaud ingest run. Ralph performs ingestion accounting: every staged recording must be accounted for as an ingested note or a logged skip, with zero silent drops.'
agent: ralph
model: sonnet
---

<!-- system:start -->
# Plaud Ingest Verification Workflow

**Goal:** Confirm the ingest run accounted for every recording it touched. Nothing disappears between "discovered" and "done" without an explicit, logged reason.

**Agent:** Ralph, Verification Agent

**Architecture:** Single-step adversarial pass. Ralph receives the ingest manifest (state.yaml accumulated-context, step outputs, staging directory listing) and returns a verdict table. The caller acts on the results; Ralph never fixes anything.

**Adversarial lens (plaud-ingest):** Ingestion accounting. The producing agent (Knox) reports what it believes it processed; Ralph reconciles the full set of discovered recordings against the set that landed as notes or were logged as skipped/personal/deferred, and flags any recording present at discovery but absent from every outcome list. A recording that silently vanishes is the failure this lens exists to catch. This is the plaud-ingest lens in `agents/adversarial-isolation.md`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Ingest manifest | state.yaml accumulated-context + step outputs | Passed from Knox / file system read |
| Ingest state | `workflows/plaud-ingest/state.yaml` | File system read |
| Step outputs | `workflows/plaud-ingest/steps/step-*.md` frontmatter | File system read |
| Staging directory | `~/Downloads/transcript-staging/` | File system listing |
| Eval record | `systems/eval-harness/runs/` plaud-ingest record | File system read |

### Paths

- `ingest_state` = `workflows/plaud-ingest/state.yaml`
- `staging_dir` = `~/Downloads/transcript-staging/`
- `step_files` = `workflows/plaud-ingest/steps/step-*.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## STATE CHECK

Read and follow `reference/state-check-protocol.md` before any execution. Workflow: `plaud-ingest-verification`; agent: `ralph`.

## EXECUTION

Read fully and follow: `steps/step-01-verify.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
