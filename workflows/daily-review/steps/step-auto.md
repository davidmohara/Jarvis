---
status: complete
started-at: "2026-04-17T13:40:00"
completed-at: "2026-04-17T13:55:00"
outputs:
  narrative-title: "2026-04-16 New Account Energy, Alice Gets the Keys, and YPO Gold After Dark"
  narrative-path: "reviews/daily/auto-2026-04-16.md"
  routing-note: "Obsidian MCP disabled — written to local fallback"
  omnifocus-status: "unavailable (3 timeouts)"
  calendar-events: 12
model: sonnet
---

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
   - `{project-root}/memory/personal/quarterly-objectives.md` — current rocks for alignment framing
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

   **Minimum-output guard:** Immediately after writing, verify the file exists and is non-empty (>100 bytes). Use `ls -la` or `wc -c` via Bash. If the file is missing or empty:
   - Do NOT exit with `success` or `partial`
   - Write to the local fallback path: `{project-root}/reviews/daily/auto-YYYY-MM-DD.md`
   - If the fallback also fails, set `status: failure` in the eval record
   - This guard fires for both the Obsidian path and the local fallback path

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
| Knowledge system unavailable | Write the narrative to `{project-root}/reviews/daily/auto-YYYY-MM-DD.md` as fallback. Note routing failure in confirmation. Run minimum-output guard on the fallback path. |
| No completions and no meetings | Write the narrative honestly: it appears to have been a light or untracked day. Do not invent activity. Still write the file — a short honest entry is not a failure. |
| Output file missing after write attempt | Do not exit with success or partial. Retry the write (fallback path if primary failed). If both fail, set `status: failure` in the eval record and log the error in state.yaml. |
| Working memory write fails | Log `working-memory-status: failed` in state.yaml. Do not let this block the state.yaml `complete` write — a working memory failure is non-blocking but must be recorded. |

---

## EVAL RECORD

**Before closing**, write an eval record for this autonomous run.

Determine status:
- `success` — narrative written to knowledge system (or fallback file) with descriptive title
- `partial` — narrative written but one major source failed in a way that indicates a real problem (NOT headless calendar — see below)
- `failure` — both primary sources failed and no substantive narrative could be written

**Headless calendar rule:** When this step runs as a scheduled (headless) task — i.e., `trigger = scheduled` and there is no active interactive session — the M365 calendar connector will return unauthenticated. This is expected behavior, not a failure. Do NOT set `status: partial` solely because calendar was unavailable in a scheduled run. Instead:
- Set `calendar-status` in `accumulated-context` to `"unavailable — headless scheduled run (expected)"`
- Proceed with OmniFocus and delegation data only
- Set eval status to `success` if a substantive narrative was produced
- Only set `partial` if OmniFocus is also unavailable, or if calendar is unavailable in an *interactive* session where auth should be present

Run:
```bash
python3 systems/eval-harness/close-eval-record.py \
  --name daily-review \
  --type workflow \
  --agent chief \
  --status {success|partial|failure} \
  --trigger scheduled \
  --steps "step-auto"
```

## STEP COMPLETE

This is the only step for auto mode. No further steps to load.

The auto narrative is a data baseline. The interactive daily review (`/chief-review` without arguments) is the definitive record when the controller runs it.
<!-- system:end -->


## WRITE WORKING MEMORY

After the workflow output has been delivered, write a working memory file to `memory/working/` using this filename pattern:

```
daily-review-YYYY-MM-DD-HHmmss.md
```

where `YYYY-MM-DD-HHmmss` is the local date and time at the moment of writing. Use the session start time from `state.yaml` if available; otherwise use current time.

The file must begin with this YAML frontmatter (all fields required):

```yaml
---
type: working
task_id: "session"
session_id: "chief-{YYYY-MM-DD}-{HHmmss}"
agent-source: chief
created: {YYYY-MM-DD}T{HH:MM:SS}
expires: {YYYY-MM-DD+2}T{HH:MM:SS}
status: active
context: "Daily review — {YYYY-MM-DD}"
---
```

Body: 3-5 bullet points summarizing key outputs, decisions, and any flags from this run. Keep it under 200 words.

**Working memory guard:** After writing, verify the file exists and is >200 bytes via Bash (`wc -c {path}`). If verification fails:
- Retry the write once
- If still failing, log `working-memory-status: failed` in `state.yaml` under `accumulated-context`
- Do NOT silently skip — a failed working memory write must be visible in the state record

## CLOSE STATE

After working memory is written (or its failure is logged), write the final `state.yaml`:

```yaml
status: complete
current-step: step-auto
accumulated-context:
  # ... preserve all accumulated-context fields from the run ...
  narrative-path: "{path to output file}"
  working-memory-path: "{path to working memory file, or null if failed}"
  working-memory-status: "{written|failed}"
```

This write is mandatory. If `status: complete` is not written, the workflow will attempt to resume on the next run rather than starting fresh.

---
<!-- personal:start -->
<!-- personal:end -->
