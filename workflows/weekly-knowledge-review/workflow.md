---
name: weekly-knowledge-review
description: Weekly review of knowledge capture — what was ingested, what's unprocessed, what action items are floating, what connections were missed
owner: knox
evolution: personal
---

<!-- personal:start -->
# Weekly Knowledge Review Workflow

Surface unprocessed captures, suggest connections between recent notes and active projects/rocks, and flag action items that never made it to OmniFocus.

## Entry Conditions

Triggered when:
- Controller says "knowledge review" or "what did I capture this week"
- Scheduled weekly (recommend: Friday afternoon or Monday morning)
- Quinn requests knowledge context during quarterly review

## Steps

| Step | File | Description |
|------|------|-------------|
| 01 | `steps/step-01-inventory.md` | Count what was captured this week across all sources |
| 02 | `steps/step-02-unprocessed.md` | Identify content that was ingested but not linked or tagged |
| 03 | `steps/step-03-orphans.md` | Find new notes that don't connect to any project, person, or initiative |
| 04 | `steps/step-04-actions.md` | Scan recent notes for action items that weren't routed to OmniFocus |
| 05 | `steps/step-05-connections.md` | Suggest links between recent captures and active rocks/initiatives |
| 06 | `steps/step-06-report.md` | Generate weekly knowledge digest |

## Report Format

```markdown
## Weekly Knowledge Digest — {week of date}

### Captured This Week
- **Remarkable**: {N} notes synced ({list})
- **Plaud**: {N} transcripts ingested ({list})
- **Manual**: {N} notes created ({list})

### Unprocessed
- {N} notes without tags
- {N} notes without links to people or projects

### Floating Action Items
Items found in notes that don't appear in OmniFocus:
- "{action}" — from {note name} ({date})
- "{action}" — from {note name} ({date})

### Suggested Connections
- **{Note}** mentions {person/project} — consider linking to [[{existing note}]]
- **{Transcript}** discusses {topic} — related to rock: {rock name}

### Vault Health (Quick)
- Total notes: {N}
- New this week: {N}
- Orphaned: {N}
```

## Rollback Protocol

This workflow is read-only — it generates a report but does not modify the vault. No rollback needed.
<!-- personal:end -->
