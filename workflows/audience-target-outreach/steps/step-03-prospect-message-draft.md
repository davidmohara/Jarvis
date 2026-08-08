---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 03: Prospect Message Draft (looped per contact)

## MANDATORY EXECUTION RULES

1. Before executing, write `status: in-progress` and `started-at` to this
   file's frontmatter.
2. Load `accumulated-context.target_contacts`,
   `accumulated-context.pain_points` (if available from an
   `episode-campaign-brief` handoff), and `accumulated-context.offering_matches`
   (same source) from `state.yaml`.
3. This step loops once per contact in `target_contacts`. Each contact's
   content requires its own explicit approval before moving to the next.
   Content approval here is NOT send approval — say so to the controller
   for every contact, every time.
4. Track approved messages incrementally in `accumulated-context` as each
   contact is completed, so an interrupted run resumes without re-drafting
   already-approved content.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** One contact at a time from `accumulated-context.target_contacts`,
plus the relevant pain point/offering pairing for that contact
**Output:** Approved message content per contact, stored in `accumulated-context`

---

## YOUR TASK

1. Initialize (or resume) `accumulated-context.approved_messages` as a list.
   On resume, skip any contact already present in this list.

2. For each remaining contact in `target_contacts`:
   a. Identify the relevant pain point + offering pairing for this contact
      (based on their role and the audience profile's rationale for
      targeting them).
   b. Read and execute `skills/prospect-message-draft/SKILL.md` in full for
      this one contact.
   c. Present the draft per that skill's Draft/Notes/Alternative-closings
      format and get explicit content approval from the controller before
      moving to the next contact.
   d. Append the approved message object to
      `accumulated-context.approved_messages`.

3. Once every contact has an approved message (or the controller chooses to
   skip a contact — record skips as `content_approved: false, skipped: true`
   rather than silently dropping them):
   - Write outputs to this file's frontmatter:
     ```yaml
     outputs:
       messages_approved: <int>
       messages_skipped: <int>
     ```
   - Update `state.yaml`: `current-step: step-04`
   - Mark this file's frontmatter `status: complete` and `completed-at`.

---

## SUCCESS METRICS

- Every approved message references a real pain point and, where a genuine
  match exists, a real offering — never a generic template
- Controller explicitly approved each contact's content individually
- Skipped contacts are recorded, not silently dropped

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Controller rejects a draft | Iterate per `workflows/email-drafting/steps/step-03-iterate.md`'s pattern until approved or skipped — do not force progression with unapproved content. |
| No offering match exists for a contact's pain point | Draft without forcing an offering pitch, per `prospect-message-draft`'s failure-mode guidance. |
| Workflow interrupted mid-loop | On resume, `accumulated-context.approved_messages` shows exactly which contacts are done — do not restart the loop from the beginning. |

## NEXT STEP

Read fully and follow: `step-04-campaign-setup.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
