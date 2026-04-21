# Semantic Memory

Distilled patterns synthesized from episodic clusters. Permanent. Always loaded at boot.

## CRITICAL RULE
**The dream cycle is the ONLY agent that writes to `memory/semantic/`.** All other agents
read semantic entries but must never write them directly. Semantic = earned, not written.

## Subdirectories
| Directory | Content |
|-----------|---------|
| `relationships/` | Patterns about people, accounts, and relationships |
| `operational/` | System behavior and process patterns |
| `domain/` | Business domain and industry patterns |

## Schema
```yaml
---
type: semantic
domain: relationships | operational | domain-knowledge | pattern
subject: "Distilled pattern description"
synthesized-from:
  - episodic/meetings/2026-04-01-143022-meeting-notes-healthcare-sync.md
last-updated: YYYY-MM-DD
tags: [tag1, tag2]
agent-source: dream-cycle
confidence: low | medium | high
---

## Pattern Summary
[Synthesized insight — not raw transcript, but distillation]

## Evidence
[Key data points supporting this pattern]

## Implications
[What agents should do differently knowing this pattern]
```

## Filename Convention
`YYYY-MM-DD-{tag-slug}-pattern.md`
