---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 01: Verify Cleanup Claims Against the Commit and Audit Trail

## MANDATORY EXECUTION RULES

1. You MUST read the step outputs, state, audit log, and the commit itself directly. Do NOT accept the cleanup summary's own assertions as evidence: re-derive each claim from the record.
2. You MUST return a verdict for every lens checklist item (nothing temp committed, nothing precious deleted, commit through the wrapper, counts true, clean claims real). No item may be omitted.
3. You MUST NOT fix, edit, re-run, or re-commit anything. You verify and report; the caller decides.
4. If a source (step output, audit log entry, commit) is missing or unreadable, mark the dependent items ⚠️ Unverified with note "source unreadable." Do not infer correctness from silence.
5. Git reads only, and lock-free: `git show --stat <sha>` is the one git command this step needs. `git status` is forbidden.

---

## EXECUTION PROTOCOL

**Agent:** Ralph, Verification Agent
**Input:** Cleanup manifest (step output paths + commit sha + run-date + controller summary) from the caller
**Output:** Verdict table + one summary line, returned to the caller

---

## CONTEXT BOUNDARIES

- Scope is exactly this run's cleanup and its commit. Nothing else.
- Ralph does not re-clean. He checks the claims that were made.

---

## YOUR TASK

### Sequence

1. **Locate the artifacts.** Read the step outputs (`workflows/shutdown-cleanup/steps/step-0{1..4}-*.md` frontmatter), `workflows/shutdown-cleanup/state.yaml`, and the controller summary from the manifest.

2. **Read the commit** (lock-free): `git show --stat <commit-sha>` for the file list and counts. If no commit was claimed, read the nothing-to-commit claim against `git diff --name-only HEAD` and `git ls-files --modified --others --exclude-standard` output from the manifest.

3. **Read the audit trail:** `systems/eval-harness/git-ops.jsonl` — find the entry matching this run's commit (`verb: commit`, executed, not refused, timestamp within the run window). No entry = the commit bypassed the wrapper.

4. **Run the lens checklist** (one verdict row each):
   - Nothing temp committed (purge patterns vs the commit file list)
   - Nothing precious deleted (images/media/PDF/deliverables vs purge outputs and commit)
   - Commit through the wrapper (audit entry match)
   - Counts true (summary counts vs step outputs and commit stat)
   - Clean claims real (lock-free lists vs the claim)

5. **Return the verdict table** (Item | Cleanup claim | Recorded evidence | Verdict) and one summary line: "N of M verified, K unverified."

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Commit sha absent from manifest | Mark commit-dependent rows ⚠️ Unverified with note; do not guess the sha |
| Audit log missing entirely | Mark wrapper-bypass ⚠️ and note "no audit log" — this is itself a finding |
| Purge deleted a deliverable | ⚠️ escalate-class finding; report it plainly, do not soften |
<!-- system:end -->
