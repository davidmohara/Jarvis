# Global Lessons

Entries are added by the dream cycle when a pattern of constraint violations
is detected (same error category 3+ times in 30 days).

---
<!-- Format:
## {YYYY-MM-DD} — {Pattern Title}
Detected: {N} occurrences over {X} days
Category: {error category from systems/error-tracking/entries/}
Pattern: {What keeps happening}
Fix: {What agents should do differently}
Status: active | resolved
-->

## 2026-04-18 — Chronic Routing Bypass
Detected: 15 occurrences over 28 days
Category: routing-error
Pattern: Jarvis repeatedly executes agent-owned work directly instead of dispatching to the owning agent (Harper for prep sheets, Knox for Plaud/reMarkable, Rigby for system evolution, Chase for card operations). This is the single most frequent error category and has been flagged as "chronic" since the fifth occurrence on March 24.
Fix: Any task matching an agent's portfolio triggers immediate dispatch to that agent. Jarvis coordinates and provides inputs; agents execute. No exceptions. If no agent owns the task, Jarvis executes but logs the gap for Quinn's weekly review.
Status: active

## 2026-04-18 — Tool Misuse Across Agents
Detected: 11 occurrences over 28 days
Category: tool-misuse
Pattern: Agents use wrong tools or wrong tool parameters: Apple Mail instead of M365 for Outlook, incorrect portal URLs for card walkthroughs, open_url instead of click-navigation on authenticated portals, Slack MCP (posts as David) instead of master-slack skill (posts as bot), improvised AppleScript instead of established agent scripts.
Fix: Before using any tool, verify: (1) correct tool for the platform (M365 for Outlook, master-slack for bot messages), (2) correct parameters from config files (portal URLs from card-registry.json), (3) correct navigation method for context (clicks on authenticated pages, open_url only for initial domain jumps). Never improvise tool calls when established patterns exist.
Status: active

## 2026-04-18 — Wrong Assumptions Leading to Bad Diagnoses
Detected: 10 occurrences over 28 days
Category: wrong-assumption
Pattern: Agents assume instead of checking: guessing meeting purpose (sales framing for a peer lunch), diagnosing API failures without reading the error (Plaud quota exhaustion misdiagnosed as audio upload issue), treating dead leads as actionable, proposing local solutions for problems the upstream tool already solves, building static config when live queries are available.
Fix: Check before assuming. For meetings: ask purpose first. For API errors: read the actual error response and check account-level issues (quota, subscription) before debugging parameters. For data: verify current state (sent items, attendee lists, lead status) before surfacing items as actionable.
Status: active

## 2026-04-18 — Data Accuracy Failures in Briefings
Detected: 11 occurrences over 28 days
Category: data-accuracy
Pattern: Morning briefings and prep sheets contain incorrect information: wrong company revenue ($100M vs $300M), wrong meeting accounts (Houston accounts in Dallas follow-up), stale task status (flagging completed items as overdue), incorrect speaker identifications, wrong benefit enrollment status from marketing displays instead of activity logs.
Fix: Cross-reference before presenting: check sent items for email tasks, check attendee lists for meetings, use identity files for company facts, read activity logs not summary displays for status. Never present unverified data as fact in a briefing.
Status: active

## 2026-04-18 — Process Skip on Boot Sequence
Detected: 8 occurrences over 28 days
Category: process-skip
Pattern: Boot sequence is truncated or improvised: skipping Plaud pull, skipping parallel agent dispatches, not logging corrections immediately, not completing speaker tagging after transcript processing. The full chief-morning workflow exists but keeps getting partially executed.
Fix: Boot is non-negotiable and must follow the full workflow. Error logging happens in the same response as correction receipt. Speaker tagging completes before marking a recording as processed. No partial execution.
Status: active

## 2026-04-18 — Format and Voice Violations
Detected: 5 occurrences over 28 days
Category: format-violation
Pattern: Em-dashes used despite explicit ban. Heavy formatting (bold headers, bullet-heavy structure) in emails that should be conversational prose. Files saved to wrong directories. reMarkable uploads with ugly filenames instead of clean labels. Cron syntax shown to executive instead of plain English.
Fix: All output to David must be executive-grade conversational prose. No em-dashes ever. reMarkable filenames are clean labels. Files go in correct subdirectories. When a tool can be invoked directly, invoke it rather than showing config format.

## 2026-04-26 — Missed Context in Prep and Briefings
Detected: 5 occurrences over 31 days
Category: missed-context
Pattern: Agents build prep sheets and briefings from incomplete data sources. Scott McMichael 1:1 prep used only email, missing Obsidian scorecard data. Monday check-in drafted from wrong source thread. Plaud speaker mappings asked of David despite calendar data being available. Agent capabilities unknown despite being fully spec'd in the system. Microsoft meetings at Irving campus missed in 1:1 prep.
Fix: Before building any prep sheet or briefing, enumerate ALL relevant data sources (Obsidian, email, calendar, Plaud transcripts, agent specs, CRM) and pull from each. Do not present partial-source output as complete. When calendar shows a meeting with known attendees, use that to resolve speaker IDs before asking David.
Status: active

## 2026-04-26 — Speaker Misidentification in Transcripts
Detected: 3 occurrences over 1 day
Category: misidentification
Pattern: Plaud transcript speaker identification repeatedly guesses wrong people. Speaker 7, 9, and 10 all incorrectly identified in the same session (Houston SKO recordings). Inferences based on YPO knowledge or name matching rather than cross-referencing calendar attendees, meeting context, and voice patterns from prior transcripts.
Fix: Speaker identification must follow a strict pipeline: (1) match calendar attendees for the recording's time window, (2) cross-reference with prior confirmed speaker IDs from the same event, (3) use content clues (role, company mentions) to narrow. Never guess from general knowledge. If confidence is below 80%, present as "unresolved" rather than proposing a wrong name.
Status: active

## 2026-06-03 — Surfacing Already-Resolved Items
Detected: 3 occurrences over 30 days
Category: assumption-error/surfaced-resolved-item
Pattern: Briefings repeatedly flag items that David has already resolved or that are tracked elsewhere as if they were live problems. Examples: TopGolf SOW flagged overdue when staffing is underway; PGA Tour tickets flagged overdue for the third time despite purchase confirmed twice; dream cycle flagged stale when it is running on another machine. The common thread is taking a tracker's status at face value without checking the latest signal (sent email, prior session confirmation, off-host execution).
Fix: Before surfacing any item as overdue, stale, or actionable: (1) check the agent's own prior session notes for a resolution confirmation, (2) check sent items / DM history for the task's outcome, (3) verify the task isn't owned outside the local system (other machine, other person). When David has confirmed completion in any prior session, treat the item as closed until new evidence reopens it. Never re-surface the same resolved item across sessions.
Status: active


## 2026-06-12 — Routing Error Pattern
Detected: 5 occurrences over 30 days
Category: routing-error
Pattern: Recurring routing-error errors logged across agents
Fix: Review systems/error-tracking entries with category=routing-error; tighten the relevant agent's guardrails
Status: active


## 2026-06-12 — Assumption Error Pattern
Detected: 6 occurrences over 30 days
Category: assumption-error
Pattern: Recurring assumption-error errors logged across agents
Fix: Review systems/error-tracking entries with category=assumption-error; tighten the relevant agent's guardrails
Status: active


## 2026-06-12 — Format Violation Pattern
Detected: 4 occurrences over 30 days
Category: format-violation
Pattern: Recurring format-violation errors logged across agents
Fix: Review systems/error-tracking entries with category=format-violation; tighten the relevant agent's guardrails
Status: active


## 2026-06-17 — Process Skip
Detected: 12 occurrences over 30 days
Category: process-skip
Pattern: protocol-skip
Fix: review recent corrections under this category and update agent runbooks
Status: active


## 2026-06-17 — Routing Error
Detected: 6 occurrences over 30 days
Category: routing-error
Pattern: protocol-skip
Fix: review recent corrections under this category and update agent runbooks
Status: active


## 2026-06-18 — process-skip / protocol-skip
Detected: 12 occurrences over 30 days
Category: process-skip
Pattern: Repeated process-skip errors with failure mode `protocol-skip`.
Fix: Review recent corrections in this category; tighten the relevant skill or rule.
Status: active


## 2026-06-18 — routing-error / protocol-skip
Detected: 6 occurrences over 30 days
Category: routing-error
Pattern: Repeated routing-error errors with failure mode `protocol-skip`.
Fix: Review recent corrections in this category; tighten the relevant skill or rule.
Status: active


## 2026-06-18 — assumption-error / surfaced-resolved-item
Detected: 3 occurrences over 30 days
Category: assumption-error
Pattern: Repeated assumption-error errors with failure mode `surfaced-resolved-item`.
Fix: Review recent corrections in this category; tighten the relevant skill or rule.
Status: active


## 2026-06-18 — tool-misuse / wrong-assumption
Detected: 3 occurrences over 30 days
Category: tool-misuse
Pattern: Repeated tool-misuse errors with failure mode `wrong-assumption`.
Fix: Review recent corrections in this category; tighten the relevant skill or rule.
Status: active

## 2026-06-19 — process-skip / protocol-skip
Detected: 11 occurrences in last 30 days (category total: 14)
Category: process-skip
Failure mode: protocol-skip
Pattern: Recurring process-skip errors via protocol-skip — surfaced by dream-cycle threshold check.
Fix: Review category process-skip entries in systems/error-tracking/entries/ and apply tier-1 (data) or tier-2 (assertion) remediation. Route to Rigby for tier-3.
Status: active

## 2026-06-19 — routing-error / protocol-skip
Detected: 6 occurrences in last 30 days (category total: 7)
Category: routing-error
Failure mode: protocol-skip
Pattern: Recurring routing-error errors via protocol-skip — surfaced by dream-cycle threshold check.
Fix: Review category routing-error entries in systems/error-tracking/entries/ and apply tier-1 (data) or tier-2 (assertion) remediation. Route to Rigby for tier-3.
Status: active

## 2026-06-19 — tool-misuse / wrong-assumption
Detected: 3 occurrences in last 30 days (category total: 6)
Category: tool-misuse
Failure mode: wrong-assumption
Pattern: Recurring tool-misuse errors via wrong-assumption — surfaced by dream-cycle threshold check.
Fix: Review category tool-misuse entries in systems/error-tracking/entries/ and apply tier-1 (data) or tier-2 (assertion) remediation. Route to Rigby for tier-3.
Status: active
