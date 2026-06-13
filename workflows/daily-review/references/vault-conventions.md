# Daily Review — Vault Conventions Reference

Quick reference for writing daily review journal entries to the knowledge system.

## Knowledge System Routing

For David's setup: write to the `Daily Reviews` folder in the Obsidian vault using the Obsidian MCP (`mcp__obsidian-mcp-tools__create_vault_file` or `mcp__obsidian-mcp-tools__patch_vault_file`).

Target path: `Daily Reviews/YYYY-MM-DD <Descriptive Title>.md`

## Folder Structure

```
Daily Reviews/
  YYYY-MM-DD <Descriptive Title>.md
  YYYY-MM-DD <Descriptive Title>.md
  ...
```

No subfolders — the date prefix provides all sorting and filtering.

## Tag Taxonomy

### Required on every daily review note

- `content/daily-review` — marks this as a daily journal entry
- `meta/timeline/YYYY/MM/DD` — temporal marker (in frontmatter YAML, not inline)

### Optional contextual tags (0-2 max, only when clearly dominant)

- `work/strategy` — day was dominated by strategic decisions or planning
- `work/operations/sales` — significant sales or pipeline activity
- `work/operations/growth` — coaching, 1:1s, team development was the defining thread
- `work/client` — major client work was the day's center of gravity
- `personal/ypo` — YPO event or forum was primary

Tag budget: 2-4 total per note. Never use both parent and child tag.

## Frontmatter Format

```yaml
---
tags:
  - content/daily-review
  - meta/timeline/2026/03/22
---
```

Rules:
- No `#` prefix inside YAML arrays
- Lowercase with hyphens for multi-word tags
- 2-4 tags per note (never more)

## Filename Convention

```
YYYY-MM-DD <Descriptive Title>.md
```

- Date prefix always present and accurate to the day being reviewed
- Title captures the defining theme — not generic ("Daily Review"), not a list, but a phrase that means something ("The Day the Partnership Moved", "Rebuilding After a Hard Week")
- Clean of special characters (letters, numbers, spaces, hyphens only)
- File extension `.md`

## Note Template

```markdown
---
tags:
  - content/daily-review
  - meta/timeline/YYYY/MM/DD
---

# YYYY-MM-DD <Descriptive Title>

<Paragraph 1: What kind of day it actually was. The dominant thread. Set the scene in first
person, past tense.>

<Paragraph 2: What moved, what stalled, and the why behind each. Connect completions and
failures to the current quarter's rocks. Be specific.>

<Paragraph 3: What's carrying forward and why. The strategic texture of the day. What does
today mean in the broader arc of the quarter? End with something forward-looking.>

<Optional Paragraph 4-5: Add only if the day had significant complexity, a decision worth
capturing, or an insight that matters in six months.>
```

## Writing Style

- First person, past tense throughout
- Prose only — no bullet lists, no headers inside the entry, no tables
- Synthesize, don't extract: this is not a task log. The task log is the operational review file.
- Length: 3-5 paragraphs
- Voice: direct, honest, occasionally sharp

## Daily Note Cross-Linking

After writing the daily review entry, add a wikilink from the daily calendar note.

### Daily note location

```
Calendar/YYYY/MM-MonthName/YYYY-MM-DD.md
```

### Adding the link

Append under the `# Notes` heading:

```
[[Daily Reviews/YYYY-MM-DD <Descriptive Title>]]
```

If no daily calendar note exists for the date, skip cross-linking — do not create the calendar note just for this purpose.
