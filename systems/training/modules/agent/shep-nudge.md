# Module: Follow-Up Nudges

<!-- system:start -->

## Metadata

| Field | Value |
|-------|-------|
| ID | shep-nudge |
| Category | agent |
| Agent | Shep |
| Tier | Building Rhythm |
| Duration | 10 minutes |
| Mastery Threshold | 2 |

## What You'll Learn

How to use Shep's nudge system to follow up on overdue delegations with calibrated tone — from gentle check-in to direct escalation.

## Before We Start

The user needs at least one active delegation, ideally one that's overdue or near due date. If no delegations exist, redirect to the Delegation Tracking module first.

## Walkthrough

### Step 1: Surface Overdue Items (2 min)

Trigger the `shep-nudge` skill or say "what needs follow-up?"

Shep surfaces everything that's overdue or approaching deadline.

**Coaching prompt:** "The system catches what your brain forgets. You delegated this [N] days ago. Without this nudge, when would you have remembered to follow up?"

### Step 2: Calibrate the Tone (3 min)

For each overdue item, Shep drafts a follow-up message with calibrated tone:

**First nudge** (1-3 days overdue): Check-in
- "Hey [name], just checking in on [item]. How's it coming along?"

**Second nudge** (4-7 days overdue): Direct
- "[Name], the [item] was due [date]. What's the current status? Anything blocking you?"

**Third nudge** (8+ days overdue): Escalation flag
- "[Name], this has been outstanding for [N] days. We need to resolve this — can we get 15 minutes today?"

Walk through one draft with the user:

**Coaching prompt:** "Notice the tone shift. The first nudge assumes good intent — they're busy. The second is direct but not hostile. The third creates urgency without blame. Every follow-up should leave the relationship intact."

### Step 3: Personalize and Send (3 min)

Let the user edit the draft. They know the person and the relationship better than the system.

Questions to consider:
- "Is this person someone who responds better to direct messages or email?"
- "Is there context the system doesn't know — are they dealing with something personal?"
- "Should this nudge come from you directly, or should someone else check in?"

### Step 4: Pattern Recognition (2 min)

If the user has multiple overdue items with the same person:

**Coaching prompt:** "Multiple overdue items from the same person is a pattern, not an accident. This is a 1:1 conversation, not another nudge. Do you want to bring this up in your next 1:1?"

If overdue items are spread across multiple people:

**Coaching prompt:** "If everything's overdue, the issue might be you — unclear expectations, unrealistic timelines, or too many active delegations. Worth an honest audit."

## Reflection

Ask: "What's your default follow-up style — too aggressive, too passive, or just right?"

Most executives are either too aggressive (which damages trust) or too passive (which enables slipping). Note their self-assessment.

## Success Criteria

Send 2 calibrated follow-up messages on overdue delegations. The user should choose the appropriate tone and personalize at least one draft.
<!-- system:end -->
