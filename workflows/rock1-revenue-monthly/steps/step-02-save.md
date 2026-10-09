---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 02: Recency Gate + Append to Obsidian

## MANDATORY EXECUTION RULES

1. You MUST run the recency check before any append. Do not write a duplicate month.
2. You MUST NOT append if a heading for the current month and year already exists in the tracking file.
3. You MUST update `state.yaml` to `status: complete` on both the skip path and the write path.

---

## EXECUTION PROTOCOL

**Agent:** Chase, spawned by the coordinator, never executed inline in the coordinator's session.
**Input:** Revenue output from step-01 (`accumulated-context.revenue`), the Obsidian Rock 1 tracking file
**Output:** Dated snapshot appended to `Mind/One Texas/Rock 1 - Revenue Snapshots.md`, `state.yaml` status complete

---

## YOUR TASK

1. **Read the tracking file** via Obsidian MCP:
   ```
   mcp__obsidian-local__get_vault_file
   filepath: Mind/One Texas/Rock 1 - Revenue Snapshots.md
   ```

2. **Recency check**: scan the file for a heading matching the current month and year
   (e.g., `## April 2026`). If found, do NOT append — output:
   ```
   [Chase]: Rock 1 revenue snapshot for [Month YYYY] already recorded. Skipping write.
   ```
   Set `state.yaml` status: complete and stop.

3. **If no entry for this month**, append the following block to the file:

   ```markdown
   ## [Month YYYY] — Revenue Snapshot
   *Pulled: [YYYY-MM-DD] | Source: Enterprise Scorecard v4*

   [full formatted output from revenue-tracker skill]

   ---
   ```

   Use `mcp__obsidian-local__append_to_vault_file` with the above content.

4. **Confirm write** and output:
   ```
   [Chase]: Rock 1 revenue snapshot for [Month YYYY] written to Mind/One Texas/Rock 1 - Revenue Snapshots.md.
   ```

5. Update `state.yaml`: `status: complete`, `current-step: step-02-save`.
<!-- system:end -->
