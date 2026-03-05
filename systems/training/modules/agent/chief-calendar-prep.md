# Module: Calendar Prep

<!-- system:start -->

## Metadata

| Field | Value |
|-------|-------|
| ID | chief-calendar-prep |
| Category | agent |
| Agent | Chief |
| Tier | Getting Started |
| Duration | 15 minutes |
| Mastery Threshold | 2 |

## What You'll Learn

How to prep for any meeting using Chief — attendee context, objectives, talking points, and relevant background pulled automatically.

## Before We Start

You need at least one upcoming meeting on your calendar. If the calendar is empty, Shep should suggest revisiting this module when a meeting is scheduled.

## Walkthrough

### Step 1: Pick a Meeting (2 min)

Pull today's or tomorrow's calendar. Ask the user to pick the meeting they most want to be prepared for.

**Coaching prompt:** "Not every meeting needs a prep. But for the ones that matter — client calls, 1:1s with your team, board meetings — 5 minutes of prep makes you 10x more effective."

### Step 2: Trigger the Prep (2 min)

Say "prep for my meeting with [name/topic]" or run the `chief-prep` skill.

Chief will pull:
- Who's attending (names, titles, organization if known)
- Recent interactions with attendees (emails, past meetings)
- Any open items related to this person or topic (delegations, tasks)
- Relevant rock or initiative context

### Step 3: Walk Through the Prep Brief (5 min)

Review the output together:

**Attendees:** "Do you know everyone on the invite? Anyone you haven't met before?"

If unknown attendees: "Chief found [name]. Here's their background. Worth knowing going in."

**Context:** "These are recent interactions with the attendees. Anything here that changes how you approach this meeting?"

**Open items:** "You have [N] open items related to this. Which ones need to come up in the meeting?"

**Talking points:** "Chief generated these talking points. Do they match your objectives for this meeting, or do you want to adjust?"

### Step 4: Identify the Objective (3 min)

Ask: "What does success look like when this meeting ends?"

**Coaching prompt:** "Every meeting should have a clear exit condition. It's either a decision, an alignment, a handoff, or a relationship moment. If you can't name which one, the meeting probably shouldn't happen."

Help the user articulate one clear objective. Add it to the prep brief if not already captured.

### Step 5: The One Thing They Won't Ask (3 min)

**Coaching prompt:** "Here's a trick: identify the one question no one else in the meeting will ask but someone should. That's your leverage. Chief can help you find it by looking at what's missing from the prep."

Look at the prep brief for gaps — recent changes in the account, unaddressed risks, competing priorities. Surface one.

## Reflection

Ask: "After seeing this prep, is there anything you would have walked into this meeting not knowing?"

This builds appreciation for what the system catches proactively.

## Success Criteria

Pre-brief 2 meetings with attendee context, objectives, and talking points. By the second time:
- User articulates a clear meeting objective before the meeting
- At least one insight from the prep brief wouldn't have been known without it
<!-- system:end -->
