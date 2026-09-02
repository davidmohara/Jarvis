---
status: complete
started-at: "2026-09-02T00:12:00-05:00"
completed-at: "2026-09-02T00:20:00-05:00"
outputs:
  drought: false
  last_round: "2026-08-29"
  weather_source: "open-meteo"
  weather_data_missing: false
  heat_streak: false
  heat_streak_days_at_or_above_99: 4
  heat_streak_calc_failed: false
  windows:
    saturday_1pm: { avg_temp_f: 96.2, max_rain_pct: 17, max_wind_mph: 18.5, condition: "clear", temp_penalty_applied: true }
    saturday_4pm: { avg_temp_f: 95.6, max_rain_pct: 17, max_wind_mph: 18.5, condition: "clear", temp_penalty_applied: true }
    sunday_230pm: { avg_temp_f: 96.4, max_rain_pct: 17, max_wind_mph: 15.7, condition: "clear", temp_penalty_applied: true }
model: haiku
---

<!-- system:start -->
# Step 03: Drought Check and Weather Evaluation

## MANDATORY EXECUTION RULES

1. Weather is a soft block — note it, don't auto-skip a day unless rain probability > 60%.
2. Do not use calendar month as a proxy for heat — use actual forecast data for the
   heat-streak rule.
3. If weather data is unavailable after both fallbacks, proceed with calendar-only scoring —
   **QUALITY GATE 3** governs exactly how that degradation must be surfaced.

---

## EXECUTION PROTOCOL

**Agent:** Sterling
**Input:** Day-status and CT windows from step-02
**Output:** `drought` flag, weather scores per candidate window, `heat_streak` flag

---

## YOUR TASK

### Last Round Check (3-Week Drought Rule)

Search Outlook calendar for golf blocks in the past 21 days:
```
mcp__b8c41a14__outlook_calendar_search
query: "golf"
start_datetime: [21 days ago]T00:00:00
end_datetime: [yesterday]T23:59:59
```

If no golf round found in 21 days → `drought: true`

When `drought: true`:
- Expand viable window to include early morning 9-hole options (Friday–Sunday, $21)
- Include late rounds (6:00 PM+, free, 9-hole) as viable fallback options
- Note in Slack (step-05): "21+ days since last round — including early morning and late options"

### Weather Evaluation

Fetch the 16-day hourly forecast for Frisco TX via Open-Meteo (free, no API key, covers up to
16 days out):

```
mcp__workspace__web_fetch
url: https://api.open-meteo.com/v1/forecast?latitude=33.1507&longitude=-96.8236&hourly=temperature_2m,precipitation_probability,precipitation,windspeed_10m,cloudcover&temperature_unit=fahrenheit&windspeed_unit=mph&precipitation_unit=inch&timezone=America%2FChicago&forecast_days=14
```

The response contains an `hourly` object with parallel arrays indexed by hour, each index
corresponding to one entry in `hourly.time` (ISO8601, local CT).

**Extracting data for a candidate window (e.g., Saturday 1:00–4:00 PM):**
1. Find all indices in `hourly.time` where the date matches the target day and the hour falls
   within the window (13:00–16:00).
2. For those indices, read `temperature_2m`, `precipitation_probability`, `precipitation`,
   `windspeed_10m`, `cloudcover`.
3. Use the **max** rain probability and **max** wind speed across the window for conservative
   scoring. Use the **average** temperature across the window.

**Weather scoring:**
- Rain > 60% → mark window `weather_blocked` (skip)
- Rain 30–60% → mark window `weather_caution` (include with warning)
- Rain < 30% → `weather_clear`
- Temperature < 45°F → flag as cold, note in Slack
- Wind > 25 mph → flag, note in Slack

**If Open-Meteo fetch fails**, fall back to:
```
mcp__workspace__web_fetch
url: https://forecast.weather.gov/MapClick.php?CityName=Frisco&state=TX&site=FWD&textField1=33.1507&textField2=-96.8236&FcstType=json
```
NWS provides 7-day hourly JSON — sufficient if the target weekend is within 7 days. If still
insufficient range, proceed with calendar-only scoring — this is where Gate 3 applies.

**Determining time preference — heat streak rule:**

Do NOT use calendar month as a proxy for heat. Use the actual forecast data.

1. Pull the daily high temperature for each of the 5 days immediately preceding the target
   Friday (i.e., ending on Thursday before the weekend). For each day, find the max
   `temperature_2m` value across all hours in `hourly.time` for that date.
2. Count how many of those 5 days had a daily high ≥ 99°F.
3. If all 5 days were ≥ 99°F → `heat_streak: true` → default preferred start is **4:00 PM**
   ($15/player)
4. If fewer than 5 days were ≥ 99°F → `heat_streak: false` → default preferred start is
   **1:00 PM** ($21/player)

When `heat_streak: false`, still check the forecast for the candidate tee time window itself.
If the average temperature during a 1:00 PM window on the target day exceeds 95°F, apply a +8
scoring penalty (applied in step-04) to push toward later windows — but do not change the
default start.

---

## QUALITY GATE 3 — Weather Data Availability (SOFT, DEGRADE-AND-FLAG)

Weather is inherently a soft input — a missing forecast should never block a viable
calendar-clear day from reaching David. But the workflow must never silently pretend it has
weather data when it doesn't.

| Condition | Required action |
|-----------|------------------|
| Open-Meteo succeeded | `weather_source: "open-meteo"`. Proceed normally. |
| Open-Meteo failed, NWS succeeded and covers the target dates | `weather_source: "nws-fallback"`. Proceed normally, no flag needed. |
| Open-Meteo failed, NWS failed or insufficient range | `weather_source: "unavailable"`. **Must** set `weather_data_missing: true` in this step's output. This flag is mandatory — step-04's Gate 4 checks for it and step-05 must surface "⚠️ Weather data unavailable for target dates." in the Slack message. Proceeding with calendar-only scoring is acceptable; proceeding *silently* is not. |
| Heat-streak calculation could not run (insufficient prior-week data) | Default to `heat_streak: false` (safer default — $21/1PM) and note `heat_streak_calc_failed: true`. |

Log:
```
[Gate 3] Weather source: open-meteo | nws-fallback | unavailable
[Gate 3] Heat streak: true | false (N of 5 days ≥ 99°F, or calc_failed)
[Gate 3] Drought: true | false
```

Update `state.yaml`'s `accumulated-context` with `drought`, `heat_streak`,
`weather_data_missing` (if applicable), and per-window weather scores. Set
`current-step: step-04`.

---

## SUCCESS METRICS

- Every available day/window has either real weather data or an explicit `weather_data_missing`
  flag — never an implicit gap
- Heat-streak determination is based on actual forecast data, never calendar month

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Both weather sources fail | Set `weather_data_missing: true`. Proceed with calendar-only scoring in step-04. Flag in Slack in step-05. Do not treat this as a hard failure of the workflow. |
| Heat-streak data incomplete | Default to `heat_streak: false`, note `heat_streak_calc_failed: true`, proceed. |

## NEXT STEP

Read fully and follow: `step-04-score-and-write-output.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
