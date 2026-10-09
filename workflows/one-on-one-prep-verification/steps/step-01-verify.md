---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 01: Verify Brief Claims Against the Delegation Tracker and OmniFocus

## MANDATORY EXECUTION RULES

1. You MUST read the brief, the workflow's accumulated-context, the delegation tracker, and the OmniFocus pull directly. Do NOT accept the brief's own assertions as evidence: re-derive each claim from the record.
2. You MUST return a verdict for every lens checklist item (open action items real, no fabricated delegations, talking points grounded, statuses honest, previous-brief continuity, calendar hygiene). No item may be omitted.
3. You MUST NOT fix, edit, or re-write the brief. You verify and report; the caller decides.
4. If a source (delegation tracker, OmniFocus pull) is missing or unreadable, mark the dependent items ⚠️ Unverified with note "source unreadable." Do not infer correctness from silence.
5. Read-only throughout. You do not modify any file or record.

---

## EXECUTION PROTOCOL

**Agent:** Ralph, Verification Agent
**Input:** Brief manifest (brief path, workflow state, delegation tracker, OmniFocus data, run-date) from the caller
**Output:** Verdict table + one summary line, returned to the caller

---

## CONTEXT BOUNDARIES

- Scope is exactly this run's brief and the delegation/task records it cites. Nothing else.
- Ralph does not re-gather communications. He checks the claims that were made.

---

## YOUR TASK

### Sequence

1. **Locate the artifacts.** Read the brief from the manifest and `workflows/one-on-one-prep/state.yaml` (accumulated-context) for the person and the gathered task/communication data.

2. **Read the records:** `delegations/tracker.md` (active and completed delegations) and `data/omnifocus-unified.json` (tasks, tags, due dates).

3. **Run the lens checklist** (one verdict row each):
   - Open action items real (each brief action item vs tracker/OmniFocus/cited thread)
   - No fabricated delegations (each named delegation vs the tracker)
   - Talking points grounded (each point vs a real step-02/03 source)
   - Statuses honest (brief statuses vs tracker/OmniFocus status)
   - Previous-brief continuity (prior open items accounted for)
   - Calendar hygiene (no excluded recurring meetings in the brief)

4. **Return the verdict table** (Item | Brief claim | Recorded state | Verdict) and one summary line: "N of M verified, K unverified."

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Brief not found | Mark all items ⚠️ Unverified with note "brief unreadable"; report it plainly |
| Delegation tracker missing | Mark delegation-dependent rows ⚠️ Unverified with note "tracker not found" |
| An action item has no source | ⚠️ escalate-class finding; report it plainly, do not soften |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
