# Boot Context Optimization — Summary

## Instrumentation + Calendar Consolidation

You've now got two complementary systems in place:

### 1. Instrumentation (Measurement)
**What it does:** Measures context bloat before and after each optimization.

**Key components:**
- `systems/boot-instrumentation/measure.py` — measures accumulated-context size
- `workflows/boot/steps/step-02.5-measure-phase2.md` — runs automatically after phase 2
- `skills/boot-context-analyzer/SKILL.md` — documentation and workflow guide
- `systems/boot-instrumentation/tracking.json` — aggregates measurements across runs

**Output:** You'll see after every boot run:
```
[Instrumentation] Phase 2 Context Measurement
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 120 KB (~30,000 tokens)

Top bloat sources:
1. phase2.email: 80 KB
2. phase2.meeting-context: 25 KB
3. phase2.tasks: 15 KB
```

---

### 2. Calendar Consolidation (Optimization #1)
**What it does:** Eliminates 3 separate M365 calendar API calls, stores result once, serves all consumers.

**Changes made:**
- ✅ New step 01.5: Unified Calendar Pull
- ✅ Boot step-02 Task G now reads from `data/calendar-unified.json` (not M365)
- ✅ Morning Briefing step-01 now reads from shared file (not M365)
- ✅ Morning Briefing step-03 reads attendee data from shared file

**Expected impact:**
- **Before:** phase2 context = 500+ KB (calendar data stored 3+ times)
- **After:** phase2 context = ~100 KB (calendar stored once, read multiple times)
- **Reduction:** ~80% for calendar-related bloat

**How it works:**
```
Step 01.5: "Fetch calendar for today + 3 days, write to disk"
    ↓
    data/calendar-unified.json (one M365 call, ~50-100 KB on disk)
    ↓
Step 02 Task G reads it ──→ filters for days+1 to +3
Step Morning-Briefing-01 reads it ──→ filters for today
Step Morning-Briefing-03 reads it ──→ extracts attendees
```

---

## Running the Optimization Cycle

### Phase 1: Establish Baseline (with Calendar Consolidation)

```bash
# 1. Run boot workflow (step 01.5 + 02.5 are automatic)
cd /Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES
# Boot via Cowork or CLI

# 2. Check the measurement output in the boot sequence
# Look for: "[Instrumentation] Phase 2 Context Measurement"
# Should show: ~100-150 KB total (down from 500+ KB baseline)

# 3. Backup the state for later comparison
cp workflows/boot/state.yaml systems/boot-instrumentation/backups/2026-07-01-post-calendar-consolidation.yaml
```

### Phase 2: Identify Next Bloat Source

From the measurement output, identify the largest remaining field:
- `phase2.email` (Task H email triage)?
- `phase2.meeting-context` (Morning briefing step-03)?
- `phase2.tasks` (OmniFocus pull)?

### Phase 3: Optimize Second Largest Source

Apply the same consolidation pattern:
1. Create a "pull once" step that writes to disk
2. Update all consuming steps to read from disk
3. Run boot again
4. Measure and compare

Example (if email is next):
```
Step 01.5: Unified Calendar Pull ← DONE
Step 02: Gather Email ← NEW: "Pull flagged/time-sensitive, write to data/email-unified.json"
Step 02 Task H ← MODIFY: "Read from email-unified.json instead of M365"
```

---

## Before vs. After: What to Expect

### Metrics to Track

| Metric | Before Consolidation | After Consolidation | Target |
|--------|----------------------|---------------------|--------|
| **Phase 2 Total Size** | 500+ KB | 100-150 KB | < 150 KB ✓ |
| **M365 Calendar Calls** | 3 | 1 | 1 ✓ |
| **Calendar Context** | 200+ KB | 40 KB | < 50 KB ✓ |
| **Estimated Tokens** | 125,000+ | 25,000-37,000 | < 37,500 ✓ |
| **First-Run Compaction?** | YES (triggers) | NO | NO ✓ |

### Measurement Files

After running boot with calendar consolidation:
```
systems/boot-instrumentation/measurements/
├── measurement-state-2026-07-01T143045.json  ← baseline (before calendar)
├── measurement-state-2026-07-01T150000.json  ← post-consolidation
└── comparison-2026-07-01T150015.json         ← shows % improvement
```

---

## Files You've Created/Modified

### New Files
- `workflows/boot/steps/step-01.5-unified-calendar-pull.md` — consolidated pull
- `systems/boot-instrumentation/measure.py` — measurement script
- `workflows/boot/steps/step-02.5-measure-phase2.md` — instrumentation step
- `skills/boot-context-analyzer/SKILL.md` — analyzer skill
- `systems/boot-instrumentation/README.md` — operational guide
- `systems/boot-instrumentation/CALENDAR-CONSOLIDATION.md` — detailed architecture
- `systems/boot-instrumentation/tracking.json` — measurement tracker

### Modified Files
- `workflows/boot/workflow.md` — added steps 01.5 and 02.5 to sequence
- `workflows/boot/steps/step-01-load-context.md` — chains to step 01.5
- `workflows/boot/steps/step-02-gather-data.md` — reads calendar from disk
- `workflows/morning-briefing/steps/step-01-gather-calendar.md` — reads from shared file

---

## Quick Commands

### Measure current state
```bash
cd /Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES
python3 systems/boot-instrumentation/measure.py measure-state workflows/boot/state.yaml
```

### Compare before/after
```bash
python3 systems/boot-instrumentation/measure.py compare \
  systems/boot-instrumentation/backups/2026-07-01-pre-consolidation.yaml \
  workflows/boot/state.yaml
```

### View latest measurement
```bash
cat $(ls -t systems/boot-instrumentation/measurements/measurement-state-*.json | head -1) | jq .
```

### Run boot with calendar consolidation
```bash
# Just run the boot workflow normally — step 01.5 and 02.5 are automatic
# Boot will output measurement summary to console
```

---

## Success Criteria

✅ When boot completes successfully:
- [ ] `data/calendar-unified.json` exists (written by step 01.5)
- [ ] Step 02 Task G completes (reads from file, no M365 error)
- [ ] Step 02.5 shows measurement (total KB, top bloat sources)
- [ ] Boot step-02 context is 100-150 KB (80% reduction from baseline)
- [ ] No first-run context window compaction occurs
- [ ] All downstream steps complete successfully

✅ When you're ready to optimize email next:
- [ ] Create step 02 task to pull email once → write to disk
- [ ] Update Task H to read from disk
- [ ] Measure and compare
- [ ] Document the pattern in OPTIMIZATION-SUMMARY.md

---

## What's Next

### Immediate (Next Boot Run)
1. Run boot workflow with calendar consolidation in place
2. Review step 02.5 measurement output
3. Compare to baseline (should see ~80% reduction in phase2.calendar context)
4. Update `systems/boot-instrumentation/tracking.json` with results

### Short Term (Next 2-3 Optimization Cycles)
1. Apply same consolidation pattern to email (Task H)
2. Apply to meeting context (Morning Briefing step-03)
3. Apply to tasks/OmniFocus data
4. Target: total phase2 context < 150 KB (no compaction)

### Medium Term (Polish & Maintenance)
1. Document the "pull once, serve many" pattern as a reusable workflow best practice
2. Create a template for future consolidations
3. Update boot workflow README with the consolidated architecture
4. Archive before/after measurements as reference

---

## Notes

- **No breaking changes**: All steps handle missing/stale calendar files gracefully
- **Caching strategy**: Step 01.5 reuses calendar file if < 12 hours old (can tune this)
- **Fallback behavior**: If `data/calendar-unified.json` missing, steps degrade or re-pull
- **Pattern is reusable**: Same "write to disk" approach works for email, tasks, meeting context

---

## Measurement Baseline Template

After first run with calendar consolidation, fill in:

```json
{
  "optimization_id": "calendar-consolidation",
  "date": "2026-07-01",
  "before": {
    "total_kb": "???",
    "phase2_kb": "???",
    "m365_calls": 3,
    "calendar_context_kb": "???"
  },
  "after": {
    "total_kb": "???",
    "phase2_kb": "???",
    "m365_calls": 1,
    "calendar_context_kb": "???"
  },
  "reduction_pct": "???",
  "measurement_file": "systems/boot-instrumentation/measurements/measurement-state-2026-07-01T*.json"
}
```

Then use that baseline for the next optimization cycle.
