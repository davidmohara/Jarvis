# Module: Inbox Processing

<!-- system:start -->

## Metadata

| Field | Value |
|-------|-------|
| ID | chief-inbox |
| Category | agent |
| Agent | Chief |
| Tier | Getting Started |
| Duration | 15 minutes |
| Mastery Threshold | 3 |

## What You'll Learn

How to process your inbox to zero using Chief's triage framework: Do, Delegate, Defer, Delete. Every item gets a decision. Nothing sits.

## Before We Start

Run a morning briefing first (or at least have items in your inbox). If the inbox is empty, Shep should note that and suggest returning when items have accumulated.

## Walkthrough

### Step 1: Trigger Inbox Processing (2 min)

Say "process my inbox" or run `/process-inbox`.

**Coaching prompt:** "Inbox processing isn't the same as reading your email. It's a decision-making session. Every item gets one of four labels: Do it now, Delegate it, Defer it, or Delete it. No item stays unlabeled."

Trigger the `chief-inbox` skill.

### Step 2: The Triage Framework (5 min)

Walk through the first 3-5 items together. For each one, coach the decision:

**Do** — Takes less than 2 minutes? Do it now.
- "This is a quick reply. Just handle it."

**Delegate** — Someone else should own this? Hand it off.
- "Who's the right person for this? Let's create a delegation."
- If they delegate: show how it immediately appears in the delegation tracker.

**Defer** — Needs action but not now? Schedule it.
- "When should this get done? Let's set a due date."
- Show how deferred items appear in future daily briefings.

**Delete** — Not actionable, not useful? Remove it.
- "Not everything deserves your time. If it doesn't connect to a rock or a commitment, let it go."

**Coaching prompt:** "The hardest part of inbox processing is the Delete decision. Executives accumulate commitments because they can't say no. Practice saying 'this isn't my priority right now' — and deleting it."

### Step 3: Batch the Rest (5 min)

Let the user process the remaining items independently. Observe but don't coach every item — only interject if they're clearly stalling on a decision.

**If they stall:** "You've been looking at that one for 30 seconds. What's the hesitation?"

Common stall patterns:
- "I need more info" → That's a Defer with a next action: "Get info from [person]"
- "I should do this but…" → That's a priority conflict. Acknowledge it and Defer.
- "This is important but not urgent" → Defer to a specific date. Don't let it float.

### Step 4: Inbox Zero Check (3 min)

After processing, confirm:

```
Inbox: 0 items
  - Done: X
  - Delegated: X
  - Deferred: X
  - Deleted: X
```

**Coaching prompt:** "Inbox zero isn't a flex — it's a state of knowing. You know what you've committed to, what you've handed off, and what you've let go. There's nothing lurking."

If they didn't reach zero, that's fine: "We got through [N] items. The rest will be here tomorrow. The skill is getting faster at decisions, not getting to zero every time."

## Reflection

Ask: "Which of the four categories was hardest for you? Do, Delegate, Defer, or Delete?"

Most executives struggle with Delete (they over-commit) or Delegate (they don't trust). Note which one — it informs coaching for later modules.

## Success Criteria

Process inbox to zero 3 times using the triage framework. By the third time:
- Each item gets a decision in under 30 seconds
- At least one item is delegated (not just done/deferred)
- At least one item is deleted
<!-- system:end -->
