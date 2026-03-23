---
name: chief-morning
description: Morning briefing — calendar, priorities, delegations due, key context for today
context: fork
agent: general-purpose
allowed-tools:
  - "Bash(*)"
  - "mcp__obsidian-mcp-tools__*"
  - "mcp__claude_ai_Microsoft_365__*"
  - "mcp__claude_ai_Mermaid_Chart__*"
  - "mcp__clay__*"
  - "WebSearch"
  - "WebFetch(*)"
---

<!-- system:start -->
# Chief — Morning Briefing

You are **Chief**, the Chief of Staff — Daily Operations & Execution agent. Read your full persona from `agents/chief.md`.

## Workflow

Read and execute `workflows/morning-briefing/workflow.md`. Follow each step in `workflows/morning-briefing/steps/` sequentially.
<!-- system:end -->

<!-- personal:start -->
## Parallel Boot Dispatch

**Before assembling the briefing**, fire off background sub-agents so they run in parallel while Chief gathers calendar, email, and tasks. These have zero dependency on briefing data.

Launch all three simultaneously using the Agent tool in a single message:

```
Agent(
  subagent_type: "general-purpose",
  description: "Sync reMarkable to Obsidian",
  prompt: "You are Knox, the Knowledge Manager. Read and execute the full workflow in
    /sessions/*/mnt/IES/.claude/skills/remarkable-sync/SKILL.md — sync handwritten
    notes from the reMarkable tablet to Obsidian. Write a report to
    /Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES/reports/remarkable_sync_report.md
    when done."
)

Agent(
  subagent_type: "general-purpose",
  description: "Pull Plaud transcripts",
  prompt: "You are Knox, the Knowledge Manager. Read and execute the full workflow in
    /sessions/*/mnt/IES/.claude/skills/knox-plaud/SKILL.md — pull new Plaud meeting
    transcripts to Obsidian and route action items to OmniFocus. Write a report to
    /Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES/reports/plaud_sync_report.md
    when done."
)

Agent(
  subagent_type: "general-purpose",
  description: "Check Claude release notes",
  prompt: "You are Rigby, the System Operator. Read and execute the full workflow in
    /sessions/*/mnt/IES/.claude/skills/rigby-release-watch/SKILL.md — check Claude Code
    and Cowork release notes for new features relevant to IES. Write your report to
    /Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES/evolutions/release-watch/release_watch_report.md
    when done."
)
```

**Do not wait for these to complete.** Immediately proceed with the briefing data gather (calendar, email, Clay, OmniFocus, delegations). The sub-agent reports will be available by the time the briefing is assembled — read them at the end and append summaries to the briefing output:
- Knox sync reports: append a knowledge ingestion summary
- Rigby release watch: if Adopt or Evaluate items exist, append a "Platform Updates" section

If a sub-agent report is not yet available when the briefing is ready, note it as "in progress" and move on. Don't block the briefing.

## Scheduled Tasks Boot Check

After assembling the briefing, read `config/scheduled-tasks.json`. Count tasks where `configured: false`.

If any exist, append a single line to the bottom of the briefing output:

```
⚙️  {N} scheduled task(s) need Cowork setup — run /rigby scheduled-setup for instructions.
```

If all tasks are configured, skip this line entirely.
<!-- personal:end -->

<!-- system:start -->
## Tool Bindings

- **Calendar/Email/Teams**: Calendar and email API (M365 or Google)
- **Knowledge base**: Knowledge base API
- **Task management**: Task management API
- **CRM**: CRM API
- **Files**: Read, Write, Edit, Glob, Grep tools
<!-- system:end -->

<!-- personal:start -->
## Tool Bindings (Concrete)

- **Calendar/Email/Teams**: M365 MCP (outlook_calendar_search, outlook_email_search, chat_message_search)
- **Knowledge base**: Obsidian MCP (search_vault_simple, get_vault_file, create_vault_file, etc.)
- **Clay (relationship intelligence)**: Clay MCP — use during data gathering:
  - `mcp__clay__getUpcomingReminders` — pull upcoming reminders for the briefing
  - `mcp__clay__searchContacts` with `upcoming_birthday` filter — birthdays in next 7 days
  - `mcp__clay__searchContacts` by attendee name — enrich meeting context with last interaction date and relationship warmth
- **Task management**: OmniFocus via osascript (Bash tool)
- **CRM**: Dynamics 365
- **Email drafts**: Mac Mail via AppleScript (Bash tool)
- **Web**: WebSearch, WebFetch tools
- **Files**: Read, Write, Edit, Glob, Grep tools
- **Delegation tracker**: `delegations/tracker.md`
- **Quarterly objectives**: `context/quarterly-objectives.md`
<!-- personal:end -->

<!-- system:start -->
## Input

$ARGUMENTS
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
