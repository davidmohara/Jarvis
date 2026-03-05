# Module: Quarterly Rock Review

<!-- system:start -->

## Metadata

| Field | Value |
|-------|-------|
| ID | quinn-rocks |
| Category | agent |
| Agent | Quinn |
| Tier | Building Rhythm |
| Duration | 20 minutes |
| Mastery Threshold | 2 |

## What You'll Learn

How to run a quarterly rock review with Quinn — assess progress on your rocks, identify at-risk items, and propose corrective actions before the quarter ends.

## Before We Start

Quarterly objectives should exist in `context/quarterly-objectives.md`. If not, the first step is creating them.

## Walkthrough

### Step 1: Load Current Rocks (3 min)

Trigger the `quinn-rocks` skill or say "how are my rocks looking?"

Quinn pulls `context/quarterly-objectives.md` and displays:
- Each rock with current status
- Time elapsed vs. time remaining in the quarter
- Any measurable progress indicators

**Coaching prompt:** "Rocks are the 3-5 things that matter most this quarter. If you can't remember yours without looking, that's a sign they're not driving your daily decisions."

### Step 2: RAG Assessment (5 min)

For each rock, assign a status:

**Green** — On track. Progress is proportional to time elapsed.
**Yellow** — At risk. Behind pace, but recoverable with focused action.
**Red** — Off track. Unlikely to complete without a significant course correction.

Walk through each one with the user:

**Coaching prompt:** "Be honest with yourself. A rock that's been 'yellow' for 6 weeks is actually red — you just haven't admitted it yet."

For role-specific coaching:
- **CEO**: "Which of your reds is actually someone else's problem to solve? Are you holding something that should be delegated?"
- **VP**: "Do your reds roll up to a company rock that's also red? That's an escalation conversation."
- **COS**: "Which reds across the leadership team are connected? Sometimes one blocker cascades."

### Step 3: Time Math (3 min)

Quinn calculates:
- Weeks remaining in quarter
- Effort required to move each yellow/red to green
- Whether the timeline is realistic

**Coaching prompt:** "This is where executives lie to themselves. 'I'll catch up in the last 3 weeks' is almost never true. If a rock needs 6 weeks of effort and you have 3 weeks left, the math doesn't work."

### Step 4: Corrective Actions (5 min)

For each yellow or red rock, develop a corrective action:

- **More resources** — Who else can contribute?
- **Reduced scope** — What's the minimum viable version?
- **Removed blockers** — What's actually in the way?
- **Deprioritize** — Is this rock still the right priority? (Yes, you can change rocks mid-quarter.)

**Coaching prompt:** "The best corrective action is often the hardest: admit the rock was too big or the wrong priority. Changing a rock mid-quarter isn't failure — it's intelligence."

### Step 5: Update and Save (4 min)

Update `context/quarterly-objectives.md` with new statuses and corrective actions.

If any action items emerged (delegations, meetings to schedule, scope changes), capture them.

## Reflection

Ask: "Which rock will define your quarter — the one you're most proud of finishing, or the one you're most afraid of missing?"

## Success Criteria

Run 2 rock reviews, identify at-risk items, propose corrective actions for each. By the second time:
- The user completes RAG assessment without coaching prompts
- At least one corrective action is specific and time-bound (not "work harder on it")
<!-- system:end -->
