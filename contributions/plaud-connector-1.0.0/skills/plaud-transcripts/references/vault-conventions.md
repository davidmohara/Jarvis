# KMS Conventions Reference

Quick reference for the configured knowledge management system (KMS).

> **KMS Configuration:** This connector is KMS-agnostic. The ingest target is determined
> by the `kms` configuration key in `config/settings.json`. Implementations must satisfy
> the `kms` interface by supplying the folder structure, tag taxonomy, note template,
> and daily note cross-linking behavior documented below. The examples here use Obsidian
> conventions (the reference implementation), but any KMS satisfying this interface is valid.
>
> **Implementing a KMS adapter:** Copy this file to your instance, update the folder paths
> and tool bindings for your KMS, and set `kms: <your-kms-name>` in `config/settings.json`.
> The plaud-transcripts skill reads this file to determine where to write notes and how
> to format them.

## Folder Structure (Meeting-Relevant)

All meeting transcripts (both Plaud and Teams) are stored under the KMS meeting root,
split by context. The meeting root path is determined by your KMS configuration:

```
<kms.meeting_root>/
├── Client/       — client-facing meetings, customer calls, sales discussions
├── Improving/    — internal Improving meetings (strategy, ops, 1:1s, all-hands)
├── YPO/          — YPO meetings, forum, events, REX calls
└── Other/        — personal, faith, family, finances, anything that doesn't fit above
```

**Reference implementation (Obsidian):** `kms.meeting_root = "zzPlaud"`, accessed via
`mcp__obsidian-mcp-tools__list_vault_files` and `mcp__obsidian-mcp-tools__create_vault_file`.

Routing logic: scan meeting title, attendee list, and transcript content to determine
the correct subfolder. When ambiguous, default to `Other/`.

## Tag Taxonomy (Meeting-Relevant Subset)

### Required on every meeting note
- `content/meeting` — marks this as a meeting note
- `meta/timeline/YYYY/MM/DD` — temporal marker (in frontmatter, not inline)

### Work tags (pick the most specific)

- `work/client` — client meetings, customer calls, sales discussions
- `work/strategy` — strategic planning, vision, company direction
- `work/strategy/board` — board meetings
- `work/strategy/vision` — company vision discussions
- `work/operations` — internal ops, process, execution
- `work/operations/sales` — sales pipeline, proposals
- `work/operations/growth` — employee growth, coaching, 1:1s
- `work/operations/finance` — financial discussions
- `work/industry` — industry events, conferences, external panels
- `work/boards` — board memberships and advisory roles
- `work/projects` — specific project-related meetings
- `work/partners` — partner and vendor meetings

### Personal tags

- `personal/ypo` — YPO meetings, forum, events, REX calls
- `personal/finances` — personal financial discussions
- `personal/faith` — faith-related meetings
- `personal/family` — family matters

## Frontmatter Format

```yaml
---
tags:
  - content/meeting
  - work/client
  - meta/timeline/2026/03/18
---
```

Rules:
- No `#` prefix inside YAML arrays
- Lowercase with hyphens for multi-word tags
- 2-4 tags per note (never more)
- Use the most specific applicable tag
- Don't include both parent and child (e.g., don't use `work` AND `work/client`)

## Filename Convention

```
YYYY-MM-DD <Title>.md
```

Examples:
- `2026-03-18 Weekly Sync.md`
- `2026-03-18 Simpson Strong-Tie AI Workshop.md`
- `2026-03-18 Plaud Recording - Client Call.md`

Rules:
- Date prefix always present
- Title cleaned of special characters (keep letters, numbers, spaces, hyphens)
- No duplicate spaces
- File extension `.md`

## Note Template for Meeting Transcripts

```markdown
---
tags:
  - content/meeting
  - <contextual-tag-1>
  - meta/timeline/YYYY/MM/DD
---

# <Meeting Title>

## Meeting Details

- **Date:** YYYY-MM-DD
- **Time:** HH:MM AM/PM - HH:MM AM/PM CST
- **Platform:** <Teams | Plaud.ai>
- **Organizer:** <n>

## Attendees

- Name (email or role)

## Summary

<2-4 sentence analytical summary>

## Key Discussion Points

### <Topic 1>

<Prose summary of this discussion thread>

### <Topic 2>

<Prose summary>

## Action Items

- [ ] Action item with owner
- [ ] Another action item

## Transcript

<details>
<summary>Full Transcript</summary>

**Speaker Name** (HH:MM:SS):
Transcript text here...

**Another Speaker** (HH:MM:SS):
More text...

</details>
```

## Daily Note Cross-Linking

Every meeting note should be linked from the daily calendar note for that date.

### Daily note location

The daily note path pattern is defined by `kms.daily_note_path_pattern` in settings.
**Reference implementation (Obsidian):**

```
Calendar/YYYY/MM-MonthName/YYYY-MM-DD.md
```

Month folder names: `01-January`, `02-February`, `03-March`, etc. (no spaces around
the dash). Some 2025 folders use `MM - MonthName` (with spaces) — match what already
exists rather than creating duplicates.

### Daily note template

If no daily note exists for the date, create one from this template:

```markdown
---
tags:
  - meta/timeline/YYYY/MM/DD
---
#timeline/YYYY/MM/DD
# Todo List


# Critical Topics


# Readings


# Notes
```

### Adding the meeting link

Append a wikilink under the `# Notes` heading. Use the meeting note's path
relative to the KMS root (no `.md` extension in wikilinks):

### Creating folders

If the year or month folder doesn't exist, create it. Use the `MM-MonthName` format
(no spaces) for new month folders.

Month name lookup: 01-January, 02-February, 03-March, 04-April, 05-May, 06-June,
07-July, 08-August, 09-September, 10-October, 11-November, 12-December.

## KMS Interface Contract

Any KMS adapter used with the plaud-connector must support:

| Operation | Description |
|-----------|-------------|
| `kms.list(path)` | List files at a path within the KMS |
| `kms.read(path)` | Read a file from the KMS |
| `kms.write(path, content)` | Write a file to the KMS |
| `kms.append(path, content)` | Append content to an existing file |
| `kms.exists(path)` | Check if a file or folder exists |

**Obsidian adapter:** uses `mcp__obsidian-mcp-tools__*` tools.
**Filesystem adapter:** uses direct Read/Write/Edit/Bash tools.
**Other adapters:** implement the operations above using whatever tools are available.

## Platform-Specific Notes

### Teams Transcripts
- Come with structured speaker labels and timestamps
- Meeting metadata (attendees, times, organizer) available from calendar event
- Transcript accessed via `meeting-transcript:///<meetingId>` URI

### Plaud.ai Transcripts
- May have timestamps but speaker identification varies
- Metadata is minimal — title and date often inferred from filename
- Export formats: plain text (.txt) or markdown (.md)
- Common filename patterns: `Recording_YYYYMMDD.txt`, `YYYY-MM-DD_<title>.txt`
- Platform field should be set to "Plaud.ai"
