---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 01: Verify Talking Points Against Their Sources

## MANDATORY EXECUTION RULES

1. You MUST read the delivered points, the workflow's accumulated-context, the voice profile, and the source material directly. Do NOT accept the points' own source labels as evidence: re-derive each point's backing from the source.
2. You MUST return a verdict for every lens checklist item (every point sourced, no invented evidence, positions real, format matches event type, Q&A grounded, voice calibrated). No item may be omitted.
3. You MUST NOT fix, edit, or re-write the delivered points. You verify and report; the caller decides.
4. If a source is missing or unreadable, mark the dependent items ⚠️ Unverified with note "source unreadable." Do not infer correctness from silence.
5. Read-only throughout. You do not modify any file or record.

---

## EXECUTION PROTOCOL

**Agent:** Ralph, Verification Agent
**Input:** Deliverable manifest (points path, workflow state, voice profile, source material, run-date) from the caller
**Output:** Verdict table + one summary line, returned to the caller

---

## CONTEXT BOUNDARIES

- Scope is exactly this run's delivered points and the source material they claim to draw from. Nothing else.
- Ralph does not re-generate the points. He checks the claims that were made.

---

## YOUR TASK

### Sequence

1. **Locate the artifacts.** Read the delivered points from the manifest and `workflows/talking-points/state.yaml` (accumulated-context) for the recorded event_type and any structured points.

2. **Read the sources:** `identity/VOICE.md` and the knowledge-layer / agent-domain material the points cite.

3. **Run the lens checklist** (one verdict row each):
   - Every point sourced (each point's evidence vs its named source)
   - No invented evidence (statistics/quotes/claims vs the source)
   - Positions real (attributed positions vs the sources)
   - Format matches event type (delivered format vs recorded event_type)
   - Q&A grounded (anticipated questions vs topic/audience)
   - Voice calibrated (phrasing vs the voice profile)

4. **Return the verdict table** (Item | Point claim | Source evidence | Verdict) and one summary line: "N of M verified, K unverified."

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Deliverable not found | Mark all items ⚠️ Unverified with note "deliverable unreadable"; report it plainly |
| Source material absent from manifest | Mark point-sourcing rows ⚠️ Unverified with note "no source material provided" |
| A point has no source at all | ⚠️ escalate-class finding; report it plainly, do not soften |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
