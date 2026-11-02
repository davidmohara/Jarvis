---
status: complete
started-at: '2026-11-02T16:21:30Z'
completed-at: '2026-11-02T16:21:51Z'
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

**Agent:** briefing subagent (Master persona), spawned by the coordinator after step-04 completes, never executed inline in the coordinator's session (see `workflow.md`).
**Input:** `workflows/_active.yaml` (index); individual `state.yaml` files only when index has entries
**Output:** List of any in-progress workflows surfaced to the controller; boot marked complete

---

## CONTEXT BOUNDARIES

- This step is informational only. Read and report. Do not take action on any workflow.
- `status: not-started` and `status: complete` workflows are not surfaced — they are noise.
- `status: aborted` workflows may be surfaced with a brief note, but they are lower priority than in-progress.

---

## YOUR TASK

1. **Run the one deterministic index-plus-consistency command** from the IES root. It reads `_active.yaml` first and prints the ground truth in the same call:

   ```bash
   python3 -I -c "
   import glob,re
   print('--- _active.yaml ---')
   print(open('workflows/_active.yaml').read())
   print('--- in-progress on disk ---')
   for p in glob.glob('workflows/*/state.yaml'):
       t=open(p).read()
       if re.search(r'^status:\s*in-progress',t,re.M): print(p)
   "
   ```

   `workflows/boot/state.yaml` is this run. It is always `in-progress` at this point and is **not** a disagreement. Ignore it when comparing the index to the ground truth.

2. **Compare and report in one line, not a sweep.** If the two sides agree once boot's own state file is excluded, say so in one line and move on. If they disagree, surface only the disagreeing workflow and move on. Do not read each indexed `state.yaml` individually; the command already answered the question.

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

5. **Write, following the WRITE PROTOCOL below.** Do not write state until the scan result exists.

---

## WRITE PROTOCOL (this block is the entire bookkeeping cost for this step)

1. One clock read: `date -u +%Y-%m-%dT%H:%M:%SZ`. Reuse that exact value for both writes below.
2. One Edit to `workflows/boot/state.yaml`, anchored on the literal `accumulated-context:` line: insert this step's key directly beneath it. No grep, no re-read. If the key already exists (a retry), edit that existing line instead of inserting a second copy. **Match the whole line including the line break**, because prose values in this file can contain the same substring, and the Edit tool refuses a non-unique `old_string`.
3. One Edit to this step file's frontmatter. Do it last, in the same turn as the state edit.
4. Issue the two Edits as parallel tool calls in one turn.
5. Never `cat` state.yaml. Never Write state.yaml.

**`workflows_scanned` value:** one line, 200 characters max, for example `"complete: 0 in-progress (index and disk agree, boot self excluded)"` or `"complete: 1 in-progress, morning-briefing at step-03"`.

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

Read and follow: `steps/step-07-verify-completion.md` (guardrail review is folded into step-07).
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
