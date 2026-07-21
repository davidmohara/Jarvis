---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 01: Entity Anchor, Disambiguation, and Timing Trigger

## MANDATORY EXECUTION RULES

1. You MUST verify the target entity's identity before writing any other content. If the company name, acronym, or domain is ambiguous — matches multiple distinct organizations, is a common word, or is a subsidiary/brand name that could refer to more than one parent — resolve it via domain match, stock ticker, HQ location, or another hard signal before proceeding. This directly targets the failure mode logged in `err-20260720T144623-LSBA9A` (OFS acronym collision). Do not pick the most prominent search result by default.
2. You MUST check for an existing account folder at `accounts/{Company}/` before doing anything else. If it exists, read `account-plan.md` in full — this is a refresh/update, not a fresh build, and prior content should inform (not be silently overwritten by) this run.
3. You MUST determine and explicitly state the engagement shape: **active-but-underleveraged** (Improving has a current engagement, beachhead, or contract vehicle at this account but is underrepresented in the capability areas being pursued — Schwab pattern) or **cold/lost re-entry** (no current engagement, or a specific lost deal/opportunity to rebuild from — Constellation pattern). This determination gates the shape of the phased strategic path built in step 05. Do not guess — check CRM for prior engagement or loss history before asserting either shape.
4. You MUST identify a specific, citable public timing trigger — a restructuring, M&A close, investor day commitment, leadership change, earnings statement, or similar event — that makes now a credible moment to pursue this account. A pursuit map without a timing trigger is generic prospecting, not a strategic play.
5. You MUST NOT assume a relationship type, deal stage, or loss reason without citable evidence (CRM record, email, filing). If CRM has no record and no one on David's team can confirm engagement history, state this as an open item rather than asserting "no relationship."
6. Do NOT proceed to step 02 until the entity is confirmed, the engagement shape is determined, and a timing trigger is identified (or explicitly flagged as not yet found).

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Target company name (from controller), CRM, web search
**Output:** Confirmed entity identity, engagement shape determination, timing trigger — stored in accumulated-context for all downstream steps

---

## CONTEXT BOUNDARIES

- This step establishes facts, not strategy. Do not draft priorities, contacts, or plays here — that happens in later steps.
- "Active-but-underleveraged" requires an actual current engagement (contract, SOW, MSA, active relationship) confirmed via CRM or direct knowledge — not just "we've talked to them before."
- "Cold/lost re-entry" covers both zero-footprint prospects and accounts with a specific lost deal. If there's a lost deal, the CRM loss record becomes a required input for step 05's next-actions sequencing (it gates the outreach, per the Constellation pattern).
- A timing trigger must be a specific, dated, citable event — not a generic statement like "companies are always investing in AI." "Schwab's CEO called AI the most significant growth opportunity in company history at the 2026 Investor Day" is a valid trigger. "AI is important to financial services" is not.

---

## YOUR TASK

### 1. Check for an existing account folder

- Look for `accounts/{Company}/account-plan.md`. Try reasonable name variants (e.g., "Constellation" vs. "Constellation Energy") before concluding it doesn't exist.
- If found: read it fully. This run updates/refreshes that document. Carry forward any facts that are still current; flag anything that looks stale (title changes, org changes, closed opportunities) for re-verification in later steps.
- If not found: this is a new pursuit map. Note the folder will be created in step 05.

### 2. Disambiguate the entity

- Confirm: full legal/public name, ticker (if public), HQ location, industry, and a distinguishing fact (e.g., "Constellation Energy Corporation, Nasdaq: CEG, Baltimore — not to be confused with [other Constellation entity]" if ambiguity exists).
- If the name is a common word, acronym, or shares a name with unrelated companies, explicitly cross-reference against any domain, ticker, or location detail already known (from the controller's request, CRM, or prior account folder) before committing to an identity.
- Record:
  ```yaml
  entity_anchor:
    confirmed_name: "{Full legal/public name}"
    ticker: "{Ticker or 'private'}"
    hq: "{City, State/Country}"
    industry: "{Industry}"
    disambiguation:
      ambiguous: true/false
      resolution_method: "{ticker match | domain match | HQ match | unresolved}"
      note: "{One line if ambiguity existed}"
    existing_account_folder: true/false
    prior_plan_summary: "{2-3 sentences if a prior plan was found, else 'None — new pursuit.'}"
  ```

### 3. Determine engagement shape

- Check CRM for: any current active engagement, contract vehicle, or MSA at this account; any closed-won or closed-lost opportunities; any documented loss reason.
- If CRM is unavailable or has no record, ask whoever has direct knowledge (or flag as an open item) rather than asserting a shape from web research alone — web sources cannot confirm Improving's own engagement status.
- Classify:
  ```yaml
  engagement_shape:
    determination: "active-but-underleveraged" | "cold-lost-reentry"
    evidence: "{What CRM/knowledge confirmed this — e.g., 'Active MSA + ID engagement per CRM' or 'CRM shows one closed-lost training opportunity, no other history'}"
    if_lost_deal:
      opportunity_name: "{If applicable}"
      loss_reason_documented: true/false
      note: "{If a loss record exists, summarize; if not, flag: 'Loss reason not yet confirmed — gate step 05 next actions on pulling this record first.'}"
  ```

### 4. Identify the timing trigger

- Search for the specific public event that makes this pursuit timely: restructuring, M&A close, investor day commitment, leadership change, earnings call statement, major press release.
- Prefer primary sources (company press releases, SEC filings, investor day materials) over secondary news coverage where possible; secondary coverage is acceptable as a supplement.
- Record:
  ```yaml
  timing_trigger:
    event: "{Specific, dated event}"
    date: "{YYYY-MM or specific date}"
    source: "{URL}"
    why_it_matters: "{1-2 sentences connecting the event to why now is the right moment}"
  ```
- If no clear trigger is found, do not invent one. State: "No specific public timing trigger identified — pursuit rationale rests on [whatever general signal exists]." and flag this as a gap for the controller.

---

## SUCCESS METRICS

- Entity confirmed with a disambiguation check explicitly performed (not skipped even when the name looks unambiguous)
- Existing account folder checked; prior plan content carried forward if found
- Engagement shape determined from CRM/direct evidence, not inferred from web research alone
- If cold/lost re-entry with a specific lost deal, the loss record status is explicitly noted (confirmed or still needs pulling)
- A specific, dated, citable timing trigger identified — or its absence explicitly flagged

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Company name ambiguous and no disambiguating signal available | Do not guess. Flag: "Entity identity unresolved — {name} matches multiple organizations, no domain/ticker/HQ evidence available to disambiguate." Surface to controller before proceeding. |
| CRM unavailable or no connector active | Note: "CRM unavailable — engagement shape determined from [direct knowledge / controller statement] only; confirm against CRM when available." Do not assert "cold" by default — ask if uncertain. |
| No timing trigger found | State the gap explicitly rather than manufacturing urgency. Proceed with whatever general rationale exists, clearly labeled as weaker than a dated trigger. |
| Existing account folder found but stale (many months old) | Note staleness explicitly; treat facts as needing re-verification in steps 02-04 rather than accepting them at face value. |
| Lost deal exists in CRM but loss reason isn't documented | Flag prominently — this becomes a required first action in step 05 ("pull the CRM loss record first, before any outreach"), mirroring the Constellation pattern. |

---

## NEXT STEP

Read fully and follow: `step-02-strategic-priorities.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
