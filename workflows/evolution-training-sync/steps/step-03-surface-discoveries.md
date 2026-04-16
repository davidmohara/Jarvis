---
step: 3
name: surface-discoveries
workflow: evolution-training-sync
model: sonnet
---

<!-- system:start -->
# Step 3 — Surface Discoveries

## Purpose

Generate "New capability available" discovery prompts for newly integrated components. Surface them at boot using capability framing (display names, not agent names or module IDs).

---

## Actions

### 3A. Skip if no new components

If `new_agents` and `new_tasks` are both empty (no additions, only deprecations), skip to 3D.

---

### 3B. Generate discovery prompts

For each new agent in `new_agents`:

Format using capability framing (NEVER use agent names in user-facing text):
```
New capability available: {display_name}
The system can now {description of what this agent enables}.
Want to try it?
```

For each new task in `new_tasks`:

Format using the module's `display_name` and `nudge_phrase`:
```
New capability available: {display_name}
The system can now {nudge_phrase}. (~{duration} min)
```

---

### 3C. Surface at boot

If invocation trigger is `boot`, display a discovery summary:

```
{N} new capabilities are available from a recent system update.
```

Show up to 3 new items using their `display_name` fields:
> "New: {display_name} — the system can now {nudge_phrase}"

If there are more than 3 new items:
> "Say 'what's new' to see all {N} new capabilities."

After displaying, the top new capability becomes the preferred nudge for the next boot cycle.

---

### 3D. Handle deprecated tasks

Do NOT mention deprecations to the executive during boot — these are system-level changes. Deprecated modules simply stop appearing in nudges and recommendations and no longer count toward completeness.

If the executive had previously mastered a deprecated module:
- Their mastery record is preserved in `training/state/mastery.json`
- The module no longer counts toward the denominator going forward
- History entries in `training/state/history.md` are preserved

---

## Failure Mode

If discovery prompts cannot be generated:
- Still display what we can from in-memory data
- Continue without blocking

---

## NEXT STEP

End of workflow. Return to the calling context (boot sequence).

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
