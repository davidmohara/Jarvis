# SOP: Partner Meeting Prep

**Scope**: External partner meetings (Confluent, Microsoft, AWS, etc.) - QBRs, co-sell alignment, intro presentations, and joint planning sessions. Not for internal Improving 1:1s.

**Trigger**: David has an upcoming partner meeting. Either requested explicitly or identified during daily/weekly prep.

**Output**: A one-pager saved to `zzClaude/Cowork/{Partner} - {YYYY-MM-DD}.md` in Obsidian.

**Reference Example**: `meetings/Confluent_QBR_Meeting_Prep.docx` (Feb 12, 2026 - Confluent TOLA QBR)

---

## Step 1: Identify the Meeting

Gather from calendar, email, or David:
- **Partner**: Company name and practice area
- **When**: Date, time, duration
- **Where**: Location / Teams / hybrid
- **Format**: QBR, intro presentation, co-sell planning, lunch & learn, etc.
- **Partner Host**: Name, title, email
- **Partner CC**: Additional partner contacts

## Step 2: Gather Raw Data

Pull from all available sources:

| Source | Method | What to Look For |
|--------|--------|-------------------|
| Email threads | Bridge → Desktop (M365 MCP) | Partner correspondence, account discussions, intro emails |
| Calendar | Bridge → Desktop (M365 MCP) | Previous meetings, upcoming shared events |
| Teams messages | Bridge → Desktop (M365 MCP) | Chat threads with Ehren, Nada, Lowell, or partner contacts |
| OmniFocus | osascript (Code) | Tasks related to partner, delegated follow-ups |
| Obsidian vault | MCP (Code) | Previous partner prep docs, project notes |
| CRM / Account data | Bridge → Desktop (Chrome) | Active accounts, pipeline, account owners |
| Partner's account list | Email or shared doc | Their target/active accounts for overlap analysis |

**Key data to collect:**
- Improving's active accounts in the partner's geography/vertical
- Partner's account list (request from Ehren/Nada if not already provided)
- Overlapping accounts where both have relationships
- Improving's target accounts where partner could provide intro
- Recent partner interactions (who from Improving has met with them, when, outcomes)

## Step 3: Assemble the One-Pager

Use this structure:

```markdown
# {Partner} {Meeting Type} – {Region/Scope}
**Meeting Prep – One-Pager**

## Meeting Details

| | |
|---|---|
| **Date** | {Day}, {Month DD, YYYY} |
| **Time** | {Time} {Timezone} |
| **Location** | {Venue / Teams link} |
| **Format** | {QBR, intro presentation, co-sell planning, etc.} |
| **Partner Host** | {Name, Title} ({email}) |
| **Partner CC** | {Name} ({email}) |

## Improving Attendees & Roles

| Name | Title | Presenting On |
|------|-------|---------------|
| David O'Hara | Regional Director, Texas | Regional client coverage & account strategy |
| {Name} | {Title} | {Role in meeting} |

## Improving Presence & Resources

Improving maintains offices and teams across Texas that are available
for joint events, workshops, and co-working:

| Location | Office | Available For |
|----------|--------|---------------|
| Dallas | Addison office | Workshops, lunch & learns, co-working, client events |
| Houston | Houston office | Same |
| {Other geographies as relevant} | | |

**We're happy to host partner events, joint workshops, or client meetings
at any of our locations.**

## Priority Accounts

### Group 1: Active Relationships (Joint Opportunity)

Accounts where Improving has existing engagement and can drive joint impact
with {Partner}:

| Account | Improving Seller | Partner Rep | Notes |
|---------|-----------------|-------------|-------|
| {Account} | {AE/VP name} | {TBD - partner to fill} | {Summary: relationship status, opportunity, key contacts} |

### Group 2: Target Accounts (Joint Pursuit)

Accounts Improving is actively pursuing where {Partner} could accelerate access:

| Account | Improving Seller | Partner Rep | Notes |
|---------|-----------------|-------------|-------|
| {Account} | {AE/VP name} | {TBD - partner to fill} | {Summary: pursuit status, what would help} |

### Group 3: Partner Accounts (Improving Can Help)

Accounts where {Partner} has relationships and Improving can add value:

| Account | Improving Seller | Partner Rep | Notes |
|---------|-----------------|-------------|-------|
| {TBD - partner to fill} | {TBD} | {Partner rep} | {TBD - partner to fill} |

## Upcoming Events

Events where joint presence, co-sponsorship, or client invitations could
create value. **Partner team: please add your events.**

### Improving Events

| Event | Date | Location | Opportunity for {Partner} |
|-------|------|----------|---------------------------|
| {e.g., Executive AI Workshop} | {Date} | {City} | {Co-present, invite clients, sponsor, etc.} |

### {Partner} Events

| Event | Date | Location | Opportunity for Improving |
|-------|------|----------|---------------------------|
| {TBD - partner to fill} | | | |

### Industry Events (Both Attending)

| Event | Date | Location | Notes |
|-------|------|----------|-------|
| {e.g., SXSW, FABCON} | {Date} | {City} | {Joint plans, booth sharing, client dinners, etc.} |

## Background & Next Steps

- {How the relationship started, key milestones}
- {Outcome of previous meetings}
- {Specific follow-ups and owners}
- {Open asks in either direction}

## Talking Points

1. {Specific topic with context - not just "discuss X"}

## Important Notes

{Sensitive context: personnel changes, losses, org changes,
relationship dynamics to be aware of}
```

## Step 4: Account Overlap Analysis

This is the most valuable part of the prep. For each account:

1. **Check CRM** for Improving's active engagement, pipeline, and AE ownership
2. **Cross-reference partner's account list** (if provided) against Improving's active and target accounts
3. **Leave Partner Rep column blank** for the partner team to fill in during or after the meeting
4. **Leave Group 3 mostly blank** - this is for the partner to populate with their accounts where Improving could help
5. **Include Improving Seller** for every account where we have one - the partner needs to know who to coordinate with

## Step 5: Populate Events Section

1. Pull Improving's upcoming events from `identity/MISSION_CONTROL.md` and calendar
2. Filter to events relevant to the partner's geography, vertical, or interest
3. Include industry events both parties might attend (SXSW, FABCON, Convergence, etc.)
4. Leave the partner events table mostly empty - explicitly ask them to fill it in
5. Frame each event with a specific collaboration opportunity (not just "attend together")

## Step 6: Improving Space Offer

Check which Improving offices are in the partner's territory and include:
- Office locations with capacity for events
- Willingness to host joint workshops, lunch & learns, client events
- Available tech/facilities (presentation rooms, etc.)

This is a differentiator - most partners don't offer physical space.

## Step 7: Quality Checks

Before saving, verify:

- [ ] Meeting details are complete (date, time, location, contacts)
- [ ] Account tables include Improving Seller column for every known account
- [ ] Partner Rep columns are present and clearly marked for partner to fill
- [ ] Active relationships include specific notes (key contacts, opportunity, status)
- [ ] Target accounts include what would help (intro, reference, joint pitch)
- [ ] Group 3 exists and is clearly marked for partner input
- [ ] Events section includes both Improving and partner tables
- [ ] Improving office/space offer is included with relevant locations
- [ ] Background section captures relationship history and momentum
- [ ] Talking points reference actual data
- [ ] Sensitive notes are included where relevant (personnel, org changes)
- [ ] No stale data - verify account statuses against CRM if possible

## Step 8: Save and Notify

1. Save to Obsidian: `zzClaude/Cowork/{Partner} - {YYYY-MM-DD}.md`
2. Open in Obsidian: `show_file_in_obsidian`
3. Tell David: "Your {Partner} meeting prep is ready. {One-line summary of the key accounts or talking point}."
4. If David needs a shareable version: generate PDF via `npx md-to-pdf`

---

## Key Principles

- **The one-pager is a collaboration tool, not just prep** - it's designed to be shared with the partner team so they can fill in their side (reps, accounts, events)
- **Improving Seller + Partner Rep pairing is the goal** - every account should have both sides identified so coordination can start
- **Space is a differentiator** - always offer Improving's offices for joint events
- **Events are a forcing function** - upcoming events create urgency and natural collaboration points
- **Leave intentional blanks** - the partner filling in gaps is part of the value

---

## Changelog

| Date | Change |
|------|--------|
| 2026-02-13 | Initial SOP created from Confluent TOLA QBR example (Feb 12, 2026) |
