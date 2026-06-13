---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

---
step: 1
name: User Intake
next: step-02-system-orientation.md
---

<!-- system:start -->
# Step 1: User Intake

**Goal:** Learn who the user is, what they do, and how they want to use the system.

## Process

### 1.1 Welcome

Greet the user warmly. Let them know this is a quick setup — about 5 minutes of questions, then they'll run their first real task.

Example: "Welcome to the system. I'm going to ask a few quick questions so everything is tuned to how you work. Then we'll jump straight into something useful."

### 1.2 Interview Questions

Ask these conversationally, not as a form:

1. **Name** — "What should I call you?"
2. **Role** — "What's your title or role?" (Map to role_key: ceo, cos, vp, director, manager)
3. **Team size** — "How many people report to you, directly or indirectly?"
4. **Direct reports** — "Who are your direct reports?" (Names only)
5. **Daily rhythm** — "What time do you typically start your day? And when do you usually wrap up?"
6. **Timezone** — Confirm or ask: "Are you in Central time?"

### 1.3 Learning Preferences

Ask one question: "Do you prefer to learn by doing with guidance, or would you rather explore on your own and ask questions when you get stuck?"

Map to:
- "guidance" / "walkthrough" → `walkthrough_then_free_play`
- "explore" / "own" → `free_play_with_support`

### 1.4 Save Config

Write answers to `training/state/config.json`:
- Set `user`, `role`, `role_key`, `timezone`, `team_size`, `direct_reports`
- Set `daily_rhythm.morning_time` and `daily_rhythm.review_time`
- Set `learning_preferences.style`
- Set `onboarded` to today's date
- Leave `connectors_active` empty (configured separately)

## Next Step

Proceed to `step-02-system-orientation.md`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
