# Module: Boot Reminders

<!-- system:start -->

## Metadata

| Field | Value |
|-------|-------|
| ID | add-reminder |
| Category | system |
| Agent | Any |
| Tier | Building Rhythm |
| Duration | 10 minutes |
| Mastery Threshold | 2 |

## What You'll Learn

How the boot reminders system works — what it is, why it exists, and how any agent in the system can use it to surface a time-gated question to David at morning boot, route the confirmed action to the right agent, and self-clean on acknowledgment.

## Before We Start

You should be familiar with the morning boot sequence (chief-morning module) before this one. Boot reminders plug into step-02 of that sequence.

## Walkthrough

### Step 1: Understand the Problem It Solves (2 min)

Some actions can't happen immediately — they require David's confirmation first, or they need to happen in N days when a condition is likely to be true. Examples:

- "Did you start your new peptide stack?" (needs to be true before Galen logs it)
- "Did Scott deliver the org chart?" (delegation follow-up)
- "Did Nexben respond to the proposal?" (sales follow-up)

Without a reminder system, these get tracked in OmniFocus or forgotten. OmniFocus tasks are for things David does. Boot reminders are for things the system needs to ask before it acts.

**Coaching prompt:** "Think of boot reminders as the system's way of asking for a go-ahead before it executes something on your behalf. You say yes, it runs. You say no, it snoozes and asks again."

### Step 2: See How a Reminder Is Structured (3 min)

Every boot reminder lives in `data/reminders.json`. Each entry has three essential parts:

1. **trigger_prompt** — the question shown to David at boot (one sentence, plain English)
2. **routing.agent + routing.action_prompt** — who handles the yes response, and exactly what they're told to do
3. **on_no** — how many days to snooze before asking again, and what message to show

The reminder removes itself (`auto_remove_on: acknowledged`) after David says yes and the action executes successfully.

A sample entry:
```json
{
  "id": "rem-20260614T125115-LJJC1M",
  "trigger_date": "2026-06-21",
  "trigger_prompt": "Did you start the stack (MOTS-C, Tesamorelin, Ipamorelin)?",
  "routing": {
    "agent": "galen",
    "action_prompt": "David confirmed he started his peptide stack..."
  },
  "on_no": { "snooze_days": 2, "message": "Got it. I'll check again in 2 days." },
  "auto_remove_on": "acknowledged"
}
```

**Coaching prompt:** "The action_prompt must be fully self-contained — the agent receiving it has no memory of the conversation where the reminder was created. Write it like a cold briefing."

### Step 3: See How Any Agent Adds a Reminder (3 min)

Any agent uses the `add-reminder` skill. The skill handles the mechanics: generating a unique `rem-` ID, validating the entry, appending to `data/reminders.json`, and writing the eval signal file.

To trigger it, an agent just says: "I need to add a boot reminder" and invokes `skills/add-reminder/SKILL.md`.

The key rule: **the action_prompt must be fully self-contained.** The agent receiving it will have zero context from the original conversation.

Bad: `"Log the stack start in Galen's files."`

Good: `"David confirmed he started his peptide stack on [date]. Read skills/galen-protocols/SKILL.md and data/health/metrics-log.json. Append a protocol_change entry with status ACTIVE for MOTS-C, Tesamorelin, and Ipamorelin. Update galen-protocols/SKILL.md to reflect ACTIVE status for all three..."`

### Step 4: See How Boot Surfaces and Handles It (2 min)

At boot, step-02 (Task J) reads `data/reminders.json` and filters for entries where `trigger_date <= today`. Due reminders are loaded into accumulated-context — not executed yet.

Step-04 (morning briefing synthesis) then surfaces each due reminder one at a time in the Reminders block, after the calendar table.

- **Yes** → spawns the `routing.agent` with `routing.action_prompt` → on success, removes the entry from `data/reminders.json`
- **No** → advances `trigger_date` by `snooze_days`, writes the updated file, shows the on_no message
- **Action fails** → keeps the entry, notes "will retry at next boot"

## Reflection

- When would you use a boot reminder vs. an OmniFocus task?
- What makes a good `action_prompt`? What makes a bad one?
- If you wanted Galen to log a supplement start in 5 days, what would the full reminder entry look like?

## Success Criteria

- You can explain the difference between a boot reminder and an OmniFocus task
- You understand the three-part structure: trigger_prompt, routing, on_no
- You know how any agent invokes `add-reminder` and what makes an action_prompt valid
- You can describe the full boot lifecycle: Task J gather → step-04 surface → yes/no branch → self-remove

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
