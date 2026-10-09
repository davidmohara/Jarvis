---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 03: Append to Obsidian

## MANDATORY EXECUTION RULES

1. You MUST run the recency check before any append. Do not write a duplicate week.
2. You MUST NOT append if an entry from the current week (within last 5 days) already exists in the tracking file.
3. You MUST update `state.yaml` to `status: complete` on both the skip path and the write path.

---

## EXECUTION PROTOCOL

**Agent:** Chase, spawned by the coordinator, never executed inline in the coordinator's session.
**Input:** Co-sell output from step-01 (`accumulated-context.cosell`), pipeline output from step-02 (`accumulated-context.pipeline`), the Obsidian Rock 4 tracking file
**Output:** Dated snapshot appended to `Mind/One Texas/Rock 4 - Pipeline Snapshots.md`, `state.yaml` status complete

---

## YOUR TASK

1. **Read the tracking file** via Obsidian MCP:
   ```
   mcp__obsidian-local__get_vault_file
   filepath: Mind/One Texas/Rock 4 - Pipeline Snapshots.md
   ```

2. **Recency check**: look for an entry from the current week (within last 5 days).
   If found, do NOT append — output:
   ```
   [Chase]: Rock 4 pipeline snapshot already recorded this week ([date]). Skipping write.
   ```
   Update `state.yaml` with `status: complete` and `last-completed: [today's date YYYY-MM-DD]`, then stop.

3. **If no entry this week**, append the following block:

   ```markdown
   ## Week of [YYYY-MM-DD] — Pipeline Snapshot
   *Pulled: [YYYY-MM-DD] | Source: Sales Analytics*

   ### Co-Sell Pipeline (Rock 4)
   [full formatted output from co-sell-pipeline skill]

   ### Pipeline Health (Rock 1 — 90-Day Weighted)
   [full formatted output from pipeline-snapshot skill]

   ---
   ```

   Use `mcp__obsidian-local__append_to_vault_file`.

4. **Confirm write** and output:
   ```
   [Chase]: Rock 4 pipeline snapshot for week of [date] written to Mind/One Texas/Rock 4 - Pipeline Snapshots.md.
   Rock 4 gap: $[X]M remaining to $15M target.
   90-Day weighted pipeline: $[X]M One Texas.
   ```

5. Update `state.yaml`:

   ```yaml
   workflow: rock4-pipeline-weekly
   agent: chase
   status: complete
   current-step: step-03
   last-completed: "[today's date YYYY-MM-DD]"
   last-written-obsidian: "[today's date YYYY-MM-DD]"
   ```
<!-- system:end -->
