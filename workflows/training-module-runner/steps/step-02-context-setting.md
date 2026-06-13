---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

---
step: 2
name: Context Setting
next: step-03-guided-execution.md
---

<!-- system:start -->
# Step 2: Context Setting

**Goal:** Tell the user what they're about to learn, in capability terms. Set expectations.

## Process

### 2.1 Frame the Capability

Use the module's `display_name` and `nudge_phrase` to introduce what they're about to do:

- WRONG: "We're going to run the chief-daily-review module."
- RIGHT: "We're going to walk through closing out your day — capturing what got done, what didn't, and setting up tomorrow."

### 2.2 Time Estimate

"This takes about {duration_minutes} minutes."

### 2.3 Previous Attempt Context

If they've done this before:
- "You've tried this {attempts} time(s). Last time: {notes}. Let's build on that."
- If practicing: "One more solid run and you'll own this."
- If mastered and returning: "Good to revisit. It's been {days} days since you last used this."

If first time:
- "This is your first time with this one. I'll walk you through it step by step."

### 2.4 Role-Specific Notes

If `role_notes` exists for the user's `role_key`, apply it:
- "For someone in your role, I'd emphasize {role_note}."

### 2.5 Confirm Ready

"Ready to jump in?"

## Next Step

Proceed to `step-03-guided-execution.md`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
