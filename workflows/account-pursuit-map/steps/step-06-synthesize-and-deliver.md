---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 06: Synthesize, Sequence, and Write the Pursuit Map

## MANDATORY EXECUTION RULES

1. You MUST synthesize step 03's leadership map and step 05's referral network into a single **Contact Prioritization & Sequencing** table — priority rank, contact name/role, entry point (the actual mechanism to reach them), goal of that specific touch.
2. You MUST produce 2-3 named, mutually exclusive **entry plays / opportunity scenarios**, each with a specific entry pitch written as an actual quote, and end with an explicit recommendation of which to lead with and why.
3. You MUST branch the **phased strategic path** on step 01's engagement-shape determination: a 30/60/90-day plan for cold/lost re-entry, or a multi-year phased table (Access → Prove → Expand → Partner, with month ranges) for active-but-underleveraged. Do not produce both — produce the one that matches the determination, and do not default to the multi-year shape if the determination was cold/lost-re-entry.
4. You MUST order the **immediate next actions** list so that any gating action comes first — e.g., "pull the CRM loss record first, before any outreach" for cold/lost re-entry cases with an undocumented loss reason (per step 01).
5. You MUST state every genuine unknown explicitly in an **Open Items to Confirm** section. Never silently assume or assert an unconfirmed fact.
6. You MUST cite every external claim in a final **Sources** section, consistent with the format used in `accounts/Schwab/account-plan.md` and `accounts/Constellation Energy/account-plan.md`.
7. You MUST write the final document to `accounts/{Company}/account-plan.md`, creating the folder if it doesn't already exist. If a prior plan existed (per step 01), this is an update to the living document, not a parallel file.
8. Before drafting, you MUST re-read whichever of the two reference plans (`accounts/Schwab/account-plan.md` for active-but-underleveraged, `accounts/Constellation Energy/account-plan.md` for cold/lost-re-entry) matches step 01's determination, to match tone, depth, and section shape.
9. Do NOT add a dated-meeting-prep-style frontmatter or filename (this is a living strategic document per `agents/conventions.md`'s Output Naming Conventions — not a `meetings/YYYY-MM-DD-slug.md` artifact). Flag this to the controller as a naming-convention gap if `agents/conventions.md` has no explicit pattern for this file type (it does not, as of this workflow's build).

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** entity_anchor + engagement_shape + timing_trigger (step 01), strategic_priorities (step 02), capability_mapping + win_wire_story + competitive_note + leadership_profiles (step 03), icp_9box (step 04), referral_network + partner_network (step 05)
**Output:** Complete account pursuit map written to `accounts/{Company}/account-plan.md`, handed off to step 07 for HTML dashboard generation before final delivery to the controller

---

## CONTEXT BOUNDARIES

- This step does no new research — it synthesizes what steps 01-05 produced. If a gap exists (missing data, unresolved ambiguity), carry it into Open Items rather than filling it with invented content.
- The document structure should mirror the two reference examples' shape and tone (direct, cited, honest about gaps) — not a generic business-plan template.
- "Mutually exclusive" entry plays means the controller could pursue any one of them as the lead play, not that all three must run simultaneously — though the plan may note how a lead play opens the door to the others.

---

## YOUR TASK

### 1. Build the Contact Prioritization & Sequencing table

- Combine step 03's leadership profiles and step 05's referral network into one ranked table.
- Sequence by: warmest/most confirmed paths first, but weighted toward whoever unlocks the most access (e.g., an economic buyer reached via a confirmed warm path outranks a cold LinkedIn approach to a working-level contact).
- Format:
  ```
  | Priority | Contact | Entry Point | Goal |
  |----------|---------|--------------|------|
  | 1 | {Name, role} | {Actual mechanism — YPO event, named intro, existing sponsor, LinkedIn, cold outreach} | {What this specific touch should accomplish} |
  ```

### 2. Draft 2-3 entry plays / opportunity scenarios

- Each play should be named, grounded in a specific stated priority (step 02) and a specific Improving capability (step 03), and include a quotable entry pitch.
- Format per play:
  ```
  ### Option {A/B/C} — {Play name}

  {1-2 sentence description of the opportunity and why it fits}

  **Entry pitch:** "{Actual quotable pitch}"
  ```
- Close with an explicit recommendation: "**Recommendation:** Lead with Option {X} because {reasoning}."

### 3. Build the phased strategic path — branch on engagement shape

**If cold/lost-re-entry:**
```
## 30 / 60 / 90 Day Plan

**Next 30 days**
- {Specific actions, gated appropriately — e.g., pull CRM loss record first if unresolved}

**Days 31-60**
- {Specific actions}

**Days 61-90**
- {Specific actions}
```

**If active-but-underleveraged:**
```
## Multi-Year Strategic Path

| Phase | Timeline | Milestone |
|-------|----------|-----------|
| Access | Month 1-3 | {Specific milestone} |
| Prove | Month 3-6 | {Specific milestone} |
| Expand | Month 6-12 | {Specific milestone} |
| Partner | Year 2+ | {Specific milestone} |
```

Use step 01's `engagement_shape.determination` to select — do not build both.

### 4. Write the immediate next actions list

- Ordered, concrete, numbered. If step 01 flagged an undocumented loss reason, the first action must be pulling that CRM record before any outreach happens.
- Each action should be specific enough to execute without further research (who, what, and ideally by when).

### 5. Write the Open Items to Confirm section

- Pull forward every unresolved flag from steps 01-05: unresolved disambiguation, unconfirmed titles/reporting lines, unverified referral paths, missing loss reason, absent timing trigger, etc.
- State each as a plain, direct open question — not buried in prose elsewhere in the document.

### 6. Assemble and write the Sources section

- Every external URL cited anywhere in the document, deduplicated, in the same reference-list style as the two example plans.

### 7. Assemble the full document and write to `accounts/{Company}/account-plan.md`

Full document structure, in order:
```
# {Company} — Strategic Account Plan / Pursuit Map

**Improving | Prepared for: David O'Hara | {Month Year}**
**Classification: Internal — Business Development**

## Situation Summary
{Entity anchor, engagement shape, timing trigger — the "read this first" section}

## {Company}'s Stated Strategic Priorities
{step 02 themes, cited}

## Improving's Competitive Positioning
{step 03 capability mapping, win-wire story, competitive note}

## Leadership / Decision-Maker Map
{step 03 profiles}

## ICP & Account 9-Box
{step 04 — Potential/Realized scoring and 9-box placement, placed immediately after the org chart and before the referral/partner network}

## Referral / Relationship Network
{step 05 — kept separate from the leadership map and the ICP/9-box section above}

## Contact Prioritization & Sequencing
{step 05 task 1 table}

## Entry Plays / Opportunity Scenarios
{step 05 task 2}

## {30/60/90 Day Plan OR Multi-Year Strategic Path}
{step 05 task 3, branched}

## Immediate Next Actions
{step 05 task 4}

## Open Items to Confirm
{step 05 task 5}

## Sources
{step 05 task 6}
```

- Create `accounts/{Company}/` if it doesn't exist.
- If updating an existing plan (per step 01), preserve anything still accurate and clearly update anything that changed — do not silently discard prior content that's still true.

### 8. Hand off to Step 07

- Do not present this as final delivery or mark the workflow complete yet — the markdown document is an input to step 07, which generates the companion HTML dashboard.
- Update `workflows/account-pursuit-map/state.yaml`: `current-step: step-07-generate-dashboard`, keep `status: in-progress`. Carry the full `accumulated-context` forward (step 07 needs steps 01-06's outputs, not just the finished markdown file).

---

## SUCCESS METRICS

- Contact Prioritization & Sequencing table synthesizes both the leadership map and referral network into one sequenced view
- 2-3 mutually exclusive entry plays produced, each with a quotable pitch, ending in an explicit recommendation
- Phased strategic path shape matches step 01's engagement-shape determination (30/60/90 for cold/lost re-entry, multi-year phased table for active-but-underleveraged) — never both, never mismatched
- Immediate next actions ordered with any gating action first
- Every unresolved item from steps 01-05 surfaced in Open Items — nothing silently dropped
- Every external claim traceable to a cited source
- Document written to `accounts/{Company}/account-plan.md`
- No dated-meeting-prep frontmatter or filename convention applied to this living document

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Engagement shape from step 01 is ambiguous/unconfirmed | Do not guess a phased-path shape. Surface to the controller: "Engagement shape unclear — confirm active-but-underleveraged vs. cold/lost re-entry before finalizing the phased path." Draft the rest of the document and flag this section as pending. |
| Accounts folder for this company doesn't exist yet | Create `accounts/{Company}/` and write the file fresh. |
| Prior plan exists and this run found materially different facts (e.g., a title changed, an opportunity closed) | Update those facts in place; do not leave stale info standing alongside new info without reconciling. |
| Some steps 01-05 data is incomplete (e.g., referral network step never ran due to earlier abort) | Note gaps explicitly in Open Items rather than fabricating filler content for missing sections. |
| Naming convention gap (no existing pattern in `agents/conventions.md` for living strategic account documents) | Flag to the controller in the delivery message: "Note — `agents/conventions.md`'s Output Naming Conventions table has no entry for a living strategic account plan like this one; `accounts/{Company}/account-plan.md` was used to match the two existing reference examples, but this may be worth adding as a documented pattern." |

---

## NEXT STEP

Read fully and follow: `step-07-generate-dashboard.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
