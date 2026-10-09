---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 06: Adversarial Verification: Cross-Check Preview Claims Against Weather and Course Source Data

## MANDATORY EXECUTION RULES

1. You MUST spawn **Ralph** with `workflows/golf-preview-verification/workflow.md`. Do NOT self-verify, and do NOT let the producing agent grade its own preview. This is a separate spawn with a distinct lens.
2. You MUST wait for Ralph's verdict table before closing the run.
3. You MUST record the verdict via `guardrail-checkpoint.py` with checkpoint name `adversarial-verification`.
4. You MUST NOT edit `preview-output.json` or a Slack message to make a finding disappear. Findings are surfaced and recorded as-is.
5. Ralph verifies claims against recorded state (the calendar pull, the weather source data, the drought check, `preview-output.json`). He does not re-score, re-fetch, or re-write anything.

---

## EXECUTION PROTOCOL

**Agent:** Sterling, spawned by the coordinator, never executed inline. Sterling spawns Ralph.
**Input:** The step 01-05 frontmatter `outputs`, `workflows/golf-preview/state.yaml`, `workflows/golf-booking/preview-output.json`, the weather source data for the target weekend
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

---

## CONTEXT BOUNDARIES

- Scope is this run's preview: the target weekend dates, the per-day calendar status, the drought flag, the weather scoring, and the scored options written to `preview-output.json`.
- This step does not re-score or re-fetch. It checks whether each claim holds up against the source data.
- Findings are a report, not a retry. A finding is surfaced and recorded.

---

## YOUR TASK

### Sequence

1. **Spawn Ralph.** Pass him:
   ```
   Agent: ralph
   Workflow: workflows/golf-preview-verification/workflow.md
   Manifest:
     step-outputs: workflows/golf-preview/steps/step-0{1..5}-*.md frontmatter outputs
     state: workflows/golf-preview/state.yaml
     preview-output: workflows/golf-booking/preview-output.json
     run-date: <YYYY-MM-DD>
   Task: Cross-check the preview's dates, calendar status, drought flag, and weather claims against the source data, and return your verdict table.
   ```

2. **Receive Ralph's verdict table** (Item | Preview claim | Recorded evidence | Verdict) and its summary line. Do not soften or edit it.

3. **Derive the checkpoint result:**
   - All verified or not-applicable → `pass`.
   - Any minor mismatch (e.g., a rounding difference in a weather figure, a Sunday flagged conditional) → `flag`.
   - Any claim that matters → `escalate`: a target date that is not the correct Friday/8-days-out, a day marked available against a hard calendar block, a `weather_data_missing` claim that contradicts the source, or a scored option that contradicts the recorded weather/calendar data.

4. **Record the result:**
   ```bash
   python3 systems/eval-harness/guardrail-checkpoint.py golf-preview adversarial-verification step-05-notify-slack <pass|flag|escalate> "<one-line reason>"
   ```

5. **Write the verdict summary to state.yaml** under `accumulated-context.adversarial-verification`:
   ```yaml
   accumulated-context:
     adversarial-verification:
       verdict: "all-verified" | "findings"
       result: "pass" | "flag" | "escalate"
       findings: [list of unsupported preview claims, or empty]
       lens: "preview claims vs weather/course source data; target dates correct, no day marked available against a hard block, weather claims match the source"
   ```

6. **On `escalate`:** halt and surface to David: `[Sterling]: Golf preview verification found [N] issue(s): [summary]. Holding before the booking workflow acts on this preview.` Wait for instruction.

7. **On `pass` or `flag`:** update step frontmatter (`status: complete`, `completed-at`, `outputs.verification_result`) and state.yaml (`current-step: null`), then close the run.

---

## SUCCESS METRICS

- Ralph was spawned (separate agent, distinct lens) and his verdict table received intact
- An `adversarial-verification` checkpoint result is recorded
- The verdict summary is written to state.yaml
- Any finding is surfaced to David, not silently absorbed

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Ralph fails to spawn | Record `result: flag` with reason "adversarial verification unavailable, Ralph not spawnable"; note it in the closing summary. Do not self-verify in place of Ralph. |
| Ralph returns a partial table | Record the partial result and note which items were missing. Do not suppress it. |
| `guardrail-checkpoint.py` fails to write | Still write the verdict summary to state.yaml; note the recording gap in the closing summary. |

---

## NEXT STEP

This is the final step in golf-preview. The run is complete. On `escalate`, halt and wait for David's decision.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
