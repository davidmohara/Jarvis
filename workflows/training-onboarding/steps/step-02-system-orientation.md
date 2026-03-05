---
step: 2
name: System Orientation
next: step-03-first-task.md
---

<!-- system:start -->
# Step 2: System Orientation

**Goal:** Give the user a mental model of what the system can do — framed as capabilities, not components.

## Process

### 2.1 Load Orientation Module

Read `training/modules/system/orientation.md` for the guided walkthrough.

### 2.2 Capability Overview

Walk the user through the five capability domains:

1. **Daily operations** — "The system can run your morning briefing, process your inbox, prep your calendar, and close out your day with a review."
2. **People & coaching** — "It tracks delegations, preps your 1:1s, nudges you on follow-ups, and helps build performance reviews."
3. **Strategy & goals** — "It connects your daily work to quarterly rocks, checks alignment, tracks initiatives, and coaches you through strategy."
4. **Revenue & clients** — "It reviews your pipeline, preps client meetings, builds account strategies, and analyzes wins and losses."
5. **Communications** — "It drafts emails, builds presentations, creates talking points, and manages content calendars."

Plus: **System operations** — "There are also tools for capturing ideas, finding things, making decisions, and managing the system itself."

### 2.3 Quick Demo

Show 2-3 examples using their actual data if available:
- "Let me show you what a morning briefing looks like..." (run chief-morning if calendar data exists)
- "Here's what your delegation tracker looks like..." (show current state)
- If no data available: "Once we connect your calendar and email, every briefing pulls real data. For now, let me show you the structure."

### 2.4 Record Orientation

Update `training/state/mastery.json`:
```json
{
  "modules": {
    "orientation": {
      "first_attempt": "{now}",
      "attempts": 1,
      "last_attempt": "{now}",
      "skill_level": "mastered",
      "notes": "Completed during onboarding"
    }
  }
}
```

## Next Step

Proceed to `step-03-first-task.md`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
