---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 01: Load the Roster

## EXECUTION PROTOCOL

**Agent:** Rigby, spawned by the coordinator, never executed inline in the coordinator's session.
**Input:** `systems/political-monitor/sources.json`
**Output:** The fetch list (active AND accessible sources) and the muted-source list

---

## YOUR TASK

Read `systems/political-monitor/sources.json`. Build the fetch list: every source where `active==true AND accessible==true`. Note the `sources_muted` list (active-desired but `accessible==false`, e.g. NYT) for the dashboard.

## NEXT STEP

Read fully and follow: `step-02-harvest.md`
<!-- system:end -->
