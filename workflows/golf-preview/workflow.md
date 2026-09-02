---
name: golf-preview
description: Phase 1 of the weekly golf booking workflow. Evaluates the upcoming weekend (Friday–Sunday) for viable tee time windows using Outlook calendar, Frisco TX weather, and drought history. Scores each window and notifies #golf at least 24 hours before the golf-booking workflow runs at midnight. Converted from skills/golf-preview/SKILL.md with deterministic quality gates added at each handoff point.
agent: sterling
model: haiku
schedule: |
  Weekly, Tuesday 11:00 PM CT (targets the following Friday–Sunday, 9 days out
  at preview time, 8 days out when golf-booking runs at midnight)
rocks: Personal — Golf & Leisure
---

<!-- system:start -->

# Golf Preview Workflow

**Goal:** Evaluate the upcoming weekend for viable tee times at Frisco Lakes Golf Club and
notify David via Slack with 2-3 scored options, at least 24 hours before the golf-booking
workflow's midnight run. This workflow never books — it only evaluates and recommends.

**Agent:** Sterling — Social Life & Leisure

**Predecessor of:** `workflows/golf-booking/workflow.md` — golf-booking reads this workflow's
output (`preview-output.json`) and performs the actual reservation.

---

## WHY THIS EXISTS AS A WORKFLOW, NOT A SKILL

The original `skills/golf-preview/SKILL.md` did all of this in one undifferentiated pass —
correct logic, but no checkpoint where a bad date calculation, a missed calendar conflict, or
a silently-failed Slack send could be caught before it propagated to the next phase. This
workflow keeps every rule from the skill but adds **four deterministic quality gates** — one
per handoff point — so a failure surfaces immediately with a specific retry instruction
instead of silently producing a bad `preview-output.json` that golf-booking then acts on at
midnight with no human in the loop.

---

## INITIALIZATION

### Data Sources

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Outlook Calendar | David + Susie conflicts for target weekend, last golf round (drought check) | MS365 MCP |
| Weather API | 14-16 day hourly forecast for Frisco TX | WebFetch (Open-Meteo, NWS fallback) |
| Working memory | Any override instructions David left on a prior preview | `memory/working/` |
| Slack | Notification delivery | master-slack skill |

### Paths

- `state_file` = `workflows/golf-preview/state.yaml`
- `preview_output` = `workflows/golf-booking/preview-output.json` (shared handoff artifact —
  lives under `golf-booking/` for backward compatibility with the existing scheduled task and
  golf-booking's read path; golf-preview writes it, golf-booking reads it)
- `verify_scripts` = `workflows/golf-preview/verify/*.py`

### Context Boundaries

- Target course: Frisco Lakes Golf Club, Frisco TX (zip: 75034)
- Members: David O'Hara + Susie O'Hara (both "41 - Frisco Lakes Total Member")
- Membership: Frisco Lakes Total Member — 8-day advance booking window
- Preview window: Friday, Saturday, Sunday of the target weekend
- Goal: one round per weekend, 18 holes preferred

---

## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.
2. If `status: in-progress`: resume from `current-step`. Load `accumulated-context`.
3. If `status: not-started` or `status: complete`: fresh run. Clear `accumulated-context`.
4. If `status: aborted` or `status: gate-failed`: surface to controller and wait for instruction
   — do not silently retry a workflow that halted on a quality gate without a human decision,
   unless this is an automatic scheduled retry within the same booking window (see FAILURE
   MODES).

---

## EXECUTION

Read and follow each step file in order. Do not skip a step's gate to save time — a failed
gate is cheaper to fix now than after golf-booking has already acted on bad data at midnight.

| Step | File | Produces | Gate |
|------|------|----------|------|
| 1 | `steps/step-01-calculate-target-weekend.md` | Validated target Fri/Sat/Sun dates | **Gate 1 — Date Validation** (hard, blocking) |
| 2 | `steps/step-02-calendar-conflict-check.md` | Per-day availability + CT time windows | **Gate 2 — CT Timeline Integrity** (soft, logged) |
| 3 | `steps/step-03-drought-and-weather.md` | Drought flag, weather scoring, heat-streak flag | **Gate 3 — Weather Data Availability** (soft, degrade-and-flag) |
| 4 | `steps/step-04-score-and-write-output.md` | `preview-output.json` | **Gate 4 — Output Schema** (hard, blocking) |
| 5 | `steps/step-05-notify-slack.md` | Slack message to #golf | **Gate 5 — Slack Delivery** (hard, blocking with fallback) |

Update `state.yaml` `current-step` after each step completes. On any hard-gate failure, set
`status: gate-failed`, record the gate's `retry_instruction` in `resolution-note`, and stop —
do not advance to the next step with unvalidated data.

---

## QUALITY GATE SUMMARY

Each gate is documented in full inside its owning step file. Summary:

| Gate | Type | Enforced by | On failure |
|------|------|-------------|------------|
| 1. Date Validation | Hard | Inline checklist in step-01 (mirrors skill's Step 1a table) | Halt, recalculate, do not proceed to step-02 |
| 2. CT Timeline Integrity | Soft | Inline self-check in step-02 | Log and flag in Slack; do not silently compare raw UTC |
| 3. Weather Data Availability | Soft | Inline fallback chain in step-03 | Degrade to calendar-only scoring, flag in Slack, never fail silently |
| 4. Output Schema | Hard | `verify/step-04-output-schema.py` | Retry step-04, do not proceed to step-05 with malformed output |
| 5. Slack Delivery | Hard (with fallback) | `verify/step-05-slack-delivery.py` + inline retry | Write `memory/working/golf-preview-YYYY-MM-DD.md` fallback and log error — never fail silently |

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Calendar unavailable | Proceed with weather only. Flag in Slack: "⚠️ Calendar unavailable — verify no conflicts." |
| Weather API fails (both Open-Meteo and NWS) | Proceed with calendar-only scoring. Note in Slack: "⚠️ Weather data unavailable for target dates." |
| No viable windows exist | Send Slack: "⛳ No viable golf windows this weekend — [reasons]. No booking will be made." Write `preview-output.json` with empty `top_options` and an explanation — Gate 4 will flag this, so include the explanation in a `no_viable_reason` field to keep the gate honest about a legitimate zero-option outcome. |
| Slack send fails | Write fallback to `memory/working/golf-preview-YYYY-MM-DD.md`, log error to `systems/error-tracking/entries/`. Do not fail silently — this is Gate 5's job to catch. |
| Gate 1 (date validation) fails | Halt immediately. Do not proceed to any calendar/weather lookup with unvalidated dates. Recalculate and re-run step-01. |
| Gate 4 (output schema) fails | Do not send Slack. Re-run step-04 with the `retry_instruction` from the verifier. |

---

## OUTPUT

- `workflows/golf-booking/preview-output.json` — scored windows, go/no-go per day, top pick
- Slack message to #golf — 2-3 options with weather + cost
- `state.yaml` updated to `status: complete`, `current-step: step-05`

## NEXT STEP

Hands off to `workflows/golf-booking/workflow.md`, which reads `preview-output.json` at
midnight (8 days before the target date) and performs the live booking.

## SKILL COMPLETE

After the workflow's final output is delivered, write the skill-run signal file so the eval
harness captures this execution:

```
systems/eval-harness/skill-runs/golf-preview-latest.json
```

Content:
```json
{
  "skill": "golf-preview",
  "agent": "sterling",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this workflow began>",
  "completed": "<ISO-8601 timestamp when this workflow finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from the morning briefing or a boot workflow, `"scheduled"`
if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if any soft
gate degraded (Gate 2 or Gate 3 flagged), `"failure"` if a hard gate (1, 4, or 5) blocked
completion and no fallback recovered it. Use the actual start time of this workflow's
execution for `started`. This write is always the final action.

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
