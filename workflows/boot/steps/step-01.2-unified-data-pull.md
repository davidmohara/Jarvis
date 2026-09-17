---
status: complete
started-at: "2026-09-16T14:22:24Z"
completed-at: "2026-09-16T14:24:00Z"
outputs:
  email_pull: "completed — 16 messages in window (2026-09-14 → 2026-09-16), 8 actionable (5 UTB board approvals via Boardvantage, 1 YPO candidate intake form, 1 BMW waiver for 09-23, 1 Opal Group partner follow-up), 8 marketing/internal/FYI"
  omnifocus_pull: "failed — Desktop Commander/osascript MCP tool unavailable this session (ToolSearch confirmed no match; 5th+ consecutive boot)"
  clay_pull: "completed — 0 reminders, 3 birthdays (COURT WESTCOTT 09-16, Kevin Gardner 09-20, Justin Etheredge 09-22) via Clay MCP"
  jarvis_inbox_pull: "nothing-to-surface — Jarvis folder search returned 0 messages"
  files_created:
    - "data/email-unified.json"
    - "data/omnifocus-unified.json"
    - "data/clay-reminders-unified.json"
    - "data/jarvis-inbox-unified.json"
  degraded: true
  degraded_reason: "omnifocus_pull unreachable — tool not present this session"
---

<!-- system:start -->
# Step 01.2: Unified Data Pull (Consolidate All External Data)

## MANDATORY EXECUTION RULES

1. You MUST pull ALL external data sources in a single phase — no repeated calls.
2. You MUST write each data source to a separate file in `data/` directory.
3. You MUST execute all pulls in parallel (fire simultaneously, do NOT wait sequentially).
4. You MUST report status for each pull (completed, nothing-to-surface, or failed — [reason]).
5. Clay MCP MUST ALWAYS attempt to pull, even if marked unavailable — this checks current state, not assumed stale data.
6. You MUST NOT proceed until all pulls have status reported.

---

## EXECUTION PROTOCOL

**Agent:** Master
**Input:** M365 MCP, Clay MCP, OmniFocus access, Jarvis folder
**Output:** Consolidated data files written to `data/` directory

---

## CONTEXT BOUNDARIES

- This step consolidates all external data pulls BEFORE phase 2 data gathering
- All downstream steps will read from these files instead of calling APIs
- Fire all pulls in parallel (non-blocking)
- No raw API responses stored in accumulated-context — only file paths and summaries

---

## YOUR TASK

Fire all pulls simultaneously. Each pull writes to disk and reports status.

### Pull A: Email (Flagged & Time-Sensitive)

**Source:** M365 MCP (`outlook_email_search`)
**Output file:** `data/email-unified.json`
**What to pull:**
- All flagged messages
- Unread messages from last 24 hours marked high priority
- Messages with explicit deadline or time-sensitive subject line
- Do NOT pull full inbox — only actionable items

**File format:**
```json
{
  "pulled_at": "ISO-8601",
  "message_count": N,
  "messages": [
    {
      "id": "...",
      "subject": "...",
      "from": "...",
      "received_at": "...",
      "is_flagged": true,
      "importance": "high",
      "snippet": "..."
    }
  ]
}
```

**Status reporting:**
```yaml
outputs:
  email_pull: "completed" | "nothing-to-surface" | "failed — [reason]"
  email_file: "data/email-unified.json"
  message_count: N
  file_size_kb: N
```

---

### Pull B: OmniFocus Inbox

**Source:** OmniFocus.

**Run the `omnifocus-data` skill.** Do NOT hand-write OmniFocus queries in this step:

```bash
python3 skills/omnifocus-data/scripts/omnifocus_data.py pull
```

That command writes `data/omnifocus-unified.json` and is the single writer for it. Read the file back and report `status` and `task_count`. A `status: failed` pull is a degraded source to surface, never something to pass over as an empty day.

For ad-hoc reads inside this step, use the same skill: `list --kind inbox`, `list --kind due`, `counts`. Prefer the script over the MCP for every read here, because it does not depend on MCP session state and boot runs unattended. If the MCP does happen to be connected, the two agree on counts, tags and projects — and note that its `query_omnifocus` returns a display rendering that omits notes, so it cannot stand in for the pull.

Why this is delegated rather than inlined here: OmniFocus query logic previously lived in five separate places and drifted, producing a 247-completed-task query and invented filter keys on 2026-09-16. The filter and the `status` contract now live in code. See `skills/omnifocus-data/SKILL.md`.

**Output file:** `data/omnifocus-unified.json`
**What to pull:**
- All active (non-completed) tasks in inbox
- Due today, overdue, or flagged
- Include: task name, due date, project, tags, flags

**File format:**
```json
{
  "pulled_at": "ISO-8601",
  "status": "available" | "failed",
  "task_count": N,
  "tasks": [
    {
      "id": "...",
      "name": "...",
      "completed": false,
      "due_date": "local date string or null",
      "project": "project name or null",
      "tags": "comma-joined tag names or null",
      "is_flagged": true,
      "note": "..."
    }
  ],
  "error": "reason, only when status is failed"
}
```

This shape is produced by `skills/omnifocus-data/scripts/omnifocus_data.py`; treat that script as the definition of record if the two ever disagree.

**`completed` MUST be present and false on every task.** The inbox holds roughly 247 completed tasks alongside the ~8 incomplete ones, and OmniFocus "Clean Up" does NOT remove them. Filtering is part of the query, never a cleanup step. Recording the field is what lets the eval harness assert that no completed task leaked into the pull.

**Status reporting:**
```yaml
outputs:
  omnifocus_pull: "completed — N tasks" | "nothing-to-surface" | "failed — [reason]"
  omnifocus_file: "data/omnifocus-unified.json"
  task_count: N
  file_size_kb: N
```

`status: available` with `task_count: 0` is a real empty result (nothing in the inbox, nothing due, nothing flagged). Report it as `nothing-to-surface`, not as a failure. `status: failed` is a degraded source and must be surfaced as such.

---

### Pull C: Clay Reminders (Next 7 Days) — MANDATORY ALWAYS

**Source:** Clay MCP
**Output file:** `data/clay-reminders-unified.json`
**MANDATORY:** This pull MUST ALWAYS attempt to fetch from Clay, even if Clay MCP is previously marked unavailable. This checks current state rather than assuming stale data.

**What to pull:**
- Upcoming reminders (next 7 days)
- Upcoming birthdays (next 7 days)
- Include: date, description, attendee/contact, relationship context

**File format:**
```json
{
  "pulled_at": "ISO-8601",
  "status": "available" | "unavailable" | "error",
  "reminders": [
    {
      "type": "reminder" | "birthday",
      "date": "YYYY-MM-DD",
      "description": "...",
      "contact_name": "...",
      "relationship": "..."
    }
  ],
  "reminder_count": N,
  "birthday_count": M
}
```

**Status reporting:**
```yaml
outputs:
  clay_pull: "completed — N reminders, M birthdays" | "nothing-to-surface — Clay returned empty" | "failed — [reason], but attempted anyway"
  clay_file: "data/clay-reminders-unified.json"
  reminder_count: N
  birthday_count: M
  file_size_kb: N
  attempted: true (always)
```

**Note:** Even if Clay appears unavailable, the attempt itself is valuable — it confirms current state and ensures we're not using stale cached assumptions.

---

### Pull D: Jarvis Inbox

**Source:** `/Jarvis` email folder
**Output file:** `data/jarvis-inbox-unified.json`
**What to pull:**
- All unread messages in /Jarvis folder
- Emails requiring David's direct attention
- Include: sender, subject, received date, summary

**File format:**
```json
{
  "pulled_at": "ISO-8601",
  "message_count": N,
  "messages": [
    {
      "id": "...",
      "from": "...",
      "subject": "...",
      "received_at": "...",
      "summary": "..."
    }
  ]
}
```

**Status reporting:**
```yaml
outputs:
  jarvis_inbox_pull: "completed" | "nothing-to-surface" | "failed — [reason]"
  jarvis_inbox_file: "data/jarvis-inbox-unified.json"
  message_count: N
  file_size_kb: N
```

---

## Recording Results

After ALL pulls complete, record outcomes in `accumulated-context`:

```yaml
accumulated-context:
  phase1-point5:
    unified-data-pulls:
      email: "completed — N messages" | "nothing-to-surface" | "failed — [reason]"
      omnifocus: "completed — N tasks" | "nothing-to-surface" | "failed — [reason]"
      clay: "completed — N reminders, M birthdays" | "nothing-to-surface" | "failed — [reason]"
      jarvis-inbox: "completed — N messages" | "nothing-to-surface" | "failed — [reason]"
    files-created:
      - "data/email-unified.json"
      - "data/omnifocus-unified.json"
      - "data/clay-reminders-unified.json"
      - "data/jarvis-inbox-unified.json"
    total_data_on_disk_kb: N
```

---

## Execution Guidelines

### Parallel Execution (Fire All Simultaneously)

```
Step 01.2 begins
  ↓
Fire all 4 pulls simultaneously:
  ├─ Pull A: Email (M365 API call)
  ├─ Pull B: OmniFocus
  ├─ Pull C: Clay reminders
  └─ Pull D: Jarvis inbox
  
Wait for all to complete
  ↓
Record status for each pull
  ↓
Proceed to step 02
```

Do NOT wait for one pull to finish before starting the next. They should all run concurrently.

### Status Reporting

Each pull MUST report one of three outcomes:
- **completed** — Pull succeeded, file written, N items found
- **nothing-to-surface** — Pull succeeded but no items (empty result)
- **failed — [reason]** — Pull failed (API unavailable, permissions, etc.)

Silence is not an option. Every pull must report status.

---

## Success Metrics

- All 4 pulls fire simultaneously (not sequentially)
- All 4 pulls report status (no silent failures)
- Files written to disk: 4 JSON files in `data/` directory
- Total data on disk: < 500 KB combined
- No raw data stored in accumulated-context (only file paths and summaries)
- Estimated context savings: 80-90% vs. storing raw data in context

---

## Failure Modes

| Failure | Action |
|---------|--------|
| M365 email API unavailable | Record: "email: failed — M365 unavailable". Continue. |
| OmniFocus connection fails | Record: "omnifocus: failed — [reason]". Continue. |
| Clay MCP unavailable | Record: "clay: nothing-to-surface — Clay unavailable". Continue. |
| Jarvis folder missing | Record: "jarvis-inbox: nothing-to-surface — folder not found". Continue. |
| File write fails for any pull | Record failure. Continue. Downstream steps handle missing files. |
| Multiple pulls fail | Record all failures. Continue to step 02. Boot will degrade gracefully. |

---

## Update State

1. **Update step frontmatter:** Set `status: complete` and `completed-at` with current timestamp.
2. **Update state.yaml:** Set `current-step: step-02-gather-data.md`.

---

## NEXT STEP

Read fully and follow: `step-01.5-unified-calendar-pull.md`

All downstream steps (phase 2 through phase 5) will read from these consolidated files instead of calling APIs.

---

## Implementation Notes for Consuming Steps

**After this step completes, all other steps should be updated to read from files instead of calling APIs:**

### Boot Step-02 (Phase 2)
- Task H (Email triage): Read from `data/email-unified.json` (not M365)
- OmniFocus data: Read from `data/omnifocus-unified.json` (not OmniFocus API)

### Morning Briefing
- Step-02 (Task gather): Read from `data/omnifocus-unified.json`
- Step-04 (Synthesis): Include Clay data from `data/clay-reminders-unified.json`

### Jarvis Inbox Skill
- Instead of reading /Jarvis folder, read from `data/jarvis-inbox-unified.json`

This pattern: **one pull per data source → all consumers read from shared file**
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
