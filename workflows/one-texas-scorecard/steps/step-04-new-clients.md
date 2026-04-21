---
status: complete
started-at: "2026-04-21T15:31:00"
completed-at: "2026-04-21T15:31:15"
outputs:
  new_clients_captured: true
  most_recent_month: March
  dallas_logos: 4
  dallas_anchors: 0
  south_texas_logos: 4
  south_texas_anchors: 1
model: sonnet
---

<!-- system:start -->
# Step 04: New Clients

## MANDATORY EXECUTION RULES

1. You MUST execute the new-clients skill in full for both Dallas and South Texas.
2. You MUST hover the most recent month with data — the chart is cumulative YTD. Do not read
   a mid-year data point and report it as YTD if a later month is available.
3. You MUST count "Select Row" entries to determine logo/anchor totals. Do not estimate.
4. You MUST verify the page is at 71% zoom before using hardcoded coordinates. If zoom differs,
   confirm month via `Month Name [Month]` in the tooltip before recording values.
5. Do NOT conflate Logos and Anchors — they are separate counts with separate targets.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Enterprise Scorecard v4 Sales Momentum page (via Playwright MCP)
**Output:** Formatted new clients report stored in `accumulated-context.new_clients` in `state.yaml`

---

## CONTEXT BOUNDARIES

- One Texas scope: Dallas and South Texas (Austin + Houston). Never report all-Improving totals.
- New Logo = brand-new client relationship. New Anchor = new strategic/anchor engagement.
- South Texas = Austin + Houston selected simultaneously in the dropdown.
- Q1 targets (2026): Dallas Logo Q1=4, South Texas Logo Q1=4; both Anchor Q1=2.
- Chart coordinates confirmed at 71% zoom: Jan≈(340,525), Feb≈(380,515), Mar≈(415,515).
  Use `Month Name [Month]` in tooltip to verify the correct data point.

---

## YOUR TASK

### Sequence

1. **Execute new-clients skill** — read and follow `skills/new-clients/SKILL.md` in full.
   The skill covers:
   - Navigate to Sales Momentum page
   - Confirm 71% zoom from screenshot
   - Filter to Dallas via Promise-based dropdown evaluate, close with Escape
   - Hover most recent month, read tooltip DOM for "Select Row" entries and targets
   - Filter to South Texas (Austin + Houston), repeat tooltip read
   - Compile formatted report with gap to target

2. **Store output** — write the complete formatted new-clients report to `state.yaml`:
   ```yaml
   accumulated-context:
     new_clients: |
       [full formatted output from skill]
   ```

3. **Update step frontmatter**:
   ```yaml
   status: complete
   completed-at: [timestamp]
   outputs:
     new_clients_captured: true
     most_recent_month: [month name]
   ```

4. **Update workflow state**:
   ```yaml
   current-step: step-05-save-to-obsidian
   ```

---

## SUCCESS METRICS

- New Logos YTD count captured for Dallas and South Texas
- New Anchors YTD count captured for Dallas and South Texas
- Q1 targets recorded for both enterprises
- Gap to target calculated for logos and anchors
- Company names from tooltip listed for Dallas logos
- Full formatted output stored in accumulated-context

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Scorecard page fails to load | Retry once. If unavailable, note "New Clients data unavailable" in accumulated-context and proceed to step 05. |
| Dropdown evaluate returns 'popup never ready' | Retry the evaluate once. If still failing, surface to controller: "[Chase]: New Clients dropdown unresponsive. Manual intervention needed." |
| Tooltip returns null at March coordinates | Try February (380, 515) and January (340, 525). Check `Month Name` in tooltip to confirm month. |
| Zoom level differs from 71% | Note zoom level. Use `Month Name [Month]` to verify correct data point at adjusted coordinates. |

---

## NEXT STEP

Read fully and follow: `steps/step-05-save-to-obsidian.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
