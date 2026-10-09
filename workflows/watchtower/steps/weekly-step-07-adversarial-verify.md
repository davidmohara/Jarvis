---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 07: Adversarial Verification - Standing-Intelligence Accounting

## MANDATORY EXECUTION RULES

1. You MUST spawn **Ralph** with `workflows/watchtower-verification/workflow.md`. Do NOT self-verify, and do NOT let the producing agent grade its own weekly run. This is a separate spawn with a distinct lens.
2. You MUST record the verdict via `guardrail-checkpoint.py` with checkpoint name `adversarial-verification` before finalizing.
3. You MUST NOT edit drafts, the weekly note, `state.yaml` content, or step outputs to make a finding disappear. Findings are surfaced and recorded as-is.
4. Ralph verifies claims against the recorded state and the real digests. He does not fix, re-run, or re-write anything.
5. This step runs after weekly-step-06 (publish drafts) - terminal verification. If step-06 was skipped, this step still runs (verifying the run's claims with `drafts_sent` empty).

---

## EXECUTION PROTOCOL

**Agent:** Knox, spawned by the coordinator, never executed inline. Knox spawns Ralph.
**Input:** Step 01-06 frontmatter outputs, `workflows/watchtower/state.yaml`, `workflows/watchtower/seen.jsonl`, the draft/angle sources, `reference/blog-ideas.md`
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

---

## CONTEXT BOUNDARIES

- Scope is this run's standing intelligence: the themes synthesized, the drafts created, the tweets generated, the sources proposed, and any drafts sent to `#content`.
- This step does not re-draft or re-send. It checks whether the run's claims hold up against the sources and the record.
- Findings are a report, not a retry.

---

## YOUR TASK

### Sequence

1. **Spawn Ralph.** Pass him:
   ```
   Agent: ralph
   Workflow: workflows/watchtower-verification/workflow.md
   Manifest:
     step-outputs: workflows/watchtower/steps/weekly-step-0{1,2,2b,3,4,5,6}-*.md frontmatter outputs
     state: workflows/watchtower/state.yaml
     seen-ledger: workflows/watchtower/seen.jsonl
     blog-ideas: reference/blog-ideas.md
     run-date: <YYYY-MM-DD>
   Task: Cross-check the weekly run's claims (drafts created vs sent, sources proposed, no claims of publishing) against the sources and the record, and return your verdict table.
   ```

2. **Receive Ralph's verdict table** (Item | Run claim | Recorded evidence | Verdict) and its summary line. Do not soften or edit it.

3. **Derive the checkpoint result:**
   - All verified → `pass`.
   - A minor accounting mismatch (e.g., a count off by one) → `flag`.
   - A draft claimed sent that was never delivered, a claim of publishing when Watchtower only sends to Slack `#content`, or a theme asserted with no source item → `escalate`.

4. **Record the result:**
   ```bash
   python3 systems/eval-harness/guardrail-checkpoint.py watchtower adversarial-verification weekly-step-06-publish-drafts <pass|flag|escalate> "<one-line reason>"
   ```

5. **Write the verdict summary to state.yaml** under `accumulated-context.adversarial-verification`:
   ```yaml
   accumulated-context:
     adversarial-verification:
       verdict: "all-verified" | "findings"
       result: "pass" | "flag" | "escalate"
       findings: [list of unsupported claims, or empty]
       lens: "standing-intelligence accounting: drafts approved/posted vs source digests, no unpublished claims of publishing"
   ```

6. **On `escalate`:** halt and surface to David: `[Knox]: Watchtower verification found [N] issue(s): [summary]. Holding the run's close until you confirm how to proceed.` Do not mark the run complete.

7. **On `pass` or `flag`:** confirm `state.yaml` `status: complete` (step-05 already set it), update this step's frontmatter (`status: complete`, `completed-at`, `outputs.verification_result`), and include the one-line verification result in the terminal report.

---

## SUCCESS METRICS

- Ralph was spawned (separate agent, distinct lens) and his verdict table received intact
- An `adversarial-verification` checkpoint result is recorded
- The verdict summary is written to state.yaml
- Any finding is surfaced to David, not silently absorbed

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Ralph fails to spawn | Record `result: flag` with reason "adversarial verification unavailable, Ralph not spawnable"; note it in the terminal report. Do not self-verify in place of Ralph. |
| Ralph returns a partial table | Record the partial result and note which items were missing. Do not suppress it. |
| `guardrail-checkpoint.py` fails to write | Still write the verdict summary to state.yaml; note the recording gap in the terminal report. |
| step-06 was skipped | Still run; verify the run's claims with `drafts_sent` empty (a legitimate "not published" outcome). |

---

## NEXT STEP

End of the weekly run. Daily run resumes Tuesday.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
