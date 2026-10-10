---
name: one-on-one-prep-verification
description: Adversarial verification of a 1:1 prep brief. Ralph cross-checks the brief's open action items and talking points against the delegation tracker and OmniFocus records before the brief is trusted.
agent: ralph
model: sonnet
---

<!-- system:start -->
# One-on-One Prep Verification Workflow

**Goal:** Confirm that the brief's open threads and action items are real: every open action item traces to the delegation tracker, OmniFocus, or a cited communication, and every talking point is backed by an actual thread. No fabricated action items, no invented delegations, no talking point built on a conversation that does not exist.

**Agent:** Ralph, Verification Agent

**Architecture:** Single-step adversarial pass. Ralph receives the brief manifest (the brief, the workflow's accumulated-context, the delegation tracker, and the OmniFocus pull) and returns a verdict table. The caller acts on the results; Ralph never fixes anything.

**Adversarial lens (one-on-one-prep):** Brief agenda/action claims vs delegation tracker and OmniFocus records. The producing agent (Shep) assembles a brief asserting open action items and talking points; Ralph re-derives each claim from the record: `delegations/tracker.md` and `data/omnifocus-unified.json`. This is the one-on-one-prep lens in `agents/adversarial-isolation.md`.

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
| Brief | The saved `{Person} - {date}.md` | File system read |
| Workflow state | `workflows/one-on-one-prep/state.yaml` accumulated-context | File system read |
| Delegation tracker | `delegations/tracker.md` | File system read |
| OmniFocus data | `data/omnifocus-unified.json` | File system read |

### Verdict table format

| Item | Brief claim | Recorded state | Verdict |
|------|-------------|----------------|---------|
| (one row per claim) | (what the brief asserts) | (what the record shows) | ✅ Verified / ⚠️ Unverified |

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
