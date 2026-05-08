# Session Index Skill

<!-- system:start -->
## Overview

The Session Index is Jarvis's continuity system for tracking file writes, open loops, and topic shifts across a session. It is an append-only JSON array stored at `memory/sessions/index.json`. Each session record captures:

- Session metadata (id, started, closed timestamps)
- Current topic being worked on
- Array of topics touched in the session, with files written and open loops (unresolved issues)

This skill documents how to read, write, and update the session index during execution.

## File Location

`memory/sessions/index.json` — IES root directory

## Schema Reference

Each session record:

```json
{
  "id": "session-{YYYY-MM-DD}-{HHMMSS}",
  "date": "YYYY-MM-DD",
  "started": "ISO 8601 timestamp",
  "closed": "ISO 8601 timestamp or null",
  "current_topic": "string or null",
  "topics": [
    {
      "topic": "string (topic name)",
      "files": ["relative/path/to/file.md", ...],
      "loops": [
        { "text": "description of open loop", "resolved": false },
        ...
      ],
      "flag": true  // Only present if this is the 'unattributed' bucket
    }
  ]
}
```

Key rules:
- `current_topic`: Set to a topic name string when work shifts to a new area. Set to null when exiting a topic or at session close.
- `topics[].files`: Automatically populated by PostToolUse hook when files are written. Manual intervention rarely needed.
- `topics[].loops`: Array of open issues, each with `text` (description) and `resolved` (boolean, always false unless you explicitly mark true during the session).
- `flag: true`: Only appears on the "unattributed" bucket for files written when `current_topic` was null.

## Operations

### 1. Read the Current Session Record

```
# Get the active session (last item in the array)
1. Read memory/sessions/index.json
2. Parse as JSON
3. Get the last item: sessions[-1]
4. This is your active session record
```

### 2. Set Current Topic

When work shifts to a new subject:

```
1. Read memory/sessions/index.json
2. Get the active session (last item)
3. Set active_session["current_topic"] = "your-topic-name"
4. If this topic doesn't exist in active_session["topics"], create it:
   {
     "topic": "your-topic-name",
     "files": [],
     "loops": []
   }
5. Write the updated session record back to memory/sessions/index.json
```

**Example:** Shifting from "morning briefing" to "email processing"
```
current_topic: "morning briefing"  →  current_topic: "email processing"
Create new topic entry if "email processing" doesn't already exist in topics[]
```

### 3. Add a Loop to Current Topic

When you surface an open issue, task, or commitment that will be carried forward:

```
1. Read memory/sessions/index.json
2. Get the active session
3. Find the topic matching current_topic
4. Append to topics[matched].loops:
   {
     "text": "description of the loop",
     "resolved": false
   }
5. Write updated record back
```

**Example:**
```
New loop: "DRC talk prep — May 21, no file started"
Append to the "session-index-build" topic's loops array
```

### 4. Manually Append a File to Current Topic

Normally the PostToolUse hook handles this. But if you need to manually add a file:

```
1. Read memory/sessions/index.json
2. Get the active session and find the topic matching current_topic
3. If the file path is not already in topics[matched]["files"], append it:
   - Use relative paths from IES root (e.g., "memory/working/2026-05-08-123456-boot.md")
   - Deduplicate — never add the same path twice
4. Write updated record back
```

### 5. Mark a Loop as Resolved

Once an open loop is handled:

```
1. Read memory/sessions/index.json
2. Get the active session
3. Find the loop in the topic's loops array by its text
4. Set resolved: true on that loop
5. Write updated record back
```

### 6. Initialize a New Session at Boot

Called automatically by Jarvis boot sequence:

```
1. If memory/sessions/index.json doesn't exist:
   Write: []
2. Read the file
3. Generate session ID: session-{YYYY-MM-DD}-{HHMMSS}
4. Append new session record:
   {
     "id": "session-2026-05-08-120000",
     "date": "2026-05-08",
     "started": "2026-05-08T12:00:00-07:00",
     "closed": null,
     "current_topic": null,
     "topics": []
   }
5. Write updated array back
```

### 7. Close the Session at Exit

Called automatically by Jarvis shutdown sequence:

```
1. Read memory/sessions/index.json
2. Get the active session (last item)
3. Set closed = current ISO 8601 timestamp
4. Set current_topic = null
5. Check for any topic with "flag": true (unattributed bucket)
   - If found, surface to David asking for topic reassignment
   - Update the topic name from "unattributed" to the correct topic once confirmed
6. Verify JSON is valid
7. Write updated array back
```

## Trigger Keywords

- session
- topic
- current topic
- set topic
- loop
- session index
- unattributed

## Owning Agent

Master / Chief (Jarvis)

## Notes

- The PostToolUse hook in `.claude/hooks/post-tool-use.py` runs automatically after every Write or Edit tool call. It reads `current_topic` and appends the file path to the matching topic's files array. No manual intervention needed.
- If `current_topic` is null when a file is written, the hook creates an "unattributed" bucket and sets `flag: true` on it. This flags the session for cleanup at shutdown.
- Always deduplicate file paths — the hook checks for this, and manual operations should too.
- `resolved` is boolean. It's only ever `false` during the session. Loops that get resolved should be marked `true` before session close.

<!-- system:end -->
