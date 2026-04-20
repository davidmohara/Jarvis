# Episodic Memory

Event-sourced knowledge entries. What happened, who was involved, what was decided.
TTL: 90 days, then compressed into quarterly digests by the dream cycle.

## Subdirectories
| Directory | Content | Written By |
|-----------|---------|------------|
| `meetings/` | Meeting notes | chief, knox |
| `people/` | Contact context | chief, chase, shep |
| `projects/` | Project history | quinn, chase |
| `decisions/` | Decision rationale | quinn, chief |
| `coaching/` | Coaching observations | shep |
| `digests/` | Quarterly compression digests (read-only after creation) | dream-cycle |

## Schema (extends existing knowledge entry)
```yaml
---
type: meeting-notes | contact-context | project-history | coaching-observation | decision-rationale
subject: "Brief description"
date: YYYY-MM-DD
tags: [tag1, tag2, tag3]
related-entities:
  people: [name1, name2]
  projects: [project-name]
  accounts: [account-name]
  meetings: [meeting-id]
agent-source: chief | chase | quinn | shep | harper | rigby | knox | galen | sterling
salience:
  score: 0                        # 0–10; managed by dream cycle
  references: []
  last-promoted-check: YYYY-MM-DD
  promoted: false
---
```

## Filename Convention
`YYYY-MM-DD-HHmmss-{type}-{slug}.md`
Example: `2026-04-17-143022-meeting-notes-q2-planning.md`
