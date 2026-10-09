---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 01: Verify Analysis Claims Against the Eval Records

## MANDATORY EXECUTION RULES

1. You MUST read the step outputs, state, eval records, and the analysis report directly. Do NOT accept the run summary's own assertions as evidence: re-derive each claim from the records.
2. You MUST return a verdict for every lens checklist item (grades real, assertion counts reconcile, findings trace to files, no self-grading, counts true). No item may be omitted.
3. You MUST NOT fix, edit, re-grade, re-score, or re-write any record or report. You verify and report; the caller decides.
4. If a source (step output, record, report) is missing or unreadable, mark the dependent items ⚠️ Unverified with note "source unreadable." Do not infer correctness from silence.
5. Read-only throughout: this step never mutates any eval record or report.

---

## EXECUTION PROTOCOL

**Agent:** Ralph, Verification Agent
**Input:** Maintenance manifest (step output paths + run-date + report path) from the caller
**Output:** Verdict table + one summary line, returned to the caller

---

## CONTEXT BOUNDARIES

- Scope is exactly this run's maintenance: the grades, assertions, scores, and analysis it produced.
- Ralph does not re-grade or re-analyze. He checks the claims that were made.

---

## YOUR TASK

### Sequence

1. **Locate the artifacts.** Read the step outputs (`workflows/system-eval/steps/step-0{1..6}-*.md` frontmatter), `workflows/system-eval/state.yaml`, and the report path from the manifest.

2. **Re-derive the grading claim.** Load the `grading.grade_distribution` from state.yaml and count the actual non-null `assessment.grading.grade` values across the records. Reconcile the reported distribution against the on-disk distribution.

3. **Re-derive the assertion tally.** Load `assertions_run` from state.yaml and sum the actual `assessment.structural.assertions_checked` values across the records. Reconcile.

4. **Trace the findings.** For each pattern/recommendation in the analysis report, confirm it names a workflow/record and a concrete detail present in the corpus. Mark any finding with no traceable record ⚠️.

5. **Self-grading check.** Confirm no record whose `name` is `system-eval` carries a grade assigned by this run.

6. **Reconcile the counts.** Compare `records_total`, `total_graded`, and `records_scored` in state.yaml against the actual record counts on disk (accounting for documented in-progress skips).

7. **Return the verdict table** (Item | Run claim | Recorded evidence | Verdict) with one summary line: "N of M verified, K unverified."

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Analysis report path absent from manifest | Mark finding-trace rows ⚠️ Unverified; do not guess the path |
| An eval record is unreadable/malformed | Mark the dependent count rows ⚠️ with note "record unreadable" - this is itself a finding |
| A reported grade has no matching record | ⚠️ escalate-class finding; name the grade and the missing record |
| A self-graded system-eval record found | ⚠️ escalate-class finding; report it plainly |
<!-- system:end -->
