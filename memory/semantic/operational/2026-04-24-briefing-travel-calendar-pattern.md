---
type: semantic
domain: operational
tags: [briefing, calendar, omnifocus, google-next, travel, overdue-tasks, leads]
confidence: medium
created: 2026-04-24
last-updated: 2026-04-25
synthesized-from:
  - memory/episodic/2026-04-20-morning-briefing.md
  - memory/episodic/2026-04-21-morning-briefing.md
  - memory/episodic/2026-04-20-afternoon-boot.md
  - memory/episodic/2026-04-22-morning-briefing-google-next.md
  - memory/episodic/2026-04-23-morning-briefing-midnight.md
  - memory/episodic/2026-04-23-morning-briefing-scheduled.md
---

# Pattern: Morning Briefings Consistently Flag Travel-Calendar Conflicts

## Pattern Summary

Morning briefings across the entire Google Next week (Apr 20-23) repeatedly surface the same pattern: travel events (Google Next Las Vegas, AA flights) create cascading calendar conflicts with recurring internal meetings, and the system detects these but the response gap persists. OmniFocus timeouts compound the problem — when task data is unavailable during travel weeks, the briefing loses half its value. Additionally, overdue tasks and unassigned leads accumulate during travel with no mechanism to delegate or triage them in David's absence.

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
5. **Overdue tasks compound during travel.** "Build Economy deck" reached 2 weeks overdue, Jack Nelson/Mainsail hit 12 days — these were flagged daily but never escalated or rescheduled. The system needs a "travel mode" that either auto-extends deadlines or escalates to EA/delegate.
6. **Lead tracker goes dark during travel.** 5 unassigned leads surfaced on Apr 23 (including Alcon at 364 days old) — no one was available to route them. Lead review during travel weeks should auto-flag for Alice or the assigned AM rather than waiting for David's return.

## Evidence

### Apr 20 Afternoon Boot (NEW — 2026-04-25 dream cycle)
- Second boot at 5:25 PM CDT. 46 active tasks, 8 due at 8 PM (2h35m away — too many to close)
- Vicki retirement party vs. Vegas team dinner conflict flagged
- 6 overdue items, Google follow-ups 16 days cold
- Co-sell at $1.1M of $15M (7.5%) — critical gap, but no bandwidth to address during event-heavy day

### Apr 22 Morning Briefing — Google Next Travel Day (NEW — 2026-04-25 dream cycle)
- Travel day: AA 783 DFW→LAS departs 9:31 AM CDT
- OmniFocus MCP FAILED — timed out x2, task data unavailable
- Afternoon recurring meetings (Sales & Recruiting, Scrum, etc.) all tentative and conflict with flight
- 72-hour look-ahead: Apr 24 return flight conflicts with 4th Friday Exec + Presidents Pipeline + Alice wrap-up

### Apr 23 Morning Briefing — Google Next Day 2, Midnight Run (NEW — 2026-04-25 dream cycle)
- OmniFocus: 38 tasks, inbox at 205+ items (bloated, stale). "Build Economy deck" 2 weeks overdue.
- 5 unassigned leads in tracker (Alcon 364 days old, AECom, IFS, Cardinal IT, Paragon, Birgo)
- Ethel Mangum (7-Eleven) needs link resend — time-sensitive, unactioned
- Temporal/Improving touchbase and Google NEXT sync with Mladen Raickovic scheduled

### Apr 23 Morning Briefing — Google Next Day 2, Scheduled 6:11 AM (NEW — 2026-04-25 dream cycle)
- OmniFocus MCP timed out 3x; fell back to osascript — 200+ inbox items confirmed
- Same 5 unassigned leads surfaced again
- Cyber Security Training deadline Apr 30 — flagged but not acted on
- Cote du Coeur Saturday — no details on calendar despite being 2 days out
