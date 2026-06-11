---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 03: Verify Phase 2 (Phase 2.5)

## MANDATORY EXECUTION RULES

1. You MUST run `workflows/boot-verification/workflow.md` before proceeding. Do not skip or self-verify.
2. You MUST wait for Ralph's verdict table before proceeding to step-04. This step is blocking.
3. Any task marked ⚠️ Unverified or ❌ Skipped must be re-run before step-04 begins.
4. Do NOT proceed to step-04 until all tasks are ✅ or ➖ (not applicable).

---

## EXECUTION PROTOCOL

**Agent:** Master
**Input:** Phase 2 task outcomes from `accumulated-context` in state.yaml
**Output:** Ralph's verification verdict; any re-runs completed

---

## CONTEXT BOUNDARIES

- Ralph verifies claims — he does not re-run tasks himself. Re-runs are Master's responsibility.
- Task E (Plaud/Knox) is expected to be fire-and-forget — Ralph will mark it ➖ if Knox was spawned correctly.
- If Ralph returns a verdict and then step-04 begins but Ralph's verdict has a failed task, that is a protocol violation. Do not proceed until clean.

---

## YOUR TASK

1. **Pass the Phase 2 task manifest to boot-verification.** Run `workflows/boot-verification/workflow.md`. Provide Ralph with the accumulated-context from state.yaml as the task manifest. The manifest covers:
   - Morning briefing steps 01-02
   - Task E: Plaud ingest (Knox spawn)
   - Task F: Lead review
   - Task G: 72-hour look-ahead
   - Task H: Email triage
   - Task I: Jarvis inbox

2. **Wait for Ralph's verdict table.** Ralph will return a table in the format:

   | Task | Status | Notes |
   |------|--------|-------|
   | Morning briefing 01-02 | ✅ Verified | ... |
   | Task E: Plaud ingest | ➖ Fire-and-forget | Knox spawned |
   | Task F: Lead review | ✅ Verified | ... |
   | Task G: 72hr look-ahead | ✅ Verified | ... |
   | Task H: Email triage | ⚠️ Unverified | No email data found in context |
   | Task I: Jarvis inbox | ✅ Verified | ... |

3. **Handle any flagged tasks:**
   - For each task marked ⚠️ Unverified: re-run that task now. Update accumulated-context with the new result.
   - For each task marked ❌ Skipped: re-run that task now. This is a protocol violation that must be corrected before proceeding.
   - For tasks marked ✅ or ➖: no action needed.

4. **Confirm all tasks are ✅ or ➖** before proceeding.

5. **Update step frontmatter:** Set `status: complete` and `completed-at` with current timestamp.

6. **Update state.yaml:** Set `current-step: step-04-gather-meeting-context.md`.

---

## SUCCESS METRICS

- boot-verification workflow was run (not skipped)
- Ralph's verdict received and reviewed
- All ⚠️ and ❌ tasks re-run before proceeding
- No tasks remain unverified or skipped when step-04 begins

## FAILURE MODES

| Failure | Action |
|---------|--------|
| boot-verification workflow unavailable | Self-verify using the accumulated-context: manually confirm each task reported a status. Note: "Boot verification unavailable — self-verified." Surface this in the briefing. |
| Ralph spawn fails | Same as above — fall back to self-verification. |
| A re-run task fails again | Record failure in accumulated-context. Surface in briefing as degraded data. Do not loop indefinitely — one re-run attempt per task. |
| Ralph verdict is missing entries | Ask Ralph to re-check the manifest. If Ralph is unavailable, proceed with self-verification. |

---

## NEXT STEP

Read fully and follow: `step-04-gather-meeting-context.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
