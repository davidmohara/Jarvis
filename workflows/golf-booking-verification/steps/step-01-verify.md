---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 01: Verify Booking Claims Against the Confirmation Evidence

## MANDATORY EXECUTION RULES

1. You MUST read the step outputs, state.yaml, and preview-output.json directly. Do NOT accept the run's own summary as evidence for its own claims.
2. You MUST return a verdict for every checklist item. No item may be omitted.
3. You MUST NOT book, cancel, or re-write anything. You verify and report; the caller decides.
4. If a source is missing or unreadable, mark the dependent items unverified. Do not infer correctness from silence.

---

## EXECUTION PROTOCOL

**Agent:** Ralph, Verification Agent
**Input:** Booking manifest (step output paths + run-date) from the caller
**Output:** Verdict table + one summary line, returned to the caller

---

## CONTEXT BOUNDARIES

- Scope is exactly this run's booking: the window check, the confirmation, the visual verification, the calendar block, and the Slack confirmation.
- Ralph does not re-book. He checks the claims that were made.

---

## YOUR TASK

### Sequence

1. **Locate the artifacts.** Read the step `outputs` frontmatter for steps 00-07, `workflows/golf-booking/state.yaml`, and `workflows/golf-booking/preview-output.json`.

2. **Apply the booking-claims-vs-evidence lens.** For each item, re-derive the truth from the record, then compare to the run's claims:

   | # | Checklist item | Ground truth source | Verdict |
   |---|----------------|---------------------|---------|
   | 1 | Window calculated correctly | Target date (preview-output.json, honoring override) vs run-date, 8-day window | Unverified if the claimed booking date is outside the window or was substituted |
   | 2 | Confirmation recorded before any success claim | Gate 3 `BOOKING-SUCCESS` evidence in step-04 outputs | Unverified if success is claimed with no `BOOKING-SUCCESS` |
   | 3 | Visual verification passed | Gate 4 outcome in step-05 outputs | Unverified if a success claim skipped Gate 4 or Gate 4 failed |
   | 4 | No double-booking | Any prior booking id in state.yaml vs the new booking | Unverified if a prior booking is still live alongside a new one |
   | 5 | Slack confirmation delivered | Gate 6 evidence in step-07 outputs, or a documented fallback | Unverified if no confirmation and no fallback |
   | 6 | Terminal outcome honest | state.yaml `booking-id`/`resolution-note` vs the claims | Unverified if a success is claimed while state records aborted/verification-failed |
   | 7 | Right-run check | Step timestamps and eval record vs this run | Unverified if claims are from a different run |

3. **Apply the "is there real confirmation evidence?" test** per item: Verified (claim traced to recorded evidence), Unverified (claim unsupported, or source unreadable), Not applicable (no booking progressed this run, a documented abort).

4. **Return the verdict table**, no preamble:

   ```
   | Item | Booking claim | Recorded evidence | Verdict |
   |------|---------------|-------------------|---------|
   | ...  | ...           | ...               | Verified / Unverified / N/A |
   ```

   Then one summary line:
   - If all verified or not-applicable: `All booking claims match the confirmation evidence: verified.`
   - If any unverified: `Findings: [items].`

5. **Update state.yaml** with `status: complete`, `current-step: step-01`, and record the verdict summary in `accumulated-context.verdict-summary` (`all-verified` or `findings`) plus `accumulated-context.findings: [list]`.

---

## SUCCESS METRICS

- Every checklist item has a verdict
- Each verified claim cites the recorded evidence it was traced to
- Any unverified item names the specific unsupported claim
- Verdict summary written to state.yaml

## FAILURE MODES

| Failure | Action |
|---------|--------|
| state.yaml unreadable | Mark all items Unverified with note "state unreadable." |
| No booking progressed (documented abort) | Mark booking items Not applicable; verify the terminal-outcome honesty item only. |
| A step output missing | Mark the dependent item Unverified with note "step output missing." |

---

## NEXT STEP

This is the final step. Return the verdict table to the caller. Workflow complete.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
