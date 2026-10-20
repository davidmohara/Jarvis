<!-- system:start -->
# Pull File Formats (boot step-01.2)

Exact output-file JSON schemas for Pulls A-D. Write files in these shapes.

## Pull A — data/email-unified.json

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

## Pull B — data/omnifocus-unified.json

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

## Pull C — data/clay-reminders-unified.json

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

## Pull D — data/jarvis-inbox-unified.json

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
## Per-pull status reporting shapes

**Status reporting:**
```yaml
# state.yaml -> accumulated-context
email_pull: "completed" | "nothing-to-surface" | "failed — [reason]"
email_file: "data/email-unified.json"
message_count: N
file_size_kb: N
```

**Status reporting:**
```yaml
# state.yaml -> accumulated-context
omnifocus_pull: "completed — N tasks" | "nothing-to-surface" | "failed — [reason]"
omnifocus_file: "data/omnifocus-unified.json"
task_count: N
file_size_kb: N
```

**Status reporting:**
```yaml
# state.yaml -> accumulated-context
clay_pull: "completed — N reminders, M birthdays" | "nothing-to-surface — Clay returned empty" | "failed — [reason], but attempted anyway"
clay_file: "data/clay-reminders-unified.json"
reminder_count: N
birthday_count: M
file_size_kb: N
attempted: true (always)
```

**Status reporting:**
```yaml
# state.yaml -> accumulated-context
jarvis_inbox_pull: "completed" | "nothing-to-surface" | "failed — [reason]"
jarvis_inbox_file: "data/jarvis-inbox-unified.json"
message_count: N
file_size_kb: N
```
## Delegation note

Why this is delegated rather than inlined here: the filter and the `status` contract live in code. See `skills/omnifocus-data/SKILL.md`.
## Delegation note

Why delegated rather than inlined: the transfer/spend filter, the 12-month window, and the `status` contract live in code. See `skills/ynab-data/SKILL.md`.
<!-- system:end -->
