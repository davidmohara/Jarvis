---
status: complete
started-at: "2026-09-02T00:20:00-05:00"
completed-at: "2026-09-02T00:25:00-05:00"
outputs:
  gate_4_result: "pass"
  candidate_windows_found: 3
  output_file: "workflows/golf-booking/preview-output.json"
model: haiku
---

<!-- system:start -->
# Step 04: Score Available Windows and Write Output

## MANDATORY EXECUTION RULES

1. Always write output to `workflows/golf-booking/preview-output.json` before sending Slack
   (that happens in step-05, not here — writing must complete first).
2. Do not proceed to step-05 until **QUALITY GATE 4** passes. This is the workflow's second
   hard gate — golf-booking trusts this file blindly at midnight with no human review, so it
   must be structurally correct before it exists.
3. If David replied to a previous Slack preview with instructions, honor them — check
   `memory/working/` for override notes before finalizing.

---

## EXECUTION PROTOCOL

**Agent:** Sterling
**Input:** Day-status, CT windows, drought flag, weather scores from steps 01-03
**Output:** `workflows/golf-booking/preview-output.json`

---

## YOUR TASK

### Score Available Windows

For each available day (not hard-blocked, not weather-blocked), generate candidate time
windows and score them.

**Candidate windows per day:**

| Day | Earliest Start | Latest Preferred | Notes |
|-----|---------------|-----------------|-------|
| Friday | 1:00 PM | 6:00 PM | Only if 3-hour block available; avoid back-to-back meetings |
| Saturday | 1:00 PM | 6:00 PM | Best day — no standing constraints |
| Sunday | 2:30 PM | 6:00 PM | Church ends 1:30 PM; 1-hour buffer |

**Scoring model (lower is better).** Start with base score 0. Add penalties:

| Condition | Penalty |
|-----------|---------|
| Round cost $21/player (1:00–3:59 PM), heat_streak: false | 0 — preferred |
| Round cost $15/player (4:00–5:59 PM), heat_streak: true | 0 — preferred when heat streak active |
| Round cost $15/player (4:00–5:59 PM), heat_streak: false | +5 |
| Round cost $21/player (1:00–3:59 PM), heat_streak: true | +8 — playing in heat |
| Round cost $0/player (6:00 PM+, 9-hole only) | +15 |
| Early morning 9-hole ($21/player) | +20 — drought fallback only |
| Weather caution (rain 30–60%) | +10 |
| Sunday (church buffer, tighter window) | +5 |
| Friday (work day, conditional availability) | +3 |
| Avg temp > 95°F during candidate window (even without heat streak) | +8 — push toward later |
| 9-hole round (non-drought fallback) | +25 |
| Drought override — 9-hole acceptable | -10 penalty removed |

Reference points: heat_streak false, Saturday 1 PM, clear weather = score 0 (ideal).
heat_streak true, Saturday 4 PM, clear weather = score 0 (ideal). heat_streak false,
Saturday 4 PM = score +5. Sunday at preferred time in good weather ≈ score 5. Friday at
preferred time in good weather ≈ score 3.

Pick the top 3 scored windows across all available days.

### Write Preview Output

Write `workflows/golf-booking/preview-output.json`:

```json
{
  "generated_at": "YYYY-MM-DDTHH:MM:SS",
  "target_weekend": {
    "friday": "YYYY-MM-DD",
    "saturday": "YYYY-MM-DD",
    "sunday": "YYYY-MM-DD"
  },
  "day_status": {
    "friday": { "status": "available|unavailable", "reason": "..." },
    "saturday": { "status": "available|unavailable", "reason": "..." },
    "sunday": { "status": "available|unavailable", "reason": "..." }
  },
  "drought": true|false,
  "weather_data_missing": true|false,
  "ct_conversion_flag": true|false,
  "top_options": [
    {
      "rank": 1,
      "day": "saturday",
      "date": "YYYY-MM-DD",
      "preferred_start": "13:00",
      "preferred_end": "14:30",
      "holes": 18,
      "cost_per_player": 21,
      "total_cost": 42,
      "weather": {
        "rain_pct": 10,
        "temp_f": 78,
        "wind_mph": 8,
        "condition": "clear"
      },
      "score": 0,
      "rationale": "Saturday 1 PM — ideal cost, clear weather, no conflicts"
    }
  ],
  "override_instructions": null,
  "no_viable_reason": null
}
```

If no viable windows exist, `top_options` must be `[]` and `no_viable_reason` must contain a
specific explanation (e.g., "All three days hard-blocked: Friday no 3hr gap, Saturday family
dinner, Sunday rain >60%"). This keeps Gate 4 able to distinguish a legitimate zero-option
outcome from a broken run.

Check `memory/working/` for any golf override notes from this week. If found, store in
`override_instructions` and weight scoring accordingly.

---

## QUALITY GATE 4 — Output Schema (HARD, BLOCKING)

Run the deterministic verifier before proceeding to step-05:

```bash
python3 workflows/golf-preview/verify/step-04-output-schema.py <<< '{"ies_root": ".", "step_completed": "<ISO-8601 now>"}'
```

This script checks:
- `preview-output.json` exists and is valid JSON
- `top_options` is a non-empty list, OR `no_viable_reason` is populated with a real
  explanation (not a stub)
- `target_weekend` has all three dates (friday, saturday, sunday)
- `day_status` has an entry for all three days
- `generated_at` is present and not stale (> 10 days old flags staleness — this workflow runs
  weekly, so anything older indicates a stuck or skipped run)

The script returns `{"result": "pass"}` or `{"result": "retry", "retry_instruction": "..."}`.

**On `result: retry`:** Do not proceed to step-05. Fix the specific issue named in
`validation_errors` and re-run this step, then re-run the gate. Do not send Slack with a
malformed or empty output file that isn't explicitly a documented zero-option outcome.

**On `result: pass`:** Log `[Gate 4] PASS — <N> candidate windows written` and proceed.

Update `state.yaml`'s `accumulated-context` with the final scored options. Set
`current-step: step-05`.

---

## SUCCESS METRICS

- `preview-output.json` written with at least 1 top option, or a documented `no_viable_reason`
- Gate 4 passes before Slack is sent

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Gate 4 fails on missing dates or day_status | Re-run step-01/step-02 outputs into the write — do not hand-patch the JSON to pass the gate. |
| Gate 4 fails on empty `top_options` with no `no_viable_reason` | Add the explanation and re-run the gate — this is very likely a real zero-option weekend, not a bug, but it must be documented. |
| Gate 4 flags staleness | Investigate why the scheduled run didn't fire this week before re-running manually. |

## NEXT STEP

Read fully and follow: `step-05-notify-slack.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
