---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->

## MANDATORY EXECUTION RULES

1. **Component 3 is self-assessed only.** Never invent entries. Only write entries David confirms.
2. **OTE: $10,000 total.** Max $5,000 per item, $2,500 minimum if logging an item.
3. **Two categories only.** Item 1 (Strategic Partnerships/GMS), Item 2 (Exec Programs/Account Plans).
4. **If David says nothing qualifies, leave the Comp 3 sheet blank for this month.** Do not default to $5,000 entries.
5. **Scan both calendar and Plaud.** Evidence is calendar events + transcript mentions. Pre-populate the prompt with both.

---

## EXECUTION PROTOCOL

| Role | Input | Output |
|------|-------|--------|
| **Chase** | Search calendar for update month; retrieve Plaud transcripts; open Comp 3 sheet; get David's confirmation | Updated Comp 3 sheet with confirmed strategic entries (Item 1, Item 2, or blank if no qualifiers); flagged amounts ($2.5K or $5K per item) |

---

## CONTEXT BOUNDARIES

**In scope for this step:**
- Searching calendar for qualifying activities this month
- Scanning Plaud transcripts for strategic activity mentions
- Pre-populating a prompt for David with calendar and transcript evidence
- Writing confirmed entries to Comp 3 sheet only after David approves
- Logging dollar amounts for each confirmed item

**Out of scope:**
- Final summary and delivery — that's step 8

---

## YOUR TASK

### 1. Determine the update month

From accumulated-context, retrieve the current month being processed (e.g., "April 2026").

---

### 2. Search calendar for qualifying activities

Search David's Outlook calendar for the update month using `mcp__b8c41a14__outlook_calendar_search`:

**Query keywords:**
- "QBR" (Quarterly Business Review)
- "account plan"
- "workshop"
- "GMS" (Global Managed Services)
- "executive" (executive engagement, executive review)
- "strategic" (strategic partnership, strategic initiative)
- Partner names: "Microsoft", "AWS", "Google", "Confluent", "SAP"

**Date range:**
```
afterDateTime: [First day of update month]
beforeDateTime: [Last day of update month]
```

**Example search:** `"QBR OR account plan OR workshop OR GMS OR executive OR strategic OR Microsoft OR Confluent"`

Collect all matching events. For each event, extract:
- **Date** (YYYY-MM-DD)
- **Title** (event name)
- **Description** (if available — details about the activity)
- **Attendees** (if relevant — which client/partner)

---

### 3. Scan Plaud transcripts for the update month

Search Obsidian vault (where Plaud transcripts are stored) for the same month:

Use `mcp__obsidian-local__search_vault_smart` or `search_vault_simple` to find transcripts mentioning:
- "Strategic partnerships" or specific partner names (Microsoft, AWS, Confluent, SAP)
- "QBR" or "quarterly business review" or "executive review"
- "Account plan" or "account planning"
- "GMS" or "global managed services"
- "Workshop" or "executive workshop"

**Search for files from the update month.** Transcripts usually have dates in their filenames or metadata.

For each match, extract:
- **Date** (when the call/meeting occurred)
- **Participant** (who was involved)
- **Activity description** (what was discussed)
- **Outcome or impact** (if mentioned)

---

### 4. Organize evidence by Component 3 category

Sort calendar events and transcript mentions into two categories:

**Category 1: Strategic Partnerships / GMS Utilization**
- Microsoft partner activations
- AWS/Google/Confluent leveraging for regional revenue
- GMS (Global Managed Services) deployments or activations
- Strategic partner pipeline influence

Example calendar events:
- "Microsoft Partner Summit - 2 EVPs"
- "GMS Deployment Kickoff - XYZ Corp"

Example transcript mentions:
- "Brought in Confluent architect to help close the pipeline"
- "Activated Microsoft managed services for this account"

**Category 2: Executive Programs / Account Plan Elevations**
- QBRs with clients (quarterly business reviews)
- Account plan elevations (moving account strategy to exec level)
- Executive workshops or roundtables
- Exec-level deliverables (strategy docs, roadmaps, etc.)

Example calendar events:
- "QBR - AT&T Services"
- "Executive Account Planning Session - Marriott"
- "Exec Workshop - Q2 2026"

Example transcript mentions:
- "Ran the QBR with the account team"
- "Elevated account plan to VP level"
- "Delivered executive summary on strategic opportunities"

---

### 5. Build the pre-populated prompt

Construct a clear, evidence-based prompt for David:

```
===== COMPONENT 3 STRATEGIC IMPACT — [MONTH] [YEAR] =====

Based on calendar events and Plaud transcripts for [Month], the following activities may qualify for Component 3:

ITEM 1 — STRATEGIC PARTNERSHIPS / GMS UTILIZATION ($2,500–$5,000)
Did you activate global partnerships or GMS resources that influenced regional pipeline/revenue?

Evidence found:
  [ ] Calendar: [Event date - Event title]
      Description: [Details about what happened]
      
  [ ] Transcript: [Call date - Participant]
      Mention: "[Quoted text from transcript]"
      
Your assessment (if any of above qualifies):
  Did this activity result in qualified pipeline or revenue influence?
  Impact (one sentence):  _____________________
  Estimated amount: $2,500 / $5,000 / None

---

ITEM 2 — EXECUTIVE PROGRAMS / ACCOUNT PLAN ELEVATIONS ($2,500–$5,000)
Did you run QBRs, elevate account plans, or deliver executive-level strategic activities?

Evidence found:
  [ ] Calendar: [Event date - Event title]
      Description: [Details about what happened]
      
  [ ] Transcript: [Call date - Participant]
      Mention: "[Quoted text from transcript]"

Your assessment (if any of above qualifies):
  Which activity elevated an account plan or produced an exec-level deliverable?
  Account / deliverable:  _____________________
  Impact (one sentence):  _____________________
  Estimated amount: $2,500 / $5,000 / None

---

If nothing qualifies this month, reply: "Nothing to log."

Component 3 Total OTE: $10,000 max ($5,000 per item). Minimum $2,500 if logging an item.
```

**If NO calendar or transcript evidence exists for the month:**
```
===== COMPONENT 3 STRATEGIC IMPACT — [MONTH] [YEAR] =====

No calendar events or Plaud transcripts found matching strategic activities for [Month].

Do you have any strategic partnerships, GMS activations, QBRs, or account plan elevations to log that aren't reflected in calendar or transcripts?

If so, describe the activity and impact. If not, reply: "Nothing to log."
```

---

### 6. Wait for David's confirmation

Present the prompt to David and wait for a response. Possible responses:
- Item 1 description + amount (e.g., "$5,000 for Microsoft GMS activation")
- Item 2 description + amount (e.g., "$2,500 for AT&T QBR")
- Both items
- "Nothing to log."
- Other clarification or modification

**Do NOT assume any amount or entry.** Only write what David explicitly confirms.

---

### 7. Write confirmed entries to Comp 3 sheet

Once David confirms, open the `Comp 3 - Strategic` tab (if not already open from prior steps).

**Expected columns:**
- Month
- Item 1 / Item 2 (or similar labeling)
- Activity / Initiative
- Date
- Impact Description / Revenue Influence
- Notes
- Dollar Amount

For each confirmed item, write:

```
Row: [Month] Item 1 (or Item 2)
  Activity: [David's description, one line]
  Date: [Month of occurrence]
  Impact: [David's impact statement]
  Notes: [Additional context if provided]
  Dollar Amount: [$2,500 or $5,000 as confirmed]
```

---

### 8. Calculate total and validate against OTE

Sum all Component 3 entries for the month:
```
Total = Item 1 Amount + Item 2 Amount

Validation:
  Max per item: $5,000 ✓
  Total OTE: ≤ $10,000 ✓
  Min if logging: ≥ $2,500 ✓
```

If total > $10,000, flag and ask David: "Component 3 total exceeds OTE. Which entries should I keep?"

---

### 9. Save the spreadsheet

Use `mcp__Excel__By_Anthropic___save_workbook`.

---

### 10. Store outputs in state.yaml

Update `state.yaml` with:
```yaml
current-step: 7
accumulated-context:
  (all prior context, plus:)
  comp3_items_logged: 0
  comp3_item1: { logged: false, amount: 0, description: "" }
  comp3_item2: { logged: false, amount: 0, description: "" }
  comp3_total: 0.00
  comp3_timestamp: "2026-04-17T10:00:00Z"
```

---

## SUCCESS METRICS

✅ **Step 7 complete when:**
1. Calendar searched for qualifying activities this month
2. Plaud transcripts scanned for strategic mentions
3. Evidence pre-populated into a prompt for David
4. David's response received (confirmed items or "nothing to log")
5. Confirmed entries written to Comp 3 sheet (if any)
6. Component 3 total validated against $10K OTE
7. Spreadsheet saved
8. accumulated-context in state.yaml updated with comp3 entries

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| **Calendar search returns no results** | Continue with transcript scan. If both are empty, present prompt indicating no evidence found — ask David if there are strategic activities to log. |
| **Plaud transcripts not accessible** | Note in prompt: "Plaud transcripts unavailable. Calendar evidence: [list calendar events]." Ask David to add any transcript-level activities. |
| **David responds with vague or unclear amount** | Ask: "For [activity], did you want $2,500 or $5,000?" Confirm amount before writing. |
| **David's total exceeds $10K OTE** | Flag: "Component 3 total is $[amount], which exceeds $10K OTE. Confirm which entries to log." Wait for clarification. |
| **Calendar event is borderline (not clearly strategic)** | Include it in the prompt with: "⚠️  Uncertain fit for Component 3. Is this a qualifying activity?" Let David confirm. |

---

## NEXT STEP

→ `step-08-close.md`

Pass all accumulated-context (including comp3_items_logged, comp3_total, comp3 entries) to Step 8. Step 8 will deliver the final one-screen summary.

<!-- system:end -->
