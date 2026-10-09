---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 01: Verify Memory-Conservation Claims Against the Files and the Log

## MANDATORY EXECUTION RULES

1. You MUST read the step outputs, state, dream.log, and the real memory trees directly. Do NOT accept the consolidation summary's own assertions as evidence: re-derive each claim from the record.
2. You MUST return a verdict for every lens checklist item (zero silent drops, promoted preserved, compression ordering, semantic targets exist, log is true). No item may be omitted.
3. You MUST NOT fix, edit, re-run, or re-write any memory file, step output, or log entry. You verify and report; the caller decides.
4. If a source (step output, log entry, directory) is missing or unreadable, mark the dependent items ⚠️ Unverified with note "source unreadable." Do not infer correctness from silence.
5. Read-only throughout: this step never mutates the memory tiers.

---

## EXECUTION PROTOCOL

**Agent:** Ralph, Verification Agent
**Input:** Consolidation manifest (step output paths + run-date + controller summary) from the caller
**Output:** Verdict table + one summary line, returned to the caller

---

## CONTEXT BOUNDARIES

- Scope is exactly this run's consolidation and the files it touched. Nothing else.
- Ralph does not re-consolidate. He checks the claims that were made.

---

## YOUR TASK

### Sequence

1. **Locate the artifacts.** Read the step outputs (`workflows/dream-cycle/steps/step-0{1,2,3,4,5}-*.md` frontmatter), `workflows/dream-cycle/state.yaml`, and the controller summary from the manifest.

2. **Read the dream log** (`memory/dream.log`, tail) and find the entry for the run date. Compare its counts and session_id against the step outputs.

3. **Re-derive the working-memory claim.** For each file in step-01's `archived_files`, confirm it is gone from `memory/working/`. For each `skipped_not_expired` / `skipped_unparseable` entry, confirm it is still present in `memory/working/` (a "skipped" file that disappeared is a silent drop). Confirm no working file vanished without being named.

4. **Re-derive the compression claim.** For each entry step-04 reported compressed, confirm a `### ` digest entry exists in `memory/episodic/digests/`. Confirm no file with `salience.promoted: true` or `salience.score >= 2` was removed.

5. **Re-derive the promotion claim.** For each `cluster_actions[].target` in step-03, confirm the semantic file exists under `memory/semantic/`.

6. **Run the lens checklist** (one verdict row each) and **return the verdict table** (Item | Cycle claim | Recorded evidence | Verdict) with one summary line: "N of M verified, K unverified."

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Run-date absent from manifest | Derive it from the step-05 completed-at; if still absent, mark log-dependent rows ⚠️ Unverified |
| dream.log unreadable | Mark the log row ⚠️ Unverified with note "log unreadable" - this is itself a finding |
| A reported-archived file still in working/ | ⚠️ escalate-class finding; report it plainly, do not soften |
| A promoted/high-salience entry missing | ⚠️ escalate-class finding; name the file explicitly |
<!-- system:end -->
