---
status: not-started
started-at: ~
completed-at: ~
model: sonnet
---

<!-- system:start -->
# Step 04: Build the Partner Meeting Prep Document

## MANDATORY EXECUTION RULES

1. You MUST assemble the document using the exact structure specified below.
2. You MUST include intentional blanks throughout -- sections marked for the partner to fill. This is a collaboration tool, not a one-way briefing.
3. You MUST include the account overlap table as the centerpiece, with both Internal Seller and Partner Rep columns.
4. You MUST include the office/space offering section.
5. You MUST include discussion topics with open-ended questions for the partner.
6. You MUST save to the knowledge base at `working directory/{Partner} - {YYYY-MM-DD}.md`.
7. Do NOT fill in partner-side columns with guesses. If you don't know, leave it blank and mark it for the partner.
8. You MUST save the document with the partner's name slug in the filename and record its path. See Output Persistence (MANDATORY) below.

---

## EXECUTION PROTOCOL

**Agent:** Chase, spawned by the coordinator, never executed inline
**Input:** All working memory from steps 01-03
**Output:** Complete partner meeting prep document saved to knowledge layer

---

## CONTEXT BOUNDARIES

- This step is assembly and quality-check only. Do not make new data calls.
- The document is designed to be SHARED with the partner team. Write accordingly -- professional, collaborative tone.
- Intentional blanks are a feature, not a bug. The partner filling in their side is part of the value.
- Use Chase's voice for internal notes (talking points, strategy). Use neutral professional voice for the shareable sections.

---

## YOUR TASK

### Document Structure

Assemble the document using the exact structure in `references/document-structure.md` (read it before assembling).

### Assembly Rules

1. **Account overlap table is THE artifact.** Spend the most care here. Every account should have:
   - Account name (verified against CRM where possible)
   - Controller's seller name (never blank for known accounts)
   - Partner rep column (blank is fine -- that's the point)
   - Meaningful notes (not just "active" -- what's the status, what's the opportunity)

2. **Discussion topics must be specific.** Not "discuss accounts" but "What are you seeing at AT&T since their reorg?" Reference actual data from steps 01-03.

3. **Intentional blanks are marked clearly.** Use `{TBD - partner to fill}` for partner-side data. Use the phrase "Partner team: please add/share..." for sections they should populate.

4. **Events have specific collaboration framing.** Not "both attending SXSW" but "SXSW -- joint client dinner opportunity, we have 6 mutual accounts in Austin."

5. **Previous meeting action items carry forward.** If a prior prep doc exists, extract the action items and note which are complete vs. outstanding. Outstanding items become discussion topics.

### Quality Checks

Before saving, verify:

- [ ] Meeting details complete (date, time, location, contacts)
- [ ] Account tables include Seller column for every known account
- [ ] Partner Rep columns present and clearly marked for partner to fill
- [ ] Group 3 exists with explicit invitation for partner input
- [ ] Events include both sides' tables
- [ ] Office/space offering included with relevant locations
- [ ] Discussion topics reference actual data (not generic)
- [ ] Intentional blanks are clearly marked
- [ ] Previous meeting action items included (if applicable)
- [ ] Sensitive notes included where relevant
- [ ] No stale data -- account statuses verified against CRM if possible

### Save and Deliver

1. **Save to knowledge base:** `working directory/{Partner} - {YYYY-MM-DD}.md`
2. **Open in knowledge base:** present the file to the controller
3. **Present summary to the controller:**
   ```
   Your {Partner} meeting prep is ready.

   Key numbers:
   - {N} accounts in the overlap table ({X} active, {Y} target, {Z} for partner to fill)
   - {N} events identified for joint planning
   - {N} discussion topics queued

   {One sharp insight: the single most important thing to know going in.}
   ```
4. **If shareable version needed:** Generate PDF via `npx md-to-pdf`

### Output Persistence (MANDATORY)

The verifier for this step finds the saved document on disk (searching `outputs/`, `meetings/`, `accounts/`, and the repo root for a filename containing the partner's name slug), then validates its content. Record the save path in `state.yaml` `accumulated-context.output_file`. The saved document MUST contain these three exact section headers and use the intentional-blank marker `TBD - partner to fill` where partner-side data is left for them:

```yaml
# state.yaml -> accumulated-context
output_file: "meetings/{Partner} - {YYYY-MM-DD}.md"
```

Required section headers in the saved document:

- `## Meeting Details`
- `## Priority Accounts`
- `## Discussion Topics`

If the knowledge base save genuinely fails, deliver the document inline and record `delivery_note: "presented inline because knowledge base save failed"` in accumulated-context (the verifier accepts a documented inline fallback, but not a claimed save with no file).

---

## SUCCESS METRICS

- Document assembled in the exact structure above
- Account overlap table complete with all three groups
- Intentional blanks present and clearly marked
- Discussion topics specific and data-backed
- Document saved to knowledge base
- Summary delivered to controller with key numbers

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Thin data across all sections | Deliver what you have. Be honest: "Data is thin on this partner. The meeting itself is the discovery opportunity. Here's the framework -- it'll be more valuable after the conversation." |
| Knowledge base save fails | Present the document inline. Offer to retry save or output as file. |
| Previous prep doc can't be read | Omit the action items section. Note: "Prior prep doc found but unreadable. Recommend reviewing manually before the meeting." |

---

## HANDOFF

After the document is delivered:

- If an account needs deeper strategy (large deal, competitive situation) --> route to **Chase** account-strategy task
- If the partner relationship involves executive engagement (C-level introductions, sponsor alignment) --> flag for **Shep**
- If follow-up actions were identified (emails to send, meetings to schedule) --> route to **Chief** for task tracking
- If the meeting requires a presentation or deck --> hand to **Harper**

---

## NEXT STEP

The partner meeting prep document has been delivered. Update `state.yaml`: set `current-step: step-05` (do NOT set `status: complete` yet).

Then read fully and follow `step-05-adversarial-verify.md`, the terminal adversarial verification step. Ralph cross-checks the account-overlap and event claims against the actual CRM, calendar, and email records and records the `adversarial-verification` checkpoint. The workflow is marked complete only at the end of step-05. The controller reviews, adjusts, and optionally shares with the partner team before the meeting.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
