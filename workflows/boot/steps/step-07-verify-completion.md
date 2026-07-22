---
status: complete
started-at: "2026-07-22T11:22:00-05:00"
completed-at: "2026-07-22T11:23:00-05:00"
outputs:
  verification: passed
  steps_verified: 6
  failed_steps: []
---

<!-- system:start -->
# Step 07: Verify Boot Completion

## MANDATORY EXECUTION RULES

1. You MUST check every prior step's frontmatter status. No step is exempt — including step-01.
2. This step is a hard gate. Boot is NOT complete until this step passes.
3. If any step failed verification, boot status MUST remain `in-progress`. Do NOT mark complete.
4. Do NOT skip this step for any reason — not for time, not because boot "felt complete."

---

## EXECUTION PROTOCOL

**Agent:** Master
**Input:** Frontmatter status of steps 01–06
**Output:** Verification report surfaced to controller; boot marked complete only if all steps pass

---

## CONTEXT BOUNDARIES

- This step reads step frontmatter only. It does not re-execute any prior step.
- A step with `status: complete` passes. All other statuses fail.
- A missing step file is a failure — surface it as such.

---

## YOUR TASK

1. **Read the frontmatter of every prior step file in order:**
   - `steps/step-01-load-context.md`
   - `steps/step-02-gather-data.md`
   - `steps/step-03-verify-phase2.md`
   - `steps/step-04-gather-meeting-context.md`
   - `steps/step-05-synthesize-briefing.md`
   - `steps/step-06-scan-workflows.md`

2. **For each step, record:**
   - `status` field value
   - `completed-at` timestamp (if present)
   - PASS if `status: complete` — FAIL otherwise

3. **Compute the overall result:**
   - **PASS** — all 6 steps show `status: complete`
   - **FAIL** — one or more steps are not complete

4. **Surface the verification report to the controller:**

   If PASS:
   > ✓ Boot verification passed. All 6 steps completed.
   > | Step | Status | Completed At |
   > |------|--------|--------------|
   > | step-01-load-context | complete | {timestamp} |
   > | step-02-gather-data | complete | {timestamp} |
   > | ... | ... | ... |

   If FAIL:
   > ✗ Boot verification FAILED. The following steps did not complete:
   > | Step | Status | Action Required |
   > |------|--------|-----------------|
   > | step-03-verify-phase2 | not-started | Re-execute this step before boot can be marked complete |
   >
   > Boot is NOT complete. Say `resume boot` to continue from the failed step.

5. **If PASS only:** Update step frontmatter and boot state:
   - Set this step's `status: complete` and `completed-at` with current timestamp
   - Set `outputs: { verification: passed, steps_verified: 6, failed_steps: [] }`
   - Update `workflows/boot/state.yaml`: `status: complete`, `current-step: null`, record `completed-at`

6. **If FAIL:** Do NOT update boot state.yaml to complete. Leave `status: in-progress` and set `current-step` to the first failed step. Surface the failure and await controller instruction.

---

## SUCCESS METRICS

- All 6 prior step files read
- Each step's status evaluated against the pass criteria
- Verification report surfaced to the controller
- Boot marked complete if and only if all steps passed
- Boot left in-progress if any step failed, with failed steps identified

## FAILURE MODES

| Failure | Action |
|---------|--------|
| A step file is missing | Treat as FAIL. Surface: "step-0N file not found — cannot verify." |
| A step shows `status: in-progress` | Treat as FAIL. The step was interrupted. Surface it for re-execution. |
| A step shows `status: not-started` | Treat as FAIL. The step was skipped. Surface it for execution. |
| A step shows `status: skipped` | Treat as FAIL unless the step's own instructions explicitly authorize skipping. Surface for review. |
| This step's own frontmatter shows in-progress on resume | Re-execute from the top of YOUR TASK. Do not trust partial verification results. |

---

## NEXT STEP

None. If verification passed, boot workflow is complete.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
