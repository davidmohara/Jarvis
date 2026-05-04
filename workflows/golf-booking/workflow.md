---
name: golf-booking
description: Weekly tee time booking workflow for Frisco Lakes Golf Club. Runs in two phases — preview (11pm, 9 days out) evaluates calendar, weather, and scores the best windows, then notifies David via Slack. Booking (midnight, 8 days out) reads the preview output, opens ChronoGolf via Chrome, and books the best available slot in real time.
agent: sterling
model: sonnet
schedule: |
  Preview: weekly, Tuesday 11:00 PM CT (targets the following Friday–Sunday)
  Booking: weekly, Wednesday 12:00 AM CT (8 days before target Saturday)
rocks: Personal — Golf & Leisure
---

<!-- system:start -->

# Golf Booking Workflow

**Goal:** Automatically secure a weekly tee time at Frisco Lakes Golf Club for David and Susie
O'Hara, optimizing for cost, weather, and calendar fit. Minimize David's involvement to a
single Slack message review — unless he redirects.

**Agent:** Sterling — Social Life & Leisure

**Architecture:** Two sequential phases per week.
- **Phase 1 — Preview** (`skills/golf-preview/SKILL.md`): Calendar + weather + scoring → Slack notification
- **Phase 2 — Booking** (`skills/golf-booking/SKILL.md`): Real-time ChronoGolf booking → calendar block + Slack confirmation

---

## INITIALIZATION

### Data Sources

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Outlook Calendar | David + Susie conflicts for target weekend | MS365 MCP |
| Weather API | Hourly forecast for Frisco TX on target days | WebFetch (wttr.in or open-meteo) |
| Obsidian / Calendar | Last golf round played (for 3-week drought check) | Search calendar for prior golf blocks |
| ChronoGolf | Live tee time availability | Control Chrome MCP |
| Slack | Notification delivery | master-slack skill |

### Paths

- `preview_skill` = `skills/golf-preview/SKILL.md`
- `booking_skill` = `skills/golf-booking/SKILL.md`
- `state_file` = `workflows/golf-booking/state.yaml`
- `preview_output` = `workflows/golf-booking/preview-output.json`

### Target Weekend Calculation

The workflow targets the **Friday, Saturday, and Sunday** that are 8 days from the Wednesday
midnight booking run. At preview time (Tuesday 11pm), this is 9 days out.

Example: Preview runs Tuesday May 5 at 11pm → targets Fri May 9, Sat May 10, Sun May 11.
Booking runs Wednesday May 6 at midnight → books into that same weekend.

---

## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.
2. If `status: in-progress`: resume from `current-step`. Load `accumulated-context`.
3. If `status: not-started` or `status: complete`: fresh run. Initialize `state.yaml`.
4. If `status: aborted`: surface to controller and wait for instruction.
5. **Check for already-booked round this weekend**: search calendar for a golf block on the
   target Friday/Saturday/Sunday. If found, skip booking and output:
   `[Sterling]: Golf already booked for this weekend ([date] [time]). No action needed.`

---

## EXECUTION

### Phase 1 — Preview (Tuesday 11:00 PM CT)

Read and follow `skills/golf-preview/SKILL.md` in full.

Produces:
- Scored list of candidate windows (day + time range) for the target weekend
- Go/no-go decision per day based on calendar and weather
- Recommended top option with rationale
- Slack message to David with 2-3 options

Store output in `workflows/golf-booking/preview-output.json`.
Update `state.yaml`: `current-step: phase-2-booking`, `status: in-progress`.

### Phase 2 — Booking (Wednesday 12:00 AM CT)

Read and follow `skills/golf-booking/SKILL.md` in full.

Reads `preview-output.json` for the pre-scored preference order.
Opens ChronoGolf, evaluates real-time availability, books best match.

Produces:
- Booked tee time (or failure + reason)
- Calendar block (tee time + 30min range lead)
- Slack confirmation to David

Update `state.yaml`: `status: complete`.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Calendar unavailable at preview | Proceed with weather only. Flag calendar check failed in Slack message. |
| Weather API unavailable | Proceed with calendar only. Note in Slack: "weather data unavailable — verify before playing." |
| No viable windows found | Notify David via Slack: "No viable tee times found this weekend — [reasons]. No booking made." |
| ChronoGolf unavailable at midnight | Retry once after 60 seconds. If still down, notify David via Slack immediately. |
| All preferred times booked | Take best available option per scoring rules. Notify David with what was booked and why. |
| Login session expired | Surface to David: "[Sterling]: ChronoGolf session appears expired. Please log in at chronogolf.com/dashboard and re-run booking." |

---

## OUTPUT

- `workflows/golf-booking/preview-output.json` — scored windows, go/no-go per day, top pick
- Slack message to #jarvis (preview) — 2-3 options with weather + cost
- Calendar block — tee time window + 30min range buffer
- Slack message to #jarvis (booking confirmation) — date, time, cost, weather snapshot

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
