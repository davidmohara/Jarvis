<!-- system:start -->
# Step 02: Account Overlap Analysis

## MANDATORY EXECUTION RULES

1. You MUST build the account overlap table. This is the centerpiece of the entire meeting prep. No document without it.
2. You MUST include an "Internal Seller" column for every account where the controller's team has one assigned.
3. You MUST include a "Partner Rep" column -- leave it blank for the partner to fill. This is intentional, not incomplete.
4. You MUST categorize accounts into three groups: Active Relationships, Target Accounts, and Partner Accounts.
5. You MUST include accounts where only ONE side is engaged -- these are expansion opportunities.
6. Do NOT fabricate account data. If CRM is unavailable, work from email threads and the controller's knowledge.
7. Do NOT proceed to step 03 until the overlap table structure is complete.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Partner details from step 01, CRM data, email threads, knowledge layer
**Output:** Categorized account overlap table stored in working memory for step 04

---

## CONTEXT BOUNDARIES

- This is about OVERLAP -- where do both organizations touch the same accounts?
- The goal is pairing: Internal Seller + Partner Rep for every relevant account.
- Accounts where only one side has a relationship are just as valuable -- they represent intro and expansion opportunities.
- Revenue figures are included when available but not required. The pairing is the value.
- The partner's side of the table has intentional blanks. This is by design -- the meeting itself is where they fill in.

---

## YOUR TASK

### Sequence

1. **Pull the controller's active accounts from CRM.**
   - Query CRM for active accounts with open opportunities or recent activity.
   - For each: account name, assigned seller/AE, opportunity status, revenue (if available).
   - Filter for accounts in the partner's relevant geography, vertical, or technology stack.

2. **Cross-reference with known partner accounts.**
   - Check email threads from step 01 for accounts mentioned in partner correspondence.
   - Check previous prep docs for accounts discussed in prior meetings.
   - If the partner previously shared an account list, reference it.
   - If the partner operates in a specific technology domain (e.g., Confluent = data streaming), filter for accounts using or evaluating that technology.

3. **Categorize accounts into three groups:**

   **Group 1: Active Relationships (Joint Opportunity)**
   Accounts where the controller's team has existing engagement AND the partner has a known relationship or could add value.
   - These are the immediate co-sell opportunities.
   - Include: account name, internal seller, partner rep (blank if unknown), active opportunities, engagement status, key contacts.

   **Group 2: Target Accounts (Joint Pursuit)**
   Accounts the controller's team is actively pursuing where the partner could accelerate access.
   - These are "help us get in the door" accounts.
   - Include: account name, internal seller, partner rep (blank), pursuit status, what would help (intro, reference, joint pitch).

   **Group 3: Partner Accounts (Controller Can Help)**
   Accounts where the partner has relationships and the controller's team can add value.
   - These are largely blank -- the partner fills them in during the meeting.
   - Include: account name (blank or from prior intel), internal seller (TBD), partner rep (if known), notes (blank).
   - Explicitly mark this section for partner input: "Partner team: which of your accounts could benefit from {controller's org} services?"

4. **Build the structured table for each group:**
   ```
   account_overlap:
     group_1_active:
       - account: ...
         internal_seller: ...
         partner_rep: {TBD - partner to fill}
         opportunities: ...
         revenue: ... (if known)
         status: ...
         notes: ...
     group_2_target:
       - account: ...
         internal_seller: ...
         partner_rep: {TBD - partner to fill}
         pursuit_status: ...
         what_would_help: ...
     group_3_partner:
       - account: {TBD - partner to fill}
         internal_seller: {TBD}
         partner_rep: {if known}
         notes: {TBD - partner to fill}
     summary:
       total_accounts: N
       group_1_count: N
       group_2_count: N
       group_3_count: N (mostly blanks)
   ```

5. **Identify co-sell patterns.**
   - Which accounts have the most momentum?
   - Where is the partner's technology a fit for the controller's active deals?
   - Are there accounts where introducing the partner could differentiate the pitch?
   - Note these as talking points for step 04.

---

## SUCCESS METRICS

- Account overlap table built with all three groups
- Every known account has an Internal Seller assigned
- Partner Rep column present and intentionally blank where unknown
- Group 3 exists with explicit invitation for partner to populate
- Co-sell patterns identified for talking points

## FAILURE MODES

| Failure | Action |
|---------|--------|
| CRM unavailable | Build the table from email threads, previous meeting notes, and the controller's knowledge. Ask the controller: "What are your top 5 accounts where {Partner} could add value?" Flag that CRM data is missing. |
| No known account overlap | This is valuable information. Note it: "No known overlap yet -- meeting objective should be discovery of mutual accounts." Populate Group 2 with controller's target accounts and leave Group 1/3 for discussion. |
| Partner's account list not available | Leave Group 3 mostly blank. Add a note: "Requesting {Partner}'s priority accounts during the meeting." This is expected -- getting the list IS part of the meeting's value. |
| Too many accounts (20+) | Prioritize. Top 10 for Group 1 (by revenue or activity), top 5 for Group 2 (by strategic value). Note the full list is available if needed. |

---

## NEXT STEP

Read fully and follow: `step-03-events-and-context.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
