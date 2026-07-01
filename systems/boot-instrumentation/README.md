# Boot Instrumentation System

Tracks context window usage in the boot workflow to identify and eliminate bloat sources.

## Directory Structure

```
systems/boot-instrumentation/
├── measure.py                 ← Python script to measure and compare states
├── measurements/              ← Snapshots from each boot run
│   ├── measurement-state-{timestamp}.json
│   └── comparison-{timestamp}.json
├── backups/                   ← Snapshots of state.yaml before optimization
│   ├── 2026-07-01-baseline.yaml
│   └── 2026-07-02-pre-optimization.yaml
├── tracking.json              ← Summary of all measurements to date
└── README.md                  ← This file
```

## Workflow Integration

**Step 02.5** (`workflows/boot/steps/step-02.5-measure-phase2.md`) runs automatically on every boot:
1. Measures accumulated-context size after Phase 2 completes
2. Writes snapshot to `measurements/`
3. Surfaces top bloat sources to David
4. Does NOT block boot (non-critical)

## Quick Commands

### Measure current state
```bash
cd /Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES
python3 systems/boot-instrumentation/measure.py measure-state workflows/boot/state.yaml
```

### Compare before/after
```bash
python3 systems/boot-instrumentation/measure.py compare \
  systems/boot-instrumentation/backups/2026-07-01-baseline.yaml \
  workflows/boot/state.yaml
```

### View latest measurement
```bash
ls -ltr systems/boot-instrumentation/measurements/ | tail -1
cat $(ls -t systems/boot-instrumentation/measurements/measurement-state-*.json | head -1) | jq .
```

## Optimization Workflow

1. **Establish baseline**: Run boot, note Phase 2 measurement
2. **Identify bloat**: Review field_breakdown — what's largest?
3. **Backup state**: `cp workflows/boot/state.yaml systems/boot-instrumentation/backups/{date}-before.yaml`
4. **Optimize**: Edit the step/task that produces the bloated field
5. **Re-measure**: Run boot again
6. **Compare**: Use measure.py compare script to see % improvement
7. **Iterate**: Repeat for next-largest field until target is met

## Success Criteria

### Baseline (before optimization)
- Expect: 400-800 KB context bloat
- Common: Phase 2 pulls raw API responses verbatim

### Target (after optimization)
- Phase 1 (identity files): 20-30 KB
- Phase 2 (gathered summaries): 50-100 KB
- Phase 3 (meeting context): 10-20 KB
- **Total: 100-150 KB** (fits in ~400 tokens, no compaction)

### Validation
- Boot completes without context window compaction
- Measurements show 70-80% reduction
- All Phase 2 tasks still report status correctly
- Ralph verification still works

## Files Modified

To enable instrumentation:
- `workflows/boot/workflow.md` — added step 2.5 to execution sequence
- `workflows/boot/steps/step-02-gather-data.md` — updated to chain to step 2.5
- `workflows/boot/steps/step-02.5-measure-phase2.md` — NEW instrumentation step
- `systems/boot-instrumentation/measure.py` — NEW measurement script
- `skills/boot-context-analyzer/SKILL.md` — NEW analyzer skill

No changes to core boot logic. Instrumentation is read-only and non-blocking.
