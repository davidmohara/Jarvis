---
model: sonnet
---

<!-- system:start -->
# Step 01: Account Data Aggregation

## MANDATORY EXECUTION RULES

1. You MUST pull the full account record from CRM before proceeding. No partial account pulls.
2. You MUST capture all key contacts with their role, relationship status, and last touchpoint date.
3. You MUST pull all open opportunities on this account — not just the most recent.
4. You MUST build a relationship map from CRM and knowledge layer data. Gaps in the map are risks.
5. Do NOT fabricate account data. If CRM has no record, say so explicitly.
6. Do NOT analyze or strategize in this step. Pull the data clean and move on.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Account name (from controller or upstream workflow), CRM, knowledge layer
**Output:** Complete account data stored in working memory for step 03

---

## CONTEXT BOUNDARIES

- Pull all contacts on the account, not just recent ones. Dormant contacts are still relationship assets.
- "Active opportunities" means any deal not marked closed-won, closed-lost, or archived.
- Relationship strength is inferred from: frequency of interaction, recency, and meeting participation.
- Knowledge layer context enriches CRM data — use both, not just one.
- If CRM has no account record, flag the gap and proceed with whatever data is available.

---

## YOUR TASK

### Sequence

1. **Pull account record from CRM** (CRM):
   - Account name and industry
   - Account owner (relationship lead)
   - Account classification or tier (if defined)
   - Account creation date and tenure
   - Total lifetime revenue (sum of closed-won opportunities)
   - Active engagements (current projects, deployed resources)
   - Account health score or satisfaction data (if captured in CRM)

2. **Pull all key contacts with roles and relationship status:**
   - For each contact:
     - Name, title, department
     - Role in buying process: `economic-buyer` | `champion` | `influencer` | `gatekeeper` | `user` | `unknown`
     - Relationship strength: `strong` | `moderate` | `new` | `dormant`
     - Last touchpoint date (email, meeting, or CRM interaction)
     - Who on the controller's team owns this relationship
   - Identify which contacts have no documented interaction in 90+ days (relationship decay risk)

3. **Pull all open opportunities with stage and value:**
   - For each:
     - Opportunity name
     - Stage and stage probability
     - Total amount and weighted amount
     - Owner
     - Expected close date
     - Last activity date
     - Next step (if defined)
     - Days in current stage
   - Flag any at-risk opportunities (no activity in 14+ days)

4. **Build relationship map across the account from knowledge layer:**
   - Search knowledge layer for: meeting notes, relationship summaries, account files
   - Extract: who was in the room, decisions made, relationship history
   - Identify:
     - Executive sponsors (if any) and their current engagement level
     - Champions who advocate for the controller's org
     - Blockers or skeptics
     - Contacts with no current relationship (whitespace)

5. **Store results** in working memory:
   ```
   account_data:
     account:
       name: ...
       industry: ...
       owner: ...
       tier: ...
       tenure: N years
       lifetime_revenue: $X
       active_engagements: [{name, team_size, status}, ...]
     contacts:
       - name: ...
         title: ...
         department: ...
         buying_role: economic-buyer | champion | influencer | gatekeeper | user | unknown
         relationship_strength: strong | moderate | new | dormant
         last_touchpoint: YYYY-MM-DD
         relationship_owner: ...
     opportunities:
       - name: ...
         stage: ...
         amount: $X
         weighted: $X
         owner: ...
         close_date: YYYY-MM-DD
         last_activity: YYYY-MM-DD
         next_step: ...
         days_in_stage: N
         at_risk: true/false
     relationship_map:
       executive_sponsors: [{name, title, buying_role, relationship_strength, last_touchpoint, engagement: active | passive | dormant}, ...]
       champions: [{name, title, buying_role, relationship_strength, last_touchpoint}, ...]
       blockers: [{name, title, buying_role, relationship_strength, last_touchpoint, concern}, ...]
       whitespace_contacts: [{title, department}, ...]
     knowledge_layer_notes:
       - file: ...
         date: YYYY-MM-DD
         key_points: [...]
         open_items: [...]
   ```

---

## SUCCESS METRICS

- Full account record pulled with revenue history and active engagements
- All contacts catalogued with buying roles, relationship strength, and last touchpoint date
- All open opportunities identified with stage, value, and risk status
- Relationship map built showing sponsors, champions, blockers, and whitespace
- Knowledge layer context layered in for relationship history

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Account not found in CRM | Flag: "No CRM record found for [account]." Proceed with knowledge layer and web data only. Note the gap prominently. |
| CRM unavailable | Use knowledge layer data only. Flag: "CRM unavailable — account data may be incomplete." |
| No contacts on account | Flag: "No contacts on record. This is a major relationship risk." Proceed to competitive research. |
| No open opportunities | Flag: "No active opportunities on this account." Suggest the executive consider a prospecting or re-engagement conversation to identify new pipeline. |
| Knowledge layer returns no data | Proceed without historical context. Note: "No knowledge layer data for this account." |

---

## NEXT STEP

Read fully and follow: `step-02-competitive-intel.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
