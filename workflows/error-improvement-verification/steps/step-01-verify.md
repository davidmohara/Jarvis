---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 01: Verify Fix Claims Against the Error Log Entries

## MANDATORY EXECUTION RULES

1. You MUST read state.yaml, the error entries, and the target files directly. Do NOT accept the cycle's own summary as evidence for its own claims.
2. You MUST return a verdict for every checklist item. No item may be omitted.
3. You MUST NOT fix, edit, re-apply, or re-run anything. You verify and report; the caller decides.
4. If a source is missing or unreadable, mark the dependent items unverified. Do not infer correctness from silence.

---

## EXECUTION PROTOCOL

**Agent:** Ralph, Verification Agent
**Input:** Improvement manifest (state.yaml path + run-date + eval-record-id) from the caller
**Output:** Verdict table + one summary line, returned to the caller

---

## CONTEXT BOUNDARIES

- Scope is exactly this cycle's applied fixes and the entries they claim to resolve.
- Ralph does not re-apply fixes. He checks the claims that were made.

---

## YOUR TASK

### Sequence

1. **Locate the artifacts.** Read `workflows/error-improvement/state.yaml` (`accumulated-context.approved_fixes`, `files_modified`, `assertion_results`). Read the error entries under `systems/error-tracking/entries/`. Read `evolutions/.pending-changes.json`.

2. **Apply the fix-claims-vs-error-log lens.** For each item, re-derive the truth from the log and the files, then compare to the cycle's claims:

   | # | Checklist item | Ground truth source | Verdict |
   |---|----------------|---------------------|---------|
   | 1 | Every approved fix traces to a real entry | `approved_fixes[].entry_ids` exist as `err-*.json` files | Unverified if a fix names an entry that does not exist |
   | 2 | Every applied-fix target change is present | The target file contains the claimed edit | Unverified if the target file lacks the change |
   | 3 | Every entry marked `applied` has a matching fix | `files_modified[].entry_ids_updated` vs the entries' `fix_status` | Unverified if an entry is `applied` with no fix naming it |
   | 4 | No fabricated correction | Every `fix_id`/`entry_id` in the state exists in the log | Unverified if a claimed correction has no corresponding log record |
   | 5 | Pending-changes matches the cycle | `evolutions/.pending-changes.json` error-improvement item vs `files_modified` | Unverified if the logged file list omits a modified file |
   | 6 | Assertion results are consistent | `assertions_total`/`assertions_passed` vs `assertion_results` | Unverified if counts disagree with the recorded results |
   | 7 | Right-cycle check | Entry timestamps and eval-record-id vs this run | Unverified if claims are from a different cycle |

3. **Apply the "does the log actually say that?" test** per item: Verified (claim traced to a real entry and a real file change), Unverified (claim unsupported, or source unreadable), Not applicable (no fixes this cycle).

4. **Return the verdict table**, no preamble:

   ```
   | Item | Fix claim | Recorded evidence | Verdict |
   |------|-----------|-------------------|---------|
   | ...  | ...       | ...               | Verified / Unverified / N/A |
   ```

   Then one summary line:
   - If all verified or not-applicable: `All fix claims traced to real entries and real file changes: verified.`
   - If any unverified: `Findings: [items].`

5. **Update state.yaml** with `status: complete`, `current-step: step-01`, and record the verdict summary in `accumulated-context.verdict-summary` (`all-verified` or `findings`) plus `accumulated-context.findings: [list]`.

---

## SUCCESS METRICS

- Every checklist item has a verdict
- Each verified fix cites the entry file and the target-file change it was traced to
- Any unverified item names the specific fabricated correction or unsupported claim
- Verdict summary written to state.yaml

## FAILURE MODES

| Failure | Action |
|---------|--------|
| state.yaml unreadable | Mark all items Unverified with note "state unreadable." |
| No fixes applied this cycle | Mark fix items Not applicable; verify only the pending-changes and assertion-consistency items. |
| A target file unreadable | Mark the dependent fix item Unverified with note "target unreadable." |

---

## NEXT STEP

This is the final step. Return the verdict table to the caller. Workflow complete.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
