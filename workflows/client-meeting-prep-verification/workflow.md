---
name: client-meeting-prep-verification
description: Adversarial verification of a client/prospect prep sheet. Ralph traces every attendee and company fact in the sheet back to a calendar, email, or CRM record before the prep is trusted.
agent: ralph
model: sonnet
---

<!-- system:start -->
# Client Meeting Prep Verification Workflow

**Goal:** Confirm that the prep sheet's factual claims match the source records: every attendee named actually exists on the invite or thread, every company fact traces to a real source, and the reason-for-the-call is grounded in email evidence rather than invented. No invented attendees, no fabricated sales narrative, no wrong titles.

**Agent:** Ralph, Verification Agent

**Architecture:** Single-step adversarial pass. Ralph receives the prep-sheet manifest (the sheet, the workflow's accumulated-context, and the source records it cites) and returns a verdict table. The caller acts on the results; Ralph never fixes anything.

**Adversarial lens (client-meeting-prep):** Prep-sheet claims vs source data. The producing agent (Chase) writes a prep sheet asserting attendees, company facts, and a reason for the call; Ralph re-derives each claim from the actual record: the calendar invite (attendee list), the introduction/most-recent email thread, and the CRM account record. This is the client-meeting-prep lens in `agents/adversarial-isolation.md`.

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
| Prep sheet | The saved `{Person} - {Company} - {date}.md` | File system read |
| Workflow state | `workflows/client-meeting-prep/state.yaml` accumulated-context | File system read |
| Calendar invite | The meeting's attendee list, time, organizer | Calendar read (from the manifest) |
| Email thread | The introduction / most-recent thread the sheet cites | Email read (from the manifest) |
| CRM record | Prior account/opportunity history, if the sheet claims it | CRM read (from the manifest) |

### Verdict table format

| Item | Prep-sheet claim | Source evidence | Verdict |
|------|------------------|-----------------|---------|
| (one row per claim) | (what the sheet asserts) | (what the record shows) | ✅ Verified / ⚠️ Unverified |

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
