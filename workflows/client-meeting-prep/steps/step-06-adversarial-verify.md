---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 06: Adversarial Verification: Cross-Check the Prep Sheet Against Source Data

## MANDATORY EXECUTION RULES

1. You MUST spawn **Ralph** with `workflows/client-meeting-prep-verification/workflow.md`. Do NOT self-verify, and do NOT let the producing agent (Chase) grade its own prep sheet. This is a separate spawn with a distinct lens.
2. You MUST wait for Ralph's verdict table before declaring the workflow complete. Findings are surfaced so they can be corrected before the controller walks into the meeting.
3. You MUST record the verdict via `guardrail-checkpoint.py` with checkpoint name `adversarial-verification`.
4. You MUST NOT edit the prep sheet to make a finding disappear. Findings are surfaced and recorded as-is.
5. Ralph verifies claims against recorded state and the source records. He does not fix, re-run, or re-write anything.
6. This step runs after the PDF has been delivered (step-05). The prep sheet's markdown is still the artifact under review, a finding can still be corrected and the PDF regenerated if the controller chooses.

---

## EXECUTION PROTOCOL

**Agent:** Chase, spawned by the coordinator, never executed inline. Chase spawns Ralph.
**Input:** The prep sheet markdown (`{Person Name} - {Company} - {YYYY-MM-DD}.md`), step-01/02/03 accumulated-context, and the source records it cites (calendar invite, email thread, CRM account record)
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

---

## CONTEXT BOUNDARIES

- Scope is this run's prep sheet and the source data it claims to be grounded in.
- This step does not re-write the prep sheet. It checks whether the sheet's factual claims hold up against the record.
- Findings are a report, not a retry. A finding is surfaced and recorded so it can be corrected before the meeting.

---

## YOUR TASK

### Sequence

1. **Spawn Ralph.** Pass him:
   ```
   Agent: ralph
   Workflow: workflows/client-meeting-prep-verification/workflow.md
   Manifest:
     prep-sheet: meetings/{Person Name} - {Company} - {run-date}.md
     step-context: workflows/client-meeting-prep/state.yaml (accumulated-context)
     source-records: calendar invite, introduction/most-recent email thread, CRM account record
     run-date: <YYYY-MM-DD>
   Task: Trace every attendee and company fact in the prep sheet back to a calendar, email, or CRM record and return your verdict table.
   ```

2. **Receive Ralph's verdict table** (Item | Prep-sheet claim | Source evidence | Verdict) and its summary line. Do not soften or edit it.

3. **Derive the checkpoint result:**
   - All ✅ or ➖ → `pass`.
   - Any ⚠️ that is a minor mismatch (e.g., a stale title, a soft claim) → `flag`.
   - Any ⚠️ that is an invented attendee, a fabricated company fact, or a reason-for-call that contradicts the email evidence → `escalate`.

4. **Record the result:**
   ```bash
   python3 systems/eval-harness/guardrail-checkpoint.py client-meeting-prep adversarial-verification step-05-remarkable-delivery <pass|flag|escalate> "<one-line reason>"
   ```

5. **Write the verdict summary to state.yaml** under `accumulated-context.adversarial-verification`:
   ```yaml
   accumulated-context:
     adversarial-verification:
       verdict: "all-verified" | "findings"
       result: "pass" | "flag" | "escalate"
       findings: [list of unsupported claims, or empty]
       lens: "prep-sheet claims vs source data; every attendee/company fact traced to calendar, email, or CRM"
   ```

6. **On `escalate`:** surface to David before the workflow is marked complete: `[Chase]: Prep-sheet verification found [N] issue(s): [summary]. Do not rely on [field] until corrected.` Record the finding and mark the workflow complete with the escalation noted, the meeting may be imminent.
7. **On `pass` or `flag`:** update step frontmatter (`status: complete`, `completed-at`, `outputs.verification_result`) and set `state.yaml` `status: complete`.

---

## SUCCESS METRICS

- Ralph was spawned (separate agent, distinct lens) and his verdict table received intact
- An `adversarial-verification` checkpoint result is recorded
- The verdict summary is written to state.yaml
- Any finding is surfaced to David, not silently absorbed

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Ralph fails to spawn | Record `result: flag` with reason "adversarial verification unavailable, Ralph not spawnable"; note it in the closing summary. Do not self-verify in place of Ralph. |
| Ralph returns a partial table | Record the partial result and note which items were missing. Do not suppress it. |
| `guardrail-checkpoint.py` fails to write | Still write the verdict summary to state.yaml; note the recording gap in the closing summary. |

---

## NEXT STEP

This is the terminal step. On `pass` or `flag`, set `state.yaml` `status: complete` and deliver the closing summary to David. On `escalate`, deliver the finding to David and still mark the workflow complete with the escalation recorded.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
