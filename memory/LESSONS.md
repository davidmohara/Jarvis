# Global Lessons

Entries are added by the dream cycle when a pattern of constraint violations
is detected (same error category 3+ times in 30 days).

---
<!-- Format:
## {YYYY-MM-DD} — {Pattern Title}
Detected: {N} occurrences over {X} days
Category: {error category from error-log.json}
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
