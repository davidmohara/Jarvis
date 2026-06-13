---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 04: Synthesize Briefing

## MANDATORY EXECUTION RULES

1. You MUST deliver the briefing in the exact format specified below. No freestyle.
2. You MUST lead with the narrative — synthesize first, don't list.
3. You MUST write three paragraphs of prose before the calendar table. No bullet points or tables outside the calendar. The prose must reason about connections between data points, not extract and list them.
4. You MUST end with "What do you want to tackle first?"
5. Do NOT include data you don't have. If a source was unavailable, weave that gap into the narrative where relevant.

---

## EXECUTION PROTOCOL

**Agent:** Chief
**Input:** All working memory from steps 01-03
**Output:** Structured morning briefing delivered to the controller

---

## CONTEXT BOUNDARIES

- This step is synthesis only. Do not make new data calls.
- Use Chief's voice: direct, efficient, occasionally sharp. No filler. No pleasantries beyond the opening line.
- The briefing is the deliverable. It should stand alone — the controller should not need to ask follow-up questions to understand their day.

---

## YOUR TASK

### Briefing Format

Deliver the briefing using this structure exactly:

```
## Morning Briefing — {Day of Week}, {Month DD, YYYY}

{Paragraph 1 — The day's character. What kind of day is this? What's the dominant theme across
the calendar, priorities, and current rocks? Connect the meetings to the quarter's objectives.
Surface the most important tension or opportunity. 4-6 sentences. Do not list items — synthesize
them into a coherent picture. Weave in rock status, who's on the calendar, and what the day is
really about underneath the schedule.}

{Paragraph 2 — The execution reality. What must happen today and why it matters right now. Weave
together priority tasks due, overdue delegations, and rock alignment. Name the specific item most
likely to slip — who owns it, how late it is, what the consequence is. If yesterday's review was
missing, note it here as an accountability gap. 4-6 sentences.}

{Paragraph 3 — The sharp edge. What could go wrong, what needs watching, and what would make
today a success. Fold in inbox state if critical (>20 items), calendar overload if 3+ video calls
or back-to-back blocks with no buffer, and any flags demanding immediate attention. Recommend
running Chase or Shep prep where context is thin — name the meeting. End with one sentence that
sets the tone for how to attack the day.}

---

### Today's Calendar

| Time | Meeting | Context |
|------|---------|---------|
| {HH:MM} | {Subject} | {1-line: type, key attendee, prep note, or handoff recommendation} |
| ... | ... | ... |

{Warning line if back-to-back blocks with no buffer or 3+ video calls.}
{If no meetings today: "No meetings scheduled today. Open calendar."}

---

What do you want to tackle first?
```

### Synthesis Rules

1. **Prose reasoning, not extraction:**
   - Rocks, priority tasks, delegations, and flags all belong in the narrative paragraphs — not in separate sections.
   - Force yourself to reason about connections: why does this task matter today given what's on the calendar? Why is this delegation overdue significant right now?
   - If a day has nothing urgent: the narrative should say so clearly. "Clean calendar, nothing overdue, inbox under control — use the open blocks to push the [rock] forward."

2. **Calendar table is reference, not analysis:**
   - Keep context column to 1 line. The analysis belongs in the prose.
   - Chronological order always.
   - Flag prep recommendations inline: "Recommend Chase prep" or "Recommend Shep prep" in the context column.

3. **Handoff callouts** (embed in narrative or calendar context column):
   - Client meeting today with thin context → name it in paragraph 3, recommend Chase prep in context column
   - 1:1 today with thin context → recommend Shep prep in context column
   - Content deadline approaching → name it in paragraph 2
   - Goal drift visible → name it in paragraph 1, escalate to Quinn

4. **Nothing urgent is still a signal:**
   - A clear day with no overdue items and no flags is worth naming explicitly in the narrative. It's an opportunity, not a non-event.

---

## SUCCESS METRICS

- Three paragraphs of prose narrative delivered before the calendar table
- Narrative synthesizes connections between data points rather than listing them
- Calendar table present with 1-line context per meeting
- Handoff recommendations named in narrative or calendar context column
- Ends with "What do you want to tackle first?"

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Missing calendar data | Note in paragraph 3: "Calendar data unavailable — check manually before your first meeting." Show empty calendar table with that note. |
| Missing task data | Weave into paragraph 2: "Task system was unavailable — priorities are based on delegation tracker and rocks only." |
| All data sources failed | Deliver minimal briefing: read rocks and delegation tracker directly, write 3 paragraphs from that data alone, note all unavailable sources in paragraph 3. |

---

## WRITE OUTPUT FILE

**After delivering the briefing**, write a working memory file to `memory/working/` using this exact filename pattern:

```
morning-briefing-YYYY-MM-DD-HHmmss.md
```

where `YYYY-MM-DD-HHmmss` is the local date and time at the moment of writing (e.g., `morning-briefing-2026-05-25-071532.md`). Use the session start time from `state.yaml` if available; otherwise use current time.

The file **must** begin with this YAML frontmatter block (all fields required):

```yaml
---
type: working
task_id: "session"
session_id: "chief-{YYYY-MM-DD}-{HHmmss}"
agent-source: chief
created: {YYYY-MM-DD}T{HH:MM:SS}
expires: {YYYY+0 days, MM, DD+2}T{HH:MM:SS}
status: active
context: "Morning briefing — {YYYY-MM-DD}"
---
```

Field rules:
- `session_id`: `chief-` followed by the same timestamp used in the filename (e.g., `chief-2026-05-25-071532`)
- `created`: ISO 8601 local time, no Z suffix (e.g., `2026-05-25T07:15:32`)
- `expires`: `created` + exactly 2 days, same time (e.g., `2026-05-27T07:15:32`)
- `status`: always `active` when first written

After the frontmatter, include the full briefing body:

```
# Morning Briefing — {Day of Week}, {Month DD, YYYY}

## Data Sources
- Calendar (M365): {pulled successfully | unavailable}
- OmniFocus: {pulled successfully | unavailable}
- Clay: {pulled | unavailable | nothing to surface}
- Delegations tracker: {summary}

## Calendar Conflicts Surfaced
{List any back-to-back blocks, overload warnings, or "None"}

## Overdue Items Flagged
{List overdue tasks or delegations, or "None"}

## 72-Hour Look-Ahead Flags
{Any flags for the next 3 days from look-ahead scan, or "None surfaced"}

## Interruptions / Missing Data
{Any data sources that failed or returned no data, or "None"}

---

{Full briefing text exactly as delivered to the controller — all three narrative paragraphs, the calendar table, and the closing line}
```

This file is the durable record consumed by the eval harness assertions. Do not skip this write. Do not abbreviate the content. The filename timestamp pattern is mandatory — a date-only filename will fail the assertion.

---

## EVAL RECORD

**Before returning the briefing**, write an eval record for this run. This is mandatory — it feeds the dashboard and weekly review health check.

Determine status based on what actually happened:
- `success` — briefing delivered with all 3 paragraphs + calendar table
- `partial` — briefing delivered but one or more data sources failed (OmniFocus, calendar, Clay)
- `failure` — briefing could not be delivered

Run:
```bash
python3 systems/eval-harness/close-eval-record.py \
  --name morning-briefing \
  --type workflow \
  --agent chief \
  --status {success|partial|failure} \
  --trigger boot \
  --started "{session_started from state.yaml}" \
  --steps "step-01-gather-calendar,step-02-gather-tasks,step-03-meeting-context,step-04-synthesize-briefing"
```

If any data source failed, use `--status partial`. If the briefing was not delivered at all, use `--status failure`.

## WORKFLOW COMPLETE

**After writing the eval record**, write `state.yaml` in the workflow directory with `status: complete` and `current-step: step-04`. This is mandatory — do not skip it.

```yaml
workflow: morning-briefing
agent: chief
status: complete
current-step: step-04
```

The morning briefing has been delivered. The controller drives from here.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
