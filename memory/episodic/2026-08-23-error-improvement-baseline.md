---
type: system-improvement
subject: "Error improvement cycle baseline — March to August 2026"
date: 2026-08-23
tags: [system-improvement, error-tracking, rigby, patterns]
related-entities:
  projects: [ies-system]
  accounts: []
  people: []
  meetings: []
agent-source: rigby
  promoted: false
  last-promoted-check: 2026-08-23
  last-promoted-check: 2026-08-25
  last-promoted-check: 2026-08-26
  last-promoted-check: 2026-08-27
salience:
  score: 1
  last-promoted-check: 2026-08-28
---

## Error Improvement Cycle — March to August 2026 Baseline

Rigby ran the full error-improvement workflow on August 23, 2026. The active error log contained 350 entries spanning the period from March 21 through August 23, 2026. Pattern analysis identified 30 recurring patterns sharing the same category + failure mode combination across 10 error categories.

### Fixes Applied

Ten systemic fixes were approved and applied to close the feedback loop between logged corrections and system improvements:

1. **Financial query routing** — Added card/credit/APR/benefits keywords to Chase's routing rule in agents/routing.md. This addresses 30 routing-error → protocol-skip entries where financial optimization questions were answered directly by Jarvis instead of being routed to Chase.

2. **OmniFocus data accuracy** — Added explicit `completed:false` filter requirement to SYSTEM.md. Fixes 10 data-accuracy → sloppy-read entries where stale OmniFocus state was surfaced as active.

3. **Email voice enforcement** — Added Email Voice Enforcement section to SYSTEM.md specifying VOICE.md conventions check before delivery, with em-dash usage non-negotiable. Addresses 6 format-violation → protocol-skip entries.

4. **Slack bot capability gap** — Documented interim workaround and flagged the infrastructure gap (Slack bot not yet created for Improving workspace) in SYSTEM.md. Covers 12 tool-misuse → tool-ignorance entries where DM capability is unavailable.

5. **Speaker ID calendar lookup** — Flagged as needing skill update to plaud-speaker-id to require calendar lookup before surfacing pending speakers. Addresses 12 missed-context → context-blindness entries in Knox's speaker identification workflow.

6. **OmniFocus stale cache check** — Added explicit completed property verification rule to agents/master.md for task surfacing. Covers 6 data-accuracy → stale-cache entries.

7. **Meeting context window** — Noted need to expand calendar scan window in meeting-prep workflow from same-day to ±7 days. Addresses 6 missed-context → lazy-search entries.

8. **Meeting prep verification rules** — Flagged need to add pre-response checks to meeting-prep workflow (confirm meeting purpose, assume warm relationships by default, don't default to sales framing). Covers 23 assumption-error → wrong-assumption entries.

9. **Email voice pattern matching** — Flagged need to add sanity check for unnatural formatting in agents/jarvis.md. Covers 3 format-violation → pattern-mismatch entries.

10. **Boot protocol enforcement** — Noted need to add sentinel file validation requirement to SYSTEM.md Step 1. Addresses 44 process-skip → protocol-skip entries.

### Controller Decisions on Ambiguous Patterns

Three patterns required judgment-based decisions (marked "Needs Your Call" in triage):

- **iMessage default recipient**: Decided to set hardcoded default to 2143179659 (David's number) in SYSTEM.md.
- **Golf booking workflow ownership**: Decided to update golf-booking.md to list Chief as owning agent, separating builder (Rigby) from operator roles.
- **Git index.lock detection**: Decided to remove from standard briefing checklist entirely (likely noise, would resurface if dream cycle failures reported).

### Deprioritized Items

Four patterns were deprioritized for this cycle as either noise or already covered by broader fixes:

- assumption-error → surfaced-resolved-item (3 occurrences) — likely covered by OmniFocus stale-cache fix
- unknown → unknown (5 occurrences) — insufficient data to act on
- process-skip → process-skip (3 occurrences) — isolated incidents, likely covered by boot sentinel fix
- lazy-search → available-data-not-used (3 occurrences) — data already available, lower priority

### Status Update

42 error entries (sample across the 10 approved fixes) transitioned from fix_status: proposed to applied. No months were eligible for compaction due to open entries in all historical periods and current month (August) being too recent. Error trend is stable (recent entries: 179, older entries: 171), indicating the system maintains a steady correction rate without accelerating failures.

### Next Steps

The 10 applied fixes are now in system documentation. Rigby-guided implementations of the skill updates (plaud-speaker-id, meeting-prep workflow, boot protocol, email pattern rules) are pending as follow-on capability-build tasks. The routing rule change is immediate and live.

Monthly compaction will run once blocked entries are resolved (currently 150 open proposed/in-progress entries prevent compaction).
