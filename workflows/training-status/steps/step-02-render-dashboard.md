---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

---
step: 2
name: Render Dashboard
next: null
---

<!-- system:start -->
# Step 2: Render Dashboard

**Goal:** Display the full training progress report.

## Process

### 2.1 Progress Bar

```
System training: ████████████░░░░ {percent}% — {mastered} of {total} capabilities learned
```

Scale: 16 blocks. Fill proportional to completion_percent.

### 2.2 Domain Breakdown

For each domain, list EVERY module with its status:

```
Daily operations (3 of 6 learned)
  ✓ Morning Briefings — learned Feb 18
  ✓ Inbox Processing — learned Feb 22
  ✓ Daily Reviews — learned Mar 1
  ~ Calendar Preparation — tried once (Mar 4)
  ○ Weekly Planning — not started
  ○ Meeting Preparation — not started
```

Status markers:
- `✓` = mastered (show date of mastery)
- `~` = tried but not mastered (show attempt count and last date)
- `○` = not started

### 2.3 Summary Block

```
Completed: {N} capabilities
In progress: {N} (tried but not yet mastered)
Remaining: {N} not started

Current tier: {tier_name}
Sessions: {total_sessions} | Streak: {streak_days} days

Suggested next: {display_name} — {nudge_phrase}
```

### 2.4 Reinforcement Flags

If any mastered module hasn't been used in 14+ days:

```
Worth revisiting: {display_name} (last used {N} days ago)
```

### 2.5 Next Recommendation

Using the same logic as `/training-next`:
1. Current tier priority
2. Role alignment
3. Recency
4. Connector availability

End with: "Want to try {display_name} now?"

## Workflow Complete
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
