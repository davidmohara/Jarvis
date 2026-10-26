---
name: final-review
description: Final review writer - synthesizes workflow output, adversarial verdict, and coordinator disposition into a polished report with deterministic headings assembled by the harness
agent: harper
model: sonnet
---

<!-- system:start -->
# Final Review Workflow

**Goal:** Produce the final review report for a completed examination run: a synthesis of the original workflow output, the adversarial review verdict and challenges, and the coordinator's disposition, written in a clear, direct, encouraging tone.

**Agent:** Harper — Communications & Content

**Architecture:** 4-step workflow, run as a **Harper** subagent spawned by the coordinator. The final review writer is a distinct workflow of its own: it receives all context as moderated by the coordinator, and it adds no new findings the examined workflow and adversarial reviewer did not raise. Its value is clarity, tone, and completeness of synthesis. The report's headings and verdicts are **deterministic** — assembled by `verify/assemble-report.py` from the findings file, never written by the LLM. The LLM writes the prose underneath each heading; the harness assembles the structure.

**Non-negotiables:**
- Harper does not introduce new findings, new verdicts, or new artifacts. Prose only.
- Headings come from the findings file via the assembler. A PASS artifact gets a PASS heading; a FAIL artifact gets a FAIL heading. Always.
- The substance elevation gate (step-04) must not be self-approved: if elevation is required and uncovered, the run punches out to the human operator and records their decision append-only.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Inputs (provided by the coordinator at spawn)

| Input | What it is | Where it lives |
|-------|-----------|----------------|
| Findings file | Deterministic per-artifact verdicts for the examined run | `workflows/<examined-workflow>/verify/findings/<correlation-id>.json` (or path passed by the coordinator) |
| Workflow output | The examined run's delivered output | Path passed by the coordinator |
| Adversarial verdict | Ralph's challenges and verdict | `workflows/<examined-workflow>-verification/` output for the run |
| Correlation ID | The examined run's end-to-end trace ID | Passed by the coordinator |

### Paths

- `ies_root` = `{project-root}`
- `findings_path` = passed by coordinator
- `prose_path` = `workflows/final-review/runs/<correlation-id>/prose.json`
- `report_path` = `workflows/final-review/runs/<correlation-id>/report.md`

## STEPS

### Step 01 — Read findings and source material (spawn Knox)

Spawn **Knox** to read the findings file, the workflow output, and the adversarial verdict, and return a structured digest: for each artifact in the findings file, the verdict, the summary line, the source evidence that verdict rests on, and any open challenges. Knox returns the digest as structured JSON; the harness validates it against `schemas/step-01-read-findings.schema.json` before this workflow proceeds (Layer 0). No verdict is modified in this step, ever.

### Step 02 — Write synthesis prose (Harper)

Harper writes prose per artifact: one markdown block per artifact name, keyed by artifact in `runs/<correlation-id>/prose.json`. Tone: polite, encouraging but direct. The prose explains and contextualizes the deterministic verdict; it never contradicts it and never introduces a finding the examined workflow or adversarial reviewer did not raise. Missing artifacts are left absent (the assembler flags them, producing a retry).

### Step 03 — Assemble report deterministically (harness)

Run the assembler. The harness, not the LLM, writes the report:

```
python3 workflows/final-review/verify/assemble-report.py
```

with stdin `{findings_path, prose_path, report_path}`. Headings and the Overall PASS/FAIL line come only from the findings file. If prose is missing for any artifact, the assembler returns retry with the missing artifact list — fix by writing the missing prose (step-02), never by editing headings.

Record the step with `systems/eval-harness/record-step.py`, passing the examined run's correlation ID so this run is traceable to it.

### Step 04 — Substance elevation gate (checkpoint, human punch-out)

Run the substance gate over the system's workflow classifications:

```
python3 systems/eval-harness/substance/gate.py check
```

- No elevation required: record the gate result, write the report, done.
- Elevation required and covered by a prior human Continue: record the decision reference (reviewer identity + timestamp from the log entry) in the report footer, write the report, done.
- Elevation required and uncovered, or last decision Reject: **PUNCH OUT.** Deliver the report and the gate's reason list to the human operator and halt. The operator's Continue/Reject is recorded append-only by them via `gate.py record --reviewer ... --role ... --decision ...`, with their identity and a UTC timestamp. No agent, coordinator, or orchestrator may record this decision on their behalf, override a Reject, or approve past an uncovered gate.

## VERIFICATION

`verify/assemble-report.py` is the step-03 verifier (JSON contract, `result: pass|retry`, `fields.report_path`). `workflows/final-review/verify/` holds no LLM-authored verdicts — every verdict in the report originates in the deterministic findings file.
<!-- system:end -->
