---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 04: Pre-cluster

## EXECUTION PROTOCOL

**Agent:** Rigby, spawned by the coordinator, never executed inline in the coordinator's session.
**Input:** `harvest.json` from step-03
**Output:** `systems/political-monitor/clusters.json` (hint grouping only)

---

## YOUR TASK

Run `python3 systems/political-monitor/cluster.py --hours 72`. It writes `clusters.json` (loose keyword grouping; `is_shared` flags clusters with both left and right). This is a HINT, not the final grouping.

## NEXT STEP

Read fully and follow: `step-05-analyze.md`
<!-- system:end -->
