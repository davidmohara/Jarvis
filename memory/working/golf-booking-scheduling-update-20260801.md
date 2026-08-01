# Golf Booking Scheduled Task — Updated to 11:00 PM

## Configuration Change

The golf tee time booking workflow has been added to Cowork's scheduled tasks with the following configuration:

| Field | Value |
|-------|-------|
| **Task ID** | golf-tee-time-booking |
| **Schedule** | Wednesday–Friday at 11:00 PM CST |
| **Cron** | `0 23 * * 3-5` |
| **Timezone** | America/Chicago (CST) |
| **Booking Window** | Midnight EST (11:00 PM CST) |
| **Agent** | Chief |
| **Workflow** | `workflows/golf-booking/workflow.md` |
| **Configured** | ✅ True (ready to execute) |
| **Keep Awake** | False (standard execution) |

---

## Rationale for 11:00 PM CST (Midnight EST)

The booking window opens at **midnight EST** on the target date (8 days ahead). Running the workflow at **11:00 PM CST** (which equals midnight EST) provides:

1. **Timezone alignment**: 11:00 PM CST = Midnight EST
   - Matches ChronoGolf's EST-based booking window opening
   - No race conditions or early/late timing issues
   - System runs exactly when the window opens

2. **Wed/Thu/Fri schedule**: 
   - Books for target weekends (Fri/Sat/Sun after 8 days)
   - Aligns with golf scheduling preferences
   - No runs on Mon/Tue (unnecessary for next-week bookings)

3. **Confirmation window safety**: After booking:
   - Confirmed on the same night (before next day)
   - Calendar event created immediately
   - Slack notification sent before sleep

---

## Previous Execution (Manual)

The first execution ran manually at **midnight EST** (2026-08-01 00:00:27 EDT / 23:00:27 CDT):
- Successfully booked when window opened
- Confirmed for Sunday, August 9 @ 3:25 PM
- Calendar event created, booking verified

---

## Next Scheduled Execution

The workflow will next run automatically on **Wednesday, Thursday, or Friday at 11:00 PM CST** (midnight EST), approximately **8 days before the target golf date**.

Example: 
- Run at 11:00 PM on Friday = Books for the following Friday (8 days out)
- Run at 11:00 PM on Wednesday = Books for the following Wednesday (8 days out)

**Manual override**: If you want to book outside the scheduled window, run:
```
Read /Users/davidohara/develop/jarvis/skills/golf-booking/SKILL.md
```

---

## File Updates

- **Config**: `/config/scheduled-tasks.json` — Added golf-tee-time-booking task
- **State**: `/workflows/golf-booking/state.yaml` — Current status: complete (previous execution)
- **Reference**: This document at `/memory/working/golf-booking-scheduling-update-20260801.md`

---

**Status**: ✅ Scheduled task configured and ready for next weeknight execution.
