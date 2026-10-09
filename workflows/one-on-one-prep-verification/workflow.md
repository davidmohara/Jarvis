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

## Lens checklist (what Ralph checks that the producer structurally cannot)

1. **Open action items are real:** every row in the brief's Open Action Items table traces to the delegation tracker, an OmniFocus task, or a cited email/Teams thread. An item with no source is a finding.
2. **No fabricated delegations:** any delegation named in the brief exists in `delegations/tracker.md` (or OmniFocus) with the stated direction and status.
3. **Talking points are grounded:** each talking point references a real thread, task, or delegation from steps 02-03, not an invented one.
4. **Statuses are honest:** a delegation marked "resolved"/"complete" in the brief matches the tracker; an overdue item is not shown as on-track.
5. **Previous-brief continuity:** if a prior brief exists, its open items are accounted for (resolved, carried forward, or flagged stale), nothing disappears silently.
6. **Calendar hygiene:** excluded recurring meetings (all-hands, standups, townhalls) do not appear in the brief's calendar section.

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
