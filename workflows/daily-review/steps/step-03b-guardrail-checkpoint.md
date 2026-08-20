---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 03b: Guardrail Checkpoint — Review Before Commit

## MANDATORY EXECUTION RULES

1. This step reviews the output of step-03 (daily review file, narrative journal entry, delegation tracker changes) before step-04/05 commit it to the knowledge system and git. It is an automated adversarial review, not a rubber stamp.
2. You MUST record the checkpoint result via `guardrail-checkpoint.py` before proceeding — pass, flag, or escalate.
3. `escalate` HALTS the workflow and surfaces the finding to David. It is distinct from a step failure — do not write `status: failure` on step-03 because of an escalation here.
4. Do NOT silently fix a flagged issue by rewriting content without noting it. Any correction you make must be logged in the checkpoint reason.

---

## EXECUTION PROTOCOL

**Agent:** Chief
**Input:** Step-03 outputs — daily review file, narrative journal entry, updated delegation tracker
**Output:** Guardrail checkpoint result recorded; workflow proceeds (pass/flag) or halts (escalate)

---

## YOUR TASK

### Review checklist

Check step-03's output against these risk criteria:

1. **Leakage check** — does the narrative journal entry or review file contain anything that reads like a credential, API key, or raw personal/health data that shouldn't be written to a permanent knowledge-system record? (Distinct from ordinary work content — this is about accidental copy-paste of sensitive strings, not about whether the day involved sensitive topics.)
2. **Delegation tracker integrity** — did the update remove or overwrite rows that weren't part of today's confirmed completions? Compare the written tracker against what step-01 confirmed as done.
3. **Fabrication check** — does the narrative claim specific outcomes (a deal closed, a meeting decision) that aren't traceable to `capture_data` or `tomorrow_data` from steps 01–02? Flag anything that reads like invention rather than synthesis.
4. **Scope check** — did step-03 touch quarterly objectives despite the rule against it (see step-03's MANDATORY EXECUTION RULES #7)?

### Decision

- **No issues found** → `pass`.
- **Minor issue you can point to but that doesn't block the day from closing** (e.g., a slightly overstated claim in the narrative) → `flag`, note it, and let step-04 proceed. Note the flag in the closing summary the controller will see.
- **A leaked secret, a tracker row that looks wrongly deleted, or a fabricated claim** → `escalate`. Do not let step-04 write to git or the knowledge system until David has seen and confirmed it.

### Record the result

```bash
python3 systems/eval-harness/guardrail-checkpoint.py daily-review pre-commit-review step-03-update-system <pass|flag|escalate> "<one-line reason>"
```

### If escalating

Halt here. Surface to David:

```
[Chief]: Guardrail checkpoint flagged an issue before committing today's review — [one-line description]. I'm holding the commit until you confirm how to proceed.
```

Wait for instruction. Do not proceed to step-04 until resolved.

---

## SUCCESS METRICS

- Every daily-review run has exactly one guardrail checkpoint result recorded before the day is committed.
- No escalation was ever silently bypassed.

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `guardrail-checkpoint.py` fails to write | Log a note in the closing summary that the checkpoint couldn't be recorded; proceed as `pass` only if manual review found nothing — otherwise escalate verbally. |

---

## NEXT STEP

If `pass` or `flag`: load and execute `steps/step-04-root-audit.md`.
If `escalate`: halt and wait for David's decision before proceeding.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
