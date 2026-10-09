# Stage 5 Compliance Audit: All Workflows (2026-10-08)

**Method:** read-only audit of all 62 workflow directories against the instrumentation standard set by the 2026-10-08 remediation (exemplars: daily-review, boot, plaud-ingest, shutdown-cleanup). Three parallel audit passes (21 + 20 + 21 workflows) plus a registry reverse-check. Nothing was modified; this document is the correction plan.

**Locations checked (all canonical workflow locations in IES):** `workflows/` (62 dirs, the complete set), the Task Portfolio registry in `agents/master.md`, `agents/routing.md` domain routing, `systems/eval-harness/assertions/`, `systems/eval-harness/runs/` usage records. `.claude/workflows/` does not exist. `.claude/skills/` is the skills library (no workflow definitions). No workflow definitions exist outside `workflows/` and the registries.

## Aggregate verdict (62 workflows)

| Verdict | Count | Workflows |
|---------|------:|-----------|
| COMPLIANT (fully instrumented) | 4 | boot, daily-review, plaud-ingest, morning-briefing (style-only notes) |
| MINOR GAPS (partial instrumentation) | 11 | shutdown-cleanup (2 real violations), one-on-one-prep, partner-meeting-prep, podcast-prep, content-approval, content-discovery, content-pipeline, rock1-revenue-monthly, rock4-pipeline-weekly, system-eval, weekly-review |
| VERIFICATION SUB-WORKFLOW | 5 | boot-verification, daily-review-verification, morning-briefing-verification, plaud-ingest-verification, shutdown-cleanup-verification (1 violation) |
| NON-COMPLIANT | 42 | the remainder (full list in the per-workflow matrix below) |

## Per-workflow matrix (compact)

Owner = workflow.md frontmatter agent. V = verifier coverage. G = guardrail json. A = adversarial Ralph wiring. AS = assertions file (gcr = has guardrail_checkpoint_ran). E = eval records. Verdict: C compliant, M minor gaps, S sub-workflow, N non-compliant.

| Workflow | Owner | V | G | A | AS | E | Verdict |
|---|---|---|---|---|---|---|---|
| account-pursuit-map | chase | 0/7 | - | - | MISSING | 0 | N |
| account-strategy | chase | 0/3 | - | - | yes | 0 | N |
| audience-target-outreach | harper | 0/5 | - | - | MISSING | 0 | N (unregistered) |
| boot | master | 12/12 | 9 | YES | yes+gcr | 45 | C |
| boot-verification | ralph | - | - | lens | MISSING | 2 | S (2-step deviation, spawn line) |
| calendar-prep | chief | 0/3 | - | - | yes | 0 | N |
| card-review | chase | 0/3 | - | - | yes | 0 | N (no Agent lines) |
| card-walkthrough | chase | 0/1 | - | - | yes | 0 | N (no Agent line) |
| card-which | chase | 0/1 | - | - | yes | 0 | N (no Agent line) |
| client-meeting-prep | chase | 0/5 | - | - | yes | 2 | N |
| comp-tracker | chase | 0/11 | - | - | yes | 0 | N (no model fm, orphaned steps) |
| content-approval | harper | 2/2 | - | - | MISSING | 1 | M |
| content-calendar | harper | 0/5 | - | - | yes | 0 | N (raw git, weak routing) |
| content-discovery | harper | 2/2 | - | - | MISSING | 1 | M |
| content-pipeline | harper | 3/3 | - | - | yes | 2 | M (state.yaml no agent, unregistered) |
| daily-review | chief | 8/8 | 1 (03b json missing) | YES | yes+gcr | 58 | C |
| daily-review-verification | ralph | - | - | lens | - | 0 | S compliant |
| delegation-tracker | shep | 0/3 | - | - | yes | 0 | N |
| dream-cycle | jarvis | 0/6 | none | - | yes+gcr | 58 | N (git status instruction) |
| email-drafting | harper | 0/3 | - | - | yes | 0 | N |
| episode-campaign-brief | harper | 0/4 | - | - | MISSING | 0 | N (unregistered) |
| episode-prep-generator | harper | 0/4 | - | - | yes | 0 | N |
| error-improvement | rigby | 0/7 | - | - | yes | 3 | N (unregistered) |
| evolution-deployment | rigby | 0/7 | - | - | yes | 0 | N (git status, unbalanced block) |
| evolution-training-sync | shep-training | 0/3 | - | - | yes | 0 | N (unregistered agent) |
| follow-up-nudges | shep | 0/3 | - | - | yes | 0 | N |
| galen-monthly-health-review | galen | inline | - | - | yes | 0 | N (no steps/ dir) |
| goal-alignment | quinn | 0/3 | - | - | yes | 0 | N |
| golf-booking | sterling | 0/8 (2 misnamed) | - | - | yes | 1 | N |
| golf-preview | sterling | 0/5 (2 misnamed) | - | - | yes | 2 | N (unregistered) |
| inbox-processing | chief | 0/3 | - | - | yes | 0 | N |
| initiative-tracker | quinn | 0/4 | - | - | yes | 0 | N |
| knowledge-ingest | knox | inline | - | - | yes | 0 | N (no steps/ dir) |
| lead-log | chase | 0/2 | - | - | yes | 0 | N (no Agent lines) |
| lead-review | chase | 0/2 | - | - | yes | 0 | N (no Agent lines) |
| leadership-prep | quinn | 0/4 | - | - | yes | 0 | N |
| morning-briefing | chief | 6/6 | yes | YES | yes+gcr | 18 | C (style notes) |
| morning-briefing-verification | ralph | - | - | lens | - | 0 | S compliant |
| one-on-one-prep | shep | 5/5 | - | - | yes | 1 | M (spawn language) |
| one-texas-scorecard | chase | 0/5 | - | - | yes | 0 | N |
| partner-meeting-prep | chase | 4/4 | - | - | yes | 1 | M (spawn language) |
| pipeline-review | chase | 0/4 | - | - | yes | 0 | N |
| plaud-ingest | knox | 7/7 | yes | YES | yes+gcr | 31 | C |
| plaud-ingest-verification | ralph | - | - | lens | - | 0 | S compliant |
| podcast-prep | harper | 5/5 | - | - | yes | 1 | M (spawn language) |
| political-monitor | rigby | inline | - | - | MISSING | 0 | N (no steps/, unregistered) |
| presentation-builder | harper | 0/4 | - | - | yes | 0 | N |
| rock-review | quinn | 0/4 | - | - | yes | 0 | N |
| rock1-revenue-monthly | chase | 1/2 | - | - | yes | 0 | M (inline steps) |
| rock4-pipeline-weekly | chase | 1/3 | - | - | yes | 0 | M (inline steps) |
| shutdown-cleanup | rigby | 5/5 | yes | YES | yes+gcr | 6 | M (state.yaml agent stale, unbalanced block) |
| shutdown-cleanup-verification | ralph | - | - | lens | - | 0 | S (unbalanced block) |
| skill-optimize | rigby | 0/8 | - | - | MISSING | 0 | N (loose step files, unregistered) |
| system-eval | rigby | 0/7 | call, no json | - | yes+gcr | 20 | M (verifiers, spawn) |
| talking-points | harper | 0/3 | - | - | yes | 1 | N |
| training-module-runner | shep | 0/5 | - | - | yes | 0 | N (no Agent lines) |
| training-onboarding | shep | 0/4 | - | - | yes | 0 | N (no Agent lines) |
| training-status | shep | 0/2 | - | - | yes | 0 | N (no Agent lines) |
| watchtower | knox | 0/15 | call, no json | - | yes | 1 | N (table-row agents only) |
| weekly-knowledge-review | knox | broken refs | - | - | yes | 0 | N (6 step files missing) |
| weekly-review | master | 8/8 | - | - | yes | 0 | M (dropped candidate; spawn language) |
| win-loss-analysis | chase | 0/3 | - | - | yes | 0 | N |

## Violation classes (cross-system, by severity)

**Class 1 — Forbidden `git status` instructions (2):** dream-cycle step-05:68 (contradicts its own workflow.md's prohibition; worst instance), evolution-deployment workflow.md:54.

**Class 2 — Raw or weakly-routed git writes (1):** content-calendar step-05 (inline `git add/commit/push`, routing only via a passing note; contrast content-approval/content-discovery which mandate the skill).

**Class 3 — Structural breaks:** weekly-knowledge-review (workflow.md references 6 step files that do not exist — worst in system); skill-optimize (8 step files loose in the workflow root, no steps/); galen-monthly-health-review, knowledge-ingest, political-monitor, rock1-revenue-monthly, rock4-pipeline-weekly (steps defined inline in workflow.md, no steps/ dir); comp-tracker (frontmatter missing `model`; 3 orphaned stale step variants alongside the referenced numbered ones).

**Class 4 — Identity/registry defects:** evolution-training-sync owned by unregistered agent "shep-training"; 11 workflows with no Task Portfolio row (audience-target-outreach, content-pipeline, dream-cycle, episode-campaign-brief, error-improvement, evolution-training-sync, golf-preview, political-monitor, skill-optimize, system-eval, watchtower); routing.md lists "shutdown" under Chief's keywords while shutdown-cleanup is Rigby-owned (ambiguity); dream-cycle's owner "jarvis" has no persona file (folded into master.md — acceptable, document it).

**Class 5 — Missing assertions files (8):** account-pursuit-map, audience-target-outreach, boot-verification, content-approval, content-discovery, episode-campaign-brief, political-monitor, skill-optimize.

**Class 6 — Unbalanced system/personal comment blocks (3):** evolution-deployment step-06 (5 start / 4 end); shutdown-cleanup step-05 and shutdown-cleanup-verification step-01 (both created 2026-10-08 in the compliance pass — the author's own files; fix first).

**Class 7 — Spawn language missing (the dominant class, ~40 workflows):** bare `**Agent:** X` lines without spawn language (most non-compliant workflows), or no Agent line at all (card-review/walkthrough/which, lead-log/review, comp-tracker, training-module-runner/onboarding/status, watchtower's table-row-only ownership, evolution-deployment, evolution-training-sync, lead class), or table-row ownership only.

**Class 8 — Zero verifier coverage (35+ workflows, ~170 steps):** everything non-compliant plus system-eval (0/7), watchtower (0/15). Partial or misnamed coverage: golf-booking (2/8, non-exact names), golf-preview (2/5, non-exact), rock1 (1/2), rock4 (1/3).

**Class 9 — Exemplar-level gaps (3, small):** daily-review step-03b calls guardrail-checkpoint with no guardrails/step-03b json (the exemplar itself); system-eval and watchtower call the checkpoint with no json; boot-verification is 2-step (deliberate, document rather than restructure).

**Class 10 — state.yaml defects (2):** shutdown-cleanup state.yaml `agent: master` (stale 09-17 record); content-pipeline state.yaml has no agent field.

**Style (not certification-blocking):** em-dashes pervasive repo-wide including the exemplars (reported counts, no action proposed below the certified surface); several workflows (card-*, comp-tracker, content-pipeline) have no system:personal block structure at all.

## Correction plan (tiered, plan only)

### Tier 1 — Fix now (certification surface, ~1 session, Rigby) — **COMPLETE 2026-10-09** (all items: both unbalanced blocks balanced, shutdown-cleanup state.yaml agent, 3 missing guardrail checkpoint jsons, boot-verification spawn language + 2-step deviation documented, routing.md shutdown keyword removed, both git status instructions replaced with lock-free lists)
The 4 candidates, shutdown-cleanup, their verification sub-workflows, and the two exemplar gaps:
1. Balance the 2 unbalanced blocks in shutdown-cleanup step-05 and shutdown-cleanup-verification step-01 (author's own files).
2. shutdown-cleanup state.yaml agent field → rigby.
3. daily-review guardrails/step-03b-guardrail-checkpoint.json (mirror the step-03c pattern); same for system-eval and watchtower's pre-publish-review checkpoint.
4. boot-verification: spawn language for step-01; document the deliberate 2-step structure.
5. routing.md: remove "shutdown" from Chief's keyword row (Rigby owns shutdown-cleanup).
6. dream-cycle step-05:68 and evolution-deployment workflow.md:54 git status → lock-free lists.

### Tier 2 — Mechanical hygiene pass, all 62 (~2-3 sessions, scriptable, Rigby)
7. Spawn language: append the standard clause to every bare Agent line; add Agent lines where absent (~40 workflows, ~120 step files). Scriptable with a review pass.
8. Assertions files for the 8 missing (template: state-complete + working-memory pattern).
9. Registry: Task Portfolio rows for the 11 unregistered workflows (dream-cycle → jarvis/master documented as the memory persona); evolution-training-sync owner → shep with the shep-training label retired; a registry section for verification sub-workflows.
10. comp-tracker: add `model` frontmatter, delete the 3 orphaned step variants after a reference check (rigby-impact).
11. content-calendar step-05: route git through skills/git + ies-git wrapper (mirror content-approval's mandated-path language).
12. Balance evolution-deployment step-06's comment blocks; content-pipeline state.yaml agent field.

### Tier 3 — Structural repair (~2 sessions, Rigby, gated on David's decisions)
13. weekly-knowledge-review: restore or formally retire the 6 missing step files (workflow is currently unrunnable).
14. skill-optimize: move 8 loose step files into steps/.
15. Inline-spec workflows (galen-monthly-health-review, knowledge-ingest, political-monitor, rock1, rock4): either extract steps into steps/ dirs or accept and document the single-file form as a sanctioned variant of the standard.
16. golf-booking/golf-preview: rename misnamed verifiers to exact step-name matches.

### Tier 4 — Instrumentation by usage (the strategic decision, ~2 weeks if full scope)
Verifier coverage is the expensive class (~170 uncovered steps across 42 workflows). Three options:
- **A (recommended): certify the used surface.** Full per-step verifiers + adversarial wiring for the 10 workflows with real usage (the 4 candidates + shutdown-cleanup + dream-cycle 58 evals, system-eval 20, one-on-one-prep, partner-meeting-prep, client-meeting-prep, podcast-prep, content-* trio, watchtower as weekly standing flow). For the remaining ~32 zero-usage workflows, apply Tiers 2-3 hygiene only and disclose honestly to Tim: certified surface vs. legacy surface, with this audit as the boundary document.
- **B: instrument everything.** ~170 verifiers + adversarial wiring across 42 mostly-unused workflows; weeks of work, ongoing maintenance burden, and certification value is low for workflows that never run (a verifier on a workflow with 0 records can never record a pass).
- **C: prune the dead surface.** Combine with the Phase 0 rationalization memo: remove the never-used, skill-duplicated workflows (card-*, training-*, content-calendar, etc.) after rigby-impact scans and your approval; shrink the certified surface to what actually runs.

### Sequencing
Tier 1 immediately (it includes the author's own defects). Tier 2 next (mechanical, scriptable, unblocks honest registry). Tier 3 needs your call on items 13-15 (restore vs retire vs document-as-variant). Tier 4 needs your A/B/C decision — recommendation: A now, revisit C's pruning after the Stage 5 resubmission lands, so the pruning decision is not rushed before certification.

## Decisions needed from David
1. Tier 3 items: weekly-knowledge-review restore or retire? skill-optimize restructure? inline-spec workflows: extract or sanction the single-file form?
2. Tier 4: certify-the-used-surface (A), instrument everything (B), or prune the dead surface (C)?
3. weekly-review's fate: 8/8 verifiers exist and its structure is sound, but 0 eval records ever and it is already dropped from the candidate set. Keep as dormant-but-compliant, or fold into the quinn-weekly-review skill per the Phase 0 memo?
