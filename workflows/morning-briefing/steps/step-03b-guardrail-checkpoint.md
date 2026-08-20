---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 03b: Guardrail Checkpoint — Review Before Synthesis

## MANDATORY EXECUTION RULES

1. This step reviews the gathered data from steps 01–03 (calendar, tasks, meeting context, and the Watchtower hand-off from Knox) before step-04 synthesizes it into the briefing David actually reads. It catches bad data before it reaches the user, not after.
2. You MUST record the checkpoint result via `guardrail-checkpoint.py` before proceeding.
3. `escalate` HALTS the workflow and surfaces the finding to David — distinct from a data-source failure, which is handled by the existing DATA SOURCE UNREACHABLE protocol in workflow.md and does not need escalation here.

---

## EXECUTION PROTOCOL

**Agent:** Chief
**Input:** `accumulated-context` from steps 01–03, including `watchtower_output`
**Output:** Guardrail checkpoint result recorded; workflow proceeds (pass/flag) or halts (escalate)

---

## YOUR TASK

### Review checklist

1. **Stale or wrong-day data** — does the calendar data actually correspond to today's date, not a cached prior day? Spot-check the first event's date against today.
2. **Watchtower sanity** — if `watchtower_output` is present, do the top-scored items look like genuine signal (not an empty/garbage synthesis, not items with scores that don't match their content)?
3. **Attendee/context mismatch** — for any meeting flagged `needs_prep`, does the gathered context actually reference the right meeting (not a stale prep from an old recurring-meeting instance)?
4. **Nothing sensitive leaking into a section that gets read aloud or copy-pasted elsewhere** — same leakage check as the daily-review checkpoint, applied to gathered context rather than a narrative.

### Decision

- **No issues** → `pass`.
- **A minor data quirk that won't mislead David** (e.g., one calendar event missing a location) → `flag`, note it, proceed.
- **Wrong-day data, a Watchtower synthesis that looks broken, or genuinely stale meeting context that would misdirect David's morning** → `escalate`. Do not let step-04 synthesize a briefing built on bad data without flagging it first — at minimum, note the issue prominently in the delivered briefing rather than silently presenting it as clean.

### Record the result

```bash
python3 systems/eval-harness/guardrail-checkpoint.py morning-briefing pre-synthesis-review step-03-gather-context <pass|flag|escalate> "<one-line reason>"
```

### If escalating

For morning-briefing specifically, "halt" does not mean deliver nothing — David still needs a briefing. Instead: proceed to step-04 but require it to open with an explicit data-quality warning naming what's wrong, before the routine content. This is the one workflow where blocking outright is worse than a flagged deliverable — but the escalation must still be visible to David, not silently absorbed.

---

## SUCCESS METRICS

- Every morning-briefing run has one guardrail checkpoint result recorded before synthesis.
- No escalation was silently dropped from the delivered briefing.

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `guardrail-checkpoint.py` fails to write | Note in the briefing's own text that the checkpoint couldn't be recorded; proceed. |

---

## NEXT STEP

Read fully and follow: `step-04-synthesize-briefing.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
