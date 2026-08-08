---
name: campaign-send
owning_agent: harper
model: sonnet
trigger_keywords: [send the campaign email, send to this contact, trigger the journey send]
trigger_agents: [harper]
description: >
  Ninth skill in the Podcast-to-Pipeline pipeline. Creates/updates the Email
  asset in Customer Insights – Journeys for one contact's journey step and
  triggers the send via Chrome automation. The one skill in this system with a
  real, irreversible side effect — requires explicit per-contact human
  confirmation immediately before send, regardless of Plan-Only setting, and
  re-verifies send-readiness at run time. Called by
  workflows/audience-target-outreach/workflow.md step 05, looped once per
  contact, never batched.
---

<!-- system:start -->
# Campaign Send

## Purpose

Fire the actual send, for exactly one contact, via Customer Insights –
Journeys. This is the highest-risk skill in the whole Podcast-to-Pipeline
system: it is CRM write automation over Chrome/Playwright against the live
Dynamics UI (no API/MCP connector exists), and a stale page state or wrong
selector could write to, or send from, the wrong record. Treat every
invocation accordingly.

## Input

- One approved message (subject + body) from `prospect-message-draft`
  (`content_approved: true`)
- The Contact record for that message
- The Journey created by `campaign-setup`

## Critical Rule — Content Approval Is Not Send Approval

`prospect-message-draft`'s content approval and this skill's send
confirmation are two separate gates. Never treat a `content_approved: true`
flag from step 8 as sufficient to send. This skill must independently obtain
an explicit, per-contact confirmation immediately before triggering the send
— **every single time, with no batch/bulk confirmation shortcut, and
regardless of whether Plan-Only Mode is set** (see below — Plan-Only Mode
governs whether the CRM write tools run at all; the live per-contact
confirmation requirement is a separate, additional control that still
applies even when a controller has pre-approved a whole batch's content).

## Process

1. **Re-verify send-readiness at run time**, even if `campaign-setup` already
   checked this for the episode: confirm the sending domain/email channel is
   still configured and verified in Customer Insights – Journeys. Config can
   drift between setup and send, especially across a multi-day outreach run.

2. **Confirm the target contact and Journey.** Re-read the Contact record and
   Journey identifiers passed in — do not proceed from a cached assumption
   about which record is which if any ambiguity exists (e.g. duplicate
   contact records, per the CBRE unmerged-account lesson).

3. **Create/update the Email asset** for this contact's journey step in
   Customer Insights – Journeys, using the approved subject and body from
   `prospect-message-draft` verbatim — do not silently edit content at send
   time.

4. **Obtain explicit per-contact live confirmation immediately before
   triggering the send.** Present to the controller:
   ```
   About to send to: {Contact Name}, {Title}, {Account}
   Journey: {Journey Name}
   Subject: {Subject}
   ---
   {Full body}
   ---
   Confirm send to this contact? (yes / no / skip)
   ```
   Do not proceed without an explicit "yes" for this specific contact. "Skip"
   moves to the next contact without sending; "no" halts the loop for
   controller review.

5. **Trigger the send** via Chrome/Playwright automation against the live
   Dynamics UI, for this one contact only.

6. **Verify the send registered** — check that the contact's Email insights
   show sent/delivered status tied to the correct Journey before moving to
   the next contact. If verification fails or is ambiguous, flag it rather
   than assuming success.

## Plan-Only Mode

If the prompt contains the phrase "do not execute" or `eval-mode: plan-only`,
do not run any live CRM write or send-trigger action via Chrome/Playwright.
Instead, produce a markdown plan describing, in order, each contact's
intended send: the Email asset content, the Journey it attaches to, and the
exact UI actions you would take to trigger it. Save the plan to the requested
output path and stop. Do not call any browser-automation write action under
any circumstances in plan-only mode.

**Plan-Only Mode does not replace the per-contact live confirmation
requirement above when NOT in plan-only mode.** These are independent
controls: Plan-Only Mode governs whether real sends can happen at all in this
invocation; the live confirmation governs whether, in a real-send
invocation, any individual contact is actually sent to without a human
saying yes to that specific person. A live (non-plan-only) run must never
fire a send based solely on earlier content approval or a batch-level
"go ahead."

## Failure Modes

| Failure | Action |
|---------|--------|
| Sending domain/email channel not configured or no longer verified at send time | Stop before any send. Report the gap. Do not send anyway. |
| Contact record is ambiguous/duplicated (per CBRE unmerged-account pattern) | Stop, flag the duplicate, ask the controller which record is correct before sending. |
| Controller says "no" or doesn't respond to a confirmation prompt | Do not send. Halt the loop and surface remaining unconfirmed contacts. |
| Send appears to fail (UI error, timeout) | Do not retry silently — report the failure for that specific contact and move to the next only with controller direction. |
| Email insights don't show the expected sent status after send | Flag as unverified — do not report success without confirmation. |

## SKILL COMPLETE

After the send loop for this invocation ends (whether all contacts were sent,
skipped, or the run was halted), write the skill-run signal file so the eval
harness captures this execution:

```
systems/eval-harness/skill-runs/campaign-send-latest.json
```

Content:
```json
{
  "skill": "campaign-send",
  "agent": "harper",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

**Eval-harness exception:** if this invocation is an eval-harness executor run (simulating this skill for grading, benchmarking, or testing rather than a genuine Harper-invoked production run), do NOT write this signal file. Writing it from a simulation would falsely register a live skill run in the production eval-harness tracking system. Only write it when this is an actual production invocation.

Set `trigger` to `"boot"` if called from a boot workflow, `"scheduled"` if
called from a scheduled task, `"manual"` otherwise. Set `status` to
`"partial"` if some contacts were sent and others skipped/halted (expected in
normal use — the loop is designed to allow partial progress), `"failure"` if
a send-readiness check failed or the run could not proceed at all. Use the
actual start time for `started`. This write is always the final action.
<!-- system:end -->
