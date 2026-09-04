---
status: complete
started-at: "2026-09-04T15:30:00Z"
completed-at: "2026-09-04T15:31:00Z"
outputs:
  workflows_scanned: "complete — _active.yaml read (active: []), but a direct check of workflows/plaud-ingest/state.yaml shows status:in-progress, session pi-20260904-001, current-step step-01, started 2026-09-04T00:00:00-05:00 — NOT reflected in the index. Same recurring index/state mismatch pattern as the prior boot session."
  active_workflows: "1 (plaud-ingest, in-progress per its own state.yaml, missing from _active.yaml index)"
  background_tasks: "workflows/plaud-ingest/state.yaml: status in-progress, current-step step-01, session pi-20260904-001 (Knox), started 2026-09-04T00:00:00-05:00 — this is the session already spawned by the parent Master session per this task's instructions; not re-spawned here."
  result: "Surfacing plaud-ingest as in-progress despite empty _active.yaml index, since its own state.yaml is authoritative. Index discrepancy flagged again (recurring issue — same as 2026-09-03 boot). Not auto-resumed — awaiting controller instruction per protocol."
---

<!-- system:start -->
# Step 06: Scan In-Flight Workflows (Phase 5)

## MANDATORY EXECUTION RULES

1. Read `workflows/_active.yaml` first. If `active: []`, skip the per-directory scan entirely.
2. Surface any `status: in-progress` workflow immediately after the briefing. Do not bury it.
3. Do NOT auto-resume any in-progress workflow. Surface only. Await controller instruction.
4. This step concludes boot. Set workflow status to complete when done.

---

## EXECUTION PROTOCOL

**Agent:** Master
**Input:** `workflows/_active.yaml` (index); individual `state.yaml` files only when index has entries
**Output:** List of any in-progress workflows surfaced to the controller; boot marked complete

---

## CONTEXT BOUNDARIES

- This step is informational only. Read and report. Do not take action on any workflow.
- `status: not-started` and `status: complete` workflows are not surfaced — they are noise.
- `status: aborted` workflows may be surfaced with a brief note, but they are lower priority than in-progress.

---

## YOUR TASK

1. **Read `workflows/_active.yaml`.**
   If `active: []` → skip to step 4. No in-flight workflows.

2. **For each entry in the active list**, read its `state.yaml` to verify current status and capture:
   - `workflow` name
   - `status`
   - `current-step` (if in-progress)
   - `session-started` (if available)

3. **Filter for actionable states:**
   - `status: in-progress` — surface immediately.
   - `status: aborted` — note these; do not surface unless David asks.

4. **Surface in-progress workflows to the controller** in this format:

   > **In-Flight Workflows**
   > | Workflow | Current Step | Started |
   > |----------|-------------|---------|
   > | morning-briefing | step-03-... | 2026-06-10 |
   >
   > These were not auto-resumed. Say `resume [workflow]` to continue, or `abort [workflow]` to close it out.

   **If no in-progress workflows:** Surface a single line: "No in-flight workflows."

5. **Update step frontmatter:** Set `status: complete`, `completed-at` with current timestamp, and `outputs.workflows_scanned` with a summary (e.g. "complete — active.yaml read, N in-progress workflows found" or "complete — active.yaml read, 0 in-progress workflows found").

---

## MAINTAINING THE INDEX

Workflow agents must update `workflows/_active.yaml` at state transitions:
- **On in-progress:** Add `{workflow, status: in-progress, current-step, session-started}` to the active list.
- **On complete or aborted:** Remove the entry from the active list.

This keeps the index accurate so step-06 can trust the fast path.

---

## SUCCESS METRICS

- `workflows/_active.yaml` read first
- In-progress workflows surfaced (or absence confirmed via empty index)
- Controller informed and awaiting instruction (not auto-resumed)
- Step frontmatter updated to complete

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `_active.yaml` missing | Fall back to scanning all `workflows/*/state.yaml` files. Note: "Active index missing — full scan performed." |
| A state.yaml is unreadable | Note the workflow and skip it. Flag: "Could not read state for [workflow] — check manually." |
| state.yaml missing for an indexed workflow | Remove the stale entry from `_active.yaml`. Log: "Removed stale index entry for [workflow]." |

---

## NEXT STEP

Read and follow: `steps/step-06.5-guardrail-checkpoint.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
