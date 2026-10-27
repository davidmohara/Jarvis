---
status: complete
started-at: '2026-10-26T14:58:10Z'
completed-at: '2026-10-26T14:58:40Z'
knox_status: success
knox_reason: 'eval record eval-20261026T141644-ES64TT (agent knox, plaud-ingest)
  status no-op; completed 2026-10-26T14:16:44Z with no-new-recordings, 0 staged,
  0 ingested, 0 skipped. plaud-discover eval-20261026T141650-CV37G4 also success.'
knox_eval_id: eval-20261026T141644-ES64TT
---

<!-- system:start -->
# Step 08: Knox Completion Check (Background Task Monitoring)

## MANDATORY EXECUTION RULES

1. Knox was spawned fire-and-forget in step-01 to process plaud-ingest workflow.
2. You MUST check its final status before marking boot complete.
3. Recording Knox's completion is informational — boot completion does not depend on Knox success.
4. You MUST log the outcome (success, failure, incomplete) so eval harness knows if background work finished.
---

## EXECUTION PROTOCOL

**Agent:** briefing subagent (Master persona), spawned by the coordinator after step-04 completes, never executed inline in the coordinator's session (see `workflow.md`).
**Input:** Knox eval record (if it exists in runs directory)
**Output:** Knox completion status recorded in frontmatter

---

## YOUR TASK

1. **Check for Knox eval record:**
   - Search `systems/eval-harness/runs/` for eval records matching:
     - `name: "plaud-ingest"` (or contains "knox")
     - `started` date matches current session (today)
     - Most recent record

2. **Determine status:**
   - If record found and `status: success`: Record "knox_completed_success"
   - If record found and `status: failure` or `status: partial`: Record "knox_completed_failure — [reason]"
   - If record found and `status: in_progress` or no completed time: Record "knox_still_running — background job still processing"
   - If no record found: Record "knox_no_eval_record — background job may not have started"

3. **Report Knox completion:**
   - Do NOT halt boot even if Knox failed — it's fire-and-forget background work
   - Surface Knox status to David as informational note in step output
   - If Knox escalated (has punch_out_signal), note that separately

4. **Update frontmatter:**
   ```yaml
   # state.yaml -> accumulated-context
   knox_status: "success" | "failure" | "still_running" | "no_record"
   knox_reason: "[detail about why]"
   knox_duration_seconds: N (if available)
   knox_eval_id: "[eval record ID]" (if found)
   ```

5. **Stamp this step's frontmatter.** Read the real clock with `date -u +%Y-%m-%dT%H:%M:%SZ`, then set `status: complete` and `completed-at` to that exact value. Do not estimate or round. (Step-07 already closed `workflows/boot/state.yaml`; do not rewrite it here.)

---

## Success Metrics

- Step checks for Knox eval record (success if attempted, regardless of result)
- Knox status is recorded (success, failure, running, or not_found)
- Boot completion is not blocked by Knox status

## Failure Modes

| Failure | Action |
|---------|--------|
| Knox eval record not found | Record "no_record" and continue. This is normal if Knox hasn't finished yet. |
| Knox status = in_progress | Record "still_running" and continue. Boot complete, Knox finishing in background. |
| Knox status = failure | Record failure reason. Continue boot. Note to David that plaud-ingest hit an issue. |
| Eval file read fails | Record "eval_read_error" and continue. Non-blocking. |

---

## WORKFLOW END

This is the final step. Boot is complete once Knox status is recorded here.

---

## Implementation Notes

This step records whether the fire-and-forget Knox background job finished. It never blocks boot.

<!-- system:end -->
