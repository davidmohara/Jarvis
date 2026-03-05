---
step: 4
name: Progression Introduction
next: null
---

<!-- system:start -->
# Step 4: Progression Introduction

**Goal:** Show the user the training path ahead. Make it feel exciting, not overwhelming. Close the onboarding session.

## Process

### 4.1 Show Progress

Display the progress bar:

```
System training: █░░░░░░░░░░░░░░░ 7% — 2 of 28 capabilities learned
```

"You just completed your first two capabilities — system orientation and {first_task_display_name}. There are 28 total, organized into four tiers."

### 4.2 Explain Tiers (briefly)

"Here's the path:

**Getting Started** — Your daily operations loop. Morning briefings, inbox processing, daily reviews. This is where the immediate time savings live.

**Building Rhythm** — Delegation tracking, 1:1 prep, rock reviews. This is where the system starts managing your team alongside you.

**Strategic Mode** — Pipeline reviews, strategy building, communications. This is where the system becomes a strategic partner.

**Full System** — Everything orchestrated together, including external integrations.

You don't have to follow this order — everything is available now. But this sequence builds naturally."

### 4.3 Set Expectations

"Every few days, when you start your morning, the system will suggest a new capability to try. Something like 'Would you like to learn how to process your inbox to zero?' You can try it, skip it, or ask for something different.

You can also check your progress anytime — just ask 'how's my training' or 'what should I learn next.'"

### 4.4 Recommend Next

Based on their role and time of day:
- Morning user → "Tomorrow morning, try starting your day with the full briefing on your own."
- Afternoon user → "Tomorrow, run your morning briefing first thing. The system will have everything ready."
- Manager → "When you have your next 1:1, the system can prep your agenda automatically. Just say 'prep my 1:1 with {direct_report_name}.'"

### 4.5 Save & Close

Append to `training/state/history.md`:

```markdown
### {Date} — Onboarding Complete
- Modules completed: System Orientation, {First Task Display Name}
- Role: {role}
- Learning style: {style}
- First impression: {their reflection from step 3}
- Recommended next: {next module display name}
```

Close with warmth: "You're set up. The system is ready when you are. Welcome aboard, {name}."

## Workflow Complete
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
