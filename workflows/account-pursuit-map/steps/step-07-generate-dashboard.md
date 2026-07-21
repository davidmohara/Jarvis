---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 07: Generate the HTML Pursuit Dashboard

## MANDATORY EXECUTION RULES

1. You MUST use `workflows/account-pursuit-map/examples/pursuit-dashboard-template.html` as the structural and visual base. This is the fixed design system for this workflow's HTML output — do not redesign the palette, typography, or layout per account. Only the content changes.
2. You MUST populate every `{{PLACEHOLDER}}` token from the finalized `accounts/{Company}/account-plan.md` written in step 06. Never invent a figure to fill a gap — if a data point genuinely doesn't exist (e.g., no CRM revenue for a cold pursuit), adapt the stat tile's label/sub-line to say so honestly (see the template's status-strip comment) rather than fabricating a number.
3. You MUST branch the timeline block on step 01's engagement-shape determination, exactly as step 06 branched the markdown document: "Multi-Year Strategic Path" (4 phase rows: Access/Prove/Expand/Partner) for active-but-underleveraged, or "30 / 60 / 90 Day Plan" (3 rows: Next 30 days / Days 31-60 / Days 61-90) for cold/lost-re-entry — same `.timeline`/`.tl-row` markup either way, just different labels and content.
4. You MUST compute the 9-box SVG plot coordinates and shaded-cell position mathematically from step 04's Potential/Realized scores and zone, using the formula documented in the template's header comment. Do not eyeball the dot position.
5. You MUST reserve full `.profile-card` treatment only for the 3-5 most strategically relevant contacts from step 03 (same rule as the markdown document) — everyone else goes in the compact reference tables.
6. You MUST publish the result as a Claude Code Artifact (via the Artifact tool), not just save a local file — David needs a live link, not just a path.
7. You MUST also save the generated HTML to `accounts/{Company}/pursuit-dashboard.html` so a durable copy lives alongside `account-plan.md`.
8. Do NOT add sections, tabs, or design elements beyond what the template defines. If step 01-06 produced content that doesn't fit an existing template region, put it in the Notes tab's accordion (adding a new `<details class="note">` block follows the template's existing pattern) rather than inventing new page furniture.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** The complete, finalized `accounts/{Company}/account-plan.md` from step 06, plus the accumulated context from steps 01-06 (engagement_shape, icp_9box scores, leadership_profiles, referral_network, partner_network, entry plays, contact sequencing, phased path, next actions, open items, sources)
**Output:** A published Artifact (HTML dashboard) plus `accounts/{Company}/pursuit-dashboard.html`, delivered to the controller alongside the markdown document

---

## CONTEXT BOUNDARIES

- This step does no new research and changes no facts — it is a pure re-rendering of what steps 01-06 already produced and wrote to the markdown document. If step 06's document is incomplete or has open gaps, carry those gaps into the dashboard's Notes tab as-is; do not "fill in" anything here.
- The template's visual design (color tokens, type pairing, layout) is intentionally fixed across every run of this workflow so that every pursuit map reads as one consistent system. Do not introduce a new palette or typeface, even if it "feels more fitting" for a given company's brand — this dashboard is Improving's internal tool, not the client's.
- Reference the filled-in example at `accounts/Schwab/pursuit-dashboard.html` for what a fully populated dashboard looks like end to end.

---

## YOUR TASK

### 1. Read the template and the finalized document

- Read `workflows/account-pursuit-map/examples/pursuit-dashboard-template.html` in full — note every `{{PLACEHOLDER}}` and every block marked `REPEAT`.
- Read the just-written `accounts/{Company}/account-plan.md` in full.

### 2. Map document sections to template regions

| Template region | Source in `account-plan.md` |
|---|---|
| Status strip (5 tiles) | 9-box zone/scores (step 04), TTM revenue or cold-pursuit status, open pipeline, warmest contact (step 05/06), recommended play (step 06) |
| Pitch hero + secondary play cards | Entry Plays / Opportunity Scenarios section (step 06 task 2) — recommended play is the hero, the other 1-2 are the expandable secondary cards |
| Contact Priority Queue | Contact Prioritization & Sequencing table (step 06 task 1), one `.queue-row` per row, in order |
| 9-box SVG | ICP & Account 9-Box section (step 04) — compute plot coordinates per the template's documented formula |
| Timeline | Multi-Year Strategic Path or 30/60/90 Day Plan (step 06 task 3) — branch per engagement shape |
| Immediate Next Actions | step 06 task 4 list, one `.action-item` per action, gating action first |
| Profiles tab — cards | The 3-5 full narrative profiles (step 03) |
| Profiles tab — reference tables | Remaining C-suite and one-level-down compact listings (step 03) |
| Notes tab — Open Items | step 06 task 5 |
| Notes tab — 9-Box Methodology | step 04's factor breakdown and any workflow-issue flags |
| Notes tab — Strategic Priorities | step 02 themes |
| Notes tab — Competitive Positioning | step 03 capability mapping, win-wire story, competitive note |
| Notes tab — Referral & Partner Network Detail | step 05 |
| Notes tab — Sources | step 06 task 6, deduplicated |

### 3. Compute the 9-box plot

Using step 04's `potential_score` and `realized_score`:
```
cx = 30 + ((potential_score + 5) / 10) * 240
cy = 250 - ((realized_score  + 5) / 10) * 240
```
Shade the one 80x80 cell matching the assigned zone (cell x-origins: Low=30, Mid=110, High=190 for Potential; cell y-origins: High=10, Mid=90, Low=170 for Realized).

### 4. Fill the template

- Replace every `{{PLACEHOLDER}}` with real content from the mapped source. Do not leave any placeholder token in the output.
- Expand every block marked `REPEAT` to the actual number of rows/cards needed (contact queue rows, profile cards, table rows, action items, entry plays, sources) — remove the REPEAT comments themselves from the final output.
- If a stat tile has no honest value to show (e.g., cold pursuit with $0 revenue), follow the template's own guidance: relabel the tile and say so plainly rather than inventing a number.

### 5. Write and publish

- Write the completed HTML to `accounts/{Company}/pursuit-dashboard.html`.
- Publish it via the Artifact tool (title/description reflecting the company and pursuit; reuse a stable favicon choice — 🧭 was used for the first run — unless the controller has a preference).

### 6. Deliver

- Present both outputs to the controller: the markdown document path and the published Artifact link.
- Update `workflows/account-pursuit-map/state.yaml`: `status: complete`, `current-step: null`.

---

## SUCCESS METRICS

- Every `{{PLACEHOLDER}}` in the template replaced with real, sourced content — none left in the output
- Every `REPEAT` block expanded to the correct count with no invented rows
- 9-box dot and shaded cell mathematically correct per the documented formula
- Timeline block matches step 01's engagement-shape determination (never both shapes, never mismatched)
- Status strip never fabricates a figure — honest "no data" framing where appropriate
- Design system (palette, type, layout) unchanged from the template — no per-account redesign
- Dashboard published as a Claude Code Artifact AND saved to `accounts/{Company}/pursuit-dashboard.html`
- Both the markdown document and the dashboard link delivered to the controller together

## FAILURE MODES

| Failure | Action |
|---------|--------|
| A template placeholder has no corresponding data anywhere in steps 01-06 | Surface it in the Notes tab's Open Items rather than inventing content, and flag it to the controller in the delivery message |
| Engagement shape ambiguous (per step 06's own failure mode) | Render whichever timeline shape step 06 actually used in the markdown document; do not re-decide this here |
| Company has fewer than 3 full narrative profiles worth building | Render however many genuinely qualify (even 1-2) rather than padding the profile grid with thin cards |
| Artifact publish fails or is unavailable | Still write `accounts/{Company}/pursuit-dashboard.html` locally and tell the controller the file exists but wasn't published; do not silently skip the HTML output entirely |
| Template file itself is missing or has drifted from this step's expectations | Stop and flag to the controller — do not freehand a new design under time pressure; this template is the fixed system referenced by `agents/chase.md` |

---

## WRITE WORKING MEMORY

After both outputs have been delivered, write a working memory file to `memory/working/` using this filename pattern:

```
account-pursuit-map-YYYY-MM-DD-HHmmss.md
```

where `YYYY-MM-DD-HHmmss` is the local date and time at the moment of writing. Use the session start time from `state.yaml` if available; otherwise use current time.

The file must begin with this YAML frontmatter (all fields required):

```yaml
---
type: working
task_id: "session"
session_id: "chase-{YYYY-MM-DD}-{HHmmss}"
agent-source: chase
created: {YYYY-MM-DD}T{HH:MM:SS}
expires: {YYYY-MM-DD+2}T{HH:MM:SS}
status: active
context: "Account pursuit map — {Company} — {YYYY-MM-DD}"
---
```

Body: 3-5 bullet points summarizing the engagement shape determination, the recommended lead play, and any major open items. Keep it under 200 words.

---

## WORKFLOW COMPLETE

Account pursuit map delivered as both `accounts/{Company}/account-plan.md` and a published HTML dashboard (`accounts/{Company}/pursuit-dashboard.html` + Artifact link).

### Handoff Rules

| Condition | Route To | Action |
|-----------|----------|--------|
| Controller wants a deep-dive on an existing CRM account instead of a new pursuit | `account-strategy` workflow | Redirect — this workflow is for new-business pursuit, not existing-account deep-dives |
| Upcoming meeting scheduled with a contact from this plan | `client-meeting-prep` workflow | Chase runs client meeting prep using this pursuit map as account context |
| Entry play requires a proposal, deck, or one-pager | Harper (Communications) | Route content request with the recommended entry play and win-wire story |
| Relationship risk or recovery play needed | Shep (People & Leadership) | Flag for relationship strategy input |
| Pursuit requires executive sponsor engagement at Improving | Escalate to David directly | Present the plan and dashboard, ask for sponsor commitment |
| Dashboard reveals a template gap (a data point with no home in any region) | Flag to whoever owns this workflow | Note the gap so the template can be extended in a future revision, rather than silently reshaping the template per-run |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
