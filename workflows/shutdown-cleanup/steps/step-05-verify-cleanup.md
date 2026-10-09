---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 05: Adversarial Verification: Cross-Check the Cleanup Against the Commit and Audit Trail

## MANDATORY EXECUTION RULES

1. You MUST spawn **Ralph** with `workflows/shutdown-cleanup-verification/workflow.md`. Do NOT self-verify, and do NOT let the producing agent grade its own cleanup. This is a separate spawn with a distinct lens.
2. You MUST record the verdict via `guardrail-checkpoint.py` with checkpoint name `adversarial-verification`.
3. You MUST NOT edit step outputs to make a finding disappear. Findings are surfaced and recorded as-is.
4. Ralph verifies claims against recorded state and the git audit trail. He does not fix, re-run, or re-write anything.
5. This step runs after the commit (terminal verification, matching morning-briefing and plaud-ingest's post-deliverable pattern; the pre-commit review duty is covered by step-04's own wrapper enforcement and verifier).

---

## EXECUTION PROTOCOL

**Agent:** Rigby, spawned by the coordinator, never executed inline. Rigby spawns Ralph.
**Input:** Step 01-04 frontmatter outputs, `workflows/shutdown-cleanup/state.yaml`, `systems/eval-harness/git-ops.jsonl`, the commit sha from step-04
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

---

## CONTEXT BOUNDARIES

- Scope is this run's cleanup: purge outputs, deliverable organization, gitignore check, and the commit.
- This step does not re-do the cleanup. It checks whether the cleanup's claims hold up against the commit and the audit trail.
- Findings are a report, not a retry.

---

## YOUR TASK

### Sequence

1. **Spawn Ralph.** Pass him:
   ```
   Agent: ralph
   Workflow: workflows/shutdown-cleanup-verification/workflow.md
   Manifest:
     step-outputs: workflows/shutdown-cleanup/steps/step-0{1,2,3,4}-*.md frontmatter outputs
     state: workflows/shutdown-cleanup/state.yaml
     git-audit: systems/eval-harness/git-ops.jsonl
     commit-sha: <from step-04 outputs>
     run-date: <YYYY-MM-DD>
   Task: Cross-check the cleanup claims against the commit and audit trail and return your verdict table.
   ```

2. **Receive Ralph's verdict table** (Item | Cleanup claim | Recorded evidence | Verdict) and its summary line. Do not soften or edit it.

3. **Derive the checkpoint result:**
   - All ✅ or ➖ → `pass`.
   - Any ⚠️ minor mismatch (e.g., summary counts off by one) → `flag`.
   - Any ⚠️ that matters → `escalate`: temp artifacts committed, a deliverable/media file deleted rather than preserved (see the standing no-screenshot-deletion feedback), a commit that bypassed the wrapper (no git-ops.jsonl entry), or a false "workspace clean" claim.

4. **Record the result:**
   ```bash
   python3 systems/eval-harness/guardrail-checkpoint.py shutdown-cleanup adversarial-verification step-04-commit <pass|flag|escalate> "<one-line reason>"
   ```

5. **Write the verdict summary to state.yaml** under `accumulated-context.adversarial-verification`:
   ```yaml
   accumulated-context:
     adversarial-verification: "<result> — <one-line summary> (<date>)"
   ```

6. **Surface any finding to the controller** in the final cleanup summary, verbatim from Ralph's table.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Ralph cannot spawn | Record `flag` with reason "ralph-unavailable", note it in the summary; do not block the session exit |
| No commit was needed (workspace clean) | Verify the nothing-to-commit claim against the lock-free diff lists; record Ralph's verdict on that claim |
| guardrail-checkpoint refuses (validation or no record) | Fix the arguments and retry; an unrecordable escalate is a loud failure, surface it to the controller directly |
<!-- system:end -->
