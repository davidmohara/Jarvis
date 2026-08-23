---
status: complete
started-at: "2026-08-23T12:19:15-05:00"
completed-at: "2026-08-23T12:19:45-05:00"
outputs:
  checkpoint_result: "pass"
  reason: "All data sources live and current. Calendar fresh (updated 07:10 CT today). Briefing reflects Phase 1-4 data accurately. No stale cached data or leakage detected. In-flight workflow scan correct. Session index valid."
model: sonnet
---

<!-- system:start -->
# Step 06.5: Guardrail Checkpoint — Review Before Completion Gate

## MANDATORY EXECUTION RULES

1. This step reviews everything boot gathered and synthesized (steps 01–06: identity context, unified data pull, calendar, meeting context, the synthesized briefing, and the in-flight workflow scan) before step-07's hard completion gate. It is a review of content quality and safety, not a mechanical completeness check — step-07 already does that.
2. You MUST record the checkpoint result via `guardrail-checkpoint.py` before proceeding.
3. `escalate` HALTS boot before it is marked complete and surfaces the finding to David — distinct from step-07's mechanical gate, which checks that steps ran, not that their content is sound.

---

## EXECUTION PROTOCOL

**Agent:** Master
**Input:** `accumulated-context` from steps 01–06
**Output:** Guardrail checkpoint result recorded; workflow proceeds to step-07 (pass/flag) or halts (escalate)

---

## YOUR TASK

### Review checklist

1. **Synthesized briefing sanity** — does the briefing produced in step-05 actually reflect the data gathered in steps 01–04, or does it show signs of stale/cached context being presented as live?
2. **In-flight workflow scan integrity** — did step-06 correctly distinguish genuinely in-progress workflows from stale index entries, per its own failure-mode table? A scan that surfaces every workflow as "in progress" (or none at all, when `_active.yaml` clearly has entries) is a red flag.
3. **Leakage check** — same as the other checkpoints: nothing that looks like a credential or raw sensitive data should have been pulled into the session-index or briefing content.
4. **Session index sanity** — the personal Session Index Boot section created a new session record; confirm nothing else in boot has already corrupted or duplicated that record.

### Decision

- **No issues** → `pass`.
- **A minor data quirk** (e.g., one identity file loaded with a stale cache but boot otherwise fine) → `flag`, note it, proceed.
- **A synthesized briefing that misrepresents the gathered data, or a workflow scan that is clearly broken** → `escalate`. Boot should not be marked complete on top of a broken foundation — surface it and let David decide whether to proceed or restart data gathering.

### Record the result

```bash
python3 systems/eval-harness/guardrail-checkpoint.py boot pre-completion-review step-06-scan-workflows <pass|flag|escalate> "<one-line reason>"
```

### If escalating

Surface to David before step-07 runs:

```
[Master]: Guardrail checkpoint flagged an issue before marking boot complete — [one-line description]. Proceeding to the completion gate anyway so the session isn't blocked, but flagging this needs your attention.
```

Boot's hard gate (step-07) is mechanical and should still run — escalating here means flagging the content issue to David, not blocking the session from starting. This differs from daily-review's checkpoint, where the risk is an irreversible write; here the risk is bad context silently shaping the rest of the session.

---

## SUCCESS METRICS

- Every boot run has one guardrail checkpoint result recorded before the completion gate.
- No escalation was silently dropped without surfacing to David.

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `guardrail-checkpoint.py` fails to write | Note the gap verbally to David; proceed to step-07. |

---

## NEXT STEP

Read and follow: `steps/step-07-verify-completion.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
