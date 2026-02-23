---
name: partner-meeting-prep
description: Partner meeting prep (QBRs, co-sell reviews) - account overlap, mutual opportunities, events, and collaboration points
agent: chase
---

<!-- system:start -->
# Partner Meeting Prep Workflow

**Goal:** Walk into partner meetings with a clear picture of where accounts overlap, what's active, and what to propose for co-sell. The output is a collaboration document with intentional blanks for the partner to fill.

**Agent:** Chase -- Closer, Revenue, Pipeline & Client Strategy

**Architecture:** Sequential 4-step workflow. Identify the partner and meeting, map account overlap (the centerpiece), gather events and context, then assemble the final document. Minimal user interaction until the document is delivered.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### What Makes This Different from Client Meeting Prep

Partner meetings are NOT client meetings. The key differences:

| Dimension | Client Meeting Prep | Partner Meeting Prep |
|-----------|-------------------|---------------------|
| **Focus** | Selling to the client | Co-selling WITH the partner |
| **Centerpiece** | Account context + talking points | Account OVERLAP table |
| **Output** | Internal-only prep brief | Shareable collaboration document |
| **Blanks** | None -- fully populated | Intentional -- partner fills their side |
| **Columns** | Our team only | Our Seller + Partner Rep side by side |
| **Events** | Our events only | Both sides + joint opportunities |
| **Tone** | Competitive intelligence | Collaborative intelligence |

### Required Input

- **Who**: Partner company name (e.g., Confluent, Microsoft, AWS)
- **When**: Date and time of the meeting (if known, otherwise find it on calendar)

### Data Sources Required

| Source | What to Pull | Lookback | Access Method |
|--------|-------------|----------|---------------|
| Calendar | Meeting details, attendees, previous partner meetings | 2 weeks back + 4 weeks forward | M365 MCP |
| Email | Partner correspondence, account discussions, intro emails | 4 weeks | M365 MCP |
| CRM | Active accounts, pipeline, account owners, partner-tagged opportunities | Current | CRM API |
| Knowledge layer | Previous partner prep docs, meeting notes, relationship history | Most recent | Knowledge base API |
| Web | Partner's recent news, events, program updates | Current | Web search |
| Task management | Tasks related to partner, delegated follow-ups | Current | Task management API |

### Output

- Partner meeting prep doc saved to knowledge layer: `working directory/{Partner} - {YYYY-MM-DD}.md`
- Designed to be shared with the partner team so they can fill in their side
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Read fully and follow: `steps/step-01-identify-partner.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
