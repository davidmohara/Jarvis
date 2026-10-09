---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 01: Verify Prep-Sheet Claims Against Source Data

## MANDATORY EXECUTION RULES

1. You MUST read the prep sheet, the workflow's accumulated-context, and the source records directly. Do NOT accept the sheet's own assertions as evidence: re-derive each claim from the record.
2. You MUST return a verdict for every lens checklist item (invented attendees, company identity, reason-for-call grounding, title sourcing, no post-call content, verified local time). No item may be omitted.
3. You MUST NOT fix, edit, or re-write the prep sheet. You verify and report; the caller decides.
4. If a source (calendar invite, email thread, CRM record) is missing or unreadable, mark the dependent items ⚠️ Unverified with note "source unreadable." Do not infer correctness from silence.
5. Read-only throughout. You do not modify any file or record.

---

## EXECUTION PROTOCOL

**Agent:** Ralph, Verification Agent
**Input:** Prep-sheet manifest (sheet path, workflow state, source records, run-date) from the caller
**Output:** Verdict table + one summary line, returned to the caller

---

## CONTEXT BOUNDARIES

- Scope is exactly this run's prep sheet and the source data it claims to be grounded in. Nothing else.
- Ralph does not re-research the meeting. He checks the claims that were made.

---

## YOUR TASK

### Sequence

1. **Locate the artifacts.** Read the prep sheet from the manifest, and `workflows/client-meeting-prep/state.yaml` (accumulated-context) for the recorded classification and evidence.

2. **Read the source records** named in the manifest: the calendar invite's attendee list, the introduction/most-recent email thread, and the CRM account record if the sheet claims one.

3. **Run the lens checklist** (one verdict row each):
   - Invented attendees (each named external attendee vs the invite/thread)
   - Company identity (named company vs email-domain/thread evidence)
   - Reason-for-call grounding (stated reason vs a specific thread, or explicit "unverified")
   - Title sourcing (stated title vs first-party evidence)
   - No post-call content (no Next Steps / action-item section)
   - Verified local time (time in sheet vs timezone-verified local time)

4. **Return the verdict table** (Item | Prep-sheet claim | Source evidence | Verdict) and one summary line: "N of M verified, K unverified."

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Prep sheet not found | Mark all items ⚠️ Unverified with note "prep sheet unreadable"; report it plainly |
| Email thread absent from manifest | Mark reason-for-call and title rows ⚠️ Unverified with note "no email source provided" |
| A named attendee has no source | ⚠️ escalate-class finding; report it plainly, do not soften |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
