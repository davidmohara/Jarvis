# Working Memory

Volatile task state scoped to a single session. Entries expire after 2 days.

## Rules
- Written by any agent during an active session
- TTL: 2 days from creation (`expires` frontmatter field)
- Expired entries are archived or deleted by the dream cycle (Phase 1)
- Non-trivial expired entries move to `memory/episodic/` as `type: working-archive`

## Schema
```yaml
---
type: working
task_id: "todo-2026-04-17-001"
session_id: "chief-2026-04-17-091532"
agent-source: chief | chase | quinn | shep | harper | rigby | knox
created: YYYY-MM-DDTHH:MM:SS
expires: YYYY-MM-DDTHH:MM:SS
status: active | archived
context: "Brief description of what this captures"
---
```
