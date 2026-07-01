# First Run Checklist: Calendar Consolidation + Instrumentation

Execute this checklist to validate the optimized boot workflow.

---

## Pre-Run Setup

- [ ] You are in the IES root directory: `/Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES`
- [ ] You have read `CALENDAR-CONSOLIDATION.md` (understand the architecture)
- [ ] You have read `OPTIMIZATION-SUMMARY.md` (understand the measurement system)
- [ ] You have backups directory ready: `mkdir -p systems/boot-instrumentation/backups/`

---

## Step 1: Run Boot Workflow

**Action:** Execute the boot workflow normally.

**What will happen:**
- Step 01: Load identity files (as before)
- Step 01.5: **NEW** — Pull calendar once for 4-day window, write to `data/calendar-unified.json`
- Step 02: Gather Phase 2 data (reads calendar from shared file, not M365)
- Step 02.5: **NEW** — Measure context bloat, write snapshot to `systems/boot-instrumentation/measurements/`
- Steps 03-07: Continue as normal

**Expected duration:** Same as before (measurement and calendar consolidation are non-blocking)

**How to run:**
```bash
# Via Cowork: Start new session in IES folder
# Or via CLI: invoke the boot workflow
```

---

## Step 2: Check Step 01.5 Output

**Action:** Verify the unified calendar file was created.

**Look for in the boot output:**
```
[Step 01.5] Unified Calendar Pull
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
File: data/calendar-unified.json
Events: 25-35 (typical for 4-day window)
Date range: [today] to [today+3]
Status: written
```

**Verification:**
```bash
# Check file exists
ls -lh data/calendar-unified.json

# Check it's valid JSON
cat data/calendar-unified.json | jq . | head -20

# Expected output:
# {
#   "pulled_at": "2026-07-01T...",
#   "date_range": { "start": "2026-07-01", "end": "2026-07-04" },
#   "event_count": 25-35,
#   "events": [...]
# }
```

**Checkpoints:**
- [ ] File exists at `data/calendar-unified.json`
- [ ] File size is 50-150 KB (reasonable for 25-35 events)
- [ ] File contains valid JSON
- [ ] event_count is 20+

---

## Step 3: Check Step 02 Output

**Action:** Verify Phase 2 data gathering completed (should now read from shared file).

**Look for in the boot output:**
```
[Step 02] Gather Data (Phase 2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Task G (72-hour look-ahead): completed
  → Reading from data/calendar-unified.json
  → No M365 call made
  → 12-15 events extracted for days+1 to +3
```

**Verification:**
```bash
# Check step 02 completed
grep -A 5 "task-g-72hr-lookahead" workflows/boot/state.yaml
# Should show: "completed"
```

**Checkpoints:**
- [ ] Task G shows "completed" status
- [ ] Output mentions reading from calendar file (not M365)
- [ ] 72-hour events captured (10-15 events expected)

---

## Step 4: Check Step 02.5 Measurement Output

**Action:** Verify instrumentation ran and show you the bloat baseline.

**Look for in the boot output:**
```
[Step 02.5] Measure Phase 2 Context Size
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Measurement file: systems/boot-instrumentation/measurements/measurement-state-2026-07-01T143045.json

Phase 2 Context Measurement:
Total: 120 KB (~30,000 tokens)

Top bloat sources:
1. phase2.email: 80 KB
2. phase2.meeting-context: 25 KB  
3. phase2.tasks: 15 KB
```

**Verification:**
```bash
# Find the latest measurement file
LATEST=$(ls -t systems/boot-instrumentation/measurements/measurement-state-*.json | head -1)
echo $LATEST

# View the measurement
cat $LATEST | jq .

# Expected structure:
# {
#   "timestamp": "...",
#   "total_size_bytes": <number>,
#   "total_size_kb": <number>,
#   "estimated_tokens": <number>,
#   "field_breakdown": [...]
# }
```

**Checkpoints:**
- [ ] Measurement file created (check filename)
- [ ] total_size_kb is 100-200 KB (if > 250 KB, consolidation not effective yet)
- [ ] field_breakdown lists top bloat sources
- [ ] No errors in measurement

---

## Step 5: Compare to Expected Baseline

**Action:** Verify that calendar consolidation achieved ~80% reduction in calendar context.

**Expected savings:**
```
Before calendar consolidation:
  phase2.calendar: 200 KB (raw 25-35 event responses × 3 consumers)
  phase2 total: 500+ KB

After calendar consolidation:
  phase2.calendar: 40 KB (single response, filtered at read time)
  phase2 total: 100-150 KB
```

**Verification:**
```bash
# Check field_breakdown from the measurement file
cat $LATEST | jq '.field_breakdown | .[0:5]'

# Look for phase2 total — should be 100-150 KB range
cat $LATEST | jq '.accumulated_context.size_kb'
```

**Checkpoints:**
- [ ] phase2 total is 100-150 KB (down from 500+ KB)
- [ ] Largest field is now email (80 KB) or meeting-context (25 KB), not calendar
- [ ] Calendar-related context is < 50 KB

---

## Step 6: Verify Boot Completed Without Compaction

**Action:** Confirm that boot finished normally without context window compaction.

**Look for in the boot output:**
```
[Master]: Boot verification complete
[Master]: Morning briefing delivered to controller

Boot Status: COMPLETE ✓
```

**Checkpoints:**
- [ ] Boot workflow finished (state.yaml shows `status: complete`)
- [ ] No "context window compaction" warning
- [ ] No "accumulated-context exceeded limits" errors
- [ ] Morning briefing was delivered
- [ ] All steps 01-07 show "complete" or "not-applicable"

---

## Step 7: Backup the Measurement

**Action:** Save the measurement file for future comparisons.

```bash
# Backup the current state and measurement
cp workflows/boot/state.yaml systems/boot-instrumentation/backups/2026-07-01-post-consolidation.yaml
cp $(ls -t systems/boot-instrumentation/measurements/measurement-state-*.json | head -1) \
   systems/boot-instrumentation/backups/2026-07-01-measurement.json
```

**Checkpoints:**
- [ ] Backup files exist in `systems/boot-instrumentation/backups/`
- [ ] Files are readable

---

## Step 8: Document the Baseline

**Action:** Record the baseline measurement in tracking.json.

```bash
# Edit tracking.json and fill in the first measurement entry:
{
  "measurement_id": "post-calendar-consolidation",
  "timestamp": "2026-07-01T14:30:00Z",
  "total_kb": <from measurement>,
  "total_tokens": <from measurement>,
  "top_bloat_sources": [<from field_breakdown>],
  "status": "baseline-established"
}
```

**Checkpoints:**
- [ ] tracking.json updated with baseline values

---

## Success Summary

If all checkpoints are complete:

✅ **Calendar consolidation is working**
- Single M365 call made (step 01.5)
- Data written to shared file
- Boot step-02 reads from file (not M365)
- ~80% reduction in phase2.calendar context achieved

✅ **Instrumentation is working**
- Step 02.5 measured context bloat
- Measurement file created with detailed breakdown
- Top bloat sources identified

✅ **Boot is stable**
- No context window compaction
- All steps completed
- No data loss
- Ready for next optimization

---

## Troubleshooting

### Issue: data/calendar-unified.json not found

**Solution:** Step 01.5 may have failed silently.

```bash
# Check step 01.5 output
grep -A 10 "step-01.5" workflows/boot/state.yaml

# If failed, check for errors:
# - M365 MCP unavailable? Check Outlook connection
# - File write failed? Check permissions on data/ directory
```

### Issue: Measurement shows no improvement (still 500+ KB)

**Solution:** Calendar consolidation may not have been applied properly.

```bash
# Check if boot step-02 Task G is reading from file
grep -B 5 -A 5 "task-g-72hr-lookahead" workflows/boot/state.yaml

# Check if it mentions "calendar-unified.json"
# If not, the workflow changes weren't applied — see CALENDAR-CONSOLIDATION.md
```

### Issue: Boot compaction still occurs

**Solution:** There are other bloat sources beyond calendar.

```bash
# Check field_breakdown for next-largest source
cat $(ls -t systems/boot-instrumentation/measurements/measurement-state-*.json | head -1) | jq '.field_breakdown | .[0:10]'

# Common sources: email, meeting-context, tasks
# Next optimization cycle should target that field
```

### Issue: Step 01.5 seems to slow down boot

**Solution:** Calendar file reuse is working as intended.

```bash
# First run pulls fresh (slower)
# Subsequent runs within 12 hours reuse the file (fast)
# This is the desired behavior for optimization

# To force a fresh pull, delete the cache:
rm data/calendar-unified.json
# Then run boot again
```

---

## Next Steps After First Run

1. ✅ Establish calendar consolidation baseline (this checklist)
2. **Identify next bloat source** from step 02.5 measurement
3. **Apply same consolidation pattern** to largest remaining field (email, meeting-context, or tasks)
4. **Re-run boot** and compare
5. **Iterate** until phase2 total is < 150 KB and no compaction occurs

See `OPTIMIZATION-SUMMARY.md` for the optimization cycle workflow.
