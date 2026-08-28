---
status: complete
started-at: "2026-08-28T16:06:00Z"
completed-at: "2026-08-28T16:04:49Z"
outputs:
  phase2_measurement_file: "[redacted for certification submission — internal business/schedule detail, not relevant to guardrail/workflow mechanism]"
  total_kb: "[redacted for certification submission — internal business/schedule detail, not relevant to guardrail/workflow mechanism]"
  total_tokens: "[redacted for certification submission — internal business/schedule detail, not relevant to guardrail/workflow mechanism]"
  measurement_method: "[redacted for certification submission — internal business/schedule detail, not relevant to guardrail/workflow mechanism]"
---

<!-- system:start -->
# Step 02.5: Measure Phase 2 Context Size (Instrumentation)

## MANDATORY EXECUTION RULES

1. You MUST measure accumulated-context size AFTER step-02 completes but BEFORE step-03 begins.
2. You MUST capture a snapshot of state.yaml for later comparison.
3. You MUST NOT alter or compact any data — this step is read-only measurement only.
4. You MUST record the measurement in outputs for David's review.

---

## EXECUTION PROTOCOL

**Agent:** Master (read-only instrumentation)
**Input:** Current state.yaml with accumulated-context from step-02
**Output:** Measurement snapshot written to `systems/boot-instrumentation/measurements/`

---

## CONTEXT BOUNDARIES

- This step is non-blocking — if measurement fails, proceed to step-03 anyway.
- Measurement is read-only; no data modification.
- Purpose: establish baseline before optimization changes are made.

---

## YOUR TASK

1. **Call the measurement script** to analyze accumulated-context:
   
   From bash in the IES root directory, run:
   ```bash
   IES_ROOT=/Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES \
   python3 systems/boot-instrumentation/measure.py measure-state workflows/boot/state.yaml
   ```

2. **Capture the output** which will include:
   - `total_size_bytes` — full accumulated-context size
   - `accumulated_context` — size and token count
   - `field_breakdown` — breakdown by top-level field (phase1, phase2, verification, etc.)
   
3. **Extract the top 5 bloat sources** from field_breakdown and surface to David:
   ```
   [Instrumentation] Phase 2 Context Measurement
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Total: {size_kb} KB (~{estimated_tokens} tokens)
   
   Top bloat sources:
   1. {field_name}: {size_kb} KB
   2. {field_name}: {size_kb} KB
   3. {field_name}: {size_kb} KB
   
   Snapshot: systems/boot-instrumentation/measurements/measurement-state-{timestamp}.json
   
   (No action needed — proceeding to step-03)
   ```

4. **Store measurement path** in outputs:
   ```yaml
   outputs:
     phase2_measurement_file: "systems/boot-instrumentation/measurements/measurement-state-{timestamp}.json"
     total_kb: N
     total_tokens: N
   ```

5. **Update step frontmatter:** Set `status: complete` and `completed-at` with current timestamp.

6. **Update state.yaml:** Set `current-step: step-03-verify-phase2.md`.

---

## SUCCESS METRICS

- Measurement snapshot written to disk
- Size breakdown captured (bytes, KB, tokens)
- Largest fields identified
- No data was modified
- David sees the baseline numbers

## FAILURE MODES

| Failure | Action |
|---------|--------|
| JSON serialization fails | Record failure. Continue to step-03 anyway — measurement is optional. |
| File write fails | Log error. Continue to step-03. |
| accumulated-context is empty | Record: "No data to measure (early boot termination)". Continue. |

---

## NEXT STEP

Read fully and follow: `step-03-verify-phase2.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
