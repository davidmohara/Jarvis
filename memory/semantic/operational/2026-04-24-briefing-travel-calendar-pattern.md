---
type: semantic
domain: operational
tags: [briefing, calendar, omnifocus, google-next, travel, overdue-tasks, leads]
confidence: high
created: 2026-04-24
last-updated: 2026-05-02
synthesized-from:
  - memory/episodic/2026-04-20-morning-briefing.md
  - memory/episodic/2026-04-21-morning-briefing.md
  - memory/episodic/2026-04-20-afternoon-boot.md
  - memory/episodic/2026-04-22-morning-briefing-google-next.md
  - memory/episodic/2026-04-23-morning-briefing-midnight.md
  - memory/episodic/2026-04-23-morning-briefing-scheduled.md
  - memory/episodic/2026-04-24-morning-briefing.md
  - memory/episodic/2026-04-27-morning-briefing.md
  - memory/episodic/2026-04-28-morning-briefing.md
  - memory/episodic/2026-04-26-morning-briefing-glc-travel.md
  - memory/episodic/2026-04-29-morning-briefing-glc-day4.md
  - memory/episodic/2026-04-30-morning-briefing.md
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

### Apr 24 Morning Briefing — Return Day, Final Google Next Day (NEW — 2026-04-27 dream cycle)
- OmniFocus timed out again (3 attempts, 60s each) — 4th consecutive day of task data unavailability during travel week
- AA 783 LAS to DFW departs 1:25 PM CDT — back-to-back cluster (9:15/9:30/10:00) leaves zero buffer
- Alice Wrap-Up at 12:00 PM directly conflicts with airport departure — flagged but no rescheduling action taken by system
- Lead tracker workflow directory missing entirely — lead review not just stale but structurally broken
- Q2 Cyber Security Training deadline 6 days out, still unflagged as action item
- 72-hour look-ahead surfaced yet another flight (DFW to ORD, YPO GLC Chicago) two days out — pattern of back-to-back travel weeks with no recovery buffer
- Quarterly rocks: Rock 1 and Rock 2 still "Not Started" — travel week consumed all bandwidth

## Implications

7. **OmniFocus failure is now systemic, not intermittent.** Four consecutive travel-day briefings (Apr 21-24) had OmniFocus unavailable. The MCP server cannot be relied upon during automated/scheduled runs. The osascript fallback should be the primary path for scheduled tasks, with MCP as the upgrade path.
8. **Alice Wrap-Up scheduling conflict was detected but not resolved.** The system flagged the 12:00 PM meeting vs. airport departure but took no action (no reschedule suggestion, no message to Alice). Detection without action is the core failure mode of this pattern.
9. **Lead tracker infrastructure gap.** The workflow directory was missing entirely on Apr 24 — not a timeout or connectivity issue but a structural gap. Lead review needs a pre-flight check that the workflow exists before attempting to run it.

### Apr 27 Morning Briefing — GLC Chicago Day 1 (NEW — 2026-04-30 dream cycle)
- GLC Chicago at Hyatt Regency. Regional Officers Workshop full day (9 AM-4:30 PM).
- Fab Con Planning and Alice Kick-Off Call both at 4:30 PM CDT — schedule conflict flagged but not resolved.
- OmniFocus failed 3x again — 5th consecutive multi-day travel period with task data unavailable.
- 72-hour look-ahead: Thursday Apr 30 AA 1693 ORD→DFW (9:45 AM) conflicts with AI Mastermind (9:30 AM), DRC Debrief (9:00 AM), and multiple morning meetings. Critical cluster.
- One Texas Sales Update (Rock 2, 3:00 PM Thu) flagged as must-attend — first formal Rock 2 rhythm meeting.
- 4 unassigned leads persisting (Alcon now 368 days, AECom, IFS, Cardinal IT).
- DRC Intelligence OS v2 talk (May 21) 24 days out with no prep visible. Forbes article (Rock 3) still no activity.

### Apr 28 Morning Briefing — GLC Chicago Day 2 (NEW — 2026-04-30 dream cycle)
- 4 events: Devlin 1:1, Google Next follow-up sync, Tim Rayburn 1:1. Light day relative to GLC schedule.
- OmniFocus failed 3x — 6th consecutive travel day with no task data. Pattern now spans two separate trips (Google Next + GLC Chicago).
- Thursday flight conflict still unresolved from previous day's briefing. Same AI Mastermind / DRC / flight cluster flagged again.
- Howard Dierking (Capital One) replied wanting lunch — timing perfect. Ehren forwarded Google contact "Mick" for Dallas synergy. Both actionable but no mechanism to capture during travel.
- DRC Executive AI Workshop (May 21) registration problem surfaced via David Belcher email — new operational risk.
- Lead tracker still missing from workspace. Plaud inaccessible from VM.

## Implications (continued — 2026-04-30)

10. **The pattern extends beyond Google Next to GLC Chicago.** The same failure modes (OmniFocus timeout, unresolved calendar conflicts, lead tracker unavailable, actionable emails accumulating without capture) reproduced identically during a second consecutive travel trip. This is not event-specific — it is a structural travel-mode gap.
11. **Rock 2 milestone meeting (One Texas Sales Update, Apr 30) is at risk.** Flagged in two consecutive briefings as must-attend but David is flying ORD→DFW that morning. The system detected this but generated no mitigation action (no dial-in link verification, no "join from airport" plan).
12. **Actionable relationship opportunities decay during travel.** Howard Dierking (Capital One) and "Mick" (Google/Dallas) are both time-sensitive relationship signals that need capture within 24-48 hours. The briefing surfaced them but there is no delegation pathway to Alice or a CRM to log them for follow-up post-travel.

### Apr 26 Morning Briefing — GLC Travel Day (NEW — 2026-05-01 dream cycle)
- Sunday travel day. AA 2896 DFW→ORD departed 8:49 AM CDT. Boot ran at 4:38 PM when David was already in Chicago.
- Frontera Grill dinner 6:30 PM. Full GLC week ahead: Apr 27-29 conference, Apr 30 return + stacked meetings, May 1 exec day, May 2 golf + Make a Wish gala.
- Thursday Apr 30 flagged as brutal: return flight + Dallas Town Hall + One Texas Sales Update + IDSC Kickoff all stacked. This is the 3rd consecutive briefing to flag this day as critical.
- 37 OmniFocus tasks, most unassigned to projects. 9 Kare Devices tasks all overdue (due Apr 25). Inbox at 205 items — unchanged from Google Next week.
- Unknown context for 3 upcoming meetings: Devlin catch-up (Tue), SMU collaboration (Wed), McCabe call (Fri). No prep initiated.

### Apr 29 Morning Briefing — GLC Day 4, Final Day (NEW — 2026-05-01 dream cycle)
- 4 meetings: Sales Scrum (tentative), US Town Hall (tentative), David/Robyn 1:1, SMU Collaboration.
- Thursday flight conflict STILL unresolved: AA 1693 departs ORD 9:45 AM, 4 morning meetings conflict. One Texas Sales Update (3 PM) must be preserved — Rock 2 milestone. Decision needed before boarding but no mechanism to force it.
- Cyber training deadline Apr 30 for Don McGreal and Robyn Fuentes — both not started. InfoSecIQ notifications received. Flagged for Alice delegation but no action taken.
- SMU Collaboration (3 PM) with Aren Cambre — AI for Business program partnership first touch. No prior context in episodic memory.
- Jarvis inbox: "Project Profitability" email with attachment (Apr 26) still unprocessed after 3 days.
- OmniFocus failed again (2 timeouts) — 7th travel day in a row across two trips with no task data.

## Implications (continued — 2026-05-01)

13. **The flight-conflict pattern now has a completion data point.** Apr 30 (the day that was flagged across 4+ briefings) has now passed. The system should check in the next boot whether the One Texas Sales Update actually happened, whether the flight conflict was resolved, and what was lost. This is the first pattern that can be validated against outcomes, not just flagged as risk.
14. **Cyber training compliance deadlines were flagged but not actioned across 3 consecutive briefings.** Don McGreal and Robyn Fuentes had an Apr 30 deadline. The system surfaced this on Apr 22, Apr 29, and in between — but never escalated beyond "flagged for Alice." Compliance deadlines need an automatic escalation path with countdown pressure, not passive flagging.
15. **Meeting prep gap is widening.** Three meetings on the GLC week (Devlin, SMU, McCabe) had "context unknown" flagged but no prep was initiated despite 2-5 days of lead time. The pre-departure checklist (Implication #4) would have caught this if it existed.

### Apr 30 Morning Briefing — Return Day from GLC (NEW — 2026-05-02 dream cycle)
- Return day. AA 1693 ORD to DFW departs 9:45 AM CDT, conflicting with AI Mastermind (9:30 AM), DRC Debrief (9:00 AM), Sales Scrum (10:00 AM). The conflict flagged across 4+ consecutive briefings finally arrived.
- One Texas Sales Update at 3:00 PM (Rock 2 milestone, first monthly sync) flagged as must-attend.
- OmniFocus timed out 3x — 8th travel day in this streak with no task data.
- Jarvis inbox: "Project Profitability" email with attachment unprocessed since Apr 26 (now 4 days stale). No delegation pathway existed.
- YPO RBM receipts due COB same day — first time a hard external deadline landed on a travel return day.
- Dustin Shaffer intro (Arborstone Capital) and Devlin/Blake AI training thread both actionable but surfaced into a day with zero bandwidth.
- 72-hour look-ahead: Scott McMichael Q1 close-out (May 1), Make-A-Wish Gala (May 2, black tie), golf (May 2 AM). Recovery window is minimal.
- Daily review gap: last review was Apr 28 — 2 days of accountability gap during travel.

## Implications (continued — 2026-05-02)

16. **The Apr 30 flight conflict is now a past event and can be validated.** This is the first instance where the pattern's predicted risk has materialized and passed. The next boot should confirm: did the One Texas Sales Update happen? Were the conflicting morning meetings missed, declined, or handled via mobile? This outcome data is critical for calibrating future risk severity.
17. **External deadlines on travel return days are a new risk category.** YPO RBM receipts were due COB on the same day as the ORD-DFW return. The system had no mechanism to pre-complete this or escalate it before departure. Hard external deadlines within 24 hours of a return flight need to be surfaced at the pre-departure stage, not on the day itself.
18. **Jarvis inbox items decay without a processing pathway.** The "Project Profitability" email sat for 4 days with no processing because it required Chase-level analysis and attachment review — capabilities unavailable in automated mode. Items that need specific agent capabilities should be auto-routed to the next live session rather than carrying forward in each briefing as an unactionable flag.
