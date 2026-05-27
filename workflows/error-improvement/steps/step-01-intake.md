---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: haiku
---

<!-- system:start -->
# Step 01: Intake & Gate Check

## MANDATORY EXECUTION RULES

1. You MUST run `compact.py --status` before anything else — it shows what's already in state.
2. You MUST abort if another error-improvement run is in-progress (check state.yaml).
3. You MUST report the gate result clearly — not silently pass or fail it.
4. You MUST write entry count and eligibility assessment to state.yaml before moving on.

---

## EXECUTION PROTOCOL

**Agent:** Rigby
**Input:** Error tracking entries, compaction state
**Output:** Entry count, open vs. closed breakdown, eligible months, go/no-go decision

---

## YOUR TASK

### 1. Check state.yaml

Read `workflows/error-improvement/state.yaml`. If `status: in-progress`, surface:

> "[Rigby]: error-improvement is already in-progress at step [current-step]. Resume? Or start fresh (will reset state)?"

Wait for the controller's answer before proceeding. Do not auto-resume or auto-reset.

### 2. Run compact status

```bash
python3 systems/error-tracking/compact.py --status
```

Capture: total entries, fix_status breakdown, per-month breakdown (open count, eligible flag).

### 3. Assess volume and eligibility

Compute:
- `entry_count`: total entries in `entries/`
- `open_count`: entries with `fix_status: proposed` or `in-progress`
- `closed_count`: entries with `fix_status: applied`, `deferred`, or `not-applicable`
- `eligible_months`: months marked ✓ eligible by compact status
- `ineligible_months`: months with open entries (blocked from compaction)
- `current_month_entries`: May not be compacted — note count for context

### 4. Gate decision

| Condition | Decision |
|-----------|----------|
| `open_count == 0` AND `entry_count < 50` AND no eligible months | "Clean log — nothing to do. Exiting." |
| `open_count == 0` AND eligible months exist | Proceed — compaction only run |
| `open_count > 0` | Proceed — full analysis + triage needed |
| `entry_count >= 100` | Flag as threshold breach — proceed regardless |

For a "compaction only" run (all entries already applied, just need to compact): skip Steps 2-3, jump directly to Step 5.

### 5. Load historical context

Check `systems/error-tracking/digests/` for existing compaction digests. If any exist, note:
- Most recent period covered
- Top category from that period (for trend comparison in Step 2)

Check `systems/error-tracking/_meta.json` for `patterns.last_analyzed` date. If analysis ran recently (< 7 days), note it — the analysis in Step 2 can be abbreviated.

### 6. Open eval record and write initial state

Open the eval record for this workflow run:

```bash
cd <IES root> && python3 systems/eval-harness/new-eval.py
```

Capture the returned eval id (e.g. `eval-20260527T143022-AB1234`). Open the created file and update these fields:

```json
{
  "type": "workflow",
  "name": "error-improvement",
  "agent": "rigby",
  "trigger": "<manual | scheduled | weekly-review>",
  "status": "in-progress"
}
```

Record the step start time now, so Step 7 has accurate per-step timing.

Update `workflows/error-improvement/state.yaml`:

```yaml
status: in-progress
session-started: <ISO-8601 UTC>
session-id: <generate: rigby-YYYY-MM-DD-HHmmss>
eval-record-id: <eval id from new-eval.py>
current-step: step-02-analyze
accumulated-context:
  entry_count_at_start: <N>
  analysis_period: "<oldest entry date> to <newest entry date>"
  step_timings:
    - step: step-01-intake
      started: <ISO-8601 UTC>
      completed: <ISO-8601 UTC>
```

---

## SUCCESS METRICS

- Gate decision reached and reported
- Entry count and eligibility breakdown captured
- state.yaml updated with session-id and initial context

## FAILURE MODES

| Failure | Action |
|---------|--------|
| compact.py not found or fails | Report error, attempt `python3 systems/error-tracking/rebuild-log.py --out /tmp/error-log-view.json` as fallback for entry count |
| entries/ directory empty | Report: "Clean log — no entries. Nothing to analyze or compact." Set status: complete. Exit. |
| state.yaml already in-progress | Ask controller before proceeding |

## NEXT STEP

[Step 02 — Analyze](step-02-analyze.md)
<!-- system:end -->
