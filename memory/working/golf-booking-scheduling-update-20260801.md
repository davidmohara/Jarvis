# Golf Booking Scheduled Task — Updated to 11:00 PM

## Configuration Change

The golf tee time booking workflow has been added to Cowork's scheduled tasks with the following configuration:

| Field | Value |
|-------|-------|
| **Task ID** | golf-tee-time-booking |
| **Schedule** | Weekdays (Mon-Fri) at 11:00 PM CT |
| **Cron** | `0 23 * * 1-5` |
| **Agent** | Chief |
| **Workflow** | `workflows/golf-booking/workflow.md` |
| **Configured** | ✅ True (ready to execute) |
| **Keep Awake** | False (standard execution) |

---

## Rationale for 11:00 PM

The booking window opens at **midnight (00:00)** on the target date (8 days ahead). Running the workflow at **11:00 PM** provides:

1. **Timing buffer**: 1 hour before the window opens
   - Allows system clock synchronization
   - Prevents race conditions near midnight boundary
   - Gives ChronoGolf server time to update booking eligibility

2. **Booking window certainty**: By 11:00 PM, we know:
   - The booking window will definitely open within the hour
   - System time is synchronized globally
   - No additional delays from timezone edge cases

3. **Confirmation window safety**: After booking, the 5-minute confirmation timer has full resolution:
   - Booked at 11:01 PM, confirm by 11:06 PM (well before next day)
   - Calendar event created immediately
   - Slack notification sent same night

---

## Previous Execution (Midnight)

The first execution ran at **midnight exactly** (2026-08-01 00:00:27 CDT), which was borderline:
- System was accepting bookings by the time we reached the tee time selection
- But timing was tight and could be unreliable for future runs

---

## Next Execution

The workflow will next run automatically on a weeknight at **11:00 PM CT**, approximately **8 days before the target golf date**.

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
