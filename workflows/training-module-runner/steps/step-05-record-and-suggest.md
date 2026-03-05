---
step: 5
name: Record & Suggest Next
next: null
---

<!-- system:start -->
# Step 5: Record & Suggest Next

**Goal:** Update all training state files and recommend what to learn next.

## Process

### 5.1 Update Mastery

Write to `systems/training/state/mastery.json`:

If new module:
```json
"{module_id}": {
  "first_attempt": "{now}",
  "attempts": 1,
  "last_attempt": "{now}",
  "skill_level": "tried",
  "notes": "{brief summary from reflection}"
}
```

If existing module:
- Increment `attempts`
- Update `last_attempt` to now
- Update `skill_level`:
  - 1 attempt → "tried"
  - 2+ attempts → "practicing"
  - meets `mastery_threshold` → "mastered"
- Append to `notes`

### 5.2 Update Progress

Write to `systems/training/state/progress.json`:
- Recalculate `completion_percent`: (mastered modules / total modules) × 100
- Update `by_category` counts for the module's category
- Set `last_session` to now
- Increment `total_sessions`
- Update `streak_days`:
  - If `last_session` was yesterday → increment streak
  - If `last_session` was today → no change
  - Otherwise → reset to 1
- Check tier thresholds: if `completion_percent` crosses a tier boundary, update `tier`

### 5.3 Append to History

Append to `systems/training/state/history.md`:

```markdown
### {Date} — {display_name}
- Attempt: #{N}
- Status: {tried/practicing/mastered}
- Notes: {brief summary}
```

### 5.4 Celebrate and Suggest

Based on the result:

**If mastered:**
"You've got {display_name} down. Next up: the system can {next_module_nudge_phrase}. Want to try it now, or save it for another day?"

**If practicing:**
"Good run. One more solid session and you'll own this. Want to go again, or move on to something new?"

**If first try:**
"Nice start. The second time through, you'll notice things you missed. I'd suggest running this again in a day or two."

**If tier changed:**
"That moved you into {new_tier_name}. New capabilities unlocked: {list 2-3 display_names}."

### 5.5 Show Updated Progress Bar

```
System training: ████████████░░░░ 47% — 13 of 28 capabilities learned
```

## Workflow Complete
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
