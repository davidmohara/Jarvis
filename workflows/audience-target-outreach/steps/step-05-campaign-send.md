---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 05: Campaign Send (looped per contact, live confirmation required)

## MANDATORY EXECUTION RULES

1. Before executing, write `status: in-progress` and `started-at` to this
   file's frontmatter.
2. Load `accumulated-context.approved_messages`, `accumulated-context.journey_name`,
   `accumulated-context.segment_name`, and `accumulated-context.contacts_sent`
   from `state.yaml`.
3. **Never send to a contact already present in `contacts_sent`.** This is
   the resume-safety mechanism that prevents double-sending after an
   interruption.
4. **Every single contact requires its own explicit live confirmation
   immediately before send — this applies regardless of Plan-Only Mode
   setting for the workflow as a whole**, per `skills/campaign-send/SKILL.md`.
   If the controller invoked the workflow with "do not execute" or
   `eval-mode: plan-only`, this step produces a send plan for all contacts
   and stops (no confirmations are prompted in that mode, since nothing will
   actually fire) — but a live run must confirm every contact individually,
   with no batch shortcut, even if content was already batch-approved in
   step 03.
5. Never send more than one contact per confirmation. Never infer "yes to
   all" from a single "yes."

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** One approved message + its Contact + the episode's Journey, one at a time
**Output:** Send confirmations and results, stored in `accumulated-context`

---

## YOUR TASK

1. For each message in `approved_messages` not already in `contacts_sent`:
   a. Read and execute `skills/campaign-send/SKILL.md` in full for this one
      contact — including its live per-contact confirmation prompt.
   b. On confirmed send: append the contact to
      `accumulated-context.contacts_sent` immediately (before moving to the
      next contact — this write must not be batched at the end, since an
      interruption between sends must not lose track of what already went out).
   c. On "skip": record the skip, do not add to `contacts_sent`, move to the next contact.
   d. On "no" or non-response: halt the loop. Do not process remaining
      contacts without controller direction. Set `state.yaml`
      `current-step: step-05` and `status: in-progress` (not aborted — this
      is a normal pause point, resumable).

2. Once all contacts are processed (sent, skipped, or the controller ends the
   session):
   - Write outputs to this file's frontmatter:
     ```yaml
     outputs:
       contacts_sent_count: <int>
       contacts_skipped_count: <int>
       contacts_remaining: <int>
     ```
   - Update `state.yaml`: `status: complete` (only if all contacts have been
     resolved — sent or skipped; otherwise leave `status: in-progress` for
     resume).
   - Mark this file's frontmatter `status: complete` and `completed-at` only
     when the full loop has been resolved.

3. Present a final summary to the controller: which contacts were sent,
   which were skipped, and — for each sent contact — confirmation that Email
   insights show the expected sent/delivered status.

---

## SUCCESS METRICS

- Zero contacts sent without an individual, explicit live confirmation
- Zero double-sends on resume (verified against `contacts_sent`)
- Every send verified against Email insights before being reported as successful

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Send-readiness check (re-verified at send time) fails | Stop before that send. Report the gap. Do not send anyway even if setup confirmed readiness earlier. |
| Ambiguous/duplicate Contact record | Stop, flag, ask the controller which record is correct before sending to that contact. |
| Send appears to fail or Email insights don't confirm it | Report as unverified for that contact specifically — do not mark it in `contacts_sent` until confirmed, but do not silently retry either; surface to controller. |
| Workflow interrupted mid-loop | On resume, STATE CHECK loads `contacts_sent` and the loop continues only with unresolved contacts. |

## NEXT STEP

This is the final step of `audience-target-outreach`. On completion, note
that `campaign-response-log` runs separately and on-demand as replies arrive
— it is not part of this workflow's execution.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
