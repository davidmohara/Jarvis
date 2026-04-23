---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->

## MANDATORY EXECUTION RULES

1. **Never invent activities.** Only log what David explicitly confirms. No guessing.
2. **OTE cap: $10,000/month total.** Up to $5,000 per item (Item 1 + Item 2).
3. **Scan calendar AND Plaud transcripts.** Both sources feed the prompt.
4. **Present candidates to David — wait for confirmation before writing anything.**
5. **Write only to the Comp 3 sheet.** No other sheets.

---

## COMP 3 OVERVIEW

Component 3 covers Strategic Impact — two items:

| Item | Category | OTE |
|------|----------|-----|
| Item 1 | Strategic Partnerships / GMS (Go-to-Market Strategy) | Up to $5,000/month |
| Item 2 | Exec Programs / Account Plans | Up to $5,000/month |
| **Total** | | **Up to $10,000/month** |

David must confirm which activities qualify before any values are written.

---

## EXECUTION PROTOCOL

| Role | Input | Output |
|------|-------|--------|
| **Chase** | Calendar events + Plaud transcripts from current month → present qualifying candidates to David → write confirmed amounts to Comp 3 sheet |

---

## YOUR TASK

### 1. Retrieve the current month being processed

From `accumulated-context.month` in state.yaml (e.g., "2026-04" = April 2026).

---

### 2. Scan calendar for strategic activity candidates (Item 1 & Item 2)

Use `mcp__b8c41a14__outlook_calendar_search` to pull calendar events from the current month.

Look for events that could qualify as:

**Item 1 — Strategic Partnerships / GMS:**
- GMS meetings, go-to-market strategy sessions
- Partnership calls with external organizations
- Strategic planning sessions with senior stakeholders
- Exec-level business development meetings

**Item 2 — Exec Programs / Account Plans:**
- Executive briefings or EBCs (Executive Briefing Center sessions)
- Account planning sessions
- QBR (Quarterly Business Review) participation
- Strategic account reviews with VP-level or above

Build a candidate list:
```json
{
  "item1_candidates": [
    { "date": "2026-04-15", "event": "GMS Strategy Session with [Partner]", "duration_hrs": 2 }
  ],
  "item2_candidates": [
    { "date": "2026-04-10", "event": "QBR with [Account] — Exec team", "duration_hrs": 1.5 }
  ]
}
```

---

### 3. Scan Plaud transcripts for strategic activity mentions

Use `mcp__obsidian-local__search_vault` to search the Plaud notes ingested this session for the current month.

Search terms to look for:
- "GMS", "go-to-market", "strategic partnership"
- "account plan", "exec briefing", "EBC", "QBR"
- "strategic impact", "Comp 3"
- Any mention of activities that sound like the categories above

Look at transcripts from the last 30 days. Extract any activities mentioned that could qualify.

Add these to the candidate lists.

---

### 4. Deduplicate candidates

Cross-check calendar events vs. Plaud transcript mentions. If the same event appears in both, count it once.

---

### 5. Present candidates to David

Output the candidate list in this exact format:

```
================================================================================
  COMP 3 — STRATEGIC IMPACT CANDIDATES ([MONTH YEAR])
================================================================================

ITEM 1 — STRATEGIC PARTNERSHIPS / GMS (OTE: up to $5,000)
  Candidates found:
  1. [Date] — [Event description] ([duration])
  2. [Date] — [Event description] ([duration])
  
  → Confirm: Which of these qualify? Enter dollar amount for Item 1 (0 to $5,000):

ITEM 2 — EXEC PROGRAMS / ACCOUNT PLANS (OTE: up to $5,000)
  Candidates found:
  1. [Date] — [Event description] ([duration])
  2. [Date] — [Event description] ([duration])
  
  → Confirm: Which of these qualify? Enter dollar amount for Item 2 (0 to $5,000):

If no qualifying activities occurred this month, enter $0 for that item.
================================================================================
```

**Wait for David's response before writing anything.**

---

### 6. Write confirmed amounts to Comp 3 sheet

After David confirms dollar amounts for Item 1 and/or Item 2:

Open the comp tracker (still open from prior steps, or re-open using path from state.yaml).

Select the **"Comp 3"** sheet.

**Read the sheet structure first.** The Comp 3 sheet layout may vary — do not assume cell locations. Identify:
- The row for Item 1 (Strategic Partnerships/GMS)
- The row for Item 2 (Exec Programs/Account Plans)
- The column for the current month

Write David's confirmed amounts to the correct cells.

If the Comp 3 sheet does not exist or has an unexpected structure, report: "Comp 3 sheet not found or layout unclear — manual entry needed."

---

### 7. Save the workbook

Call `mcp__Excel__By_Anthropic___save_workbook`.

---

### 8. Update state.yaml

```yaml
current-step: 7
accumulated-context:
  (all prior context, plus:)
  comp3_updated: true
  comp3_item1_amount: 0.00
  comp3_item2_amount: 0.00
  comp3_total: 0.00
  comp3_month: "2026-04"
  comp3_timestamp: "YYYY-MM-DDTHH:MM:SSZ"
  comp3_notes: "Item 1: [description]. Item 2: [description]."
```

---

## SUCCESS METRICS

✅ **Step 7 complete when:**
1. Calendar scanned for strategic activity candidates
2. Plaud transcripts scanned for strategic activity mentions
3. Candidates presented to David with specific options for Item 1 and Item 2
4. David's confirmation received before writing anything
5. Confirmed amounts written to Comp 3 sheet
6. Workbook saved
7. state.yaml updated with confirmed amounts

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| **No calendar events found** | Surface to David: "No Comp 3 candidates found in calendar for [month]. Enter amounts manually if applicable, or confirm $0." |
| **Plaud search unavailable** | Proceed with calendar data only. Note: "Plaud transcripts not available for scanning." |
| **Comp 3 sheet not found** | Report layout issue. Do not write. Ask David: "Comp 3 sheet not found in the tracker — should I create it or skip?" |
| **David confirms $0 for both items** | Write $0 (or leave blank per sheet convention). Note in summary: "No Comp 3 activities logged for [month]." |
| **David confirms amounts that exceed OTE cap** | Flag: "Item [1/2] confirmed amount ($X) exceeds OTE cap ($5,000). Confirm you want to log $X?" Wait for re-confirmation. |

---

## NEXT STEP

→ `step-08-close.md`

Pass all accumulated-context (comp3_item1_amount, comp3_item2_amount, comp3_total) to Step 8. Step 8 will synthesize the full one-screen summary.

<!-- system:end -->
