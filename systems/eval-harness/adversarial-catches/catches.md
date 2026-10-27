# Adversarial Catches

Human-readable rendering of `catches.jsonl` (the canonical machine-readable log).
Format and the entry bar are defined in `README.md`.

**8 catches as of 2026-10-26.** CATCH-01..05 are assertion-level catches (2026-10-16);
CATCH-06..08 are lens-level catches by the verification sub-workflows themselves,
recorded 2026-10-26 from the verification runs' own state. See the README's
Status section defines the bar.

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
- **Caught by:** attribution audit (the `SubagentStart` payload carries
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
- **Disposition:** recorded-sentinel. Step-05 was wired to spawn Ralph and record
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

## CATCH-06: Morning briefing overstated calendar warnings and unconfirmed dates

- **Date:** 2026-10-19 · **Workflow:** morning-briefing · **Status:** recorded
- **Producing agent:** chief
- **Claim:** delivered briefing stated calendar warnings, Teams-call placement, a
  Rock 5 due date, a SPARC package-in-inbox note, and a GoTogether reminder as fact.
- **Ground truth:** 41 of 46 claims verified; 5 did not hold. The calendar warning
  overstates (the full-day bootcamp block does not collide with Hot 26 or Prayer
  Call), is imprecise about open gaps, and the three Teams calls do not all sit inside
  the bootcamp block. The Rock 5 Dec 15 date is proposed/soft-confirmed in source.
  The SPARC package-in-inbox claim is not confirmed by the recorded email snippet.
  The GoTogether reminder is gone from `data/reminders.json` though boot state
  recorded it due.
- **Caught by:** Ralph via `workflows/morning-briefing-verification/`
  (briefing-vs-source lens). Verified 41, unverified 5.
- **Evidence:** `workflows/morning-briefing-verification/state.yaml`
  (findings, verified-count 41, unverified-count 5);
  `memory/working/morning-briefing-2026-10-19-161051.md`.

---

## CATCH-07: Daily review claimed captures and numbers the source state contradicts

- **Date:** 2026-10-20 · **Workflow:** daily-review · **Status:** recorded
- **Producing agent:** chief
- **Claim:** daily review recorded capture outputs, 7 GoTogether drafts confirmed
  sent, 140 uncompleted OmniFocus tasks, GEHC deep-dive at 14:00-15:00, bootcamp
  attendance, and a complete System State section.
- **Ground truth:** no persisted capture outputs in `workflows/daily-review/state.yaml`
  (same-session working memory only); no sent record for the 7 drafts and
  `err-20261019T214500-FRIED1` records at least one draft address invalid;
  `data/omnifocus-unified.json` shows 42 uncompleted, not 140; the GEHC deep-dive is
  11:00-12:00 per `data/calendar-unified.json` (the review also drops the real 11:00
  SAP Group collision); no attendance record backs "attended"; two boot-state items
  (conventions-migration in-progress since 2026-10-18, step-03b eval-recording
  failures) are silently absent from the review's System State.
- **Caught by:** Ralph via `workflows/daily-review-verification/`
  (output-vs-source-data lens). 10 verified blocks, 6 findings.
- **Evidence:** `workflows/daily-review-verification/state.yaml` (findings, verified
  list); `reviews/daily/2026-10-19.md`.

---

## CATCH-08: Plaud-ingest primary outcome verified; integrity findings around it

- **Date:** 2026-10-09 · **Workflow:** plaud-ingest · **Status:** recorded
  (integrity findings; primary outcome verified)
- **Producing agent:** knox
- **Claim:** 2026-10-09 run recorded complete with 2 recordings ingested-note +
  shared + monday-review-task.
- **Ground truth:** both recordings verified against the vault (note-verified true,
  frontmatter file_id match true). The verification additionally found non-blocking
  integrity issues: step frontmatter timestamps stale (2026-09-18/28, never
  reflecting the 2026-10-09 run), the eval record `eval-20261009T160824-LCEFD5` left
  in-progress while workflow state was complete, one recording carrying an unresolved
  Speaker 5 (12 segments) plus a flagged mis-tag, and one orphan `plaud_pending.json`
  entry no longer in the API.
- **Caught by:** Ralph via `workflows/plaud-ingest-verification/`
  (ingest-completeness lens).
- **Evidence:** `workflows/plaud-ingest-verification/state.yaml` (recordings
  verified, findings F1-F5).

---

## What the verification did NOT find

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
