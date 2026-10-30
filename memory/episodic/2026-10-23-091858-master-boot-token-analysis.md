---
type: working-archive
task_id: "session"
session_id: "master-2026-10-23-091858"
agent-source: master
created: 2026-10-23T09:18:58-05:00
expires: 2026-10-25T09:18:58-05:00
status: archived
context: "Boot token performance analysis (per-step, 10/13..10/23) — 2026-10-23"
date: 2026-10-23
source_file: memory/working/2026-10-23-091858-master-boot-token-analysis.md
tags:
  - master
  - briefing
  - morning-briefing
  - calendar
  - omnifocus
  - plaud
  - boot
  - rigby
  - knox
related_people:
salience:
  score: 10
  last-promoted-check: 2026-10-30
  promoted: true
---

# Boot Token Performance Analysis — 2026-10-23

## What was requested and produced

David asked for a stepwise + aggregate token comparison of today's boot (2026-10-23) vs the past 2 days (10/22, 10/21) and last week (10/13, 10/19). Delivered via a read-only eval-harness analysis subagent (70,889 tokens, hand-parsed from `systems/eval-harness/runs/` — no aggregation script covers per-step extraction; generate-dashboard.py / version-trend.py are trend-only).

## Key data points

| Date | Record | Status | Input | Output | Fully-loaded |
|---|---|---|---|---|---|
| 10/13 | eval-20261013T114019-Q5UJLE | success | 11,772,962 | 72,646 | — |
| 10/19 | eval-20261019T203151-IA1AX8 | success | 16,954,420 | 87,061 | — |
| 10/21 | eval-20261021T151330-QNQLC5 | success | 2,536,301 | 9,201 | 3,215,908 / 14,269 |
| 10/22 | eval-20261022T114238-IP36P9 | partial | 4,471,902 | 31,320 | 5,565,310 / 41,209 |
| 10/23 | eval-20261023T131721-QQIZKW | partial | 5,869,892 | 66,237 | 7,639,504 / 71,074 |

Today's per-step executor input/output (each its own dedicated subagent):

| Step | Eval id | Input | Output |
|---|---|---|---|
| 01.5 calendar | eval-20261023T132142-LSR4DE | 371,940 | 7,419 |
| 01.2 data pull | eval-20261023T132525-OEWXL8 | 590,599 | 11,148 |
| 02 gather | eval-20261023T133214-1V8SN5 | 586,064 | 8,061 |
| 03 verify | eval-20261023T133710-4ZK81X | 347,024 | 3,946 |
| 04 meeting ctx | eval-20261023T133946-6TY4R8 | 656,267 | 4,973 |
| 05-08 briefing | eval-20261023T134258-CMONGZ | 1,528,972 | 20,055 |

Today's total composition: 4.08M executors + 912K Master orchestration + 817K Knox (no-op plaud run, eval-20261023T132126-OR7TTP) + 60K plaud-discover.

## Findings

1. **Restructure worked vs last week**: today's 5.87M (7.64M FL) is ~50% of 10/13 and ~35% of 10/19.
2. **vs 10/21 the comparison is rigged**: 10/21 recorded 0 tokens for steps 01.5 and 05-08 (turns outside step windows), understating its total. Real per-step costs are comparable: 02 within 8%, 03 down 30%, 04 up 23% (04's rise is real: identity files + Obsidian searches).
3. **Attribution quality**: 10/22 has zero per-step attribution (Bash state writes, empty steps array). 10/13 and 10/19 used lenient_fallback (same window count stamped on every step — not real per-step costs). 10/23 is the first fully-attributed run.
4. **Optimization targets surfaced**:
   - 05-08 briefing subagent at 1.53M input is the biggest single block — the one-long-lived-agent pattern has re-concentrated there. Next cut: split synthesis from completion/bookkeeping steps.
   - Knox no-op discovery cost 817K input to find 0 new recordings; the plaud-discover fork itself ran at 60K. Fat is in Knox's context build (full workflow + persona + vault walk). Rigby candidate.

## Data quality notes

- No boot eval records exist for 10/16, 10/17, 10/18.
- 10/22 also has three aborted/incomplete restructure experiment records (7OUMW0, TPZO43, 5C4OEY) — not the morning briefing run.
- Today's QQIZKW was status `partial` (grading in progress) at analysis time.
- Conflicting duplicate agent records for the plaud-discover fork (JYBOFB/VEAF2Y/CQ2Q18/K76HD0 + partial UJ3YLY); the workflow record's 59,952/58 is authoritative.

## Follow-up

- **David asked to redo and expand this analysis after Monday (10/26) and Tuesday (10/27) boots** — boot reminder rem-20261023T141926-H6H5JB, surfaces at the 2026-10-28 boot. Expansion should cover: post-fix measurement snapshots (Rigby fixed measure.py default=str today), whether step-01 frontmatter stamping lands on next boot, per-step trend across fully-attributed runs, and progress on the two optimization targets.
- Rigby already applied today: measure.py default=str fix (validated, snapshot 20261023T135854 writes full content) and step-01 frontmatter Master-stamping instruction.
