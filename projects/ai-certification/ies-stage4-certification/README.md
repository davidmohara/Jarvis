# Stage 4 Certification Submission — IES (Jarvis)

**Submitted by:** David O'Hara
**Source system:** IES, a personal executive-operating-system agent orchestration platform
built on Claude Code, in daily production use.

This submission is built entirely from real, currently-running artifacts of IES's `boot`
workflow and the eval harness that governs it — nothing here was constructed for the
purpose of this submission. Business-specific content (calendar details, account names,
internal scheduling) has been redacted from the workflow step files where it isn't
relevant to demonstrating the mechanism; the mechanism itself — the workflow definition,
the guardrail/hook code, the monitoring and audit-trail records, and a real human
punch-out event — is unmodified.

## How this maps to the Stage 4 rubric

| Stage 4 requirement | Where it is in this submission |
|---|---|
| Multiple Stage-3-style evaluated prompts linked into a cohesive workflow, with defined handoffs and branching | `01-workflow/workflow.md` + `01-workflow/steps/*.md` — boot's 12-step dispatch model, each step individually evaluated (see `03-monitoring-audit-trail`), with explicit escalate/retry/continue branching logic (`workflow.md`, "After each step" section) |
| The workflow itself is a Stage-3 prompt, evaluated as a whole | `03-monitoring-audit-trail/boot.json` — deterministic assertions run against the whole workflow's outcome (state.yaml completion, session index integrity, guardrail-checkpoint execution), not just individual steps |
| Automated guardrails between steps, replacing what used to be human-in-the-loop checkpoints | `02-guardrails-hooks/` — the hook scripts (`eval-turn-start.py`, `eval-turn-stop.py`, `eval-agent-start.py`, `eval-agent-stop.py`, `eval-tool-failure.py`, `post-tool-use.py`, `hook_utils.py`) that fire automatically on every prompt, subagent spawn, and tool call to open/close eval records and run guardrail checkpoints — no human has to remember to check anything |
| A proven, evaluated way to punch out to a human, kept separate from prompt failure | `04-human-punchout-evidence/case-study-plaud-ingest-punchout.md` — a real, unmodified example from the same session: a sibling workflow (`plaud-ingest`) hit a Plaud API condition it correctly recognized as a human decision boundary (possible transcription-minute exhaustion), and punched out with a direct question instead of retrying blindly or failing silently |
| Monitoring across the whole workflow, not just single-prompt success rate | `03-monitoring-audit-trail/sample-eval-records/` — two real eval records from two full boot runs the same day, each showing per-subagent status, guardrail pass/fail, and assertion results across the entire 12-step run |
| End-to-end success rate, measured not asserted | `06-success-rate-report/e2e-success-rate-report.md` — computed directly from all 23 genuine `boot` workflow eval records in `systems/eval-harness/runs/` (2026-08-21 to 2026-08-28): 26.1% full-success rate, 52.2% mechanical completion, 81.4% structural assertion pass rate, with an honest breakdown of what the non-success statuses actually represent (session-exit artifacts vs. genuine failures) — plus a documented case of a 24th, phantom record caught and deleted before it could distort the count |
| A real audit trail: which step produced which output, token counts, and actual cost | `03-monitoring-audit-trail/sample-eval-records/run1-morning-clean.json` and `run2-afternoon-fixed.json` — both carry `subagents[]` entries with `tokens_input`, `tokens_output`, and `cost_usd` per subagent, plus workflow-level `total_tokens_input`/`total_tokens_output`/`total_cost_usd` |
| Evidence the monitoring/audit trail is real and actively used, not decorative | `05-error-accountability/` — a real self-detected error entry (`err-20260828T144849-I60TAU.json`) generated the same day, showing the audit trail catching a defect (a tool-misuse bug affecting hook execution), root-causing it, and recording a systemic fix, per the schema in `error-tracking-schema.md` |

## A note on `run2-afternoon-fixed.json`

This record is included deliberately, not because it's the cleanest possible example, but
because of what happened to produce it: the first version of this run's audit-trail data
was itself found to be broken (a subagent-attribution bug misattributed a sibling
workflow's cost into this record and lost the real workflow's completion data). That bug
was root-caused, fixed at the hook level, and the record was corrected using the real
subagent's own independently-recorded data — rather than discarded or silently accepted.
That correction cycle is itself evidence of the audit trail being load-bearing: the system
caught its own instrumentation defect and could prove what the right numbers should have
been.

## Contents

```
ies-stage4-certification/
├── README.md
├── 01-workflow/
│   ├── workflow.md              — the boot workflow's dispatch model and step table
│   └── steps/                   — all 12 step files (each independently evaluated)
├── 02-guardrails-hooks/         — automated guardrail/hook code, fires on every turn/subagent/tool call
├── 03-monitoring-audit-trail/
│   ├── schema.md                — eval record schema (what's tracked per run)
│   ├── boot.json                — deterministic assertions checked against every boot run
│   └── sample-eval-records/     — two real, complete eval records from two boot runs today
├── 04-human-punchout-evidence/
│   └── case-study-plaud-ingest-punchout.md
├── 05-error-accountability/
│   ├── err-20260828T144849-I60TAU.json
│   └── error-tracking-schema.md
└── 06-success-rate-report/
    └── e2e-success-rate-report.md   — real, computed end-to-end success rate across all boot runs
```
