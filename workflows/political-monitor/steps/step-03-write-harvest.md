---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 03: Write harvest.json

## EXECUTION PROTOCOL

**Agent:** Rigby, spawned by the coordinator, never executed inline in the coordinator's session.
**Input:** The merged item set from step-02
**Output:** `systems/political-monitor/harvest.json`

---

## YOUR TASK

Write `systems/political-monitor/harvest.json` in this shape:
```json
{ "generated": "<ISO8601>", "window_hours": 72,
  "items": [ { "source": "CNN Politics", "source_id": "cnn", "lean": "left",
               "title": "...", "url": "https://...", "summary_raw": "...", "seen_passes": 2 } ] }
```
Keep only items inside the window. Dedupe obvious repeats.

## NEXT STEP

Read fully and follow: `step-04-pre-cluster.md`
<!-- system:end -->
