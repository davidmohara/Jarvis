---
name: golf-preview
description: Phase 1 of the golf booking workflow. Evaluates the upcoming weekend (Friday–Sunday) for viable tee time windows by checking David's Outlook calendar, Frisco TX weather, and last round played. Scores each window, selects top 2-3 options, and sends a Slack notification to #golf at least 24 hours before the midnight booking run.
agent: sterling
model: sonnet
trigger_keywords: ["golf preview", "golf options", "tee time preview"]
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->

## MANDATORY EXECUTION RULES

1. Never hardcode dates — always calculate the target weekend dynamically from the current date.
2. Never book a round — this skill only evaluates and notifies. Booking is Phase 2.
3. Always send the Slack notification even if only one viable window is found.
4. If no viable windows exist, still send Slack explaining why — do not silently skip.
5. Always write output to `workflows/golf-booking/preview-output.json` before sending Slack.
6. Treat calendar conflicts as hard blocks. Treat weather as a soft block (note it, don't auto-skip unless rain probability > 60%).

---

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Rigby |
| Input | Current date, Outlook calendar, weather API, calendar history |
| Output | `preview-output.json`, Slack message to #golf |

---

## CONTEXT BOUNDARIES

- Target course: Frisco Lakes Golf Club, Frisco TX (zip: 75034)
- Members: David O'Hara + Susie O'Hara (both "41 - Frisco Lakes Total Member")
- Membership: Frisco Lakes Total Member — 8-day advance booking window
- Booking opens: midnight, 8 days before the target date
- Preview window: Friday, Saturday, Sunday of the target weekend
- Goal: one round per weekend, 18 holes preferred

---

## YOUR TASK

### Step 1 — Calculate Target Weekend

Get the current local date from Mac:
```bash
mcp__Desktop_Commander__start_process
command: osascript -e 'do shell script "date \"+%Y-%m-%d %A\""'
```

Calculate:
- **Target Saturday** = current date + 9 days (preview runs Tuesday 11pm, Saturday is 10 days out; use +9 for the day that opens at midnight in ~1 hour)
- **Target Friday** = Target Saturday - 1
- **Target Sunday** = Target Saturday + 1

Store: `target_friday`, `target_saturday`, `target_sunday` (YYYY-MM-DD format)

---

### Step 2 — Calendar Conflict Check

Pull Outlook calendar for the target Friday, Saturday, and Sunday using MS365 MCP:

```
mcp__b8c41a14__outlook_calendar_search
query: ""
start_datetime: [target_friday]T00:00:00
end_datetime: [target_sunday]T23:59:59
```

For each day, identify conflicts:

**Hard blocks (mark day as unavailable):**
- Travel / flights / out of town
- Evening dinners with family (parents dinner etc.) — check Saturday and Sunday
- All-day events

**Sunday-specific rules:**
- Church volunteering blocks 8:30 AM – 1:30 PM every Sunday. Hard-coded — no golf before 2:30 PM on Sundays.
- If Sunday has a dinner with parents on the calendar → prefer Saturday that week. If Saturday also has an event, Sunday is still viable after 2:30 PM.

**Friday-specific rules:**
- Susie works from home Fridays — her schedule mirrors David's calendar.
- Scan for back-to-back work meetings that would block a continuous 3-hour window between 1:00 PM and 6:00 PM. If no 3-hour window exists, mark Friday unavailable.
- If a clear 3-hour window exists (e.g., 3:00–6:00 PM free), Friday is viable.

**Already booked:**
- Search calendar for any existing golf block on the target weekend. If found, mark that day unavailable.

Store per-day status: `available` | `unavailable` | `conditional`
Store reason for any unavailable day.

---

### Step 3 — Last Round Check (3-Week Drought Rule)

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
- Note in Slack: "21+ days since last round — including early morning and late options"

---

### Step 4 — Weather Evaluation

Fetch the 16-day hourly forecast for Frisco TX via Open-Meteo (free, no API key, covers up to 16 days out):

```
mcp__workspace__web_fetch
url: https://api.open-meteo.com/v1/forecast?latitude=33.1507&longitude=-96.8236&hourly=temperature_2m,precipitation_probability,precipitation,windspeed_10m,cloudcover&temperature_unit=fahrenheit&windspeed_unit=mph&precipitation_unit=inch&timezone=America%2FChicago&forecast_days=14
```

The response contains an `hourly` object with parallel arrays indexed by hour. Each index corresponds to one entry in `hourly.time` (ISO8601, local CT).

**Extracting data for a candidate window (e.g., Saturday 1:00–4:00 PM):**
1. Find all indices in `hourly.time` where the date matches the target day and the hour falls within the window (13:00–16:00).
2. For those indices, read:
   - `hourly.temperature_2m[i]` → temperature (°F)
   - `hourly.precipitation_probability[i]` → rain probability (%)
   - `hourly.precipitation[i]` → actual precip (inches)
   - `hourly.windspeed_10m[i]` → wind speed (mph)
   - `hourly.cloudcover[i]` → cloud cover (%)
3. Use the **max** rain probability and **max** wind speed across the window for conservative scoring. Use the **average** temperature across the window.

**Weather scoring:**
- Rain > 60% → mark window `weather_blocked` (skip)
- Rain 30–60% → mark window `weather_caution` (include with warning)
- Rain < 30% → `weather_clear`
- Temperature < 45°F → flag as cold, note in Slack
- Temperature > 95°F → flag as hot, prefer later windows (4:00 PM+)
- Wind > 25 mph → flag, note in Slack

**If Open-Meteo fetch fails**, fall back to:
```
mcp__workspace__web_fetch
url: https://forecast.weather.gov/MapClick.php?CityName=Frisco&state=TX&site=FWD&textField1=33.1507&textField2=-96.8236&FcstType=json
```
NWS provides 7-day hourly JSON — sufficient if the target weekend is within 7 days (e.g., Friday preview with Saturday target). If still insufficient range, proceed with calendar-only scoring and note in Slack: "⚠️ Weather data unavailable for target dates."

**Seasonal time preference:**
- May–September (hot months): prefer 4:00–4:30 PM start → costs $15/player
- October–April (mild months): 1:00–2:00 PM start → costs $21/player
- Current month determines default. Override toward later if temp > 90°F at 1 PM.

---

### Step 5 — Score Available Windows

For each available day (not hard-blocked, not weather-blocked), generate candidate time windows and score them.

**Candidate windows per day:**

| Day | Earliest Start | Latest Preferred | Notes |
|-----|---------------|-----------------|-------|
| Friday | 1:00 PM | 6:00 PM | Only if 3-hour block available; avoid back-to-back meetings |
| Saturday | 1:00 PM | 6:00 PM | Best day — no standing constraints |
| Sunday | 2:30 PM | 6:00 PM | Church ends 1:30 PM; 1-hour buffer |

**Scoring model (lower is better):**

Start with base score 0. Add penalties:

| Condition | Penalty |
|-----------|---------|
| Round cost $21/player (1:00–3:59 PM) | 0 — preferred |
| Round cost $15/player (4:00–5:59 PM) | +5 |
| Round cost $0/player (6:00 PM+, 9-hole only) | +15 |
| Early morning 9-hole ($21/player) | +20 — drought fallback only |
| Weather caution (rain 30–60%) | +10 |
| Sunday (church buffer, tighter window) | +5 |
| Friday (work day, conditional availability) | +3 |
| Temperature > 90°F at preferred time | +8 — push toward later |
| 9-hole round (non-drought fallback) | +25 |
| Drought override — 9-hole acceptable | -10 penalty removed |

**Saturday at 1 PM in good weather = score 0 (ideal).**
**Sunday at 4:30 PM in good weather = score ~10.**
**Friday at 3 PM in good weather = score ~3.**

Pick the top 3 scored windows across all available days.

---

### Step 6 — Write Preview Output

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
  "override_instructions": null
}
```

If David replied to a previous Slack preview with instructions, honor them:
- Check working memory (`memory/working/`) for any golf override notes from this week
- If found, store in `override_instructions` and weight scoring accordingly

---

### Step 7 — Send Slack Preview

Read and follow `.claude/skills/master-slack/SKILL.md`.

Send to **#golf** (C0B15SW9FB5):

```
*⛳ Golf Options — Weekend of [Fri date] – [Sun date]*

[For each top option, show:]
*[Rank]. [Day, Month D] — [Time range]*
• 🌤 [Weather summary: temp, rain%, wind]
• 💰 $[cost]/player · [18|9] holes
• [Any notes: drought flag, weather caution, conflict reason]

_Booking at midnight. Reply to redirect — otherwise top option is booked._
```

Example:
```
*⛳ Golf Options — Weekend of May 9–11*

*1. Saturday, May 10 — 1:00–2:30 PM*
• 🌤 78°F, 10% rain, 8 mph wind
• 💰 $21/player · 18 holes

*2. Sunday, May 11 — 2:30–4:00 PM*
• 🌤 82°F, 20% rain, 12 mph wind
• 💰 $21/player · 18 holes

*3. Friday, May 9 — 3:00–5:00 PM*
• 🌤 75°F, 5% rain, 6 mph wind
• 💰 $21/player · 18 holes

_Booking at midnight. Reply to redirect — otherwise top option is booked._
```

---

## SUCCESS METRICS

- `preview-output.json` written with at least 1 top option
- Slack message sent to #golf before midnight (at least 1 hour before booking run)
- All available days evaluated — no silent skips
- Weather data present for all candidate windows

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Calendar unavailable | Proceed with weather only. Flag in Slack: "⚠️ Calendar unavailable — verify no conflicts." |
| Weather API fails | Proceed with calendar only. Note in Slack: "⚠️ Weather data unavailable." |
| No available days | Send Slack: "⛳ No viable golf windows this weekend — [reasons]. No booking will be made." Write empty preview-output.json with explanation. |
| Slack fails | Write output to `memory/working/golf-preview-YYYY-MM-DD.md` as fallback. Log error. |

---

## NEXT STEP

Phase 2 — `skills/golf-booking/SKILL.md` runs at midnight, reads `preview-output.json`, and books.

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
