# Module: Delegation Tracking

<!-- system:start -->

## Metadata

| Field | Value |
|-------|-------|
| ID | shep-delegation |
| Category | agent |
| Agent | Shep |
| Tier | Building Rhythm |
| Duration | 15 minutes |
| Mastery Threshold | 3 |

## What You'll Learn

How to create, track, and close delegations through Shep. The delegation system is the accountability backbone of IES — it ensures that when you hand something off, it doesn't disappear.

## Before We Start

The user should have completed the morning briefing module and have at least one task they could delegate. If they can't think of one, coach them: "What's on your plate right now that someone on your team could do 80% as well as you?"

## Walkthrough

### Step 1: The Delegation Mindset (3 min)

Before touching the system, set the frame:

**Coaching prompt:** "Delegation isn't about offloading work — it's about multiplying your impact. Every task you do that someone else could do is time stolen from the work only you can do."

Ask: "What percentage of your current work could only be done by you?" Most executives say 50-60%. The real answer is usually 20-30%.

### Step 2: Create a Delegation (4 min)

Say "delegate [task] to [person]" or run `/delegate`.

Walk through the fields:
- **What**: Clear, specific deliverable (not "work on the project" but "deliver first draft of the proposal by Friday")
- **To whom**: The person who owns it
- **Due date**: When it's expected
- **Context**: Why it matters, what good looks like

**Coaching prompt:** "The most common delegation failure is vague instructions. 'Handle the client situation' is not a delegation. 'Send a follow-up email to [client] confirming the March 15 timeline and cc me' is a delegation."

Show the delegation appearing in `delegations/tracker.md`.

### Step 3: View Active Delegations (3 min)

Say "what's delegated" or trigger the `shep-delegations` skill.

Walk through the tracker:
- Active items with owners and due dates
- Any overdue items (if they exist)
- Status indicators

**Coaching prompt:** "This is your accountability dashboard. Glance at it every morning during your briefing. Chief already surfaces overdue items, but this is the full picture."

### Step 4: Follow Up on One (3 min)

If any delegation is overdue or approaching due date, draft a follow-up:

Say "nudge [person] about [delegation]" or trigger the `shep-nudge` skill.

Show how Shep calibrates the tone:
- First nudge: gentle check-in
- Second nudge: direct inquiry
- Third nudge: escalation flag

**Coaching prompt:** "Following up isn't micromanaging. It's the most respectful thing you can do — it says 'I trust you with this AND I care enough to check.' Silence says 'I forgot I asked you.'"

### Step 5: Close a Delegation (2 min)

If anything is done, close it:

Show the delegation moving from active to completed. Note how it stays in the history for reference in 1:1s and performance reviews.

**Coaching prompt:** "Always close the loop. Don't just mentally check it off — close it in the system. The next time you prep for a 1:1 with this person, you'll see their completion record."

## Reflection

Ask: "Think about your team right now. Who have you been under-delegating to? Who might be ready for more?"

Note the answer — it feeds into Shep's 1:1 prep coaching.

## Success Criteria

Create 3 delegations, track through completion, use the nudge system for at least one overdue item.
<!-- system:end -->
