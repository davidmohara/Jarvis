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
Status: active

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

## 2026-06-20 — Process-Skip / Protocol-Skip
Detected: 13 occurrences over 29 days
Category: process-skip
Pattern: Recurring process-skip due to protocol-skip
Fix: Review related error entries in `systems/error-tracking/entries/` and update protocols
Status: active

## 2026-06-20 — Data-Accuracy / Wrong-Assumption
Detected: 3 occurrences over 25 days
Category: data-accuracy
Pattern: Recurring data-accuracy due to wrong-assumption
Fix: Review related error entries in `systems/error-tracking/entries/` and update protocols
Status: active

## 2026-06-20 — Routing-Error / Protocol-Skip
Detected: 8 occurrences over 26 days
Category: routing-error
Pattern: Recurring routing-error due to protocol-skip
Fix: Review related error entries in `systems/error-tracking/entries/` and update protocols
Status: active

## 2026-06-20 — Tool-Misuse / Wrong-Assumption
Detected: 3 occurrences over 29 days
Category: tool-misuse
Pattern: Recurring tool-misuse due to wrong-assumption
Fix: Review related error entries in `systems/error-tracking/entries/` and update protocols
Status: active

## 2026-06-21 — Process-Skip / protocol-skip
Detected: 13 occurrences in last 30 days
Category: process-skip
Pattern: Recurring protocol skip in the process-skip category.
Fix: Review error entries for this category; tighten the guard in the workflow or skill that owns it.
Status: active

## 2026-06-21 — Data-Accuracy / wrong-assumption
Detected: 3 occurrences in last 30 days
Category: data-accuracy
Pattern: Recurring wrong assumption in the data-accuracy category.
Fix: Review error entries for this category; tighten the guard in the workflow or skill that owns it.
Status: active

## 2026-06-21 — Routing-Error / protocol-skip
Detected: 9 occurrences in last 30 days
Category: routing-error
Pattern: Recurring protocol skip in the routing-error category.
Fix: Review error entries for this category; tighten the guard in the workflow or skill that owns it.
Status: active

## 2026-06-21 — Tool-Misuse / wrong-assumption
Detected: 3 occurrences in last 30 days
Category: tool-misuse
Pattern: Recurring wrong assumption in the tool-misuse category.
Fix: Review error entries for this category; tighten the guard in the workflow or skill that owns it.
Status: active

## 2026-06-22 — data-accuracy / wrong-assumption
Detected: 3 occurrences over 30 days
Category: data-accuracy
Failure mode: wrong-assumption
Pattern: Recurring data-accuracy category errors with failure mode `wrong-assumption`.
Fix: Tighten the guard rail in the relevant agent/workflow. See systems/error-tracking/entries/ for source records.
Status: active


## 2026-06-25 — Hallucination Pattern
Detected: 3 occurrences over 30 days
Category: hallucination
Pattern: Recurring hallucination occurrences across multiple sessions
Fix: Review error entries for hallucination; consider tightening protocols
Status: active

## 2026-06-26 — assumption-error / wrong-assumption
Detected: 3 occurrences in last 30 days
Category: assumption-error
Failure mode: wrong-assumption
Pattern: Recurring assumption-error category errors with failure mode `wrong-assumption` — surfaced by dream-cycle threshold check.
Fix: Review category assumption-error entries in `systems/error-tracking/entries/` and apply tier-1 (data) or tier-2 (assertion) remediation. Route to Rigby for tier-3.
Status: active

## 2026-06-26 — format-violation / wrong-assumption
Detected: 3 occurrences in last 30 days
Category: format-violation
Failure mode: wrong-assumption
Pattern: Recurring format-violation category errors with failure mode `wrong-assumption` — surfaced by dream-cycle threshold check.
Fix: Review category format-violation entries in `systems/error-tracking/entries/` and apply tier-1 (data) or tier-2 (assertion) remediation. Route to Rigby for tier-3.
Status: active

## 2026-06-26 — format-violation / protocol-skip
Detected: 3 occurrences in last 30 days
Category: format-violation
Failure mode: protocol-skip
Pattern: Recurring format-violation category errors with failure mode `protocol-skip` — surfaced by dream-cycle threshold check.
Fix: Review category format-violation entries in `systems/error-tracking/entries/` and apply tier-1 (data) or tier-2 (assertion) remediation. Route to Rigby for tier-3.
Status: active


## 2026-06-27 — missed-context/context-blindness
Detected: 3 occurrences over 30 days
Category: missed-context
Pattern: Repeated occurrences of `missed-context` with failure mode `context-blindness` across the 30-day window.
Fix: Review category-specific systemic fixes from individual entries in `systems/error-tracking/entries/`. Schedule a Rigby-led pattern-analysis pass if recurrence continues.
Status: active

## 2026-06-28 — Process Skip / Protocol Skip
Detected: 10 occurrences over 30 days
Category: process-skip
Pattern: process-skip/protocol-skip — appearing repeatedly in recent error log
Fix: Review failure mode; tighten protocol or add guardrail. See systems/error-tracking/entries/ for instances.
Status: active

## 2026-06-28 — Routing Error / Protocol Skip
Detected: 7 occurrences over 30 days
Category: routing-error
Pattern: routing-error/protocol-skip — appearing repeatedly in recent error log
Fix: Review failure mode; tighten protocol or add guardrail. See systems/error-tracking/entries/ for instances.
Status: active

## 2026-06-28 — Data Accuracy / Wrong Assumption
Detected: 4 occurrences over 30 days
Category: data-accuracy
Pattern: data-accuracy/wrong-assumption — appearing repeatedly in recent error log
Fix: Review failure mode; tighten protocol or add guardrail. See systems/error-tracking/entries/ for instances.
Status: active

## 2026-06-28 — Assumption Error / Wrong Assumption
Detected: 3 occurrences over 30 days
Category: assumption-error
Pattern: assumption-error/wrong-assumption — appearing repeatedly in recent error log
Fix: Review failure mode; tighten protocol or add guardrail. See systems/error-tracking/entries/ for instances.
Status: active

## 2026-06-28 — Format Violation / Wrong Assumption
Detected: 3 occurrences over 30 days
Category: format-violation
Pattern: format-violation/wrong-assumption — appearing repeatedly in recent error log
Fix: Review failure mode; tighten protocol or add guardrail. See systems/error-tracking/entries/ for instances.
Status: active

## 2026-06-28 — Format Violation / Protocol Skip
Detected: 3 occurrences over 30 days
Category: format-violation
Pattern: format-violation/protocol-skip — appearing repeatedly in recent error log
Fix: Review failure mode; tighten protocol or add guardrail. See systems/error-tracking/entries/ for instances.
Status: active

## 2026-06-29 — unknown/unknown
Detected: 3 occurrences over 30 days
Category: unknown
Pattern: Recurring unknown errors with failure_mode=unknown.
Fix: Review recent error-tracking entries with this signature; codify guardrail in the relevant agent/skill.
Status: active

## 2026-07-02 — Data Interpretation pattern
Detected: 4 occurrences over 30 days
Category: data-interpretation
Pattern: Recurring `data-interpretation` errors observed in the 30-day window ending 2026-07-02.
Fix: Investigate root cause; add guardrail or checklist entry to the responsible agent/skill.
Status: active

## 2026-07-04 — Data Accuracy (sloppy-read)
Detected: 3 occurrences over 30 days
Category: data-accuracy
Pattern: sloppy-read
Fix: Address per systems/error-tracking/entries — see Rigby error analysis.
Status: active



## 2026-07-06 — Hallucination — unverified-inference
Detected: 5 occurrences over 30 days
Category: hallucination
Pattern: unverified-inference
Marker: hallucination/unverified-inference
Fix: Review recurring hallucination/unverified-inference errors; systemic fix required.
Status: active


## 2026-07-06 — Tool Misuse — tool-ignorance
Detected: 14 occurrences over 30 days
Category: tool-misuse
Pattern: tool-ignorance
Marker: tool-misuse/tool-ignorance
Fix: Review recurring tool-misuse/tool-ignorance errors; systemic fix required.
Status: active


## 2026-07-06 — Authentication — pattern-mismatch
Detected: 4 occurrences over 30 days
Category: authentication
Pattern: pattern-mismatch
Marker: authentication/pattern-mismatch
Fix: Review recurring authentication/pattern-mismatch errors; systemic fix required.
Status: active


## 2026-07-06 — Data Interpretation — date-miscalculation
Detected: 5 occurrences over 30 days
Category: data-interpretation
Pattern: date-miscalculation
Marker: data-interpretation/date-miscalculation
Fix: Review recurring data-interpretation/date-miscalculation errors; systemic fix required.
Status: active

## 2026-07-07 — Data Accuracy / sloppy-read
Detected: 4 occurrences in the last 30 days
Category: data-accuracy
Failure mode: sloppy-read
Marker: data-accuracy/sloppy-read
Fix: Investigate root cause; codify a check that prevents this failure mode.
Status: active

## 2026-07-17 — Under-Delivery Pattern
Detected: 3 occurrences over 30 days (window 2026-06-17 to 2026-07-17)
Category: under-delivery
Pattern: Instructions get a "close enough" interpretation instead of literal, complete execution. Examples: asked to remove a byline containing personal information but anonymized it instead of deleting it; checked Plaud only for today's date and declared nothing pending, missing a recording from the prior day; paraphrased condensed bullet summaries instead of copying the actual source slide content verbatim for a QBR deck.
Fix: When an instruction specifies an action (remove, copy verbatim, check a range), execute that literal action rather than a substitute that seems functionally similar. For time-bounded checks (Plaud, inbox), default to a window wide enough to catch spillover from the prior period rather than the single named date. When source content exists verbatim, reuse it directly instead of re-summarizing.
Status: active

## 2026-07-21 — Missed Context / Wrong Assumption
Detected: 3 occurrences over 30 days
Category: missed-context
Failure mode: wrong-assumption
Pattern: Agent proceeds on a wrong assumption about available context rather than failing to pull context at all. Distinct from context-blindness (which is not pulling sources) — here the agent pulls but misreads or misapplies what it finds. Examples: assuming a file path is current when it reflects a prior state, assuming a connector is unavailable without checking deferred tools, assuming a task is complete because a prior step succeeded without verifying the output.
Fix: When a step's result is load-bearing (gate for next action), verify the actual output rather than inferring it from the step's success flag. For paths and states, re-read rather than assuming continuity from a prior read. For tool availability, run ToolSearch before declaring a capability absent.
Status: active

## 2026-07-22 — Missed Context / Lazy Search
Detected: 3 occurrences over 30 days
Category: missed-context
Failure mode: lazy-search
Pattern: Agent declares something not found after a single search attempt instead of exhausting the 3-strategy minimum. Distinct from context-blindness (not knowing to look) and wrong-assumption (misreading what was found) — here the agent looked once, got no result, and stopped. SYSTEM.md explicitly requires 3 different search strategies before declaring not found.
Fix: Follow the Search Discipline rule in SYSTEM.md: minimum 3 search strategies before declaring not found. For files: filename, content keyword, directory browse. For calendar: subject, attendee, date range. For contacts: name, email, organization. State all strategies tried when reporting not found.
Status: active

## 2026-07-28 — Process Skip / Context Blindness
Detected: 3 occurrences over 30 days
Category: process-skip
Failure mode: context-blindness
Pattern: Agent skips a required process step not because of a deliberate shortcut (protocol-skip) but because it failed to recognize that the context called for the step at all. The agent is not ignoring a rule — it is not seeing the trigger. Distinct from protocol-skip (knows the rule, skips it) and lazy-search (looks but not hard enough).
Fix: Before completing any multi-step task, explicitly enumerate required steps from the owning workflow or skill and confirm each was executed. Do not rely on recognition — use checklist verification. When a step is gated on a condition, verify the condition is checked rather than assumed.
Status: active

## 2026-07-28 — Data Accuracy / Protocol Skip
Detected: 3 occurrences over 30 days
Category: data-accuracy
Failure mode: protocol-skip
Pattern: Data inaccuracies arise specifically from skipping a validation or cross-reference step that the protocol requires. Agent presents or acts on data without running the prescribed verification — not because verification failed, but because it was omitted. Examples: presenting briefing data without cross-referencing against sent items, reporting pipeline figures without re-running the filter isolation gate.
Fix: Any data presented in a deliverable must pass the cross-reference step mandated by the owning workflow. Flag unverified data explicitly rather than presenting it as fact. If the verification step cannot be completed, say so rather than omitting it silently.
Status: active

## 2026-08-14 — Lazy Search / Available Data Not Used
Detected: 3 occurrences over 30 days
Category: lazy-search
Failure mode: available-data-not-used
Pattern: Agent performs a search or lookup, gets no result, and declares the data unavailable — without first checking data sources it already has in context or that are directly accessible. Distinct from missed-context/lazy-search (which is about not searching hard enough across strategies) — here the failure is that available data (already pulled, already in session, or trivially accessible via a tool that was loaded) is bypassed in favor of a fresh lookup that fails. The agent treats a search miss as a terminal finding rather than checking existing context first.
Fix: Before declaring any data item unavailable, check: (1) was it already pulled earlier this session? (2) is it in a file already read? (3) is it accessible via a loaded tool without a network call? Exhaust in-session context before issuing external lookups. When a lookup fails, surface what sources WERE checked and what remains.
Status: active

## 2026-08-01 — Under-Delivery / Wrong Assumption
Detected: 3 occurrences over 30 days
Category: under-delivery
Failure mode: wrong-assumption
Pattern: Agent delivers a result based on an incorrect assumption about scope, data, or completion state — and the assumption is never surfaced or checked. Examples: declaring a find-and-remove task complete after checking only one literal string while paraphrased variants remain; treating a sub-agent's completion report as verified fact without spot-checking the output; reporting pipeline figures using stale cached data while assuming it's current. The wrong assumption isn't caught because it's never made explicit — the agent acts as though it knows something it has only inferred.
Fix: Before declaring any multi-part or verification-dependent task complete, explicitly name the assumption being made and confirm it against the actual artifact. For find/remove tasks, grep for synonyms and paraphrases, not just the literal target string. For sub-agent reports, spot-check one claim against the actual file before relaying the report upward. For data freshness, check the cache date and surface it if it exceeds 24 hours.
Status: active

## 2026-08-27 — Tool Misuse / Protocol Skip
Detected: 3 occurrences over 30 days
Category: tool-misuse
Failure mode: protocol-skip
Pattern: A documented skill or protocol exists specifically to handle the situation at hand, but the agent bypasses it — refusing the task and offering an ad-hoc alternative, giving manual instructions instead of following the skill's recovery path, or shipping code that doesn't match its own documented spec. Distinct from tool-misuse/tool-ignorance (not knowing a tool exists) — here the agent knows the skill exists and skips invoking it anyway. Examples: refusing to post to Slack instead of reading master-slack; telling the controller to manually re-register rmapi instead of following remarkable-upload's documented delete-and-retry protocol; a script whose file-discovery scope silently narrower than the step file's own stated CONTEXT BOUNDARIES.
Fix: Before refusing a request or improvising a manual workaround, check whether a skill file already exists for this exact situation (skills/ and .claude/skills/, per the Hidden Skills Directory rule) and read it before responding. When a skill or script's actual behavior needs verifying against its own spec, check its documented CONTEXT BOUNDARIES or usage section rather than assuming the implementation matches the description.
Status: active

## 2026-08-28 — Tool Misuse / Pattern Mismatch
Detected: 4 occurrences over 30 days
Category: tool-misuse
Failure mode: pattern-mismatch
Pattern: A script or tool's actual regex/parsing behavior is assumed to match its intent or docstring, without being tested against real data. This repeatedly hit systems/dream-cycle/salience-score.py's frontmatter merge-write: three straight nights (08-25 APAWBB, 08-26 NBGENM, 08-28 J571BH) each found more of the same corruption and revised the theory of what was causing it, before the 08-28 entry finally reproduced the exact mechanism in isolation (a trailing-newline slicing edge case that strands the last line of every salience block, every night, on every file — not the "legacy, frozen" damage the 08-26 entry had concluded). A fourth (08-27, 8HOA70) hit the same failure mode in a different script's guardrail check. In every case the bug was invisible from reading the code casually; it only surfaced by testing the actual regex against real file content.
Fix: When a script's output looks wrong or a bug's root cause still feels like a guess after one investigation pass, don't settle for a plausible narrative — reproduce the exact failing input in isolation (a small standalone repro, not just re-reading the source) before writing the finding down as fact. Treat "does not add new corruption going forward" or similar going-forward claims as unverified until tested on a fresh, clean input from this cycle, not just inferred from a code read. This is distinct from tool-misuse/protocol-skip (skipping a known-good path) — here the agent used the right tool but trusted an untested assumption about how it behaves.
Status: active

## 2026-08-29 — Data Accuracy / Stale Cache
Detected: 3 occurrences over 30 days
Category: data-accuracy
Failure mode: stale-cache
Pattern: Agent trusts a tool or skill's freshness/completion signal at face value instead of cross-checking it against the actual underlying source, and a stale or miscounted cache produces a large false-positive result. Examples: plaud-discover reporting 116-of-120 then 127-of-128 recordings as "new" when a direct vault check showed the true count was single digits, because stale leftover files in the staging directory were being counted without a dedup check against the vault; OmniFocus surfacing a task as overdue for the 8th time after David confirmed it was completed over a month ago, because the MCP's completion status was trusted without the standing "verify if disputed" caveat being acted on. Distinct from tool-misuse/pattern-mismatch (a script's parsing logic doesn't match its own docstring) — here the logic runs as designed, but the data it's counting is stale relative to the real state.
Fix: Before surfacing a count, status, or "new/changed" flag from a cache-backed tool (discovery skills, MCP completion status, staging directories), cross-check it against the authoritative source it's meant to reflect — not just re-run the same tool. When a skill or MCP has a documented reliability caveat (e.g. OmniFocus completion status per SYSTEM.md), treat that caveat as an active verification step, not passive boilerplate to append to output. A result that contradicts a recently-verified baseline by an order of magnitude is a signal to verify before reporting, not to report with a caveat.
Status: active

## 2026-09-06 — Data Accuracy / Pattern Mismatch
Detected: 3 occurrences over 30 days
Category: data-accuracy
Failure mode: pattern-mismatch
Pattern: Recurring data-accuracy errors with failure mode `pattern-mismatch` — surfaced by dream-cycle threshold check (err-20260814T154248-OC1SIQ, err-20260827T183203-RSVL2A, err-20260901T081243-R58BYW). The three underlying incidents are not a single coherent failure (a misidentified call subject, an eval-record selection error, and the salience-score.py frontmatter-stranding bug) but each shares the same shape: the agent matched on a superficial pattern (a name fragment, a file naming convention, a plausible-looking parse) instead of verifying against the actual underlying data before acting on the match.
Fix: When a match is based on a naming pattern, keyword, or superficial similarity rather than a direct lookup of the authoritative record, treat the match as a hypothesis and verify against the actual source before using it — don't let a pattern that "looks right" substitute for confirming it against ground truth.
Status: active
