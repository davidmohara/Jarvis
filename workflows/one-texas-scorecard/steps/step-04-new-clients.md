---
status: complete
started-at: "2026-07-14T00:08:00"
completed-at: "2026-07-14T00:09:00"
outputs:
  new_clients_captured: true
  cache_used: true
  data_through: May 2026
  dallas_logos: 6
  dallas_anchors: 1
  south_texas_logos: 1
  south_texas_anchors: 1
  one_texas_logos: 7
  one_texas_anchors: 2
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

2. **Store output** in `state.yaml`.

3. **Update step frontmatter** and **Update workflow state** to `step-05-save-to-obsidian`.

---

## STEP COMPLETION TRACKING

```bash
python3 systems/eval-harness/record-step.py one-texas-scorecard step-04-new-clients complete "${{frontmatter.started-at}}" "${{frontmatter.completed-at}}"
```

## NEXT STEP

Read fully and follow: `steps/step-05-save-to-obsidian.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
