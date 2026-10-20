---
status: not-started
started-at: ~
completed-at: ~
model: sonnet
---

<!-- system:start -->
# Step 05: Synthesize Monthly Health Note

## EXECUTION PROTOCOL

**Agent:** Galen, spawned by the coordinator, never executed inline in the coordinator's session.
**Input:** `whoop_monthly`, `bloodwork_monthly`, `body_comp_monthly`, and `lifebook_progress` from working memory
**Output:** `Mind/Health/Monthly Review - [Month Year].md`

---

## YOUR TASK

**Format:** Markdown file suitable for Obsidian vault

**Path:** `Mind/Health/Monthly Review - March 2026.md`

**Frontmatter:**
```yaml
---
date: 2026-03-29
month: March 2026
tags: [health, monthly-review, WHOOP, bloodwork, body-comp]
---
```

**Content Structure:** assemble the note using the exact template in `references/monthly-note-template.md` (read it before writing). Fill every bracketed placeholder from the accumulated analysis.

## NEXT STEP

Read fully and follow: `step-06-metrics-log.md`
<!-- system:end -->
