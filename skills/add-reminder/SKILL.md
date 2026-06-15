---
name: add-reminder
owning_agent: master
model: haiku
trigger_keywords: [remind, reminder, boot reminder, follow up on boot, add reminder, set reminder, check at boot]
trigger_agents: [master, chief, galen, chase, quinn, shep, harper, rigby, knox, sterling]
description: "Write a boot-time reminder to data/reminders.json. Any agent calls this when it needs to surface a question to David at a future boot. The reminder contains a trigger prompt and a fully self-contained action prompt routed to a specific agent on yes."
---

<!-- system:start -->
## Purpose

`add-reminder` is a system-wide utility skill. Any agent uses it when they need to:
- Surface a question to David at a future morning boot
- Gate a follow-up action on David's confirmation
- Route the confirmed action to the correct agent with a pre-built prompt
- Self-remove the reminder once acknowledged

This skill writes to `data/reminders.json`. Boot reads this file at step-02 (Task J) and surfaces due reminders. The reminder removes itself after David says yes and the action executes successfully.

---

## When to Use This Skill

Use `add-reminder` when:
- An action is pending David's confirmation before it can be executed (e.g., "did you start X?")
- A follow-up needs to happen in N days but there's no calendar event to anchor it
- An agent completes setup work and needs to know when David has done his part
- A protocol, cycle, or commitment has a future checkpoint that should not be forgotten

Do NOT use `add-reminder` for:
- Things that should be OmniFocus tasks (use `omnifocus-tasks` skill instead)
- One-time scheduled automations (use scheduled tasks instead)
- Internal agent state tracking (use `data/health/metrics-log.json` or other domain stores)

---

## Skill Execution

### Step 1: Generate a Unique ID

Run:
```bash
python3 /Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES/systems/error-tracking/new-entry.py --id-only
```

Replace the `err-` prefix with `rem-` in the output. Example: `err-20260614T125115-LJJC1M` → `rem-20260614T125115-LJJC1M`.

### Step 2: Build the Reminder Entry

Construct a JSON object following this schema exactly:

```json
{
  "id": "rem-YYYYMMDDTHHMMSS-XXXXXX",
  "created": "ISO 8601 local timestamp",
  "created_by": "agent name (e.g. galen, chase, chief)",
  "trigger_date": "YYYY-MM-DD — first date boot should surface this",
  "trigger_prompt": "Short plain-English question shown to David at boot. Max 1 sentence. E.g.: 'Did you start the peptide stack?'",
  "routing": {
    "agent": "agent name that handles the yes response",
    "action_prompt": "FULLY SELF-CONTAINED prompt passed to routing.agent when David says yes. Must include: what to do, which files to read/write, exact field values, and what to report back. The agent receiving this has no memory of this conversation — write it as if briefing a new agent cold."
  },
  "on_yes": "execute_action_prompt",
  "on_no": {
    "action": "snooze",
    "snooze_days": 2,
    "message": "Short message to show David when he says no. E.g.: 'Got it. I'll check again in 2 days.'"
  },
  "auto_remove_on": "acknowledged",
  "notes": "Optional context for future debugging. What was happening when this reminder was created."
}
```

### Step 3: Append to `data/reminders.json`

Read the current file, append the new entry to the `reminders` array, write it back.

File path: `/Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES/data/reminders.json`

**Append-only.** Never modify or delete existing entries — that is Boot's job on acknowledgment.

### Step 4: Confirm to the Calling Agent

Return:
```
Reminder set. ID: rem-XXXXXX. Will surface at boot on [trigger_date].
Trigger prompt: "[trigger_prompt]"
```

---

## Schema Reference

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `rem-` + timestamp + random suffix. Generated via new-entry.py |
| `created` | ISO 8601 | Local timestamp at creation |
| `created_by` | string | Agent name that created this reminder |
| `trigger_date` | YYYY-MM-DD | First date boot surfaces this reminder. Boot checks `trigger_date <= today`. |
| `trigger_prompt` | string | The question shown to David. One sentence. Plain English. |
| `routing.agent` | string | Agent that handles the yes response |
| `routing.action_prompt` | string | Fully self-contained execution prompt. No assumed context. |
| `on_yes` | string | Always `"execute_action_prompt"` |
| `on_no.action` | string | Always `"snooze"` |
| `on_no.snooze_days` | integer | Days to advance trigger_date when David says no |
| `on_no.message` | string | What to say to David when he says no |
| `auto_remove_on` | string | Always `"acknowledged"` |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `notes` | string | Context for debugging. Not shown to David. |
| `expires` | YYYY-MM-DD | If set, Boot auto-removes this reminder after this date even if never acknowledged |
| `max_snoozes` | integer | If set, Boot removes after this many snoozes regardless of acknowledgment |

---

## Writing a Good `action_prompt`

The `action_prompt` is handed cold to another agent. Write it like you're briefing someone who just walked into the room with zero context. Include:

1. **What David confirmed** — what the yes answer means
2. **What files to read** — full paths
3. **What to write** — exact field names, values, and file paths
4. **What to report back** — summary of what was done

Bad: `"Log the stack start in Galen's files."`
Good: `"David confirmed he started his peptide stack. Append a protocol_change entry to /path/metrics-log.json with the following values for each peptide: [full field list]... Then update /path/galen-protocols/SKILL.md to change status from PENDING START to ACTIVE..."`

---

## Boot Integration

Boot reads `data/reminders.json` at step-02 (Task J). Reminder handling at boot:

1. Filter `reminders` where `trigger_date <= today`
2. Surface each in the briefing reminders block (after calendar table)
3. When David responds:
   - **Yes** → spawn `routing.agent` with `routing.action_prompt` → on success, remove entry from `reminders` array → write file
   - **No** → advance `trigger_date` by `snooze_days` → update `on_no.message` shown → write file
4. If `expires` is set and today > `expires` → remove silently, log to working memory

---

## Example Usage by Any Agent

```
// Galen sets a reminder after documenting a pending peptide stack
add-reminder:
  trigger_date: "2026-06-21"
  trigger_prompt: "Did you start the stack (MOTS-C, Tesamorelin, Ipamorelin)?"
  routing.agent: galen
  routing.action_prompt: "[full self-contained prompt]"
  on_no.snooze_days: 2
  created_by: galen

// Chase sets a reminder to follow up on a proposal
add-reminder:
  trigger_date: "2026-06-18"
  trigger_prompt: "Did Nexben respond to the proposal?"
  routing.agent: chase
  routing.action_prompt: "David confirmed Nexben responded. Pull the response from email via M365 MCP and update the opportunity in the pipeline tracker..."
  on_no.snooze_days: 1
  created_by: chase

// Chief sets a reminder to check on a delegation
add-reminder:
  trigger_date: "2026-06-17"
  trigger_prompt: "Did Scott deliver the org chart update?"
  routing.agent: chief
  routing.action_prompt: "David confirmed Scott delivered the org chart. Log it as completed in the delegation tracker at data/delegation-tracker.json..."
  on_no.snooze_days: 1
  created_by: chief
```

---

## Error Handling

| Scenario | Response |
|----------|----------|
| `data/reminders.json` missing | Create it fresh with empty `reminders` array, then append |
| ID generation fails | Use `rem-` + current ISO timestamp manually. Log the fallback. |
| `action_prompt` is empty or missing | Refuse to write the entry. Return error: "action_prompt is required — cannot create a reminder without a routable action." |
| File write fails | Report failure to calling agent. Do not silently drop the reminder. |

---

## SKILL COMPLETE

After confirming the reminder was written to `data/reminders.json`, write the skill-run signal file:

**Path:** `systems/eval-harness/skill-runs/add-reminder-latest.json`

```json
{
  "skill": "add-reminder",
  "agent": "<owning_agent or calling_agent>",
  "trigger": "manual",
  "started": "<ISO 8601 local timestamp at skill start>",
  "completed": "<ISO 8601 local timestamp at skill end>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": [],
  "reminder_id": "<rem-XXXXXX id of the entry written>"
}
```

If the skill failed (file write error, missing action_prompt, ID generation failure), set `"status": "failure"` and populate `"error_ids"` with any logged error IDs.

Do not skip this write. The eval harness uses this file to confirm the skill ran.

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
