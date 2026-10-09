---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- personal:start -->
# Step 07: Report

## EXECUTION PROTOCOL

**Agent:** Knox, spawned by the coordinator, never executed inline in the coordinator's session.
**Input:** The full run record (discover, ingest, normalize, link, file, route)
**Output:** Ingestion summary

---

## YOUR TASK

Summarize what was ingested, linked, and routed.

## ROLLBACK PROTOCOL

This workflow only adds files to the vault. It never modifies or deletes existing content. If an ingest produces bad output, delete the specific file from the vault. The sync manifest tracks what was processed, so re-running will skip already-ingested items unless the manifest is reset.
<!-- personal:end -->
