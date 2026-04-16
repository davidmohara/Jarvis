---
name: leadership-prep
description: Leadership prep — build tailored materials for board meetings, quarterly reviews, and town halls with cross-domain context aggregation
agent: quinn
model: opus
---

<!-- system:start -->
# Leadership Prep Workflow

**Goal:** Build authoritative, audience-tailored prep materials for leadership events. No generic summaries. Pull real data cross-domain, surface the risks that matter, and give the executive exactly what they need to command the room.

**Agent:** Quinn — Strategist

**Architecture:** Sequential 4-step workflow. Analyze event context → aggregate cross-domain data → generate materials → optionally hand off to Harper for deck creation.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Event Types and Content Emphasis

| Event Type | Audience | Emphasis |
|------------|----------|----------|
| `board-meeting` | Board of Directors | Metrics, risks, strategic direction, financial performance |
| `quarterly-review` | Leadership team | Progress against rocks, blockers, initiative updates, adjustments |
| `town-hall` | Entire organization | Narrative, wins, priorities, culture, forward vision |

### Data Sources by Domain

| Agent | Domain | What Quinn Pulls |
|-------|--------|-----------------|
| Quinn (self) | Strategy | Rock status, initiative tracker, goal progress |
| Chase | Revenue | Pipeline metrics, ARR, top deals, revenue forecast |
| Shep | People | Team health, open roles, delegation status, org highlights |
| Chief | Operations | Key operational wins, blockers, calendar highlights |

### Cross-Domain Conflict Rule

When data from different agents conflicts (e.g., Chase says pipeline is healthy, Quinn's initiative tracker shows a revenue rock is blocked):
- Present BOTH data points
- Add a note: "Data discrepancy — [Agent A] reports [X], [Agent B] reports [Y]. Recommend resolving before the meeting."

### Harper Handoff Trigger

Trigger Harper handoff when:
- Executive requests a formatted presentation, OR
- Event type is `board-meeting` (default: board meetings warrant a polished deck)
- Use cross-agent handoff contract per shared-definitions.md#Defined Handoff Patterns (Quinn → Harper)
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Read fully and follow: `steps/step-01-event-context.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
