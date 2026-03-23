<!-- system:start -->
# Step Auto: Autonomous Daily Review

## MANDATORY EXECUTION RULES

1. You MUST NOT ask the controller any questions. This step runs fully autonomously.
2. You MUST gather all available data before writing anything.
3. You MUST write the narrative to the knowledge system. Read `references/vault-conventions.md` for routing, format, and tagging. This is the only output — no local filesystem write.
4. You MUST NOT update the delegation tracker, OmniFocus, or any operational files. Read-only access to all sources.
5. You MUST be honest in the narrative about what the data can and cannot tell you. Do not fabricate intent, emotion, or context that isn't visible in the data.
6. You MUST deliver a brief confirmation to the controller after writing. One or two lines maximum.

---

## EXECUTION PROTOCOL

**Agent:** Chief
**Mode:** Fully autonomous — no controller interaction
**Input:** OmniFocus (osascript), M365 MCP calendar, delegation tracker, quarterly objectives, yesterday's daily review (if exists)
**Output:** Narrative journal entry written to the knowledge system

---

## YOUR TASK

### Sequence

1. **Pull OmniFocus data** via osascript (Bash tool):

   ```applescript
   tell application "OmniFocus"
     tell default document
       -- Tasks completed today
       set completedToday to every flattened task whose completion date >= (current date - 86400) and completed is true
       -- Overdue tasks
       set overdueItems to every flattened task whose due date < (current date) and completed is false
       -- Flagged incomplete
       set flaggedItems to every flattened task whose flagged is true and completed is false
       -- Inbox count
       set inboxCount to count of (inbox tasks whose completed is false)
     end tell
   end tell
   ```

   Capture: task names and projects for completions, overdue count and names, flagged count, inbox count.

2. **Pull yesterday's calendar** via M365 MCP (`outlook_calendar_search`):
   - Query for yesterday's date
   - Capture: meeting subjects, attendees, times, any cancellations

3. **Read supporting context** (read-only):
   - `{project-root}/delegations/tracker.md` — note any delegations that appear newly overdue
   - `{project-root}/context/quarterly-objectives.md` — current rocks for alignment framing
   - Yesterday's review at `{project-root}/reviews/daily/YYYY-MM-DD.md` (yesterday's date) — if it exists, pull the top 3 priorities that were set for yesterday

4. **Synthesize the narrative:**

   **Title:** Generate a descriptive title based on what the data shows dominated the day. Format: `YYYY-MM-DD <Descriptive Title>`. Examples: "The Day the Client Work Stacked Up", "A Day That Actually Moved the Needle", "Long on Meetings, Short on Execution", "Quiet Day, Good Progress". Be honest. If it was unremarkable, say so memorably. Do NOT use generic titles like "Daily Review" or "Auto Review."

   **Narrative:** Write 3-5 paragraphs in first person, past tense. Synthesize from all data above — do NOT list tasks, weave them into a coherent account of what the day looked like from the outside.

   - **Paragraph 1:** What the data shows this day was. What kind of day it appears to have been based on the calendar and OmniFocus completions. Connect what was on the calendar to the current quarter. Name the dominant thread.

   - **Paragraph 2:** What moved and what didn't. Which completions tied to quarterly rocks and which were operational. If tasks were overdue or the inbox grew, name it and what it signals about where attention went.

   - **Paragraph 3:** What is still open and what it means going forward. Delegation state, flagged items, any rocks showing no progress. Frame it as forward pressure, not a status list.

   - **Paragraph 4 (if meaningful):** Anything the data surfaced worth noting for the weekly review — a pattern, a risk, an anomaly. Only include if genuinely useful; omit if filler.

   **Close with one sentence** acknowledging this is a data-only baseline: *"This is the data's version of yesterday — the rest gets captured tonight."* (or a natural variant).

5. **Write the narrative** to the knowledge system per `references/vault-conventions.md`:
   - Tags: `content/daily-review` + `meta/timeline/YYYY/MM/DD`
   - Filename: `YYYY-MM-DD <Descriptive Title>.md`
   - Target folder and cross-linking: as specified in vault-conventions.md

6. **Deliver confirmation** (one or two lines):
   ```
   Auto review written: "{title}"
   [X] completed, [Y] still open, [Z] overdue. Interactive review available tonight.
   ```

---

## SUCCESS METRICS

- All available data sources pulled before writing
- Narrative written to knowledge system with descriptive title
- First person, past tense, prose only — no lists or tables in the narrative
- Honest about data limitations — no fabricated context
- Confirmation delivered

## FAILURE MODES

| Failure | Action |
|---------|--------|
| OmniFocus unavailable | Proceed with calendar and delegation data only. Note in narrative: "OmniFocus was unavailable — this account is based on the calendar alone." |
| Calendar unavailable | Proceed with OmniFocus data only. Note in narrative: "Calendar data was unavailable — this account is based on the task record alone." |
| Both OmniFocus and calendar unavailable | Write minimal narrative noting both sources failed. Pull rocks and delegation tracker directly. Note the data gap. Still write to knowledge system. |
| Knowledge system unavailable | Write the narrative to `{project-root}/reviews/daily/auto-YYYY-MM-DD.md` as fallback. Note routing failure in confirmation. |
| No completions and no meetings | Write the narrative honestly: it appears to have been a light or untracked day. Do not invent activity. |

---

## STEP COMPLETE

This is the only step for auto mode. No further steps to load.

The auto narrative is a data baseline. The interactive daily review (`/chief-review` without arguments) is the definitive record when the controller runs it.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
