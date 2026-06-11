# Knowledge Layer

The Knowledge Layer provides persistent storage for everything your agents learn about your world. Knowledge accumulates over time, making IES increasingly valuable with use.

### Knowledge Storage Architecture

All knowledge is stored as **markdown files with YAML frontmatter** in a tiered memory system:

```
memory/
├── working/              # Volatile task state — TTL 2 days
├── episodic/             # Event-sourced knowledge (what happened)
│   ├── meetings/         # Meeting notes and follow-ups
│   ├── people/           # Contact context and relationship notes
│   ├── projects/         # Project history and status
│   ├── decisions/        # Decision rationale and outcomes
│   ├── coaching/         # Coaching observations and development
│   └── digests/          # Quarterly compression digests (dream cycle only)
├── semantic/             # Distilled patterns — written by dream cycle ONLY
│   ├── relationships/    # Patterns about people and accounts
│   ├── operational/      # System and process patterns
│   └── domain/           # Business domain and industry patterns
├── personal/             # User config — never promoted
│   ├── org.md
│   ├── principles.md
│   ├── quarterly-objectives.md
│   ├── vision.md
│   └── PREFERENCES.md
├── LESSONS.md            # Global lessons from constraint violations
└── dream.log             # Dream cycle audit log
```

**Read priorities at boot:** `personal/` and `semantic/` are always loaded. `episodic/` and `working/` are queried on demand.

**CRITICAL:** `memory/semantic/` is written ONLY by the dream cycle. All other agents read semantic entries but must never write them directly.

### Knowledge Entry Types

The system supports 5 episodic entry types:

1. **meeting-notes** — Notes from meetings, 1:1s, calls → stored in `memory/episodic/meetings/`
2. **contact-context** — Relationship history, preferences, insights about people → stored in `memory/episodic/people/`
3. **project-history** — Project progress, decisions, learnings → stored in `memory/episodic/projects/`
4. **coaching-observation** — Team member development observations → stored in `memory/episodic/coaching/`
5. **decision-rationale** — Why decisions were made, options considered → stored in `memory/episodic/decisions/`
6. **working-archive** — Archived working memory entries promoted to episodic by the dream cycle → stored in `memory/episodic/` (any subdirectory, retains original path)
7. **account-intelligence** — Account strategy briefs, relationship maps, competitive context → stored in `memory/episodic/projects/`
8. **content-review** — Podcast hosting self-reviews, content quality assessments → stored in `memory/episodic/` (Harper-specific)
9. **cross-agent-escalation** — Initiative escalations routed between agents (e.g., Quinn → Chase) → stored in `memory/episodic/projects/`
10. **alignment-check** — Periodic goal alignment snapshots, drift analysis → stored in `memory/episodic/projects/`

### Working Memory Entry Schema

Working entries capture live task state within a session. They expire automatically after 2 days.

```yaml
---
type: working
task_id: "todo-2026-04-17-001"         # OmniFocus or IES task ID (use "session" if no task)
session_id: "chief-2026-04-17-091532"   # {agent}-{YYYY-MM-DD}-{HHmmss}
agent-source: chief | chase | quinn | shep | harper | rigby | knox | galen | sterling
created: 2026-04-17T09:15:32           # Local time, no Z suffix
expires: 2026-04-19T09:15:32           # created + 2 days
status: active | archived              # ONLY these two values
context: "Brief description of what this captures"
---
```

### Episodic Entry Schema

Every episodic entry must include this standardized frontmatter (the `salience` block is managed by the dream cycle):

```yaml
---
type: meeting-notes | contact-context | project-history | coaching-observation | decision-rationale | working-archive | account-intelligence | content-review | cross-agent-escalation | alignment-check
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
  score: 0
  references: []
  last-promoted-check: YYYY-MM-DD
  promoted: false
---
```

### Working-Archive Entry Notes

`working-archive` entries are created by dream-cycle step-01 (not by agents directly). They begin as `type: working` entries and are mutated in-place during archival. The frontmatter receives:
- `type: working-archive` (replaces `type: working`)
- `status: archived`
- `salience.score: 0`
- Enrichment fields: `date`, `tags`, `source_file`, `related_people` (derived from body content)

The `working-archive` type is NOT used by any agent writing new episodic entries — it is exclusively a dream-cycle output.

### Semantic Entry Schema

Semantic entries are written exclusively by the dream cycle. They synthesize patterns from episodic clusters. All other agents read but never write semantic files.

```yaml
---
type: semantic
domain: relationships | operational | domain-knowledge | pattern
subject: "Distilled pattern description"
synthesized-from:
  - episodic/meetings/2026-04-01-143022-meeting-notes-healthcare-sync.md
  - episodic/people/2026-03-18-093011-contact-context-sarah-chen.md
last-updated: YYYY-MM-DD
tags: [tag1, tag2]
agent-source: dream-cycle
confidence: low | medium | high
---
```

### Knowledge File Naming Convention

Files are named to prevent collisions and enable chronological sorting:

**Format:** `YYYY-MM-DD-HHmmss-{type}-{subject-slug}.md`

**Example:** `2026-02-25-143022-meeting-notes-q1-planning.md`

- Timestamp provides uniqueness and chronological sorting
- Subject converted to kebab-case for filesystem compatibility
- Each write creates a new file — agents **never append to existing knowledge files**

### Query Patterns for Agents

Agents query the knowledge layer by reading files from the appropriate `memory/episodic/` directory and examining their frontmatter. There are 5 query patterns:

#### 1. Query by Person

Find all knowledge entries mentioning a specific person.

**How:** Read all files across `memory/episodic/` subdirectories. Match entries where `related-entities.people` includes the target person name.

**Use case:** Preparing for a 1:1, understanding relationship history

**Primary directory:** `memory/episodic/people/` (check others for cross-references)

#### 2. Query by Project

Find all knowledge entries related to a project.

**How:** Read files in `memory/episodic/projects/` and cross-reference other directories. Match entries where `related-entities.projects` includes the project name.

**Use case:** Project status review, historical context

#### 3. Query by Meeting

Find notes for a specific meeting.

**How:** Read files in `memory/episodic/meetings/`. Match by filename date or `related-entities.meetings` field.

**Use case:** Meeting follow-up, action item tracking

#### 4. Query by Topic

Find knowledge entries containing specific keywords or tags.

**How:** Search across all `memory/episodic/` subdirectories. Match entries where `tags` array includes the topic OR file content contains the keyword (case-insensitive).

**Use case:** Thematic research, topic exploration

#### 5. Query by Recency

Retrieve most recent knowledge entries.

**How:** List files across `memory/episodic/` subdirectories, sort by filename (date-prefixed), return the most recent N entries.

**Use case:** "What's new?", daily briefings, recent activity review

### Handling No Results

When no matching entries are found for a query, this is **not an error**. The agent should report that no results were found and continue execution. Never treat absence of knowledge as a failure.

### Writing Knowledge Entries

When an agent creates a knowledge entry during task execution:

1. Determine the entry type and appropriate directory
2. Generate a filename following the naming convention
3. Write the file with proper YAML frontmatter and markdown content

### Concurrent Writes

Multiple agents may write to the knowledge layer in the same session. Each write creates a **separate file** — agents never append to shared files. The timestamp in the filename prevents collisions.

### Knowledge Integration with Agents

| Agent | Writes | Reads |
|-------|--------|-------|
| **Chief** | Meeting notes, daily summaries | Meeting context, task status |
| **Chase** | Account context, deal notes | Deal history, client context |
| **Shep** | Coaching observations, 1:1 notes | Relationship history, delegation status |
| **Quinn** | Decision rationale, initiative updates | Strategic context, goal progress |
| **Harper** | Content drafts | Context for presentations, talking points |
| **Rigby** | Evolution logs, package status | Manifest, evolution packages |
| **Master** | Cross-domain synthesis | All knowledge for routing decisions |

### Document Templates

Pre-built templates are available in `documents/templates/` for common document types:

- `decision-template.md` — Decision documentation with context, options, rationale
- `project-template.md` — Project tracking with milestones and risks
- `people-template.md` — Contact/team member profiles
- `meeting-template.md` — Meeting notes with agenda, decisions, action items
- `review-template.md` — Period reviews with accomplishments and goals

### Knowledge Layer Best Practices

1. **Be Specific in Subjects** — Use descriptive subjects for easy retrieval
2. **Tag Consistently** — Use consistent tag vocabulary across entries
3. **Link Entities** — Always populate `related-entities` for rich querying
4. **Date Accurately** — Use actual event date, not write date
5. **Attribute Sources** — Set correct `agent-source` for transparency
