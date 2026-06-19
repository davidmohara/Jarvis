# Golf Booking Failure — June 18, 2026

**Status:** Booking failed due to member advance booking window constraint

**Date:** June 18, 2026 (Thursday 5:02 AM)

**Attempted Target Dates:**
- Rank 1: Saturday, June 27 (within preferred 1-5 PM window)
- Rank 2: Sunday, June 28 (within preferred 2:30-6:30 PM window, after church)
- Rank 3: Saturday, June 27 @ 4 PM (fallback)

**Why It Failed:**

ChronoGolf member "41 - Frisco Lakes Total Member" can only book **8 days in advance**.

- Today: June 18, 2026 (Thursday)
- Bookable range: June 18 through June 25
- Target weekend: June 26-28 (starts one day outside booking window)

**What Is Bookable:**
- Friday, June 26 *is* within range (8 days exactly)
- But Friday preview status: **UNAVAILABLE** due to calendar conflicts
  - Podcast Filming 11:30 AM-1:30 PM
  - Drive Block 1:30-2:00 PM
  - Kazakhstan Prep 2:00-2:30 PM
  - Kazakhstan Hosting 2:30-4:00 PM
  - Earliest safe time: 5:00 PM (after hosting ends)

**Actions Taken:**
1. Verified login to ChronoGolf dashboard ✓
2. Opened booking widget ✓
3. Tested Saturday June 27 → System rejected: "out of booking range"
4. Tested Sunday June 28 → System rejected: "out of booking range"
5. Tested Friday June 26 → Tee times available, but conflicts with calendar
6. Recorded error entry: `err-20260618T050229-COB0BF`

**Next Steps:**
1. Contact David to clarify expected booking window
2. Consider whether Friday 5+ PM works, or reschedule preview for following week
3. Update workflow timing assumptions or preview generation logic

**Booking Workflow State:** `status: window-constraint-failure`

---

**REQUIRED SLACK MESSAGE (needs manual send or skill):**

```
*⛳ Golf Booking Failed — Booking Window Constraint*

Attempted to book target weekend (Fri-Sun June 26-28), but ChronoGolf member booking window is strict: only 8 days in advance maximum.

Today is June 18 (Thursday). The member can book through June 25 only.

✗ June 27 (Saturday) — UNAVAILABLE (9 days out)
✗ June 28 (Sunday) — UNAVAILABLE (10 days out)  
⚠ June 26 (Friday) — IN RANGE but calendar conflicts 2:30-4:00 PM

Friday earliest available: 5:00+ PM (after Kazakhstan hosting)

**Action required:** Clarify booking window expectations or reschedule for following week when preview generates for June 30-July 2 range.
```
