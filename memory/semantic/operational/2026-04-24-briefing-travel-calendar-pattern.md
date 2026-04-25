---
type: semantic
domain: operational
tags: [briefing, calendar, omnifocus, google-next, travel]
confidence: low
created: 2026-04-24
last-updated: 2026-04-24
synthesized-from:
  - memory/episodic/2026-04-20-morning-briefing.md
  - memory/episodic/2026-04-21-morning-briefing.md
---

# Pattern: Morning Briefings Consistently Flag Travel-Calendar Conflicts

## Pattern Summary

Morning briefings across multiple days (Apr 20-22) repeatedly surface the same pattern: travel events (Google Next Las Vegas, AA flights) create cascading calendar conflicts with recurring internal meetings, and the system detects these but the response gap persists. OmniFocus timeouts compound the problem — when task data is unavailable during travel weeks, the briefing loses half its value.

## Evidence

### Apr 20 Morning Briefing
- Google Next travel Wed Apr 22 flagged 2 days ahead
- Cowboys Club CEO Event conflicted with recurring standups
- 6 overdue items, Google follow-ups 16 days cold
- OmniFocus operational (48 tasks)

### Apr 21 Morning Briefing  
- Google Next flagged again — no prep brief detected despite being next day
- Scott Pine email needed same-day response before departure — unread
- OmniFocus timed out (2x) — unavailable
- Google Cloud Next badge confirmation unread
- Sharp edges: prep gap persisted from previous day's warning

## Implications

1. **Travel prep needs a dedicated workflow, not just a briefing flag.** The briefing surfaced Google Next as a gap on Apr 20, and again on Apr 21, but no prep brief was created. Flagging is not fixing.
2. **OmniFocus reliability during scheduled runs is poor.** Timeouts on Apr 21, 22, 23 suggest the MCP server or Mac availability is inconsistent in VM/automated mode. Fallback to osascript should be automatic, not manual.
3. **Recurring meetings during travel weeks should be auto-declined or tentative-marked.** The system detects conflicts but doesn't act on them — David has to manually handle each one.
4. **Pre-departure checklist pattern:** For any multi-day travel event, the system should verify 48 hours before: (a) prep brief exists, (b) logistics confirmed, (c) unanswered emails from event contacts resolved, (d) recurring meetings marked tentative/declined.
