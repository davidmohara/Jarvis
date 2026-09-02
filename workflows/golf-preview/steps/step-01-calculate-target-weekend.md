---
status: complete
started-at: "2026-09-02T00:00:00-05:00"
completed-at: "2026-09-02T00:05:00-05:00"
outputs:
  target_friday: "2026-09-11"
  target_saturday: "2026-09-12"
  target_sunday: "2026-09-13"
  gate_1_result: "pass"
  recalculation_count: 0
model: haiku
---

<!-- system:start -->
# Step 01: Calculate and Validate Target Weekend

## MANDATORY EXECUTION RULES

1. Never hardcode dates — always calculate the target weekend dynamically from the current date.
2. Do not proceed to step-02 until every check in **QUALITY GATE 1** below has passed.
3. Before executing, write `status: in-progress` and `started-at` to this file's frontmatter.
4. Date math for the target Friday goes through the `calendar-handler` skill
   (`skills/calendar-handler/SKILL.md`, `operation: date-calculate`) — do not re-derive the
   weekday/min-days-out arithmetic inline. That skill is now the single source of this logic
   across every workflow that needs "next occurrence of a weekday, at least N days out."

---

## EXECUTION PROTOCOL

**Agent:** Sterling
**Input:** Current date (`currentDate` from system context)
**Output:** Validated `target_friday`, `target_saturday`, `target_sunday`, stored in `state.yaml`'s `accumulated-context`

---

## YOUR TASK

### Get Today's Date

Read `currentDate` from the system context (`<env>` block / system-reminder). This is always
the authoritative source.

**Fallback only if `currentDate` is unavailable:**
```bash
mcp__Desktop_Commander__start_process
command: osascript -e 'do shell script "date \"+%Y-%m-%d %A\""'
```

### Calculate the Target Friday via calendar-handler

Call `skills/calendar-handler/SKILL.md`:

```yaml
operation: date-calculate
calendar_backend: M365   # explicit per this workflow's convention; date-calculate does no
                         # calendar lookup itself, so this has no behavioral effect today —
                         # see calendar-handler's date-calculate backend note
base_date: "{{today, from currentDate}}"
offset_type: specific-day
specific_day: "Friday"
min_days_out: 8   # membership requires 8-day advance booking — the window opens at
                  # midnight 8 days before the target date, so anything closer isn't
                  # bookable yet
```

The skill returns `target_date`, `day_of_week`, and `days_from_base` — assign
`target_date` to `target_friday`. The skill enforces the "at least 8 days out, skip to the
following Friday if not" rule internally (see calendar-handler's `date-calculate` process,
step 2, `next-weekend`/`specific-day` branch) and validates the result before returning it, so
this step does not need to re-implement or re-check that arithmetic — Quality Gate 1 below
still re-validates the *returned* dates as this workflow's own independent safety net, since a
wrong date here is expensive downstream.

Worked examples of the min-days-out behavior (for reference, not re-implementation):
- Run on Wednesday May 13: next Friday May 15 is 2 days away → too soon (< 8), skill returns May 22
- Run on Saturday May 17: next Friday May 22 is 5 days away → too soon, skill returns May 29
- Run on Thursday May 14: next Friday May 15 is 1 day away → too soon, skill returns May 22 (8 days out)

### Derive Saturday and Sunday

This is plain date arithmetic on the skill's returned `target_friday`, not calendar logic, so
it stays inline:
- **Target Saturday** = target_friday + 1
- **Target Sunday** = target_friday + 2

Store: `target_friday`, `target_saturday`, `target_sunday` (YYYY-MM-DD format)

---

## QUALITY GATE 1 — Date Validation (HARD, BLOCKING)

**This is the workflow's most important gate.** A wrong date here is silent and expensive —
it propagates through calendar checks, weather lookups, scoring, and eventually into a real
midnight booking attempt at golf-booking, where MANDATORY RULE #15 there explicitly forbids
substituting a different date. Get it right here or nowhere.

Run every check below and halt on the first failure. Do not proceed to step-02 with an
unvalidated date.

| Check | Expected | On failure |
|-------|----------|------------|
| `target_friday` is a Friday | day_of_week == 4 | **STOP.** Recalculate. Report error to controller. |
| `target_saturday` is a Saturday | day_of_week == 5 | **STOP.** Recalculate. |
| `target_sunday` is a Sunday | day_of_week == 6 | **STOP.** Recalculate. |
| `target_saturday` == `target_friday` + 1 day | Date arithmetic check | **STOP.** Recalculate. |
| `target_sunday` == `target_friday` + 2 days | Date arithmetic check | **STOP.** Recalculate. |
| `target_friday` >= today + 8 | Booking window not yet passed | **STOP.** Advance to following Friday and re-run this step. |
| `target_saturday` >= today + 9 | Booking window not yet passed for Saturday | **STOP.** Advance weekend by 7 days. |
| `target_sunday` >= today + 10 | Booking window not yet passed for Sunday | Note only — Sunday may not be bookable yet; proceed with Friday/Saturday and flag Sunday as `conditional` in step-02. Not a halt condition. |

Log the validated dates before moving on — this log line is the gate's audit trail, not
optional flavor text:

```
[Gate 1] Today: YYYY-MM-DD (DayOfWeek)
[Gate 1] Target Friday:   YYYY-MM-DD (Friday) — N days out ✓
[Gate 1] Target Saturday: YYYY-MM-DD (Saturday) — N days out ✓
[Gate 1] Target Sunday:   YYYY-MM-DD (Sunday) — N days out ✓
[Gate 1] PASS — all checks confirmed. Proceeding to step-02.
```

If any check fails, log `[Gate 1] FAIL — <check name> — recalculating` and re-run the
calculation before attempting to log a PASS.

Write the outcome to this file's frontmatter:
```yaml
outputs:
  target_friday: "YYYY-MM-DD"
  target_saturday: "YYYY-MM-DD"
  target_sunday: "YYYY-MM-DD"
  gate_1_result: "pass" | "fail-recalculated"
  recalculation_count: <int>
```

Update `state.yaml`'s `accumulated-context` with the three validated dates and set
`current-step: step-02`.

---

## SUCCESS METRICS

- Gate 1 passes on the recorded dates before step-02 begins
- No hardcoded dates anywhere in the calculation

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Gate 1 check fails repeatedly (3+ recalculations) | Abort. Set `state.yaml` `status: gate-failed`. Report to controller: "[Sterling]: Date calculation for golf preview failed validation after 3 attempts — needs a human look." |
| `currentDate` unavailable and Mac fallback also fails | Abort. Do not guess the date. Report to controller. |

## NEXT STEP

Read fully and follow: `step-02-calendar-conflict-check.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
