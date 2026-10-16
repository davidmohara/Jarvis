# Adversarial Catches

Human-readable rendering of `catches.jsonl` (the canonical machine-readable log).
Format and the honesty bar are defined in `README.md`.

**5 catches as of 2026-10-16.** Only real discrepancies are listed; see the README's
"Honest status" for how thin this is.

---

## CATCH-01: Harness mislabeled six completed specialist runs as aborted

- **Date:** 2026-10-16 · **Workflow:** eval-harness · **Status:** fixed
- **Producing agent:** eval-harness (record writer)
- **Claim:** six specialist runs spawned 2026-10-16 were written as
  `status: aborted`, `agent: general-purpose`, `owning_agent: null`, `steps: []`.
- **Ground truth:** all six ran to completion and each belongs to a named specialist.
  Their subagent transcripts end in an explicit final report / handback
  (`transcript_indicates_completion()` returns True for all six), and read-side
  attribution resolves each to its real owner.
- **Caught by:** Stage 3 Phase 0 attribution audit (the `SubagentStart` payload carries
  no prompt text, so the spawn-prompt detector never fired), then the fix run's
  transcript-based completion + attribution check.
- **Evidence (the six runs):**
  | record | recovered owner | run description |
  |--------|-----------------|-----------------|
  | `eval-20261016T130603-H4T7VY` | shep | Shep 1:1 prep run for Alice wrap-up |
  | `eval-20261016T130610-LXM5KV` | sterling | Sterling inbox sweep and social tracker run |
  | `eval-20261016T130611-CBDMA2` | galen | Galen morning snapshot measured run |
  | `eval-20261016T130736-SZNXC2` | harper | Harper talking points for Leadership Dallas |
  | `eval-20261016T130739-KR7TL6` | chase | Chase client prep for GEHC check-in |
  | `eval-20261016T130756-B0685R` | quinn | Quinn goal alignment measured run |
- **Disposition:** fixed in commit `56488e15` (read-side `resolve_record_agent`
  recovery from `agent_transcript_path`/`agent_id` + transcript-derived completion).
  Historical records are not rewritten; recovery happens at read time.

---

## CATCH-02: Boot records claim success with no pre-completion guardrail

- **Date:** 2026-10-16 · **Workflow:** boot · **Status:** quarantined
- **Producing agent:** master (record written from `workflows/boot/state.yaml`,
  `status: complete`)
- **Claim:** the record carries `status: success`, `expected_outputs_written: true`,
  `outputs_non_empty: true`.
- **Ground truth:** the record has `steps: []` and no `guardrails` array, so there is
  no evidence the step-06.5 `pre-completion-review` guardrail checkpoint ran.
- **Caught by:** assertion `boot-004-guardrail-checkpoint-ran`
  (`checkpoint_name: pre-completion-review`).
- **Evidence:** `_phantoms/eval-20261015T143056-XJKYTT.json`,
  `_phantoms/eval-20261015T143247-KOMF4O.json`,
  `_phantoms/eval-20261005T162730-Z5UEJH.json`.
- **Disposition:** quarantined. The phantom guard (commit `adc09ccc`) routes
  empty-steps cowork-hook stubs to `runs/_phantoms/` so metrics readers skip them. The
  state.yaml-vs-record mismatch is the phantom-stub artifact, not a live boot failure.

---

## CATCH-03: Morning-briefing claimed complete with no adversarial verification

- **Date:** 2026-10-16 · **Workflow:** morning-briefing · **Status:** open
- **Producing agent:** chief
- **Claim:** the briefing run recorded `status: success` (steps 01-04 complete) and
  `step-05-verify-briefing` recorded success; step-05's protocol sets `state.yaml`
  `status: complete`.
- **Ground truth:** no `adversarial-verification` guardrail is on the record, so Ralph's
  calendar/email/OmniFocus cross-check did not run. On `eval-20261015T142239-SVVBCP` the
  record status is `partial` and the only guardrail is `pre-synthesis-review`;
  `step-05` shows success but the verification it exists to perform left no evidence.
- **Caught by:** assertion `morning-008-adversarial-verification-ran`
  (`checkpoint_name: adversarial-verification`).
- **Evidence:** `eval-20261009T160313-SN12N3.json` (success, 4 steps, guardrails `[]`),
  `eval-20261015T142239-SVVBCP.json` (step-05 success, no adversarial-verification
  guardrail), `_phantoms/eval-20261014T131751-1VCMGN.json` (success, morning-008 failed).
- **Disposition:** recorded-sentinel. Phase 4A wired step-05 to spawn Ralph and record
  the guardrail on every run; the assertion now fails any run that skips it.

---

## CATCH-04: Daily review claimed success with no guardrails at all

- **Date:** 2026-10-16 · **Workflow:** daily-review · **Status:** open
- **Producing agent:** chief
- **Claim:** the daily review recorded `status: success` with 6 steps complete.
- **Ground truth:** the record carries an empty `guardrails` array, so neither the
  `pre-commit-review` checkpoint nor the step-03c `adversarial-verification` checkpoint
  ran; the run also produced no working-memory artifact for the run date.
- **Caught by:** assertions `daily-007-adversarial-verification-ran`,
  `daily-006-guardrail-checkpoint-ran`, `daily_review-wm-written/size/content`.
- **Evidence:** `eval-20261009T222114-63PRWC.json` (success, 6 steps, guardrails `[]`).
- **Disposition:** recorded-sentinel. step-03c now spawns Ralph before the commit;
  the assertions fail any run that skips it.

---

## CATCH-05: Plaud-ingest records claim success with no ingestion-accounting verification

- **Date:** 2026-10-16 · **Workflow:** plaud-ingest · **Status:** open
- **Producing agent:** knox
- **Claim:** the plaud-ingest records carry `status: success` (written from
  `workflows/plaud-ingest/state.yaml`, `status: complete`, outcome `no-new-recordings`).
- **Ground truth:** the records have `steps: []` and no `guardrails` array, so step-06's
  ingestion-accounting adversarial verification (Ralph) did not run and left no
  evidence; the required timestamped `plaud-ingest-*.md` working-memory file is also
  absent from `memory/working/`.
- **Caught by:** assertions `plaud-002-adversarial-verification-ran` and
  `plaud_ingest-wm-written/size/content`.
- **Evidence:** `_phantoms/eval-20261007T142008-IIUVI6.json`,
  `_phantoms/eval-20261009T160725-C8Y5GY.json`,
  `_phantoms/eval-20261013T114517-LYOMRC.json`,
  `_phantoms/eval-20261014T130313-JM12CI.json`,
  `_phantoms/eval-20261015T140022-XQBT3L.json`,
  `eval-20261009T160824-LCEFD5.json` (status complete, `plaud_ingest-wm-*` failed).
- **Disposition:** recorded-sentinel / quarantined. step-06 now spawns Ralph and records
  the guardrail; phantom stubs are quarantined.

---

## What the verification did NOT find (honesty note)

- No `state.yaml` among the four candidates claims `complete` with its **primary**
  artifact missing or empty. Boot's data files, the 2026-10-15 morning briefing, and
  `reviews/daily/2026-10-09.md` all exist and are substantive; plaud-ingest's
  2026-10-15 run is a vacuous no-op (`no-new-recordings`).
- The `plaud_ingest-wm-*` / `daily_review-wm-*` failures in CATCH-04/CATCH-05 are
  recorded as assertion failures; the working-memory files are genuinely absent from
  `memory/working/` today. Caveat: those files are not claimed explicitly by the
  current `state.yaml` fields, and the naming convention has varied historically, so
  this is the weakest of the five findings.
- The many `boot-004` failures on **aborted/incomplete** boot records (2026-10-07..14)
  are expected (the run aborted before step-06.5) and are therefore NOT logged as
  catches.
