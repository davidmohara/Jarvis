---
name: podcast-prep-verification
description: Adversarial verification of a podcast episode prep run. Ralph confirms both deliverables (the detailed reference sheet and the single-page studio PDF) exist, are substantive, and actually reflect the episode inputs.
agent: ralph
model: sonnet
---

<!-- system:start -->
# Podcast Prep Verification Workflow

**Goal:** Confirm that the episode prep deliverables are complete and grounded: the detailed reference sheet and the rendered studio PDF both exist and are substantive, the guest and episode identity match the inputs, and the questions reflect the real sources (Janine's SharePoint doc and/or the episode-prep-generator output) rather than being invented when a source existed.

**Agent:** Ralph, Verification Agent

**Architecture:** Single-step adversarial pass. Ralph receives the deliverable manifest (the two documents plus the rendered PDF, the workflow's accumulated-context, and the episode inputs) and returns a verdict table. The caller acts on the results; Ralph never fixes anything.

**Adversarial lens (podcast-prep):** Prep-sheet completeness vs episode inputs. The producing agent (Harper) asserts that both deliverables were built and that the questions came from the episode sources; Ralph re-derives each claim from the actual files and the recorded `sources_used`. This is the podcast-prep lens in `agents/adversarial-isolation.md`.

## Lens checklist

Ralph's lens checklist (what he checks that the producer structurally cannot) is owned by `steps/step-01-verify.md`. Do not duplicate it here.

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|--------------|
| Detailed sheet | `meetings/podcast-prep/YYYY-MM-DD-guest-name.md` | File system read |
| PDF markdown | `meetings/podcast-prep/Episode {N}.md` | File system read |
| Rendered PDF | `meetings/podcast-prep/Episode {N}.pdf` | File system read |
| Workflow state | `workflows/podcast-prep/state.yaml` accumulated-context + sources_used | File system read |
| Episode inputs | The episode-prep / SharePoint source content named in sources_used | From the manifest |

### Verdict table format

| Item | Deliverable claim | Recorded evidence | Verdict |
|------|-------------------|-------------------|---------|
| (one row per claim) | (what the run asserts) | (what the files show) | ✅ Verified / ⚠️ Unverified |

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
