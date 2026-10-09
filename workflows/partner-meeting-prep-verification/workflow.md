---
name: partner-meeting-prep-verification
description: Adversarial verification of a partner meeting prep document. Ralph cross-checks the account-overlap and event claims against the actual CRM, calendar, and email records before the document is shared with the partner.
agent: ralph
model: sonnet
---

<!-- system:start -->
# Partner Meeting Prep Verification Workflow

**Goal:** Confirm that the document's account-overlap and event claims are real: every account in the overlap table exists and is attributed to the right seller, every event is a real event, and no partner-side column was filled in with a guess. This document is shared with the partner team, so an invented account or fabricated overlap is a reputational risk.

**Agent:** Ralph, Verification Agent

**Architecture:** Single-step adversarial pass. Ralph receives the document manifest (the document, the workflow's accumulated-context, the CRM records, and the calendar/email records) and returns a verdict table. The caller acts on the results; Ralph never fixes anything.

**Adversarial lens (partner-meeting-prep):** Account-overlap and event claims vs actual records. The producing agent (Chase) builds an overlap table and an events section asserting specific accounts and events; Ralph re-derives each claim from the CRM account/pipeline records and the calendar/email records. This is the partner-meeting-prep lens in `agents/adversarial-isolation.md`.

## Lens checklist (what Ralph checks that the producer structurally cannot)

1. **Accounts are real:** every account in the overlap table exists in the CRM (or is clearly marked for the partner to fill). An invented account is a finding.
2. **Seller attribution is right:** the Internal Seller column names the actual account owner, not a guess.
3. **Overlap is grounded:** Group 1 (active) and Group 2 (target) classifications match the CRM's actual engagement/pursuit status.
4. **Partner-side columns are honest blanks:** partner-rep columns are left as `TBD - partner to fill`, not filled in with a guess.
5. **Events are real:** every event in the events section traces to a real event (calendar, known industry event), with a specific date/location.
6. **No stale data presented as current:** account statuses are not asserted as current when the CRM shows otherwise.

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|--------------|
| Document | The saved `{Partner} - {date}.md` | File system read |
| Workflow state | `workflows/partner-meeting-prep/state.yaml` accumulated-context | File system read |
| CRM records | Account/pipeline records for the accounts named | CRM read (from the manifest) |
| Calendar/email | The partner meeting invite and correspondence | Calendar/email read (from the manifest) |

### Verdict table format

| Item | Document claim | Recorded evidence | Verdict |
|------|----------------|-------------------|---------|
| (one row per claim) | (what the document asserts) | (what the record shows) | ✅ Verified / ⚠️ Unverified |

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
