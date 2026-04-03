---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

---
step: 3
name: First Real Task
next: step-04-progression-intro.md
---

<!-- system:start -->
# Step 3: First Real Task

**Goal:** Have the user run one real capability with their actual data. This isn't a demo — it's the first training module.

## Process

### 3.1 Choose the First Task

Default to **Morning Briefing** (chief-morning) — it's the most universal and immediately useful.

Exceptions:
- If it's afternoon/evening: "Normally we'd start with your morning briefing, but since it's {time}, let's close out your day with a daily review instead." → Use chief-daily-review.
- If no calendar connected: Use operations-core instead (capture, find, status commands).

### 3.2 Load the Module

Read the guided walkthrough for the selected module from `training/modules/`.

### 3.3 Coach Through It

Run the actual task — not a simulation. Use the user's real calendar, real tasks, real delegations.

Coaching voice:
- "See how it pulled your 3pm meeting with {name}? That context comes from your calendar automatically."
- "This is what you'd see every morning. Takes about 2 minutes to scan."
- "What jumps out at you? What would you act on first?"

### 3.4 Reflection

Ask one question: "What's the most useful thing you just saw?"

Note their answer — it tells you what matters to them and informs future module recommendations.

### 3.5 Record First Task

Update `training/state/mastery.json` with the module they ran:
```json
{
  "{module_id}": {
    "first_attempt": "{now}",
    "attempts": 1,
    "last_attempt": "{now}",
    "skill_level": "tried",
    "notes": "First run during onboarding. User noted: {their reflection}"
  }
}
```

Update `training/state/progress.json`:
- Set `total_sessions` to 1
- Set `last_session` to now
- Set `streak_days` to 1
- Recalculate `completion_percent`

## Next Step

Proceed to `step-04-progression-intro.md`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
