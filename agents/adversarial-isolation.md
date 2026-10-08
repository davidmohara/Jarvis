# Adversarial Review Isolation

**Established:** 2026-10-08 (Phase 5B, Stage 5 remediation) · **Maintained by:** Rigby · **Companion docs:** `agents/manifest.md`, `workflows/boot-verification/`

## Principle

Adversarial review agents verify producing agents' claims from a different lens and a separate execution context. A producing agent that grades its own work is not adversarial. In IES the adversarial layer is an agent spawned after the producing work completes, reading the same artifacts a skeptical outsider would read, with no access to the producing agent's reasoning beyond its recorded outputs.

## Isolation mechanics

1. **Separate spawn, fresh context.** The adversarial agent is spawned as its own sub-agent session. It does not share the producing agent's conversation or reasoning; it receives only the artifact paths and the verification checklist. It cannot inherit the producer's confidence.
2. **Ground truth over claims.** The adversarial agent reads raw state (`workflows/*/state.yaml`, `data/*.json`, `systems/eval-harness/runs/*.json`) and re-derives conclusions. It does not treat the producing agent's summary as evidence.
3. **Distinct lens, documented.** Each adversarial agent has a checklist of what it looks for that the producer structurally cannot: completion claims vs recorded state, output existence vs output correctness, silent drops, and punch-out behavior under failure.
4. **Failure is a finding, not a retry.** The adversarial agent reports discrepancies; it does not fix them. Fixes route back through the owning agent, so the adversarial finding stays independent of remediation.

## Current adversarial coverage

| Workflow | Adversarial agent | Lens | Invocation | Status |
|----------|-------------------|------|------------|--------|
| boot | **Ralph** (`agents/ralph.md`, `workflows/boot-verification/`) | Verifies boot completion claims against state.yaml, data files, and eval records; checks claimed data pulls against the pulled files | Spawned by the boot subagent at step-03 (`workflows/boot/steps/step-03-verify-phase2.md`, explicit spawn, never inline) | Live |
| morning-briefing | **Ralph** (`agents/ralph.md`, `workflows/morning-briefing-verification/`) | Calendar/email/OmniFocus cross-check: every briefing claim re-derived from the source data file | Spawned at step-05 (`workflows/morning-briefing/steps/step-05-verify-briefing.md`, separate spawn after synthesis) | Wired/live (Phase 4A) |
| daily-review | **Ralph** (`agents/ralph.md`, `workflows/daily-review-verification/`) | Output vs source data cross-check; every completion claim traced to recorded state | Spawned at step-03c (`workflows/daily-review/steps/step-03c-adversarial-verify.md`, separate spawn before the commit) | Wired/live (Phase 4A) |
| plaud-ingest | **Ralph** (`agents/ralph.md`, `workflows/plaud-ingest-verification/`) | Ingestion accounting: every discovered recording accounted for as an ingested note or a logged skip, zero silent drops | Spawned at step-06 (`workflows/plaud-ingest/steps/step-06-verify-ingest.md`, separate spawn after ingest/share) | Wired/live (Phase 4A) |
| shutdown-cleanup | **Ralph** (`agents/ralph.md`, `workflows/shutdown-cleanup-verification/`) | Cleanup claims vs commit and audit trail: nothing temp committed, nothing precious deleted, commit through the wrapper, counts true, clean claims real | Spawned at step-05 (`workflows/shutdown-cleanup/steps/step-05-verify-cleanup.md`, separate spawn after the commit) | Wired/live (compliance pass 2026-10-08) |

All four verification passes run Ralph with a workflow-specific lens checklist (the `workflows/*-verification/` dirs) and record their verdict via `guardrail-checkpoint.py` under the checkpoint name `adversarial-verification`. Each producing step transition is additionally guarded by a deterministic per-step verifier in `workflows/<workflow>/verify/` (dispatched by `.claude/hooks/step-complete.py`), so the adversarial layer is not the only machine check between steps.

## Evidence of catches

Honest status: Ralph's documented catches are thin so far. The boot run records are few and were historically misattributed in the harness's agent field (attribution fix in Phase 2 scope). The Phase 4A wiring changes this structurally: each of the four workflows now records an `adversarial-verification` guardrail result on every run (assertions `boot-004`, `morning-008`, `daily-007`, `plaud-002`), so a run that skips adversarial verification fails a recorded assertion rather than passing silently, and catch examples accumulate as machine-readable evidence during the Phase 4 data window rather than only as narrative.

## What adversarial agents check that producers cannot

- A producer knows what it intended to do; the adversarial agent only knows what the record says happened. That asymmetry is the point: it catches intent-vs-record gaps (claims of pulled data with no pulled file, claimed steps with no step output).
- A producer optimizes for completing its workflow; the adversarial agent optimizes for finding the case where the workflow's completion is wrong. Silent drops, empty outputs that satisfy file-existence checks, and degraded runs labeled success are exactly the failure classes the producing agent is structurally biased against reporting.
