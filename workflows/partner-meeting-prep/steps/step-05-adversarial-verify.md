---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 05: Adversarial Verification: Cross-Check the Document Against the Account and Event Records

## MANDATORY EXECUTION RULES

1. You MUST spawn **Ralph** with `workflows/partner-meeting-prep-verification/workflow.md`. Do NOT self-verify, and do NOT let the producing agent (Chase) grade its own document. This is a separate spawn with a distinct lens.
2. You MUST wait for Ralph's verdict table before declaring the workflow complete. Findings are surfaced so they can be corrected before the document is shared with the partner.
3. You MUST record the verdict via `guardrail-checkpoint.py` with checkpoint name `adversarial-verification`.
4. You MUST NOT edit the document to make a finding disappear. Findings are surfaced and recorded as-is.
5. Ralph verifies claims against recorded state. He does not fix, re-run, or re-write anything.
6. This step runs after the document has been saved (step-04). The saved document is the artifact under review, and it is intended to be shared with the partner team, so accuracy matters more than for an internal-only sheet.

---

## EXECUTION PROTOCOL

**Agent:** Chase, spawned by the coordinator, never executed inline. Chase spawns Ralph.
**Input:** The saved document (`{Partner} - {YYYY-MM-DD}.md`), step-01/02/03 accumulated-context, the CRM account records, and the calendar/email records the overlap and event claims cite
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

---

## CONTEXT BOUNDARIES

- Scope is this run's partner document and the account/event records it cites.
- This step does not re-write the document. It checks whether the account-overlap and event claims are real.
- Findings are a report, not a retry. A finding is surfaced and recorded so it can be corrected before the document is shared.

---

## YOUR TASK

### Sequence

1. **Spawn Ralph.** Pass him:
   ```
   Agent: ralph
   Workflow: workflows/partner-meeting-prep-verification/workflow.md
   Manifest:
     document: {partner-slug} - {run-date}.md
     step-context: workflows/partner-meeting-prep/state.yaml (accumulated-context)
     crm-records: account/pipeline records for the accounts named in the overlap table
     calendar-email: the partner meeting invite and correspondence
     run-date: <YYYY-MM-DD>
   Task: Cross-check the account-overlap and event claims in the document against the actual records and return your verdict table.
   ```

2. **Receive Ralph's verdict table** (Item | Document claim | Recorded evidence | Verdict) and its summary line. Do not soften or edit it.

3. **Derive the checkpoint result:**
   - All ✅ or ➖ → `pass`.
   - Any ⚠️ that is a minor mismatch (e.g., a stale account status) → `flag`.
   - Any ⚠️ that is an invented account, a fabricated overlap, a made-up event, or a partner-side column filled in with a guess → `escalate`.

4. **Record the result:**
   ```bash
   python3 systems/eval-harness/guardrail-checkpoint.py partner-meeting-prep adversarial-verification step-04-build-document <pass|flag|escalate> "<one-line reason>"
   ```

5. **Write the verdict summary to state.yaml** under `accumulated-context.adversarial-verification`:
   ```yaml
   accumulated-context:
     adversarial-verification:
       verdict: "all-verified" | "findings"
       result: "pass" | "flag" | "escalate"
       findings: [list of unsupported claims, or empty]
       lens: "account-overlap and event claims vs actual CRM/calendar records"
   ```

6. **On `escalate`:** surface to David before the workflow is marked complete: `[Chase]: Partner document verification found [N] issue(s): [summary]. Do not share the document until corrected.` Record the finding and mark the workflow complete with the escalation noted.
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
