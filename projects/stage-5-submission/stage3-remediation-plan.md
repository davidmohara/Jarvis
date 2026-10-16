# Stage 3 Remediation Plan — Every Criterion Measured Below Its Own Threshold

**Author:** Rigby (System Operator)
**Date:** 2026-10-16
**Scope:** Master J1–J4, Chief C2/C4, Harper P3/P4, Knox K3/K4, Rigby R3/R4.
**Rule:** No threshold is lowered. Every fix below is either (i) a quality
improvement to an agent's output or (ii) a measurement correction. No bar moves.

Recomputed from `systems/eval-harness/runs/*.json` on 2026-10-16 with the
attribution layer (`step_audit.resolve_record_agent` + `merge_reporting_agent`).
Numbers here supersede the stage3 artifact files where they differ (the
attribution layer now recovers 1014 total records; a parallel agent's edits have
also drifted some counts). Small count differences from the artifacts are noted.

---

## Summary Table

| Agent | Criterion | Current (recomputed 2026-10-16) | Root cause | Specific fix (file paths) | Expected effect | Closable by code? |
|-------|-----------|-------------------------------|-----------|---------------------------|-----------------|-------------------|
| master | **J1** boot success = 100% | strict 21/55 = 38.2%; mech ~55% | (a)+(b) legitimate session-exit/superseded aborts counted as failures; 100% bar treats normal interactive exits as failures | none — definitional | n/a | **NO** — needs a definition/threshold decision by David |
| master | **J2** routing = 0 violations | 2 violations on record (`err-20260611T113806-g0pfoq`, `err-20260716T220729-FNAAP8`), both already remediated | (d) missing A/B evidence for the Phase-1 refactor | run a post-refactor boot with the routing-assertion hook (`assertions/boot.json` → `boot-009-step-owner-manifest`, already wired) | produces the required evidence; 0 new violations expected | **NO** — needs a live A/B run, not code |
| master | **J3** assertions ≥ 90% | 243/369 = 65.9% | (b) measurement artifacts dominate: dream-cycle glob mismatch, stale boot-008; (d) guardrail instrumentation gap | **IMPLEMENTED** `assertions/dream-cycle.json` glob fix; boot-008 already fixed in step-01.2 (stale result); guardrail = flag | **65.9% → 83.2%** (dream fix alone). +boot-008 stale (~85%). Full close needs guardrail instrumentation | **PARTIAL** — improves, does not close without the guardrail instrumentation fix |
| master | **J4** grade ≥ 80% | 13/18 = 72.2% | (b)+(a) 2 of 5 low grades are `incomplete` via session-exit-normal; 1 is a harness bookkeeping bug; 2 genuine | reclassify session-exit `incomplete`; fix `close-eval-record.py` zsh-quoting (SXPEU9) | **72.2% → ~83%** if the 2 session-exit incompletes are excluded as non-failures | **PARTIAL** |
| chief | **C2** outputs-non-empty = 100% | 35/63 = 55.6% | (a)+(c) daily-review/morning-briefing scheduled runs wrote no working-memory/output; sample is 2026-05…08 (pre-fix) | daily-review `step-auto` must write working memory; scheduled runner session_id refresh (see C4) | moves only when the scheduled runner is fixed + a fresh window is scored | **PARTIAL** |
| chief | **C4** grade ≥ 80% | 35/65 = 53.8% (70.6% excl. scheduled) | (a)+(d)+(c) 16 F = zero-duration phantom-success scheduled runs; 14 C = wm-missing / morning-briefing no-output | fix daily-review scheduled runner (`session_id` refresh) + add wm write to `step-auto` | **closes on a fresh window** if the phantom-success runner is fixed; no artifact fix moves the old F's | **PARTIAL** — the dominant driver is genuine |
| harper | **P3** assertions ≥ 90% | 34/49 = 69.4% | (b)+(a) `yaml_field_not_equals` unimplemented (2 assertions silently skipped/failed); wm-file globs; content-discovery quality | **IMPLEMENTED** `yaml_field_not_equals` + `content-pipeline.json` field-path fix; wm globs = flag | **69.4% → ~77.6%** (content-pipeline fix). Does not close | **PARTIAL** |
| harper | **P4** grade ≥ 80% | 5/7 = 71.4% | (a)+(b) F = content-discovery quality (paraphrase/wrong image/no links); C = webinar drafts didn't persist | update content-discovery gate (`assertions/content-discovery.json`); verify draft persistence | improves on n=7; too small to close | **PARTIAL** — needs David's read on "good" content |
| knox | **K3** assertions ≥ 90% | 178/238 = 74.8% (artifact says 73.9%) | (b)+(a) `plaud_ingest-wm-*` non-run-scoped glob (passes on aborted runs, fails on success runs); `plaud-001` singleton state.yaml; genuine aborts | **IMPLEMENTED** `date_path_template` wiring enables run-scoping; wm assertion re-scope = flag | improves modestly; the aborted-run share is genuine | **PARTIAL** |
| knox | **K4** grade ≥ 80% | 23/31 = 74.2% | (a)+(b) one recurring speaker-ID defect (err-20260929T024338-K3K074) + a status-vocabulary false positive at step-06 verification (G7M41N) + aborted/cutoff runs | normalize 'completed'/'complete' at verification checkpoints; speaker-ID from calendar invite | closes if the 4 C-grades' single defect is fixed and the status-vocab artifact removed | **PARTIAL** |
| rigby | **R3** assertions ≥ 90% | 199/230 = 86.5% | (b) stale system-eval assertions (`state.yaml` singleton check already removed as "broken"; run-record-success glob) | recompute affected records under the current assertion set; exclude superseded-assertion results | 86.5% → ~90%+ on the current set | **PARTIAL** — needs a recompute path |
| rigby | **R4** grade ≥ 80% | 17/24 = 70.8% | (b) **4 of 7 low grades are spurious records** from a `close-eval-record.py` session_id bug | **IMPLEMENTED** `find_stub` name-fallback; mark + exclude the 4 spurious records from the rollup | **70.8% → 85%** (17/20) excluding the 4 spurious | **YES** (with the record-exclusion step) |

---

## Per-Criterion Detail (evidence)

### master J1 — boot success = 100%
55 boot records: success 18, complete 3, partial 8, failure 4, **aborted 19**,
incomplete 3. Strict = 21/55 = 38.2%.
- The 19 aborts include legitimate non-failures. `eval-20261013T114019-Q5UJLE`
  is `status: success` with `abort_reason: session-exit-normal`;
  `eval-20261009T161630-E85YQQ` is `aborted` with `session-ended`. Counting
  these as J1 failures is a **definitional** artifact, not a quality gap.
- Genuine failures remain: `eval-20261014T125612-OKXI5A` (13 steps, aborted,
  no abort_reason, `completed: null`), `eval-20261014T131009-FV1BPN` (12 steps,
  aborted), `eval-20261014T131614-5AMWE5` (12 steps, aborted) — boots that were
  superseded or crashed mid-run with no recorded reason.
- **Root cause:** (a) genuine + (b) definitional. **Cannot be closed by code.**
  A 100%-of-all-boot-runs bar counts normal interactive session exits as
  failures. Options for David: (1) redefine J1's denominator to exclude
  `session-exit-normal`/`session-ended` aborts (the existing "mech" metric does
  this: 28/51 = 54.9%); (2) set a realistic bar (e.g. ≥ 90% of non-session-exit
  boots). Either is a threshold decision — **left for David.**

### master J2 — routing correctness (0 violations)
Two violations on record, both already remediated with log entries
(`err-20260611T113806-g0pfoq`, `err-20260716T220729-FNAAP8`). The
routing-assertion hook already exists (`assertions/boot.json` →
`boot-009-step-owner-manifest`, `check_step_owner_manifest`). **Root cause:**
(d) missing A/B evidence for the Phase-1 refactor. **Not closable by code** —
needs a live post-refactor boot run to produce the evidence.

### master J3 — structural assertions ≥ 90%  *(largest artifact lever)*
243/369 = 65.9%. Dominant failures:
- `dream-cy-002-substantive` **0/32** and `dream-cy-003-content` **0/32** — both
  check `memory/working/dream-cycle-*.md`, but the dream cycle writes
  `memory/working/dream-summary-*.md` (confirmed on disk:
  `dream-summary-2026-10-14.md`). The sibling assertion `dream-002` correctly
  uses `memory/working/dream-*.md` and passes **32/32**. **Pure measurement
  artifact (b).** → **IMPLEMENTED** (glob corrected to `dream-*.md`).
- `dream-004-guardrail-checkpoint-ran` **2/32** — the `pre-deletion-review`
  checkpoint is not recorded on successful runs (recent success runs carry
  `guardrails: 0`). The call exists
  (`workflows/dream-cycle/steps/step-03b-guardrail-checkpoint.md:44` calls
  `guardrail-checkpoint.py`), but `guardrail-checkpoint.py:65` only attaches to
  an eval record with `status == "in-progress"` — scheduled/Cowork runs create
  their record at close time, so there is no in-progress record when the
  checkpoint runs. **Missing instrumentation (d).** → flagged.
- `boot-008-omnifocus-filter-documented` **0/8** — the pattern now matches
  `workflows/boot/steps/step-01.2-unified-data-pull.md:114` (`"completed": false`).
  The stored failures predate that rewrite. **Stale result (b/c).** → no code fix.
- **Effect of the implemented fix:** 65.9% → **83.2%** (307/369). Adding the
  stale boot-008 → ~85%. Closing to 90% additionally requires the guardrail
  instrumentation fix.

### master J4 — Tier 3 grade ≥ 80%
13/18 = 72.2%. Five low grades:
- `eval-20260916T213408-6UYHX5` (D) — boot marked `incomplete` via
  **session-exit-normal** (expected, not a failure).
- `eval-20261013T120614-SXPEU9` (D) — boot `incomplete`; `close-eval-record.py`
  was invoked with malformed args (zsh mangling: `'(eval):1: ==STATE=== not
  found'`) so close-out never ran. **Harness bookkeeping bug.**
- `eval-20260916T200831-5K8EH5` (D) — genuine boot failure (no briefing
  delivered, 3 tool failures).
- `eval-20260630T203949-E747AF` (D) and `eval-20260630T194444-4NSY9M` (F) —
  genuine execution-quality issues (remarkable-upload 8+ iterations;
  genius-spark multiple corrections).
- **Root cause:** (b) 2 session-exit `incomplete` + 1 bookkeeping bug; (a) 2
  genuine. Reclassifying the 2 session-exit `incomplete` records as
  non-failures → ~83%. **Partially closable.**

### chief C2 — outputs-non-empty = 100%
`outputs_non_empty` = 35/63 = 55.6% (doc). The failing records are the same
daily-review scheduled runs that fail C4 — the working-memory file and/or the
`reviews/daily/auto-<date>.md` output was not written. Examples:
`eval-20260804T021410-VB8NM9` (review written, wm not),
`eval-20260806T021233-NTOEO1` (wm written, review not).
**Root cause:** (a) genuine + (c) sample is 2026-05…08. → see C4.

### chief C4 — Tier 3 grade ≥ 80%  *(chief's honest headline)*
35/65 = 53.8%; 70.6% excluding `trigger: scheduled`. 30 low grades:
- **16 F-grades** — all daily-review scheduled runs with **zero output**. The
  grader notes name it precisely: "phantom success — the workflow reports
  `status: success` but produces nothing"; "duration_seconds: 0.0 — workflow
  started and closed instantaneously"; root cause "**the scheduled runner's
  session_id refresh between runs**" (`eval-20260711T021151-T7AGFP`,
  `eval-20260707T021251-KHEVMG`, `eval-20260704T021304-XNRG5T`,
  `eval-20260620T021321-T6V6WJ`, `eval-20260602T021149-SL6FJ9`, …).
- **14 C-grades** — output written but working memory skipped, or
  morning-briefing output not written: `eval-20260728T021215-1C4F7E`,
  `eval-20260805T021415-1USR62`, `eval-20260804T021410-VB8NM9`,
  `eval-20260803T111340-VR2WKL`, `eval-20260804T111258-2MDD2A`. The notes name
  the fix: "**working memory write must be added to daily-review step-auto**."
- One note also flags the assertion harness: `eval-20260725T021309-IREQ63`
  (F) — "**Assertion harness bug: date_specific templates in the assertion
  definition [are not applied]**" → the glob false-passed on prior-day files.
  **IMPLEMENTED** (see "Implemented" below).
- **Root cause:** (a) genuine + (d) instrumentation + (c) old sample.
  **Partially closable** — the dominant driver (phantom-success scheduled
  runs) is a genuine workflow-execution gap, not a measurement artifact. The
  fix is the scheduled runner + `step-auto` wm write, then a fresh window.

### harper P3 — structural assertions ≥ 90%
34/49 = 69.4% (doc: 69.4%), 8 records carry assertions, 5 fail:
- `eval-20260825T171843-FA6SUZ`, `eval-20260824T201610-83XF3P`
  (content-pipeline): `messages-scanned`, `routing-outcome-recorded` fail —
  these use check type `yaml_field_not_equals`, which **did not exist** in any
  runner (grep: 0 definitions), so they were silently skipped/mis-evaluated;
  and the field paths (`accumulated-context.messages_scanned`,
  `accumulated-context.result`) don't match the workflow's actual schema
  (`workflows/content-pipeline/state.yaml` → `outputs.messages_scanned`,
  `outputs.outcome`). **Measurement artifact (b).** → **IMPLEMENTED**.
- `eval-20260916T165703-9EF0QS` (talking-points), `eval-20260904T202057-KL6KYK`
  (podcast-prep), and the content-pipeline pair: `*-001-exists/002-substantive/
  003-content` fail on `memory/working/<wf>-*.md` globs — the output files are
  absent. Genuine-or-naming — **flag**.
- `eval-20260915T060000-harper-content-discovery` (F): `posts-in-davids-voice`,
  `images-match-post-geography`, `internal-links-present` fail. Genuine content
  quality.
- **Effect:** content-pipeline fix moves the 4 field assertions to pass →
  **69.4% → ~77.6%**. Does not close.

### harper P4 — Tier 3 grade ≥ 80%
5/7 = 71.4%. Two low grades:
- `eval-20260915T060000-harper-content-discovery` (F) — "2 of 3 posts are
  paraphrases … rather than original writing in David's voice; DFW post used a
  non-DFW city skyline image; no posts contained required internal links. **Gate
  2 passed because it did not assert on these dimensions — the gate itself
  needs to be updated.**" Genuine quality + gate gap.
- `eval-20261015T181247-IPF4AW` (C) — GoTogether webinar drafts; execution
  followed spec and personalization was strong, but grading-time verification
  showed the drafts did not persist (`list_drafts` returned only stale drafts).
  Possibly an artifact (drafts created then cleaned) — **flag for verification**.
- **Root cause:** (a)+(b). **Partially closable.**

### knox K3 — structural assertions ≥ 90%
178/238 = 74.8% (doc: 73.9%). Dominant failures:
- `plaud_ingest-wm-written/-size/-content` — the glob
  `memory/working/plaud-ingest-*.md` is **not run-scoped**: it passes on aborted
  runs (matching a prior run's file) and fails on success runs (after cleanup).
  E.g. `eval-20260823T174645-MCQPCR` (aborted) passes all three;
  `eval-20260904T154747-M8U4JO` (success) fails all three. **Measurement
  artifact (b).**
- `plaud-001-state-complete` — fails on aborted runs (13). This is **correct**
  at write time (an aborted run has no complete state); not an artifact for the
  stored rate.
- `plaud-sp-002/003/004/005`, `plaud-tr-002/003`, `remarkab-004/005/006` — the
  speaker-ID / transcript / reMarkable runs that aborted or escalated.
- **Root cause:** (b) the wm glob + (a) genuine aborts. → **IMPLEMENTED**
  `date_path_template` wiring makes run-scoping possible; re-scoping the plaud
  wm assertions is a follow-up (flag).

### knox K4 — Tier 3 grade ≥ 80%
23/31 = 74.2%. Eight low grades:
- **4 C-grades** — one recurring defect: the speaker-ID escalation that drew
  the correction `err-20260929T024338-K3K074` ("speaker ID should be resolved
  from the calendar invite rather than asked of him"):
  `eval-20260928T162039-YXK7U3`, `eval-20260928T163649-ZQQBT7`,
  `eval-20260928T162517-VQC932`, plus the step-03 agent.
- **1 C-grade** — `eval-20261013T114211-G7M41N`: died at the step-06
  adversarial-verification checkpoint with "**a status-vocabulary false
  positive, not a real verification failure**" (`'completed'` vs `'complete'`).
  **Measurement artifact (b).**
- **3 F/D** — aborted/cutoff runs: `eval-20260928T162808-S03MX5` (poll agent,
  no output), `eval-20261013T151654-KYRQYV` and `eval-20261013T114209-IMZIBC`
  (aborted boot subagents, zero steps), `eval-20261015T151515-W2956A` (cut off
  before writing output). Genuine reliability + instrumentation.
- **Root cause:** (a) one recurring defect + (b) status-vocab artifact + (a)
  aborts. **Partially closable.**

### rigby R3 — structural assertions ≥ 90%
199/230 = 86.5%. Failures concentrate in **old** system-eval records
(2026-05…08):
- `system-eval state.yaml shows status: complete` (5 fails: `eval-20260627T040618-54LOEH`,
  `eval-20260609T151829-OUXB1P`, `eval-20260609T152224-SDY4MV`,
  `eval-20260620T040734-4OUQLT`, `eval-20260527T205926-PCHVJ1`) — this check
  has been **removed** from `assertions/system-eval.json` as "broken
  (state.yaml is overwritten to in-progress before assertions run)". **Stale
  result (b).**
- `Most recent eval run record reports status: success` (5/5 fail) and
  `system-eval output contains expected content` (6/0 fail) — glob-based
  checks on `runs/eval-*.json` and `grading/analysis-*.md`.
- The October window (n=38) is at 100%. **Root cause:** (b) superseded
  assertions + (c) old sample. **Partially closable** — needs a recompute under
  the current assertion set.

### rigby R4 — Tier 3 grade ≥ 80%  *(the cleanest measurement artifact)*
17/24 = 70.8%. Seven low grades, **four of which are spurious records**:
- `eval-20260718T041610-W4CIW9` (D) — "_spurious: this record was created by
  close-eval-record.py due to session_id mismatch — the real record is
  eval-20260718T040609-6D8CK8."
- `eval-20260725T041406-RL9YH6` (D) — "Spurious record created by
  close-eval-record.py session_id mismatch … not a real independent run."
- `eval-20260711T041415-8DNQT4` (F) — "Spurious record created by
  close-eval-record.py session_id mismatch … documents a script defect."
- `eval-20260708T204409-VFJBTD` (F) — "Spurious duplicate record … no valid
  data."
- The remaining three are genuine: `eval-20260527T205926-PCHVJ1` (aborted
  system-eval, 0 steps), `eval-20260527T185503-NDAYK6` (error-improvement
  aborted), `eval-20261013T210100-MO2LSH` (1.1M-token aborted run).
- **Root cause:** (b) measurement artifact. **Closable:** excluding the 4
  spurious → 17/20 = **85%** (over the 80% bar). **IMPLEMENTED** the root-cause
  fix in `close-eval-record.py`; the record-exclusion step is left for David
  (see below).

---

## Implemented (safe, mechanical, evidence-grounded)

1. **`systems/eval-harness/assertions/dream-cycle.json`** — `dream-cy-002-substantive`
   and `dream-cy-003-content` glob corrected from `memory/working/dream-cycle-*.md`
   to `memory/working/dream-*.md` (matches the working `dream-002` sibling and the
   on-disk `dream-summary-*.md`). Master J3 lever. Verified with a `/tmp`
   fixture: both now PASS.
2. **`systems/eval-harness/assertion_checks.py`** — implemented the missing
   `yaml_field_not_equals` check (dotted-path aware), registered in `CHECKS`.
   Harper P3 lever. Verified: `messages-scanned`/`routing-outcome-recorded`
   now evaluate (were silently skipped).
3. **`.claude/hooks/eval-turn-stop.py`** — parity: added `yaml_field_not_equals`
   and `date_path_template` handling to its independent `run_assertions`.
   Verified by import.
4. **`systems/eval-harness/assertions/content-pipeline.json`** — field paths
   corrected to the workflow's actual schema (`outputs.messages_scanned`,
   `outputs.outcome`).
5. **`systems/eval-harness/assertion_checks.py`** + **`.claude/hooks/eval-turn-stop.py`**
   — implemented the declared-but-unconsumed `date_path_template` /
   `date_specific` wiring (resolves `{run_date}` from the record's `run_date`
   or `started`; falls back to the bare glob when no date is derivable).
   Fixes the "date_specific templates are not applied" harness bug named in
   `eval-20260725T021309-IREQ63`'s grade note. Verified: a daily-review record
   with no same-date file now correctly FAILS `daily-002` (no more prior-day
   false pass); backward-compatible.
6. **`systems/eval-harness/close-eval-record.py`** — `find_stub` now falls back
   to a name-only in-progress match when no session-matched stub exists, so a
   session_id mismatch closes the real stub instead of fabricating a duplicate
   "spurious" record. Root-cause fix for Rigby R4. Verified with 4 fixture cases
   (session-mismatch fallback, session-match preferred, no-stub → None, closed
   records ignored).

**Regression check:** all six hook test suites pass
(`.claude/hooks/tests/test_detect_workflow.py` 32/32,
`test_eval_session_end.py`, `test_git_gate.py`, `test_ies_git.py`,
`test_skill_capture.py`, `test_step_token_capture.py`). All modified Python
compiles; both edited JSON files parse.

---

## Left for David (with reasons)

| # | Item | Reason |
|---|------|--------|
| 1 | **master J1** — redefine the denominator / bar | A 100%-of-all-boot-runs bar counts normal `session-exit-normal`/`session-ended` aborts as failures. This is a **threshold decision** — explicitly out of scope for me to change. |
| 2 | **master J2** — run the post-refactor A/B boot | Needs a live run to produce evidence; the routing hook is already wired. Not a code change. |
| 3 | **dream-004 / boot-004 guardrail instrumentation** | Scheduled/Cowork runs create their eval record at close time, so `guardrail-checkpoint.py` finds no in-progress record to attach to. The checkpoint *calls* exist; the fix is to create an in-progress record at run start for scheduled workflows — a runner change I won't make speculatively. This also gates master J3 reaching 90%. |
| 4 | **chief C4 / C2** — daily-review scheduled runner | The 16 F-grades are a genuine phantom-success defect (zero-duration runs, stale `session_id`) and the C-grades are a missing working-memory write in `step-auto`. Both are workflow-execution fixes, not measurement artifacts; the grade notes name them. Needs a fresh scored window after the fix. |
| 5 | **knox K4** — speaker-ID defect + status-vocabulary normalization | The recurring C-grades trace to one defect (`err-20260929T024338-K3K074`: resolve speaker ID from the calendar invite before asking). The status-vocab false positive (`'completed'` vs `'complete'` at verification checkpoints) is a small normalization fix — I left it because it touches the verification checkpoint vocabulary shared by several workflows and deserves a deliberate change. |
| 6 | **knox K3** — re-scope the `plaud_ingest-wm-*` assertions to the run date | The `date_path_template` mechanism is now wired (implemented); applying it to the plaud wm assertions is a one-line change, but it makes the assertion *stricter* (won't match historical files), so I left the choice to David. |
| 7 | **rigby R3** — recompute the old system-eval records under the current assertion set | The failures are stale results from assertions since removed/changed. Closing R3 requires a recompute path (or excluding superseded-assertion results) rather than an assertion edit. |
| 8 | **rigby R4** — mark + exclude the 4 spurious records from the rollup | The root-cause bug is fixed. Only 1 of the 4 spurious records carries the `_spurious` marker; marking the other 3 and excluding `_spurious` from the rollup (17/20 = 85%) is a **data correction** I did not want to make unilaterally — retroactively editing run records is sensitive. Recommend David approve. |
| 9 | **harper P4** — content-discovery gate + draft persistence | The F is genuine content-quality (paraphrase / wrong image / no internal links) and the gate "needs to be updated" to assert on those dimensions — that needs David's read on what "original in David's voice" means. The C (webinar drafts didn't persist) needs a live check of whether Superhuman drafts are being cleaned. |
| 10 | **harper P3 / chief C2 wm-file globs** | The `memory/working/<wf>-*.md` assertions fail where the workflow writes output elsewhere or not at all. Distinguishing "genuine missing output" from "wrong expected path" needs a per-workflow output-contract decision. |
