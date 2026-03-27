# Integrations

## Primary Tools

| Tool | Purpose | Access |
|------|---------|--------|
| OmniFocus | Task management, inbox, projects | osascript via Bash |
| Obsidian | Knowledge base, vault, notes, Lifebook | MCP server |
| Microsoft Teams | Communication with team, Ilse | MCP server (if available) |
| Dynamics CRM | Account and pipeline tracking | MCP server (if available) |
| Outlook / Email | Communication | MCP server (if available) |
| Calendar | Scheduling, meeting prep | MCP server (if available) |
| PowerPoint | Presentations, strategy decks | Local file access |
| Excel | Data, planning | Local file access |
| OneDrive | Cloud storage for Improving files | Local mount at ~/Library/CloudStorage/OneDrive-Improving/ |
| Clay | Personal relationship management — contacts, notes, reminders, interaction history | MCP server (mcp__clay__*) |
| WHOOP | Recovery, sleep, strain, workout data | MCP server (whoop) — OAuth pending setup |
| Jarvis Bridge | Code-Desktop task handoff | File queue in `bridge/` |
| Phone / Texts | Quick communication | Not accessible by Jarvis |

## Clay — Personal Relationship Management

Clay is the **network intelligence layer** — it auto-imports contacts from email, calendar, messages, and LinkedIn, enriches them with work/education info, and tracks interaction history across channels. It is NOT a CRM replacement (Dynamics handles pipeline). Clay is for relationship awareness.

### Available Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `mcp__clay__searchContacts` | Search contacts by name, company, location, interaction date, keywords | Meeting prep, account strategy, "who do I know at X?" |
| `mcp__clay__getContact` | Full contact details by ID | Deep context on a specific person |
| `mcp__clay__createContact` | Create new contact | Post-event capture, new relationships |
| `mcp__clay__updateContact` | Update existing contact | Role changes, new info learned |
| `mcp__clay__createNote` | Add note to contact (with optional reminder) | Post-meeting capture, follow-up reminders |
| `mcp__clay__getGroups` | List all groups/lists | Segment-based lookups |
| `mcp__clay__getNotes` | Get notes by date range | Review recent relationship notes |
| `mcp__clay__getEvents` | Calendar events by date range | Interaction history |
| `mcp__clay__getUpcomingEvents` | Next upcoming events | Pre-meeting awareness |
| `mcp__clay__getEmails` | Emails by date range | Communication history with a contact |
| `mcp__clay__getRecentEmails` | Recent email interactions | Quick interaction check |
| `mcp__clay__getUpcomingReminders` | Pending reminders | Morning briefing, boot |
| `mcp__clay__getRecentReminders` | Past reminders | Review follow-through |
| `mcp__clay__find_duplicates` | Find duplicate contacts | Weekly hygiene |
| `mcp__clay__merge_contacts` | Merge duplicates (destructive) | Only with explicit approval |

### Integration Rules

1. **Auto-lookup on person mention**: When any agent encounters a person by name, search Clay for context before proceeding. This enriches meeting prep, email drafts, and 1:1 prep automatically.
2. **Post-meeting capture**: After meetings or events, offer to create/update Clay contacts with notes and follow-up reminders.
3. **Morning briefing**: Check upcoming reminders and birthdays (next 7 days) during `/chief-morning` and `/boot`.
4. **Relationship warmth**: Use `last_interaction_date` and email/event counts to assess how warm or cold a relationship is. Flag contacts going cold (60+ days no interaction) during relevant prep.
5. **Never replace CRM**: Clay tracks personal relationships. Dynamics tracks pipeline and revenue. They serve different purposes.
6. **Duplicate hygiene**: Run `find_duplicates` during weekly reviews. Merge only with David's approval.

## OmniFocus Conventions

- **Person tags** (e.g., Ilse, Bethany): Task has been delegated to that person or is a follow-up with them. These are *waiting-on* items, not David's direct work.
- **Inbox**: Unprocessed captures. Jarvis triages via `/process-inbox`.

## Jarvis Bridge Protocol

Two Jarvis instances collaborate via a file-based message queue in `bridge/`.

| Instance | Capabilities |
|----------|-------------|
| **Code** (terminal) | Bash, osascript, OmniFocus, git, Obsidian MCP, Mac Mail drafts |
| **Desktop** (Claude Desktop) | M365 MCP (email, calendar, Teams), filesystem |

- Messages drop into `bridge/inbox/`, get processed, move to `bridge/done/`
- Auto-routing: each instance recognizes when a request is outside its capability and queues it for the other
- Operations: `/bridge-send`, `/bridge-check`, `/bridge-status`
- Full spec: `bridge/README.md`
- Desktop instructions: `bridge/DESKTOP.md`

## Data Flow

```
Ideas / Inputs
    |
    v
OmniFocus Inbox  <-- Jarvis (Code) captures here
    |
    v
/process-inbox  <-- Jarvis (Code) triages
    |
    +---> Decisions --> decisions/ folder
    +---> Projects --> OmniFocus projects + projects/ folder
    +---> Delegations --> delegations/tracker.md
    +---> Quick actions --> Today's priorities
    +---> Reference --> context/ files or Obsidian vault
    +---> Delete --> Gone

Cross-Instance Requests
    |
    v
bridge/inbox/  <-- Either instance creates requests here
    |
    v
Receiving instance processes on /bridge-check or boot
    |
    v
bridge/done/  <-- Completed requests archived
```

## Ilse Perez (Human Integration)

- **Channel**: Teams message, text, or email
- **Capability**: Very capable. Needs direction on prioritization.
- **Jarvis role**: Draft priorities and action items for Ilse. David sends them.
- **Common asks**: Calendar management, follow-up coordination, meeting logistics

## Key File Locations

- **One Texas deck**: `~/Library/CloudStorage/OneDrive-Improving/Presentations/One Texas/One Texas.pptx`
- **Lifebook & Faith deck**: `~/Library/CloudStorage/OneDrive-Improving/Presentations/Lifebook & Faith.pptx`
- **Obsidian vault**: Accessible via MCP (Mind/, Projects/, Archive/, Remarkable/)
- **my-os system**: `/Users/davidohara/develop/my-os/`
