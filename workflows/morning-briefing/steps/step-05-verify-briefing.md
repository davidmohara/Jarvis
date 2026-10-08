---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 05: Adversarial Verification: Cross-Check the Briefing Against Source Data

## MANDATORY EXECUTION RULES

1. You MUST spawn **Ralph** with `workflows/morning-briefing-verification/workflow.md`. Do NOT self-verify, and do NOT let the producing agent grade its own briefing. The whole point is a separate spawn with a distinct lens.
2. You MUST wait for Ralph's verdict table before recording the result. This step is blocking for the checkpoint, not for delivery (the briefing was already delivered in step-04).
3. You MUST record the verdict via `guardrail-checkpoint.py` with checkpoint name `adversarial-verification`.
4. You MUST NOT edit the delivered briefing to make a finding disappear. Findings are surfaced and recorded as-is; a correction is a new run, not a silent rewrite.
5. Ralph verifies claims against source data. He does not fix, re-run, or re-synthesize anything.

---

## EXECUTION PROTOCOL

**Agent:** Chief, spawned by the coordinator, never executed inline in the coordinator's session. Chief spawns Ralph.
**Input:** The delivered briefing (`memory/working/morning-briefing-*.md`) and the source-data files from boot steps 01.2/01.5 (`data/calendar-unified.json`, `data/email-unified.json`, `data/omnifocus-unified.json`), plus `delegations/tracker.md`
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

---

## CONTEXT BOUNDARIES

- Scope is the briefing delivered in step-04 and the source data it was built from.
- This step does not re-run the briefing and does not change what was delivered. It records whether the briefing's claims hold up against the data.
- Findings are a report, not a retry: an unsupported claim is surfaced to David and recorded, so the next run (or a manual correction) can act on it.

---

## YOUR TASK

### Sequence

1. **Spawn Ralph.** Pass him:
   ```
   Agent: ralph
   Workflow: workflows/morning-briefing-verification/workflow.md
   Manifest:
     briefing-file: <most recent memory/working/morning-briefing-*.md>
     calendar-data: data/calendar-unified.json
     email-data: data/email-unified.json
     omnifocus-data: data/omnifocus-unified.json
     delegation-tracker: delegations/tracker.md
     run-date: <YYYY-MM-DD>
   Task: Cross-check every claim in the briefing against the source data and return your verdict table.
   ```

2. **Receive Ralph's verdict table** (Item | Briefing claim | Source evidence | Verdict) and its summary line. Do not soften or edit it.

3. **Derive the checkpoint result:**
   - All ✅ or ➖ → `pass`.
   - Any ⚠️ that is a minor mismatch → `flag`; note it in the closing summary David sees.
   - Any ⚠️ that is a fabricated claim, wrong-day data, or a degraded-source claim presented as clean → `escalate`.

4. **Record the result:**
   ```bash
   python3 systems/eval-harness/guardrail-checkpoint.py morning-briefing adversarial-verification step-04-synthesize-briefing <pass|flag|escalate> "<one-line reason>"
   ```

5. **Write the verdict summary to state.yaml** under `accumulated-context.adversarial-verification`:
   ```yaml
   accumulated-context:
     adversarial-verification:
       verdict: "all-verified" | "findings"
       result: "pass" | "flag" | "escalate"
       findings: [list of unsupported claims, or empty]
       lens: "calendar/email/omnifocus cross-check"
   ```

6. **Surface findings.** If `flag` or `escalate`, surface the finding to David in one line: `[Chief]: Briefing verification found [N] issue(s): [summary]. Recorded on the eval record; the briefing was already delivered.`

7. **Update step frontmatter and state.yaml:** set this step `status: complete`, `completed-at`, `outputs.verification_result`; set state.yaml `status: complete`, `current-step: step-05`.

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

This is the final step. When complete, set `state.yaml status: complete`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
