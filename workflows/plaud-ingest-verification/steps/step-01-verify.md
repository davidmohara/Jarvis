---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 01: Account for Every Staged Recording

## MANDATORY EXECUTION RULES

1. You MUST build the full discovered set from `accumulated-context.new-recordings` (step-01) and reconcile it against every downstream outcome list. Do NOT accept the run's own completion summary as the accounting.
2. You MUST return a verdict for every recording and every checklist item. No recording may be omitted.
3. You MUST NOT fix, edit, re-run, or re-ingest anything. You verify and report; the caller decides.
4. A recording that appears in the discovered set but in no outcome list is a silent drop: always ⚠️, never ➖.

---

## EXECUTION PROTOCOL

**Agent:** Ralph, Verification Agent
**Input:** Ingest manifest (state.yaml accumulated-context + step outputs) from the caller
**Output:** Verdict table + one summary line, returned to the caller

---

## CONTEXT BOUNDARIES

- Scope is exactly this ingest run: every recording it discovered, triggered, fetched, ingested, shared, or skipped.
- External systems (Plaud share links, Monday tasks) are not independently reachable offline; ground truth is what the run recorded plus the filesystem-observable staging state.

---

## YOUR TASK

### Sequence

1. **Build the discovered set.** Read `workflows/plaud-ingest/state.yaml` and extract `accumulated-context.new-recordings` (the file_ids discovered in step-01). This is the denominator.

2. **Build the outcome sets** from accumulated-context and step outputs:
   - `ingested-notes` (step-05): landed in the vault
   - `transcription-triggered` / `pending-recordings` (step-02): deferred, still transcribing
   - `recording-classification` marked `personal` (step-03): intentionally not shared
   - `unresolved_speakers` (step-03): logged but not resolved
   - share/Monday results (step-05b outputs): shared or failed-with-log
   - any explicit "skipped" log line

3. **Reconcile (the accounting core).** For every file_id in the discovered set, confirm it appears in at least one outcome set. Apply:

   | # | Checklist item | Ground truth source | Verdict |
   |---|----------------|---------------------|---------|
   | 1 | Every discovered recording accounted for | union of outcome sets vs `new-recordings` | ⚠️ for any file_id in the discovered set with no outcome |
   | 2 | Every ingested note recorded | `accumulated-context.ingested-notes` | ⚠️ if a recording is claimed ingested but not in the list |
   | 3 | Every skip logged | explicit skip log / `personal` classification | ⚠️ if a recording is absent from notes AND has no logged skip reason |
   | 4 | Staging cleaned up | `~/Downloads/transcript-staging/` vs `staged-files` | ⚠️ if any staged file remains after ingest |
   | 5 | Deferred recordings explained | `pending-recordings` | ⚠️ if a recording is deferred with no reason |
   | 6 | Terminal state reached | `state.yaml` `status` + `current-step` | ⚠️ if the run is not at its terminal state |

4. **Return the verdict table**, no preamble:

   ```
   | Recording (file_id / title) | Discovered | Outcome | Verdict |
   |-----------------------------|------------|---------|---------|
   | ...                         | yes/no     | note/skip/pending/shared | ✅/⚠️ |
   ```

   Then one summary line:
   - If all ✅: `All N discovered recordings accounted for: zero silent drops.`
   - If any ⚠️: `Re-run required: [recording ids / items].`

5. **Update state.yaml** with `status: complete`, `current-step: step-01`, and record the verdict summary in `accumulated-context.verdict-summary` (`all-accounted` or `findings`) plus `accumulated-context.findings: [list]` and `accumulated-context.discovered_count`.

---

## SUCCESS METRICS

- The discovered set is built from `new-recordings`, not from the run's summary
- Every discovered file_id has an outcome and a verdict
- Any unaccounted recording is reported as a silent drop
- Verdict summary written to state.yaml

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `new-recordings` absent from state.yaml | Surface: "No discovered set recorded: cannot reconcile." Mark item 1 ⚠️. |
| Staging directory unreadable | Mark item 4 ⚠️ with note "staging unreadable." Do not infer cleanup. |
| A source step output missing | Mark dependent items ⚠️ with note "step output missing." Do not infer success. |

---

## NEXT STEP

This is the final step. Return the verdict table to the caller. Workflow complete.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
