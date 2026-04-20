---
status: complete
started-at: "2026-04-06T04:16:00"
completed-at: "2026-04-06T04:17:00"
outputs:
  appended: true
  entry_date: "2026-04-06"
model: sonnet
---

<!-- system:start -->
# Step 05: Save to Obsidian

## MANDATORY EXECUTION RULES

1. You MUST check the tracking file for a last entry date before appending. No blind appends.
2. You MUST prompt the controller before appending if the last entry is less than 28 days ago.
   Do not proceed without explicit confirmation.
3. You MUST assemble the full snapshot from accumulated-context — do not re-pull any data.
4. You MUST include today's date as a `## [YYYY-MM-DD]` header in the appended content.
5. Do NOT overwrite existing file content — append only.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** `accumulated-context` from steps 01-04, Obsidian vault (via Obsidian MCP)
**Output:** Dated snapshot appended to `Mind/One Texas/One Texas Scorecard Tracking.md`

---

## CONTEXT BOUNDARIES

- Target file: `Mind/One Texas/One Texas Scorecard Tracking.md`
- Recency window: 28 days. Prompt if last entry is newer than 28 days ago.
- If file does not exist, create it — do not fail.
- Append only. Never replace or truncate existing content.

---

## YOUR TASK

### Sequence

1. **Read the tracking file**:
   ```
   mcp__obsidian-mcp-tools__get_vault_file
   path: Mind/One Texas/One Texas Scorecard Tracking.md
   ```

   - If file does not exist (404 error): create it with the header below, then skip to step 3.
     ```
     mcp__obsidian-mcp-tools__create_vault_file
     path: Mind/One Texas/One Texas Scorecard Tracking.md
     content: |
       # One Texas Scorecard Tracking

       _Automated snapshots appended by Chase via one-texas-scorecard workflow._

       ---
     ```

2. **Check recency**:
   - Scan file content for the most recent `## [YYYY-MM-DD]` date header.
   - Calculate days between that date and today.
   - If **less than 28 days**: prompt controller:
     > "[Chase]: Last One Texas Scorecard entry was [date] — [N] days ago. That's within the
     > 28-day window. Append anyway?"
   - Wait for confirmation. If controller says no: set step `status: aborted`,
     set workflow `status: aborted`, stop.
   - If **28 or more days**, or file was just created: proceed without prompting.

3. **Assemble snapshot** from `accumulated-context` in this order:
   ```markdown
   ## [YYYY-MM-DD]

   ### Revenue

   {accumulated-context.revenue}

   ---

   ### Co-Sell Pipeline

   {accumulated-context.co_sell}

   ---

   ### Pipeline Snapshot

   {accumulated-context.pipeline}

   ---

   ### New Clients

   {accumulated-context.new_clients}

   ---

   ### Goal Alignment — 2026 Annual Goals

   *Source: `Mind/One Texas/2026 Goals.md` — targets set Dec 29, 2025.*

   | Goal | Target | Actuals This Period | RAG |
   |------|--------|---------------------|-----|
   | G1 Revenue Growth | Beat target, both enterprises | [Dallas %] vs target · [STX %] vs target | 🟢/🟡/🔴 |
   | G2 Account Pursuit — Anchors | 3 new anchors / enterprise (6 OTX annual) | [N] anchors YTD of 6 annual | 🟢/🟡/🔴 |
   | G2 Account Pursuit — Logos | 9 logos Q1 target (annual pace TBD) | [N] logos YTD | 🟢/🟡/🔴 |
   | G4 Partner Engagement | $15M co-sell by Q2 end | $[N] of $15M ([%] complete) | 🟢/🟡/🔴 |
   | G3 Improver Growth | 1 EDP H2 + Exec Sales rollout | H2 target — track manually | ⚪ |
   | G5 Thought Leadership | 10 speaking engagements / year | Manual tracking — see goals file | ⚪ |

   [2-3 sentences of Chase-voice commentary on overall goal trajectory. Lead with the hardest number — what is most at risk of missing for the year? Call out any goal where One Texas is on pace vs. off pace. Do not soften.]

   ---
   ```

   **Populating the Goal Alignment table:**
   - G1: use Revenue vs. Target QTD % from `accumulated-context.revenue` for both enterprises
   - G2 Anchors: use New Anchors YTD from `accumulated-context.new_clients` vs. annual target (6)
   - G2 Logos: use New Logos YTD from `accumulated-context.new_clients`
   - G4: use co-sell pipeline + won total from `accumulated-context.co_sell`, compute % of $15M
   - G3, G5: always ⚪ (not in automated pull) — note H2 timing for G3
   - RAG: 🟢 = on pace for annual target, 🟡 = behind but recoverable, 🔴 = critical / off pace

4. **Append to file**:
   ```
   mcp__obsidian-mcp-tools__append_to_vault_file
   path: Mind/One Texas/One Texas Scorecard Tracking.md
   content: [assembled snapshot]
   ```

5. **Update step frontmatter**:
   ```yaml
   status: complete
   completed-at: [timestamp]
   outputs:
     appended: true
     entry_date: [YYYY-MM-DD]
   ```

6. **Update workflow state**:
   ```yaml
   status: complete
   current-step: complete
   ```

7. **Confirm to controller**:
   > "[Chase]: One Texas Scorecard updated — [YYYY-MM-DD] entry appended to
   > `Mind/One Texas/One Texas Scorecard Tracking.md`."

---

## SUCCESS METRICS

- Tracking file exists (created if needed)
- Recency check performed against last `## [YYYY-MM-DD]` header
- Controller prompted and confirmed if entry is within 28-day window
- Full snapshot assembled from all four accumulated-context sections
- Content appended with today's date header
- Workflow state set to complete

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Obsidian MCP unavailable | Surface to controller: "[Chase]: Obsidian MCP unavailable — snapshot assembled but not saved. Copy output manually." Display full assembled snapshot in conversation. |
| File read returns unexpected format (no date headers) | Treat as no prior entries. Proceed without prompting. |
| Append fails (permissions, vault sync issue) | Retry once. If still failing, display full assembled snapshot in conversation for manual paste. |
| One or more accumulated-context sections are null | Note which sections are missing in the output header. Append available sections only. |

---

## NEXT STEP

Workflow complete. No further steps.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
