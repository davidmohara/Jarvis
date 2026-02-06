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
| Phone / Texts | Quick communication | Not accessible by Jarvis |

## Data Flow

```
Ideas / Inputs
    |
    v
OmniFocus Inbox  <-- Jarvis captures here
    |
    v
/process-inbox  <-- Jarvis triages
    |
    +---> Decisions --> decisions/ folder
    +---> Projects --> OmniFocus projects + projects/ folder
    +---> Delegations --> delegations/tracker.md
    +---> Quick actions --> Today's priorities
    +---> Reference --> context/ files or Obsidian vault
    +---> Delete --> Gone
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
