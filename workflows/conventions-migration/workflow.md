---
name: conventions-migration
description: Sweep the IES capability library into conformance with reference/capability-conventions.md — mechanical fixes first, then size triage with David. Trigger on 'conventions sweep', 'migrate conventions', or after any convention changes in reference/capability-conventions.md.
agent: rigby
model: sonnet
---

<!-- system:start -->
# Conventions Migration

## Data Sources Required

| Source | Path | Purpose |
|--------|-----------|---------|
| Conventions | `reference/capability-conventions.md` | The rules being swept to. Read fully before Step 1. |
| Linter | `systems/eval-harness/validate-conventions.py` | Finding generator. Report mode only — never build-gate here. |
| Exceptions | `systems/eval-harness/conventions-exceptions.json` | Acknowledged findings are out of scope. |
| Census | `skills/rigby-skill-audit/scripts/audit.py --census` | Distribution before/after. |

## Paths

```
workflows/conventions-migration/
├── workflow.md          ← this file
├── state.yaml           ← execution state
└── steps/
    ├── step-01-baseline.md    ← run linter, bucket findings
    ├── step-02-mechanical.md  ← apply unambiguous fixes
    ├── step-03-judgment.md    ← surface judgment calls to David
    ├── step-04-size.md        ← size triage: fix, except, or accept
    └── step-05-close.md      ← re-lint, census, report
```

## Key Metrics

- **Findings at baseline** vs. **findings at close** — the sweep's effect
- **FAIL count** — must reach zero before close
- **WARN count** — target zero; anything left needs an approved exception
- **Pending exceptions** — recorded by Rigby, approved by David; nothing ships approved without David

## STATE CHECK

Read and follow `reference/state-check-protocol.md` before any execution. Workflow: `conventions-migration`; agent: `rigby`.

## EXECUTION

**Dispatch model:** Rigby subagent, spawned by the coordinator, never inline.

Run steps in order. Read each step file fully before executing it.

**Step 2 (mechanical fixes) is the only step with write authority without per-fix approval** — and only for findings the step file defines as unambiguous. Everything else surfaces to David.

**Never re-lint during a fix loop without saving the prior finding list** — deltas between runs are how regressions get caught.
<!-- system:end -->
