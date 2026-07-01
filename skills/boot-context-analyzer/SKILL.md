---
name: boot-context-analyzer
description: Analyze boot workflow context bloat — measure, identify sources, and compare before/after optimization changes
tags: [boot-workflow, instrumentation, context-optimization]
---

# Boot Context Analyzer Skill

**Purpose:** Measure context window usage in the boot workflow, identify bloat sources, and track optimization impact.

**Triggers:**
- "analyze boot context"
- "measure boot bloat"
- "boot context report"
- "compare boot before after"
- "context size baseline"

---

## Quick Start

### Measure Current Boot State
```
Run the boot workflow with instrumentation enabled (step 02.5 is now included by default).
The workflow will automatically measure and write snapshots to:
  systems/boot-instrumentation/measurements/measurement-state-{timestamp}.json
```

### Compare Before/After Optimization
```bash
cd /Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES

# Measure before making changes
python3 systems/boot-instrumentation/measure.py compare \
  workflows/boot/state.yaml \
  workflows/boot/state.yaml

# After making optimization changes:
python3 systems/boot-instrumentation/measure.py compare \
  {path/to/before-state-backup} \
  workflows/boot/state.yaml
```

---

## What Gets Measured

### Field-Level Breakdown
Each top-level field in `accumulated-context` is measured:
- **phase1**: Identity files, SYSTEM.md, all loaded identity context
- **phase2**: Calendar, email, tasks, Jarvis inbox, reminders
- **verification**: Ralph's verdict table
- **phase3**: Meeting context, Clay reminders/birthdays
- **phase4**: (if reached) Watchtower output

### Metrics
For each field:
- **size_bytes** — raw JSON serialization size
- **size_kb** — human-readable kilobytes
- **estimated_tokens** — approximate token count (bytes ÷ 4)
- **type** — Python type (dict, list, str, etc.)

### Top Bloat Sources
The analyzer automatically identifies the 5 largest fields and surfaces them to David.

---

## How to Use Results

### Red Flags (What to Fix)
| Pattern | Likely Cause | Fix |
|---------|--------------|-----|
| `phase2: 500+ KB` | Raw API responses stored verbatim | Extract summaries only, discard raw data |
| `calendar: 200+ KB` for 25 events | Each event includes full attendee objects | Store only names, strip attendee details |
| `email: 150+ KB` for 10 messages | Full message body text included | Store subject + summary only |
| `accumulated-context > 1 MB` | Context bloat causing compaction on first run | Run optimization pass before boot completes |

### Expected Sizes (Healthy Baseline)
- **phase1** (identity files): 20-30 KB
- **phase2** (gathered data): 50-100 KB
- **phase3** (meeting context): 10-20 KB
- **Total**: 100-150 KB (should fit ~400 tokens)

### After Optimization
Target: reduce total by 70-80%
- **Before**: 500-800 KB → **After**: 100-150 KB

---

## Workflow Integration

### Automatic Measurements
Every boot run now includes step 02.5, which:
1. Measures accumulated-context after Phase 2 completes
2. Writes snapshot to `systems/boot-instrumentation/measurements/`
3. Surfaces top bloat sources to David
4. Continues without blocking (non-critical)

### Manual Measurements
```bash
# Measure a specific state file
python3 systems/boot-instrumentation/measure.py measure-state workflows/boot/state.yaml

# Compare two states (before/after)
python3 systems/boot-instrumentation/measure.py compare \
  /path/to/before-state.yaml \
  /path/to/after-state.yaml
```

---

## Reading the Output

### Snapshot Format
```json
{
  "timestamp": "2026-07-01T14:30:45.123456",
  "session_id": "session-2026-07-01-143045",
  "total_size_bytes": 524288,
  "total_size_kb": 512,
  "estimated_tokens": 131072,
  "accumulated_context": {
    "size_bytes": 524288,
    "estimated_tokens": 131072,
    "type": "dict"
  },
  "field_breakdown": [
    {
      "name": "phase2",
      "size_bytes": 350000,
      "size_kb": 341.8,
      "estimated_tokens": 87500,
      "type": "dict"
    },
    {
      "name": "phase2.calendar",
      "size_bytes": 200000,
      "size_kb": 195.3,
      "estimated_tokens": 50000,
      "type": "list"
    }
  ]
}
```

### Comparison Format
```json
{
  "before_bytes": 524288,
  "before_kb": 512,
  "before_tokens": 131072,
  "after_bytes": 102400,
  "after_kb": 100,
  "after_tokens": 25600,
  "reduction_bytes": 421888,
  "reduction_kb": 412,
  "reduction_tokens": 105472,
  "reduction_pct": 80.5,
  "before_breakdown": [...],
  "after_breakdown": [...]
}
```

---

## Running Optimization Cycles

### Cycle Template
1. **Baseline**: Run boot workflow, note Phase 2 measurement
2. **Identify**: From the breakdown, pick the largest field to optimize
3. **Modify**: Edit the step that produces that field (e.g., step-02 task G, H, I)
4. **Backup**: Copy the before-state to `systems/boot-instrumentation/backups/{date}-before.yaml`
5. **Test**: Run boot again
6. **Compare**: Run the comparison script against the backed-up state
7. **Repeat**: If reduction is < 50%, go to step 2 with the next-largest field

### Example: Optimizing Calendar Pull
```
Before: phase2.calendar = 200 KB (25 events × 8 KB average)
Target: phase2.calendar = 50 KB (store only title, time, type)

Edit: workflows/boot/steps/step-02-gather-data.md → Task G
Change: Store full calendar response
To: Store {subject, start_time, end_time, type, flags_only}

Run: boot workflow again
Compare: measurement results
Result: calendar field now 60 KB (70% reduction) ✓
```

---

## Troubleshooting

### "measure.py: command not found"
Ensure you're in the IES root directory and have set `IES_ROOT`:
```bash
cd /Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES
IES_ROOT=$(pwd) python3 systems/boot-instrumentation/measure.py ...
```

### "state.yaml not found"
The measurement script expects the path relative to IES root:
```bash
# Correct
python3 systems/boot-instrumentation/measure.py measure-state workflows/boot/state.yaml

# Incorrect
python3 systems/boot-instrumentation/measure.py measure-state /absolute/path/to/state.yaml
```

### Measurements show 0 bytes
The accumulated-context may be empty. Check that the boot workflow completed step-02 before measuring.

---

## Next Steps

After collecting baseline measurements:
1. Share the Phase 2 measurement output with the team
2. Identify top 3 bloat sources
3. Create optimization tasks for each source
4. Run before/after comparisons on each change
5. Target: reduce total context by 70-80% to eliminate first-run compaction
