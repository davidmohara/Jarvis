---
status: complete
started-at: "2026-07-22T11:20:00-05:00"
completed-at: "2026-07-22T11:22:00-05:00"
outputs:
  in_flight_workflows: []
  result: "No in-flight workflows besides boot itself (expected, current run). Flagged for controller attention: shutdown-cleanup blocked at step-04-git-commit since 2026-07-16 (stale FUSE lock, 14 files staged and ready); golf-booking failure on 2026-07-18 (booked before 1:00 PM hard minimum, rule violation, grade F); plaud-ingest aborted 2026-07-15 (missing API token)."
---

<!-- system:start -->
# Step 06: Scan In-Flight Workflows (Phase 5)

## MANDATORY EXECUTION RULES

1. You MUST read state.yaml in every workflows/*/ directory. No workflow directory is exempt.
2. Surface any `status: in-progress` workflow immediately after the briefing. Do not bury it.
3. Do NOT auto-resume any in-progress workflow. Surface only. Await controller instruction.
4. This step concludes boot. Set workflow status to complete when done.

---

## EXECUTION PROTOCOL

**Agent:** Master
**Input:** All `workflows/*/state.yaml` files
**Output:** List of any in-progress workflows surfaced to the controller; boot marked complete

---

## CONTEXT BOUNDARIES

- This step is informational only. Read and report. Do not take action on any workflow.
- `status: not-started` and `status: complete` workflows are not surfaced — they are noise.
- `status: aborted` workflows may be surfaced with a brief note, but they are lower priority than in-progress.

---

## YOUR TASK

1. **Read `state.yaml` in every `workflows/*/` directory.**
   Scan all workflow state files and capture:
   - `workflow` name
   - `status`
   - `current-step` (if in-progress)
   - `session-started` (if available)

2. **Filter for actionable states:**
   - `status: in-progress` — surface immediately. These are workflows that were interrupted and may need attention.
   - `status: aborted` — note these; do not surface unless David asks.

3. **Surface in-progress workflows to the controller** in this format:

   > **In-Flight Workflows**
   > | Workflow | Current Step | Started |
   > |----------|-------------|---------|
   > | morning-briefing | step-03-... | 2026-06-10 |
   >
   > These were not auto-resumed. Say `resume [workflow]` to continue, or `abort [workflow]` to close it out.

4. **If no in-progress workflows:** Surface a single line: "No in-flight workflows."

5. **Update step frontmatter:** Set `status: complete` and `completed-at` with current timestamp.

---

## SUCCESS METRICS

- All workflow state.yaml files read
- In-progress workflows surfaced (or absence confirmed)
- Controller informed and awaiting instruction (not auto-resumed)
- Step frontmatter updated to complete

## FAILURE MODES

| Failure | Action |
|---------|--------|
| A state.yaml is unreadable | Note the workflow name and skip it. Flag: "Could not read state for [workflow] — check manually." |
| No workflows directory | Note the failure. Proceed — boot is still complete. |
| state.yaml missing for a workflow | Skip that workflow. Missing state is not an error — it means the workflow has never run. |

---

## NEXT STEP

Read and follow: `steps/step-07-verify-completion.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
