---
status: complete
started-at: "2026-08-25T17:15:00Z"
completed-at: "2026-08-25T17:15:30Z"
outputs:
  state_status: "complete — all 10 prior step files verified status:complete, boot state.yaml updated with completion timestamp, session index present"
  verification: passed
  steps_verified: 10
  failed_steps: []
  guardrail_checkpoint: "pre-completion-review: pass"
  note: "All prior steps completed successfully. Boot workflow complete. Knox spawned for plaud-ingest; returned mid-run and awaiting David's input on speaker ID for ~44 recordings — surfaced separately, not a boot blocker."
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
   - `steps/step-06.5-guardrail-checkpoint.md`

2. **For each step, record:**
   - `status` field value
   - `completed-at` timestamp (if present)
   - PASS if `status: complete` — FAIL otherwise. **Exception: step-06.5 also passes on `status: complete` with a recorded `escalate` guardrail result** — an escalation is a deliberate halt-for-human-decision, not a step failure (see `guardrail-checkpoint.py`); if step-06.5 escalated, note it in the report but do not treat it as a FAIL on its own — surface it as its own line, distinct from a failed step.

3. **Compute the overall result:**
   - **PASS** — all 7 steps show `status: complete`
   - **FAIL** — one or more steps are not complete

4. **Surface the verification report to the controller:**

   If PASS:
   > ✓ Boot verification passed. All 7 steps completed.
   > | Step | Status | Completed At |
   > |------|--------|--------------|
   > | step-01-load-context | complete | {timestamp} |
   > | step-02-gather-data | complete | {timestamp} |
   > | ... | ... | ... |
   > | step-06.5-guardrail-checkpoint | complete | {timestamp} |

   If PASS but step-06.5 escalated:
   > ✓ Boot verification passed (7/7 steps complete). Note: the guardrail checkpoint escalated — [reason from the checkpoint]. This needs your attention but did not block boot.

   If FAIL:
   > ✗ Boot verification FAILED. The following steps did not complete:
   > | Step | Status | Action Required |
   > |------|--------|-----------------|
   > | step-03-verify-phase2 | not-started | Re-execute this step before boot can be marked complete |
   >
   > Boot is NOT complete. Say `resume boot` to continue from the failed step.

5. **If PASS (including the escalated-but-complete case):** Update step frontmatter and boot state:
   - Set this step's `status: complete` and `completed-at` with current timestamp
   - Set `outputs.state_status` with a summary (e.g. "complete — all 7 prior steps verified, boot state.yaml updated with completion timestamp")
   - Set `outputs: { verification: passed, steps_verified: 7, failed_steps: [] }`
   - **Update `workflows/boot/state.yaml`: `status: complete`, `current-step: null`, record `completed-at`. This write is mandatory — it's the only event that closes out boot's eval-harness record. Do not defer it, do not skip it because the session is ending anyway.**

6. **If FAIL:** Do NOT update boot state.yaml to complete. Leave `status: in-progress` and set `current-step` to the first failed step. Surface the failure and await controller instruction.

---

## SUCCESS METRICS

- All 7 prior step files read
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
