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

**Get today's date:** Read `currentDate` from the system context (`<env>` block / system-reminder). This is always the authoritative source.

**Fallback only if `currentDate` is unavailable:** Get the current local date from Mac:
```bash
mcp__Desktop_Commander__start_process
command: osascript -e 'do shell script "date \"+%Y-%m-%d %A\""'
```

**Calculate the target Friday** — the first Friday that is at least 8 days from today. This ensures the booking window (which opens at midnight 8 days before the target date) has not already passed.

```
days_until_friday = (4 - current_day_of_week) % 7
if days_until_friday == 0:
    days_until_friday = 7   # If today IS Friday, start from next Friday
candidate_friday = today + days_until_friday

# Enforce 8-day minimum — booking window must still be openable
if candidate_friday < today + 8:
    candidate_friday = candidate_friday + 7  # Skip to the following Friday
```

Where day_of_week: Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4, Saturday=5, Sunday=6.

Examples (membership requires 8-day advance booking):
- Run on Wednesday May 13 (2): next Friday is May 15 = 2 days away → too soon (< 8), skip to May 22 ✓
- Run on Tuesday May 12 (1): next Friday is May 15 = 3 days away → too soon, skip to May 22 ✓
- Run on Saturday May 16 (5): next Friday is May 22 = 6 days away → too soon, skip to May 29 ✓
- Run on Saturday May 17 (6): next Friday is May 22 = 5 days away → too soon... wait, (4-6)%7=5, May 22 is 5 days away → too soon, skip to May 29 ✓
- Run on Friday May 15 (4): days_until=7, candidate=May 22 = 7 days away → too soon (< 8), skip to May 29 ✓
- Run on Thursday May 14 (3): next Friday May 15 = 1 day away → too soon, skip to May 22 = 8 days away ✓

Then:
- **Target Saturday** = target_friday + 1
- **Target Sunday** = target_friday + 2

Store: `target_friday`, `target_saturday`, `target_sunday` (YYYY-MM-DD format)

---

### Step 1a — Date Validation

Before proceeding to any calendar or weather lookups, validate all three dates explicitly. **Do not skip this step.**

Run the following checks and surface any failure immediately — halt execution if any check fails:

| Check | Expected | Failure action |
|-------|----------|---------------|
| `target_friday` is a Friday | day_of_week == 4 | Stop. Recalculate. Report error. |
| `target_saturday` is a Saturday | day_of_week == 5 | Stop. Recalculate. Report error. |
| `target_sunday` is a Sunday | day_of_week == 6 | Stop. Recalculate. Report error. |
| `target_saturday` == `target_friday` + 1 day | Date arithmetic check | Stop. Recalculate. |
| `target_sunday` == `target_friday` + 2 days | Date arithmetic check | Stop. Recalculate. |
| `target_friday` >= today + 8 | Booking window not yet passed | Stop. Advance to following Friday. |
| `target_saturday` >= today + 9 | Booking window not yet passed for Saturday | Stop. Advance weekend by 7 days. |
| `target_sunday` >= today + 10 | Booking window not yet passed for Sunday | Note Sunday may not be bookable yet — proceed with Friday/Saturday only. |

Log the validated dates before moving on:
```
[Validation] Today: YYYY-MM-DD (DayOfWeek)
[Validation] Target Friday:   YYYY-MM-DD (Friday) — N days out ✓
[Validation] Target Saturday: YYYY-MM-DD (Saturday) — N days out ✓
[Validation] Target Sunday:   YYYY-MM-DD (Sunday) — N days out ✓
[Validation] All dates confirmed. Proceeding.
```

---

### Step 2 — Calendar Conflict Check

Pull Outlook calendar for the target Friday, Saturday, and Sunday using MS365 MCP:

```
mcp__b8c41a14__outlook_calendar_search
query: ""
start_datetime: [target_friday]T00:00:00
end_datetime: [target_sunday]T23:59:59
```

**⚠️ UTC→CT conversion is mandatory and applies everywhere.** All event times returned by the calendar API are in UTC. David is in CT (CDT = UTC-5 in summer, CST = UTC-6 in winter). You must convert every `start` and `end` timestamp to CT before:
- Assigning an event to a calendar day
- Calculating when a busy block starts and ends
- Identifying free windows between events
- Checking whether a 3-hour gap exists within a target time range

**Conversion rule:** Subtract 5 hours from UTC timestamps (CDT, roughly April–October). If the resulting time crosses midnight backward, the event belongs to the previous calendar day.

Example: `2026-05-22T23:30:00.000Z` → subtract 5h → 6:30 PM CT on May 22 (not May 23).

**Build a CT timeline for each day before analysis.** For each of Friday, Saturday, and Sunday:
1. Collect all events whose CT start or end falls within that calendar day (midnight–11:59 PM CT)
2. Sort by CT start time
3. Map out busy blocks as CT time ranges: e.g., `[13:00–14:30, 16:00–17:00]`
4. Identify free gaps between busy blocks within the target golf window (see per-day rules below)

Do not analyze raw UTC times against CT window boundaries — convert first, analyze second.

---

For each day, identify conflicts and derive the available golf window:

**Hard blocks (mark day as unavailable regardless of timing):**
- Travel / flights / out of town
- Evening dinners with family (parents dinner etc.) — check Saturday and Sunday
- All-day events

**Sunday-specific rules:**
- Church volunteering blocks 8:30 AM – 1:30 PM CT every Sunday. Hard-coded — no golf before 2:30 PM CT on Sundays.
- If Sunday has a dinner with parents on the calendar → prefer Saturday that week. If Saturday also has an event, Sunday is still viable after 2:30 PM CT.

**Friday-specific rules:**
- Susie works from home Fridays — her schedule mirrors David's calendar.
- Using the CT timeline built above, check for a continuous 3-hour free gap between 1:00 PM and 6:00 PM CT. If no such gap exists, mark Friday unavailable.
- If a clear 3-hour window exists (e.g., 3:00–6:00 PM CT free), Friday is viable. Record the exact window start and end.

**Saturday rules:**
- No standing constraints. Using the CT timeline, identify the earliest available start at or after 1:00 PM CT with at least 4.5 hours free before any hard block or end of day (6:30 PM CT latest start for 18 holes).

**Already booked:**
- Search calendar for any existing golf block on the target weekend. If found, mark that day unavailable.

Store per-day status: `available` | `unavailable` | `conditional`
Store reason for any unavailable day.
Store the available CT window (earliest_start, latest_start) for each available day.

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
- Wind > 25 mph → flag, note in Slack

**If Open-Meteo fetch fails**, fall back to:
```
mcp__workspace__web_fetch
url: https://forecast.weather.gov/MapClick.php?CityName=Frisco&state=TX&site=FWD&textField1=33.1507&textField2=-96.8236&FcstType=json
```
NWS provides 7-day hourly JSON — sufficient if the target weekend is within 7 days (e.g., Friday preview with Saturday target). If still insufficient range, proceed with calendar-only scoring and note in Slack: "⚠️ Weather data unavailable for target dates."

**Determining time preference — heat streak rule:**

Do NOT use calendar month as a proxy for heat. Use the actual forecast data.

1. Pull the daily high temperature for each of the 5 days immediately preceding the target Friday (i.e., the 5 days ending on Thursday before the weekend). For each day, find the max `temperature_2m` value across all hours in `hourly.time` for that date.
2. Count how many of those 5 days had a daily high ≥ 95°F.
3. If all 5 days were ≥ 95°F → `heat_streak: true` → default preferred start is **4:00 PM** ($15/player)
4. If fewer than 5 days were ≥ 95°F → `heat_streak: false` → default preferred start is **1:00 PM** ($21/player)

When `heat_streak: false`, still check the forecast for the candidate tee time window itself. If the average temperature during a 1:00 PM window on the target day exceeds 95°F, apply a +8 scoring penalty to push toward later windows — but do not change the default start.

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

**heat_streak: false, Saturday at 1 PM, clear weather = score 0 (ideal).**
**heat_streak: true, Saturday at 4 PM, clear weather = score 0 (ideal).**
**heat_streak: false, Saturday at 4 PM = score +5.**
**Sunday at preferred time in good weather = score ~5.**
**Friday at preferred time in good weather = score ~3.**

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

### Step 7 — Summarize and Send Slack Preview

Before sending Slack, output the full recommendation summary inline (in the session / task log). This makes the output reviewable without opening Slack. Format it as follows:

```
**Target Weekend: [Fri date] – [Sun date]**
- Friday [date]: [available ✅ | unavailable — reason]
- Saturday [date]: [available ✅ | unavailable — reason]
- Sunday [date]: [available ✅ | unavailable — reason]

**Heat streak check ([Mon–Fri before target Friday]):** [temp], [temp], [temp], [temp], [temp] → [N] of 5 hit 95°F → heat_streak: [true|false] → default preferred start [1:00 PM | 4:00 PM]

---

**Rank 1 — [Day Month D, Time]** | Score: [N]
$[cost]/player · [temp]°F · [rain]% rain · [wind] mph wind · [condition] · [rationale]

**Rank 2 — [Day Month D, Time]** | Score: [N]
$[cost]/player · [temp]°F · [rain]% rain · [wind] mph wind · [condition] · [rationale]

[Rank 3 if applicable]
```

Then read and follow `.claude/skills/master-slack/SKILL.md`.

Send to **#golf** (C0B15SW9FB5). The Slack message should mirror the inline summary in condensed form:

```
*⛳ Golf Options — Weekend of [Fri date] – [Sun date]*

_Heat streak: [active 🔥 → default 4 PM | inactive → default 1 PM]_

*1. [Day, Month D] — [Time]*
• 🌤 [temp]°F, [rain]% rain, [wind] mph
• 💰 $[cost]/player · 18 holes · Score: [N]

*2. [Day, Month D] — [Time]*
• 🌤 [temp]°F, [rain]% rain, [wind] mph
• 💰 $[cost]/player · 18 holes · Score: [N]

[3rd option if available]

_Booking at midnight. Reply to redirect — otherwise top option is booked._
```

Example (heat streak inactive, Saturday only available):
```
*⛳ Golf Options — Weekend of May 22–24*

_Heat streak: inactive → default 1 PM ($21/player)_

*1. Saturday, May 23 — 1:00 PM*
• 🌤 83°F, 14% rain, 11 mph
• 💰 $21/player · 18 holes · Score: 0

*2. Saturday, May 23 — 4:00 PM*
• 🌤 85°F, 21% rain, 13 mph
• 💰 $15/player · 18 holes · Score: +5

_Booking at midnight. Reply to redirect — otherwise top option is booked._
```

Example (heat streak active):
```
*⛳ Golf Options — Weekend of Aug 8–10*

_Heat streak: active 🔥 → default 4 PM ($15/player)_

*1. Saturday, Aug 9 — 4:00 PM*
• 🌤 96°F, 5% rain, 8 mph
• 💰 $15/player · 18 holes · Score: 0

*2. Saturday, Aug 9 — 1:00 PM*
• 🌤 102°F, 5% rain, 9 mph
• 💰 $21/player · 18 holes · Score: +8 (playing in heat)

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
