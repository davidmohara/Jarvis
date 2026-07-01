# Calendar Consolidation: Single Pull, Multiple Consumers

## Problem Statement

The original boot workflow made **3 separate M365 calendar API calls**:
1. **Morning Briefing Step-01** — pulls today's calendar
2. **Boot Step-02 Task G** — pulls next 3 days (72-hour look-ahead)
3. **Morning Briefing Step-03** — pulls meeting context (attendee details)

Each call returned full event objects, storing them verbatim in accumulated-context. This caused:
- **API overhead** — 3 calls instead of 1
- **Context bloat** — 200+ KB of duplicated calendar data
- **First-run compaction** — triggered Cowork's context window compaction

## Solution: Unified Calendar Pull

**New architecture (Step 01.5):**
1. **Single M365 call** pulls 4-day window (today + next 3 days) → written to disk
2. **All downstream steps** read from `data/calendar-unified.json` instead of calling M365
3. **Each consumer filters** the shared data for its needs (today only, next 3 days, etc.)

### File Format

```json
{
  "pulled_at": "2026-07-01T14:30:45Z",
  "date_range": {
    "start": "2026-07-01",
    "end": "2026-07-04"
  },
  "event_count": 34,
  "events": [
    {
      "id": "...",
      "subject": "Board Meeting",
      "start": "2026-07-01T14:00:00Z",
      "end": "2026-07-01T15:00:00Z",
      "location": "Conference Room A",
      "attendees": [...],
      "response_status": "accepted",
      ...
    }
  ]
}
```

## Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Boot Workflow                                               │
└─────────────────────────────────────────────────────────────┘

Step 01: Load Context
    ↓
Step 01.5: Unified Calendar Pull ← NEW
    │   Calls M365 once (today + 3 days)
    │   Writes to data/calendar-unified.json
    ↓
Step 02: Gather Data (Phase 2)
    │   Task G reads calendar-unified.json
    │   (does NOT call M365)
    ↓
Step 02.5: Measure Phase 2
    │   Measures context bloat (should be 70-80% smaller)
    ↓
Step 03: Verify Phase 2
    ↓
...

┌─────────────────────────────────────────────────────────────┐
│ Morning Briefing Workflow (parallel)                        │
└─────────────────────────────────────────────────────────────┘

Step 01: Gather Calendar
    │   Reads calendar-unified.json (written by boot step-01.5)
    │   Filters for today's events
    │   (does NOT call M365)
    ↓
Step 02: Gather Tasks
    ↓
Step 03: Gather Context
    │   Reads attendees from calendar-unified.json
    │   Resolves attendee details via Clay
    │   (does NOT call M365 again)
    ↓
Step 04: Synthesize Briefing
```

## Data Flow Diagram

```
M365 API
   ↓
   └─→ Step 01.5 Unified Pull
       └─→ Writes: data/calendar-unified.json
           ├─→ Boot Step-02 Task G reads it
           ├─→ Morning Briefing Step-01 reads it
           └─→ Morning Briefing Step-03 reads it
```

## Expected Context Savings

### Before Consolidation
```
accumulated-context breakdown:
├─ phase2.calendar: 200 KB (full 34-event response, duplicated)
├─ phase2.morning-briefing-01: 150 KB (today's events again)
├─ phase2.morning-briefing-context: 100 KB (attendee details again)
└─ Total Phase 2: 500+ KB
```

### After Consolidation
```
accumulated-context breakdown:
├─ phase2.calendar-file-path: 1 KB ("data/calendar-unified.json")
├─ phase2.calendar-summary: 5 KB (metadata only: event count, date range)
├─ phase2.morning-briefing: 50 KB (filtered today's events + classified)
├─ phase2.morning-briefing-context: 30 KB (attendee summaries only)
└─ Total Phase 2: 100 KB (~80% reduction)
```

## Implementation Steps

### ✅ Changes Made
1. Created Step 01.5: Unified Calendar Pull
2. Updated Boot workflow sequence to include step 01.5
3. Modified Boot Step-02 Task G to read from shared file
4. Modified Morning Briefing Step-01 to read from shared file
5. Added instrumentation (Step 02.5) to measure the improvement

### ⏭ Next Steps (When Running Boot)
1. Run boot workflow (will execute new step 01.5 automatically)
2. Step 01.5 writes `data/calendar-unified.json`
3. Step 02 Task G reads from it (no M365 call)
4. Step 02.5 measures and reports ~80% reduction in phase2 context
5. Compare measurement to baseline

## Verification Checklist

After first boot run:
- [ ] `data/calendar-unified.json` exists and contains 34+ events
- [ ] File size is reasonable (50-100 KB for raw JSON)
- [ ] Boot Step-02 Task G completes (reads from file, no M365 error)
- [ ] Morning Briefing Step-01 completes (reads from file, no M365 error)
- [ ] Step 02.5 measurement shows phase2 context reduced by 70-80%
- [ ] No context window compaction occurs during first boot run
- [ ] All tasks still report "completed" status

## Fallback Behavior

If `data/calendar-unified.json` is missing or stale:
- **Boot Step-02 Task G**: Falls back to reading from accumulated-context (if available) or marks as "failed — calendar data unavailable"
- **Morning Briefing Step-01**: Gracefully degrades or re-pulls from M365 if file missing
- **Step 01.5**: Attempts fresh pull if file is > 12 hours old

No breaking changes — steps are designed to continue if the shared file is unavailable.

## Files Modified

| File | Change | Purpose |
|------|--------|---------|
| `workflows/boot/workflow.md` | Added step 01.5 to sequence | Route to unified pull |
| `workflows/boot/steps/step-01-load-context.md` | Changed next-step to 01.5 | Chain to unified pull |
| `workflows/boot/steps/step-01.5-unified-calendar-pull.md` | NEW | Execute single M365 call, write to disk |
| `workflows/boot/steps/step-02-gather-data.md` | Updated Task G description | Read from file, don't call M365 |
| `workflows/morning-briefing/steps/step-01-gather-calendar.md` | Changed input source | Read from shared file, not M365 |

## Context Bloat Comparison

| Metric | Before | After | Reduction |
|--------|--------|-------|-----------|
| Phase 2 total size | 500+ KB | 100 KB | 80% |
| M365 API calls | 3 | 1 | 67% |
| Calendar data duplicated | 3x (stored 3 times) | 1x (stored once, read many times) | 67% |
| Estimated tokens saved | ~125,000 | ~25,000 | 80% |

## Next Optimization

After validating calendar consolidation works:
- Apply same pattern to **email pulls** (currently Task H pulls raw messages)
- Pattern: Pull email once → write to disk → all steps read from file
- Expected savings: 50-70% of remaining phase2 context
