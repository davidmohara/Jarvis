---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 01: Verify Episode Deliverables Against the Inputs

## MANDATORY EXECUTION RULES

1. You MUST read the deliverables, the rendered PDF, and the workflow's accumulated-context directly. Do NOT accept the run's own assertions as evidence: re-derive each claim from the files.
2. You MUST return a verdict for every lens checklist item (both deliverables exist, PDF real/substantive, identity matches, questions reflect real sources, required sections present, no silent gaps). No item may be omitted.
3. You MUST NOT fix, edit, or re-write any deliverable. You verify and report; the caller decides.
4. If a source (episode-prep / SharePoint content) is missing or unreadable, mark the dependent items ⚠️ Unverified with note "source unreadable." Do not infer correctness from silence.
5. Read-only throughout. You do not modify any file.

---

## EXECUTION PROTOCOL

**Agent:** Ralph, Verification Agent
**Input:** Deliverable manifest (detailed sheet, PDF markdown, rendered PDF, workflow state, episode inputs, run-date) from the caller
**Output:** Verdict table + one summary line, returned to the caller

---

## CONTEXT BOUNDARIES

- Scope is exactly this run's episode deliverables and the inputs they were built from. Nothing else.
- Ralph does not re-write the prep. He checks the claims that were made.

---

## YOUR TASK

### Sequence

1. **Locate the artifacts.** Read the detailed sheet, the PDF-format markdown, and the rendered PDF from the manifest, and `workflows/podcast-prep/state.yaml` (accumulated-context + `sources_used`).

2. **Validate the PDF** directly: check the `%PDF-` magic bytes and the file size (a tiny or headerless file means the render never succeeded).

3. **Run the lens checklist** (one verdict row each):
   - Both deliverables exist (detailed sheet + rendered PDF)
   - PDF real and substantive (magic bytes, size, single page)
   - Identity matches (guest name / episode number vs step-01 inputs)
   - Questions reflect real sources (questions vs `sources_used` content)
   - Required sections present (logistics, guest background, episode topic, questions, talking points, pre-filming checklist)
   - No silent gaps (missing sources flagged, not dropped)

4. **Return the verdict table** (Item | Deliverable claim | Recorded evidence | Verdict) and one summary line: "N of M verified, K unverified."

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Detailed sheet or PDF missing | Mark the dependent rows ⚠️ Unverified; report it plainly, a missing deliverable is an escalate-class finding |
| PDF present but tiny/headerless | ⚠️ escalate-class finding; report the actual size, do not soften |
| Guest/episode identity mismatch | ⚠️ escalate-class finding; report both values |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
