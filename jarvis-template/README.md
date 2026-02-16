# Jarvis — Executive AI Operating System

## What This Is

Jarvis is an AI-powered executive assistant that runs inside Claude Desktop (Cowork mode). It functions as a chief of staff: triaging email, prepping meetings, tracking delegations, protecting your calendar, managing reviews, and closing the gap between decisions and execution.

## Quick Start

1. **Copy this entire `jarvis-template/` folder** to your Claude Desktop workspace as `my-os/`
2. **Fill in the identity files** in `identity/`:
   - `MEMORY.md` — Your personal details, family, preferences, key dates, travel info
   - `GOALS_AND_DREAMS.md` — Your business targets and personal visions
   - `RESPONSIBILITIES.md` — Your role, cadences, what you own
   - `MISSION_CONTROL.md` — Your active projects and how you capture thoughts
   - `AUTOMATION.md` — Review and adjust what Jarvis does autonomously vs. with approval
   - `VOICE.md` — Adjust personality/tone if desired (default: direct, anticipatory, dry wit)
3. **Replace all `[BRACKETED PLACEHOLDERS]`** in CLAUDE.md and the identity files with your information
4. **Create the folder structure** (or let Jarvis create them as needed):
   - `context/`, `decisions/`, `projects/`, `people/`, `meetings/`, `delegations/`, `reviews/`, `archive/`, `reference/`
5. **Start a Cowork session** and say "boot" or "good morning" — Jarvis will orient itself

## What Jarvis Does

### Autonomous (no approval needed)
- Captures follow-ups from conversations
- Preps daily briefings
- Flags overdue items and delegations
- Surfaces relevant context when topics come up
- Tracks commitments you make ("I'll do X", "remind me to Y")
- Protects your calendar from conflicts with important dates

### With Your Approval
- Drafts meeting briefs
- Drafts emails and messages
- Creates decision files
- Sends delegation follow-ups

### Never Without Explicit Permission
- Sends messages on your behalf
- Makes commitments or schedules meetings
- Modifies CRM or external systems
- Deletes or archives anything

## Slash Commands

| Command | What It Does |
|---------|-------------|
| `/boot` | Morning briefing — rocks, delegations, what's coming |
| `/capture [text]` | Quick capture — no questions asked |
| `/process-inbox` | Triage all pending items |
| `/decide [topic]` | RAPID decision framework walkthrough |
| `/delegate [task] to [person]` | Hand off and track |
| `/meet [name/topic]` | Meeting prep with context |
| `/review-daily` | End-of-day shutdown |
| `/review-weekly` | Weekly review (most important cadence) |
| `/review-monthly` | Monthly patterns and adjustments |
| `/review-quarterly` | Quarterly rock setting |
| `/prioritize` | Eisenhower matrix against rocks |
| `/status` | Quick dashboard |
| `/find [topic]` | Search all files |
| `/archive [file]` | Move to archive |

## Tools & Integrations

Jarvis works with whatever tools you use. Common setups:

- **Email**: Microsoft 365 connector in Cowork (email search, calendar, Teams)
- **Task management**: Any system — Jarvis adapts. If you don't have one, it uses markdown files.
- **Knowledge base**: Obsidian, Notion, OneNote, SharePoint — or the built-in `context/` folder
- **Mac automation**: AppleScript via osascript for native app control
- **Web**: Search, research, booking — Jarvis uses web tools as needed

## The Execution Gap

This system exists because every executive has one: the gap between deciding and completing. Jarvis closes it by capturing everything, surfacing it daily, prompting relentlessly, and connecting tasks to rocks to vision.

The more you fill in the identity files, the more effective Jarvis becomes. Start with MEMORY.md and MISSION_CONTROL.md — those have the highest immediate impact.

---

*Built by David O'Hara at Improving. Powered by Claude.*
