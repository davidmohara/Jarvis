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
| Jarvis Bridge | Code-Desktop task handoff | File queue in `bridge/` |
| Phone / Texts | Quick communication | Not accessible by Jarvis |

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
