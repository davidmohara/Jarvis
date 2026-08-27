---
name: boot
description: Session boot. Context load, data gather, verification, briefing, workflow scan.
agent: master
model: sonnet
---

<!-- system:start -->
# Boot Workflow

9 sequential steps with per-step token extraction and guardrail checkpoints.

## STATE CHECK

1. Read `state.yaml`
2. If `status: in-progress`:
   - If `session-started` > 4 hours old: treat as stale, fresh run
   - Else: resume from `current-step`
3. If `status: complete` or `not-started`: fresh run
4. If `status: aborted`: ask controller

## DATA SOURCES

| Source | Method |
|--------|--------|
| SYSTEM.md, identity/* | Read files |
| M365 Calendar (3 days) | outlook_calendar_search |
| M365 Email (flagged) | outlook_email_search |
| OmniFocus inbox | MCP |
| Clay (7 days) | MCP |
| workflows/*/state.yaml | Read all |

## EXECUTION

Master orchestrates 9 steps sequentially. After each step:
1. step-complete.py hook extracts per-step tokens
2. Guardrail checkpoint validates output
3. If escalate: punch out to controller
4. If retry: re-execute step (max 3 times)
5. Else: continue to next step

### Steps

| # | Name | Guardrail |
|---|------|-----------|
| 1 | step-01-load-context | step-01-checkpoint |
| 2 | step-01.5-unified-calendar-pull | step-01.5-checkpoint |
| 3 | step-02-gather-data | step-02-checkpoint |
| 4 | step-03-verify-phase2 | step-03-checkpoint |
| 5 | step-04-gather-meeting-context | step-04-checkpoint |
| 6 | step-05-synthesize-briefing | step-05-checkpoint |
| 7 | step-06-scan-workflows | step-06-checkpoint |
| 8 | step-06.5-guardrail-checkpoint | step-06.5-checkpoint |
| 9 | step-07-verify-completion | step-07-checkpoint |

Begin: `steps/step-01-load-context.md`

<!-- system:end -->

<!-- personal:start -->
## Session Index

After step-01 reads identity files:
- Create `memory/sessions/index.json` if missing: `[]`
- Append session record: `{started, closed: null, current_topic: null, topics: []}`

<!-- personal:end -->
