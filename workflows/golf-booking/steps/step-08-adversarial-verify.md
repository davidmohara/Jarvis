---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 08: Adversarial Verification: Cross-Check Booking Claims Against Confirmation Evidence

## MANDATORY EXECUTION RULES

1. You MUST spawn **Ralph** with `workflows/golf-booking-verification/workflow.md`. Do NOT self-verify, and do NOT let the producing agent grade its own booking. This is a separate spawn with a distinct lens.
2. You MUST wait for Ralph's verdict table before closing the run.
3. You MUST record the verdict via `guardrail-checkpoint.py` with checkpoint name `adversarial-verification`.
4. You MUST NOT edit state.yaml or a Slack message to make a finding disappear. Findings are surfaced and recorded as-is.
5. Ralph verifies claims against recorded state (the Gate results in the step outputs, `state.yaml`, the Gate 1 window arithmetic, the Slack confirmation). He does not book, cancel, or re-write anything.

---

## EXECUTION PROTOCOL

**Agent:** Sterling, spawned by the coordinator, never executed inline. Sterling spawns Ralph.
**Input:** The step 00-07 frontmatter `outputs`, `workflows/golf-booking/state.yaml`, `workflows/golf-booking/preview-output.json`, the Gate 3/4/6 evidence
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

---

## CONTEXT BOUNDARIES

- Scope is this run's booking: the window calculation, the confirmation, the visual verification, the calendar block, and the Slack confirmation.
- This step does not re-book or re-cancel. It checks whether the run's success claims hold up against the recorded evidence.
- Findings are a report, not a retry. A finding is surfaced and recorded.

---

## YOUR TASK

### Sequence

1. **Spawn Ralph.** Pass him:
   ```
   Agent: ralph
   Workflow: workflows/golf-booking-verification/workflow.md
   Manifest:
     step-outputs: workflows/golf-booking/steps/step-0{0..7}-*.md frontmatter outputs
     state: workflows/golf-booking/state.yaml
     preview-output: workflows/golf-booking/preview-output.json
     run-date: <YYYY-MM-DD>
   Task: Cross-check the booking's success claims against the confirmation evidence and return your verdict table.
   ```

2. **Receive Ralph's verdict table** (Item | Booking claim | Recorded evidence | Verdict) and its summary line. Do not soften or edit it.

3. **Derive the checkpoint result:**
   - All verified or not-applicable → `pass`.
   - Any minor mismatch (e.g., a summary count off by one, a calendar fallback not restated in the summary) → `flag`.
   - Any claim that matters → `escalate`: a booking claimed with no Gate 3 `BOOKING-SUCCESS` evidence, a Gate 4 skipped while success was claimed, a booked date that does not match the Gate 1 target (a silent date substitution), a double-booking (a prior booking still live while a new one is claimed), or a success claimed while `state.yaml` records `verification-failed`/`aborted`.

4. **Record the result:**
   ```bash
   python3 systems/eval-harness/guardrail-checkpoint.py golf-booking adversarial-verification step-07-slack-confirmation <pass|flag|escalate> "<one-line reason>"
   ```

5. **Write the verdict summary to state.yaml** under `accumulated-context.adversarial-verification`:
   ```yaml
   accumulated-context:
     adversarial-verification:
       verdict: "all-verified" | "findings"
       result: "pass" | "flag" | "escalate"
       findings: [list of unsupported booking claims, or empty]
       lens: "booking claims vs confirmation evidence; window calculated correctly, no double-booking, confirmation recorded before any success claim"
   ```

6. **On `escalate`:** halt and surface to David: `[Sterling]: Golf booking verification found [N] issue(s): [summary]. Do not assume the booking succeeded; holding for your review.` Wait for instruction.

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

This is the final step in golf-booking. The run is complete. On `escalate`, halt and wait for David's decision.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
