---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 01: Verify Preview Claims Against the Weather and Calendar Source Data

## MANDATORY EXECUTION RULES

1. You MUST read the step outputs, state.yaml, preview-output.json, and the weather source directly. Do NOT accept the preview run's own summary as evidence for its own claims.
2. You MUST return a verdict for every checklist item. No item may be omitted.
3. You MUST NOT re-score, re-fetch, or re-write anything. You verify and report; the caller decides.
4. If a source is missing or unreadable, mark the dependent items unverified. Do not infer correctness from silence.

---

## EXECUTION PROTOCOL

**Agent:** Ralph, Verification Agent
**Input:** Preview manifest (step output paths + run-date + weather source) from the caller
**Output:** Verdict table + one summary line, returned to the caller

---

## CONTEXT BOUNDARIES

- Scope is exactly this run's preview: the target weekend, per-day calendar status, drought flag, weather scoring, and the options written to `preview-output.json`.
- Ralph does not re-score. He checks the claims that were made.

---

## YOUR TASK

### Sequence

1. **Locate the artifacts.** Read the step `outputs` frontmatter for steps 01-05, `workflows/golf-preview/state.yaml`, `workflows/golf-booking/preview-output.json`, and the weather source data for the target weekend.

2. **Apply the preview-claims-vs-source lens.** For each item, re-derive the truth from the source, then compare to the preview's claims:

   | # | Checklist item | Ground truth source | Verdict |
   |---|----------------|---------------------|---------|
   | 1 | Target dates correct | Weekday arithmetic: friday is a Friday, sat +1, sun +2, friday >= today+8 | Unverified if a date is the wrong weekday or inside the window |
   | 2 | Per-day status matches the calendar | Calendar pull vs `day_status` | Unverified if a day is `available` against a hard block |
   | 3 | Drought flag matches the calendar | Last golf round in the past 21 days vs `drought` | Unverified if the flag contradicts the calendar |
   | 4 | Weather claims match the source | Open-Meteo data vs the per-window rain/temp/wind in the options | Unverified if a scored option's weather contradicts the source |
   | 5 | `weather_data_missing` honest | Weather source availability vs the flag | Unverified if the flag is false while no weather source was reached |
   | 6 | Scored options consistent | Scores vs the recorded day status and weather | Unverified if an option's score contradicts its inputs |
   | 7 | Right-run check | Timestamps and generated_at vs this run | Unverified if claims are from a different run |

3. **Apply the "does the source actually say that?" test** per item: Verified (claim traced to the source data), Unverified (claim unsupported, or source unreadable), Not applicable (item genuinely has no content this run).

4. **Return the verdict table**, no preamble:

   ```
   | Item | Preview claim | Recorded evidence | Verdict |
   |------|---------------|-------------------|---------|
   | ...  | ...           | ...               | Verified / Unverified / N/A |
   ```

   Then one summary line:
   - If all verified or not-applicable: `All preview claims match the source data: verified.`
   - If any unverified: `Findings: [items].`

5. **Update state.yaml** with `status: complete`, `current-step: step-01`, and record the verdict summary in `accumulated-context.verdict-summary` (`all-verified` or `findings`) plus `accumulated-context.findings: [list]`.

---

## SUCCESS METRICS

- Every checklist item has a verdict
- Each verified claim cites the source data it was traced to
- Any unverified item names the specific unsupported claim
- Verdict summary written to state.yaml

## FAILURE MODES

| Failure | Action |
|---------|--------|
| state.yaml or preview-output.json unreadable | Mark all items Unverified with note "source unreadable." |
| Weather source unavailable | Mark weather-dependent items Unverified with note "weather source unreadable"; do not infer correctness. |
| A step output missing | Mark the dependent item Unverified with note "step output missing." |

---

## NEXT STEP

This is the final step. Return the verdict table to the caller. Workflow complete.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
