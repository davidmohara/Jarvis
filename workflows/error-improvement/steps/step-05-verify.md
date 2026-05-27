---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: haiku
---

<!-- system:start -->
# Step 05: Verify

## MANDATORY EXECUTION RULES

1. You MUST re-read every modified file — do not trust that the edit landed correctly without checking.
2. You MUST check that fix_status was updated on every entry in the approved list — not a sample.
3. You MUST run compact.py --status again to confirm eligible months haven't changed since intake.
4. You MUST NOT proceed to Step 6 if any critical assertion fails — surface failures to controller first.
5. A failed assertion is a specific, named thing. Not "verification passed" or "looks good."

---

## EXECUTION PROTOCOL

**Agent:** Rigby
**Input:** `files_modified` from state.yaml, `approved_fixes` list
**Output:** Assertion results, pass/fail counts, go/no-go for Step 6

---

## YOUR TASK

### 1. Verify each modified file

For each file in `accumulated-context.files_modified`:

Read the file. For each fix applied to it, confirm the exact text is present. This is an assertion, not a review.

```
ASSERTION: "M365-only rule present in skills/jarvis-inbox/SKILL.md"
EXPECTED:  Contains "Do not use Apple Mail, AppleScript, or any local mail client"
RESULT:    PASS / FAIL
```

Record each assertion in state.yaml under `accumulated-context`:
```yaml
  assertions_total: 12
  assertions_passed: 12
  assertion_results:
    - assertion: "M365-only rule present in jarvis-inbox SKILL.md"
      file: "skills/jarvis-inbox/SKILL.md"
      passed: true
    - ...
```

### 2. Verify fix_status on all affected entries

For each `entry_ids` list across all approved fixes, open the entry file and confirm:
- `fix_status` is `"applied"` (not `"proposed"`)
- `fix_status` key is snake_case (not `fixStatus`)

Count passed vs. failed. If any entry still shows `proposed`, it means Step 4's update didn't land — re-apply the update now and recount.

Add to assertions:
```
ASSERTION: "fix_status=applied on err-20260401-007"
RESULT:    PASS
```

### 3. Run compact.py --status

```bash
python3 systems/error-tracking/compact.py --status
```

Confirm:
- `open_count` is equal to or lower than at intake (it should be lower — we just resolved entries)
- Eligible months are confirmed (may have changed if some previously blocked months are now unblocked)

Update state.yaml:
```yaml
  months_compacted: []   # will be filled in Step 6
  compact_eligible_months: ["2026-04"]   # from this check
```

### 4. Assess and report

Compute:
- `pass_rate` = assertions_passed / assertions_total

| Outcome | Action |
|---------|--------|
| pass_rate == 1.0 | Clean pass. Report and proceed to Step 6. |
| pass_rate >= 0.9 AND all file assertions pass | Minor entry-level issues only. Proceed to Step 6. Report failures as notes. |
| Any file assertion fails | HOLD. Surface specific failures to controller. Do not compact until resolved. |
| pass_rate < 0.9 | HOLD. Something is systematically wrong. Surface to controller. |

**Report format:**
```
## Verification Results

Assertions: [N] checked, [N] passed, [N] failed

[If any failures:]
⚠️ Failures:
- [assertion description]: FAIL — expected "[text]", found [what was actually there or absent]

[If all passed:]
✓ All fixes verified in target files.
✓ All entry fix_status values updated.
✓ [N] months eligible for compaction: [month list]
```

---

## INSTRUMENTATION

After recording assertion results in state.yaml, append this step's timing:

```yaml
  step_timings:
    - step: step-05-verify
      started: <ISO-8601 UTC when this step began>
      completed: <ISO-8601 UTC now>
      assertions_passed: <N>
      assertions_total: <N>
```

---

## SUCCESS METRICS

- All file assertions pass (fix text present in target file)
- All entry fix_status assertions pass (or re-applied and re-verified)
- Compact eligibility confirmed
- State.yaml updated with assertion results

## FAILURE MODES

| Failure | Action |
|---------|--------|
| File assertion fails (text not found) | Re-read file carefully. If edit truly didn't land, re-apply and re-verify. If still fails, surface to controller. |
| Entry fix_status still showing proposed | Re-write the entry file directly. Re-verify. |
| compact.py fails | Note. Proceed to Step 6 with manual eligibility check. |
| Controller decides not to compact after seeing failures | Update state.yaml with failure notes. Set status: aborted. Exit workflow. |

## NEXT STEP

[Step 06 — Compact](step-06-compact.md)
<!-- system:end -->
