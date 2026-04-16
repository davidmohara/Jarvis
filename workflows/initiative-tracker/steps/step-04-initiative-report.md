---
model: opus
---

<!-- system:start -->
# Step 04: Initiative Report

## MANDATORY EXECUTION RULES

1. Initiatives MUST be grouped by status: blocked first, then at-risk, then active, then planned, then completed/cancelled last.
2. Every blocked initiative MUST show: blocker description, blocker owner, and unblocking action.
3. Dependencies MUST be shown with their classification (blocking / informational / shared-resource).
4. Revenue-impacting initiatives with Chase context MUST include Chase's assessment.
5. End the report with "Initiatives needing a decision" — the short list of items that require executive action today.

---

## EXECUTION PROTOCOL

**Agent:** Quinn
**Input:** `initiative_registry`, `blocker_analysis`, `dependency_map`, `progress_trends`, `chase_context`
**Output:** Delivered initiative report

---

## YOUR TASK

### Sequence

1. **Deliver the initiative tracker report.**

   Format as follows:

   ---
   **Initiative Tracker — [Date]**
   Total: [N] initiatives | Blocked: [N] | At-Risk: [N] | Active: [N] | Planned: [N] | Completed: [N]

   ---
   **BLOCKED** ([N] initiatives)

   **[Initiative Title]**
   Owner: [name] | Due: [date] | Trend: [declining / stalled]
   Blocker: [blocker description]
   Blocker owner: [person/team responsible]
   Unblocking action: [specific action]
   [If cascade risk] Cascade impact: Blocking [N] downstream initiatives — [list]
   [If revenue-impacting] Revenue context (Chase): [affected deals, revenue at risk, recommended action]
   Dependencies: [initiative → type → this initiative]

   [Repeat for each blocked initiative]

   ---
   **AT-RISK** ([N] initiatives)

   **[Initiative Title]**
   Owner: [name] | Due: [date] | Trend: [declining / stalled]
   Status notes: [why at-risk — stale, approaching deadline, partial blocker]
   Recommended action: [specific next step]
   [If stale] Last activity: [N] days ago — needs update or status correction
   Dependencies: [if any]

   [Repeat for each at-risk initiative]

   ---
   **ACTIVE** ([N] initiatives)

   **[Initiative Title]**
   Owner: [name] | Due: [date] | Trend: [improving / stalled]
   Next action: [next action from initiative file]
   [If stale] Note: No activity in [N] days — may need follow-up

   [Repeat for active initiatives, condensed format]

   ---
   **PLANNED / COMPLETED / CANCELLED** ([N] initiatives)
   [Brief list only — title, owner, status]

   ---
   **Dependency Map**
   [For each initiative with dependencies, show the dependency and classification]

   ---
   **Initiatives needing a decision:**
   1. [Initiative name] — [one sentence on what decision is needed and why now]
   2. [Initiative name] — [one sentence]
   [Maximum 5 items — prioritize blocked with cascade risk and revenue-impacting]
   ---

2. **Progress trend display.**
   - Improving: brief positive note
   - Declining: flag with urgency
   - Stalled: flag for executive follow-up

---

## OUTPUT FORMAT RULES

- Blocked initiatives lead. Always. No executive should have to scroll to see what's stuck.
- Blocker owner must be named. "Unknown owner" is an acceptable answer but must be stated explicitly.
- Cascade risks get a dedicated line — the executive needs to see the blast radius.
- Revenue-impacting initiatives show Chase context inline, not in a separate section.
- "Initiatives needing a decision" is the call to action — keep it to 5 or fewer items.

## FAILURE MODES

| Failure | Action |
|---------|--------|
| No blocked or at-risk initiatives | Report honestly. Lead with active initiatives. Note the healthy state. |
| All initiatives are blocked | Deliver the report. Recommend executive scheduling a strategic unblocking session. |
| Initiative has no owner | Report "Owner: unassigned" — do not invent an owner. Flag it in "needing a decision." |
| Chase context was unavailable for revenue-impacting initiative | Note in the initiative entry: "Revenue context unavailable — Chase escalation failed. Manual pipeline review recommended." |

---

## WORKFLOW COMPLETE

Initiative tracker delivered.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
