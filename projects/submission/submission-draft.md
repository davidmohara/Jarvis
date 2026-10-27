# Delegation System Package

**Prepared:** 2026-10-26

## How to read this package

This is a delegation system: a dispatch-only coordinator (the Master agent) launches scoped sub-agents, each owning the steps of a single workflow; deterministic harness code enforces structure at every delegation boundary; an isolated adversarial reviewer (Ralph) checks each workflow's output against source data; a final-review workflow synthesizes results into a report whose headings and verdicts are assembled by the harness, never by the LLM; and a substance assessment gate routes final disposition to a human when the system's workflows are not all core billable work.

The package is organized by the system's design guarantees, each described and then located. The contents index at the end maps every claim to a file path.

Deterministic Python (hooks, verifiers, gates, wrappers) governs every dispatch: the coordinator's tool calls land in a harness that validates, verifies, records, and gates before any result is returned to it. The LLM executes steps; the harness owns structure, enforcement, and the audit trail. No runtime inference decision is made by ad-hoc LLM reasoning outside the governed path.

## 1. The Coordinator

The coordinator is an LLM that holds only dispatch and reasons over sub-agent results. It does not read files, call HTTP endpoints, or run commands. A coordinator that can do real work is a single agent pretending to be a delegation system.

This system's Master agent is dispatch-only. Every step file in every candidate workflow is written spawn-first: the step's content is "spawn agent X with this assignment," with Hard Stops forbidding inline execution. Where the library previously let the coordinator run git operations, inspect staged recordings, or invoke models directly, those paths were removed and routed through the owning agent and its gated skill (`skills/git/SKILL.md`, enforced mechanically by the `ies-git` wrapper and a PreToolUse git gate that transparently redirects raw git writes). A bypass-test matrix (BT-03, BT-04, BT-06) deliberately attempts coordinator-direct execution; technical enforcement holds for git writes, and the remaining procedural-only paths (direct domain-data inspection, inline specialist execution) are described with their compensating nets in the bypass-test README.

**Files:** `agents/manifest.md` (coordinator role, dispatch model, conflict resolution), `agents/master.md` (coordinator prompt definition, dispatch-only boundaries), `bypass-tests/` (BT-01 through BT-06 with logs).

## 2. Sub-Agents Scoped to One Workflow

Each sub-agent is limited to the tools, skills, and steps of its single workflow. Every workflow keeps its prompt guarantees: a defined prompt, at least three named evaluation criteria, and structured measured results (a committed results file, results table, or run record, never a prose claim).

This system has 11 agents, each with a prompt definition (`agents/<name>.md`), an owned-workflow table in `agents/manifest.md`, and criteria artifacts carrying named thresholds and measured results mined from the eval harness's run records (`systems/eval-harness/runs/`, 1,258 records). Measured results are structured: the per-step audit exports (`eval-data/audit-exports/<workflow>/step-audit.{csv,json}`) and the eval records themselves are committed JSON/CSV. Four candidate workflows carry the full instrumentation standard: boot, morning-briefing, daily-review, plaud-ingest.

**Files:** `agents/manifest.md`, `agents/*.md` (the 11 agent definition files themselves: prompts, roles, tool scopes), `eval-data/audit-exports/`, `index.md` (per-agent criteria results and measured results).

## 3. Adversarial Review in Its Own Context

A dedicated adversarial agent reviews each sub-agent's output in a distinct context window, with read access to verify claims against source files. A reviewer sharing the producing agent's history is a second opinion, not adversarial review.

Ralph is a first-class agent (`agents/ralph.md`) spawned fresh for each verification run, with file access to cross-check delivered output against source data. Each candidate workflow has a dedicated verification sub-workflow (`workflows/<wf>-verification/`) with a distinct lens: boot (briefing currency, credential scan, checkpoint presence), morning-briefing (calendar/email cross-check), daily-review (output vs. source data), plaud-ingest (ingest completeness). Isolation is by construction: Ralph is spawned as a separate subagent with a fresh context, never run inline in the producing agent's session. Adversarial verification is wired as a guardrail (assertions morning-008 / daily-007 / plaud-002), and real catches are recorded structurally in `eval-data/adversarial-catches/`.

**Files:** `agents/adversarial-isolation.md`, `verification/` (the four verification workflows), `eval-data/adversarial-catches/`, `agents/ralph.md`.

## 4. The Final Review Writer

The final review is a distinct workflow of its own. It receives the workflow output, the adversarial review verdict and challenges, and the coordinator's disposition, and synthesizes them into a polished report. The report's headings and verdicts are deterministic: a passing artifact gets a PASS heading, a failing artifact gets a FAIL heading, and the LLM writes only the prose underneath. The writer adds no new findings.

`workflows/final-review/` is a 4-step workflow. Step 01 spawns Knox to read the findings file and source material into a schema-validated digest (no verdict modified). Step 02: the writer agent (Harper) authors prose per artifact only, prohibited from new findings or verdict changes. Step 03 is fully deterministic: `workflows/final-review/verify/assemble-report.py` builds the report from the findings JSON, heading PASS/FAIL and the Overall line computed from artifact verdicts, LLM prose inserted verbatim underneath. Missing prose produces a structured retry with the artifact list, never a heading edit. Step 04 runs the substance elevation gate (section 7) and punches out to the human operator rather than self-approving. Tested end to end: pass case, missing-prose retry, and malformed-findings retry all return the contract verdicts.

**Files:** `workflows/final-review/workflow.md`, `workflows/final-review/verify/assemble-report.py`, `workflows/final-review/schemas/step-01-read-findings.schema.json`.

## 5. Continuity Guarantees

The workflow-level guarantees hold across every sub-workflow in the delegation structure:

- **Deterministic harness:** deterministic Python owns structure and enforcement at every boundary: `step-complete.py` (verification dispatch), `guardrail-checkpoint.py` (mid-run blocking checkpoints), `assertion_checks.py`, `ies-git` (gated git wrapper with per-operation audit log `git-ops.jsonl`), `validate-subagent-output.py` (Layer 0 schema validation), `substance/gate.py` (elevation gate). Agentic-CLI usage appears only in evaluation and test contexts, never as runtime decision-making.
- **Punch-outs honored:** the coordinator cannot auto-approve past a human checkpoint. Escalation is hook-enforced (`step-complete.py` escalates to `escalated_to_human: true` and halts); bypass-test BT-02 attempted to defeat escalation, found two real holes, both fixed same day with closed-loop re-test evidence. The substance elevation gate (section 7) blocks final disposition until a human records Continue/Reject.
- **Per-step evals:** every workflow keeps its prompt, named criteria, and structured measured results (`agents/`, `eval-data/audit-exports/`). Success rates reported in both strict and mechanical tiers with session-exit aborts counted separately.
- **Audit trail:** per-step model/tokens/cost persists in `systems/eval-harness/runs/*.json` and exports to CSV/JSON. Every run record mints a `correlation_id` on its first recorded step; every step entry and every audit-export row carries it, so one ID traces an execution end to end across the multi-workflow structure. Minted once, never recomputed, persisted to disk in the record itself. Tested: record, step, and CSV export all carry the same ID.

**Files:** `.claude/hooks/step-complete.py`, `systems/eval-harness/correlation.py`, `systems/eval-harness/record-step.py`, `systems/eval-harness/export-step-audit.py`, `bypass-tests/`, `eval-data/audit-exports/`.

## 6. Deterministic Guardrails Between Steps

When the coordinator dispatches a sub-agent, the harness enforces schema validation on the sub-agent's output before the coordinator ever sees it. A failure returns a structured error the coordinator can reason over, never garbage. The coordinator reasons; the harness enforces structure.

Verification is layered in `step-complete.py`, which fires when a step's status is written:

- **Layer 0, schema validation at the delegation boundary:** if the step declares a schema at `workflows/<wf>/schemas/<step>.schema.json`, `validate-subagent-output.py` validates the sub-agent's structured output (state.yaml accumulated-context or explicit payload) against it BEFORE any verification or coordinator-visible pass. A failure returns a structured retry with field-level errors ("files_loaded: required field missing") and a repair instruction, so the coordinator reasons over a well-formed error. Schemas are opt-in per step and validated in both pass and fail directions (tested).
- **Layer 1, ground-truth verifiers:** per-step deterministic verifiers (`workflows/<wf>/verify/step-*.py`) check real outputs against real state at every step transition of all candidate workflows.
- **Layer 2, guardrail checkpoints:** mid-run blocking checkpoints (boot 06.5, morning-briefing 03b, daily-review 03b, the verification steps) call `guardrail-checkpoint.py` in-step, the mid-run gate path.

Layer 0 and Layer 1 share one stdin/stdout JSON contract, so verifiers compose with schema validation without either knowing about the other.

**Files:** `systems/eval-harness/validate-subagent-output.py`, `workflows/boot/schemas/step-01-load-context.schema.json` (seed schema), `.claude/hooks/step-complete.py`, `verification/`, `bypass-tests/`.

## 7. Substance Assessment

For each workflow, its relevance to a consultant's real work: core (work a paying client would buy), peripheral (useful but not billable on its own), or toy. Any toy, or two or more peripheral, elevates for human review: the system's report is retained verbatim and a human records an append-only Continue/Reject decision with reviewer identity.

`systems/eval-harness/substance/assessment.json` carries the per-workflow classification with rationale. All five assessed workflows (the four candidates plus shutdown-cleanup, held to the same standard) are classified **peripheral**: internal productivity and system hygiene, not client-billable work. The classification trips the elevation rule.

`systems/eval-harness/substance/gate.py` enforces the gate deterministically:

- `check` exits 3 (blocking) when elevation is required and uncovered, or when the last decision is Reject. The coordinator may not proceed past it.
- `record` is the only write path, is append-only by construction (no overwrite, edit, or delete exists anywhere), and requires a human reviewer name, role, and decision. Every entry carries identity, UTC timestamp, the elevation reasons ruled on, and the verbatim report path.
- `confirm` marks classifications confirmed only when a covering Continue decision ruled on exactly the current classification state; changed classifications refuse and force a fresh decision.
- A Continue covers only the gate state it was recorded against. An unconfirmed classification cannot self-approve.

The gate has been exercised in the blocking state (uncovered elevation, exit 3), the covered state (recorded human Continue), and the confirmation path. The human operator's Continue decision on the all-peripheral classification is recorded in `elevation-log.jsonl` with identity and timestamp, and the classifications are confirmed through the gate's own path.

**Files:** `systems/eval-harness/substance/assessment.json`, `systems/eval-harness/substance/gate.py`, `systems/eval-harness/substance/elevation-log.jsonl`.

## Contents index

| Area | Files |
|---|---|
| Coordinator dispatch-only | `agents/manifest.md`, `agents/master.md`, `bypass-tests/` |
| Sub-agent scoping + per-workflow criteria | `agents/` (11 agent definitions), `agents/manifest.md`, `index.md` (per-agent measured verdicts) |
| Adversarial isolation | `agents/adversarial-isolation.md`, `agents/ralph.md`, `verification/`, `eval-data/adversarial-catches/` |
| Final review writer | `workflows/final-review/` (workflow, assembler, schema) |
| Continuity: harness, punch-outs, evals, audit trail | `.claude/hooks/`, `systems/eval-harness/` (correlation.py, record-step.py, export-step-audit.py, guardrail-checkpoint.py), `skills/git/`, `bypass-tests/`, `eval-data/audit-exports/` |
| Deterministic guardrails | `systems/eval-harness/validate-subagent-output.py`, `workflows/*/verify/`, `workflows/*/schemas/` |
| Substance assessment | `systems/eval-harness/substance/` |
