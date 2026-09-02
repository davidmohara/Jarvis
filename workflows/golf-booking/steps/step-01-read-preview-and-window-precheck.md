---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 01: Read Preview Output and Booking-Window Pre-Check

## MANDATORY EXECUTION RULES

1. **Read preview-output.json first.** Never book blind — use the pre-scored preference order.
2. **Check for override instructions** in `preview-output.json` before selecting a slot.
3. **NEVER SUBSTITUTE A DIFFERENT DATE THAN THE ONE SPECIFIED — NO EXCEPTIONS.** If
   `override_instructions` or the ranked `top_options` specify a target date, and the
   ChronoGolf 8-day booking window does not yet include that date, this is NOT a signal to
   book the nearest available date instead. David's explicit instruction on the date and time
   is authoritative and must be followed exactly, or not at all. See
   `systems/error-tracking/entries/err-20260813T122205-D64IQ7.json` for the incident this
   guards against. **This is Quality Gate 1 below — it is the single most important rule in
   this entire workflow.**

---

## EXECUTION PROTOCOL

**Agent:** Sterling
**Input:** `workflows/golf-booking/preview-output.json`
**Output:** Validated target date/time confirmed to be inside the 8-day booking window

---

## YOUR TASK

Read `workflows/golf-booking/preview-output.json`.

Extract:
- `top_options` array (preference-ranked list)
- `override_instructions` (any redirect from David)
- `drought` flag
- `day_status` (to avoid hard-blocked days)

If `override_instructions` is not null, re-rank options accordingly before proceeding.

If the file doesn't exist or `top_options` is empty (and there is no `no_viable_reason`
explaining a legitimate zero-option week):
→ Send Slack: "⛳ Golf booking failed — no preview output found. Run preview manually or check
workflow state."
→ Abort. Set `status: aborted`.

If `top_options` is empty **with** a documented `no_viable_reason`: this is not a failure —
golf-preview already determined no viable window exists this week. Send Slack acknowledging
it and set `status: complete` with `resolution-note` copying the `no_viable_reason`. Do not
proceed further.

---

## QUALITY GATE 1 — Booking Window Pre-Check (HARD, BLOCKING, NO-SUBSTITUTION)

Compute whether the target date (from `override_instructions` if present, otherwise the
top-ranked option) falls within 8 days of today.

**If it does NOT:**
→ Do not open the date calendar. Do not pick a substitute date. Do not proceed to step-02 or
beyond.
→ Send Slack: "⛳ Booking window not yet open — [target date] at [target time] requires the
window to open first. Run will retry when the date is within 8 days. No booking made, no
substitution made."
→ Set `state.yaml` `status: awaiting-window`.
→ Abort this run cleanly. This rule overrides any other logic anywhere in this workflow that
could be read as license to pick "the closest available date." There is no such license.

**If it DOES fall within the window:** log the confirmation and proceed:
```
[Gate 1] Target date: YYYY-MM-DD at HH:MM — N days from today (within 8-day window) ✓
[Gate 1] PASS — proceeding to login.
```

Run the deterministic cross-check before moving on:
```bash
python3 workflows/golf-booking/verify/step-01-window-precheck.py <<< '{"ies_root": ".", "today": "<YYYY-MM-DD>"}'
```
This script re-derives the target date from `preview-output.json` (honoring
`override_instructions` if present) and independently confirms it is ≤ 8 days out. Treat a
`retry` result from this script exactly as a Gate 1 failure above — abort, do not substitute.

Store `target_date`, `target_time`, and `days_out` in this file's outputs and in
`state.yaml`'s `accumulated-context`. Set `current-step: step-02`.

---

## SUCCESS METRICS

- Gate 1 passes (or correctly routes to `awaiting-window`) before any Chrome automation begins
- No date substitution ever occurs

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `preview-output.json` missing or empty with no explanation | Slack alert, abort. |
| Target date outside window | `status: awaiting-window`. Retry on next scheduled run — do not re-evaluate or re-rank at that point, book exactly what was already validated. |
| `verify/step-01-window-precheck.py` disagrees with the inline calculation | Trust the script. Investigate the discrepancy before proceeding — do not silently pick one answer. |

## NEXT STEP

Read fully and follow: `step-02-login-recovery.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
