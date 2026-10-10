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

**Agent:** Chief, spawned by the coordinator, never executed inline in the coordinator's session.
**Mode:** Fully autonomous — no controller interaction
**Input:** OmniFocus (via the `omnifocus-data` skill), M365 MCP calendar, delegation tracker, quarterly objectives, yesterday's daily review (if exists)
**Output:** Narrative journal entry written to the knowledge system

---

## YOUR TASK

### Sequence

1. **Pull OmniFocus data** with the `omnifocus-data` skill (it uses osascript under the hood; do not hand-write the query):

   ```bash
   python3 skills/omnifocus-data/scripts/omnifocus_data.py counts --json
   ```

   Returns `inbox_uncompleted`, `flagged_uncompleted`, `overdue_uncompleted`, `completed_today`, `total_uncompleted`, `due_within_7`.

   For task-level detail (names and projects of overdue items), use `list --kind due`. Do NOT hand-write OmniFocus AppleScript in this step: the query logic, including the mandatory completed filter, lives in `skills/omnifocus-data/SKILL.md`.

   Capture: overdue count, flagged count, inbox count, tasks completed today.

2. **Pull yesterday's calendar** — attempt in sequence, stop at first success:

   **Route A — M365 MCP:**
   ```
   mcp__b8c41a14-7a9b-4ea5-ab12-933ee04bc52f__outlook_calendar_search
   query: yesterday's date range (start of day to end of day, local time)
   ```
   If this returns events → use them. If it returns an auth error, empty result on a day that had meetings, or times out → proceed to Route B.

   **Route B — Desktop Commander osascript:**
   ```applescript
   tell application "Calendar"
     set theDate to (current date) - 1 * days
     set startOfDay to theDate - (time of theDate)
     set endOfDay to startOfDay + (23 * hours) + (59 * minutes)
     set output to ""
     repeat with cal in calendars
       repeat with ev in (every event of cal whose start date >= startOfDay and start date <= endOfDay)
         set output to output & (summary of ev) & " | " & (start date of ev as string) & linefeed
       end repeat
     end repeat
     return output
   end tell
   ```
   Use `mcp__Control_your_Mac__osascript` to run this.

   Only after **both routes fail** should calendar be declared unavailable. If both fail, note: "Calendar data was unavailable — both M365 MCP and osascript routes failed." and proceed with OmniFocus data only.

   Capture: meeting subjects, attendees (M365 route), times, any cancellations.

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

7. **Adversarial verification (Stage 5 Phase 4A).** After the narrative is written, spawn **Ralph** with `workflows/daily-review-verification/workflow.md` to cross-check the narrative's completion claims against recorded state (OmniFocus counts, calendar events, delegation tracker). This is a separate spawn with a distinct lens; do not self-verify.

   Pass Ralph:
   ```
   Agent: ralph
   Workflow: workflows/daily-review-verification/workflow.md
   Manifest:
     review-file: "{narrative-path}"
     omnifocus-data: data/omnifocus-unified.json
     delegation-tracker: delegations/tracker.md
     run-date: <YYYY-MM-DD>
   Task: Cross-check the auto narrative's claims against recorded state and return your verdict table.
   ```

   Record the verdict via `guardrail-checkpoint.py` (checkpoint name `adversarial-verification`), mapping an all-clear verdict to `pass` and any unsupported claim to `flag`:
   ```bash
   python3 systems/eval-harness/guardrail-checkpoint.py daily-review adversarial-verification step-auto <pass|flag> "<one-line reason>"
   ```

   Write the verdict summary to `state.yaml` under `accumulated-context.adversarial-verification` (`verdict`, `result`, `findings`). If Ralph cannot be spawned, record `result: flag` with reason "adversarial verification unavailable, Ralph not spawnable" rather than skipping silently.

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
| Calendar unavailable | Only declare unavailable after both M365 MCP and osascript routes fail. If both fail, proceed with OmniFocus data only. Note in narrative: "Calendar data was unavailable — both M365 MCP and osascript routes failed." |
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
- `partial` — narrative written but one major source failed
- `failure` — both primary sources failed and no substantive narrative could be written

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

Follow `reference/post-step-protocol.md` (Working Memory Write). Filename: `daily-review-{YYYY-MM-DD}-{HHmmss}.md`; agent-source `chief`; compose the body from this step's output: the day's narrative and any flags (3-5 bullets, under 200 words).

**Working memory guard:** After writing, verify the file exists and is >200 bytes via Bash (`wc -c {path}`). If verification fails: retry the write once; if still failing, log `working-memory-status: failed` in `state.yaml` under `accumulated-context`. Do NOT silently skip. A failed working memory write must be visible in the state record.

## CLOSE STATE

After working memory is written (or its failure is logged), write the final `state.yaml`.

**Output file guard — required before writing `status: complete`:**
Verify the narrative output file exists and is >100 bytes:
```bash
wc -c "{narrative-path}"
```
- If the file exists and is >100 bytes → set `status: complete`
- If the file is missing or ≤100 bytes → set `status: partial` and log `output-guard: failed` in `accumulated-context`. Do NOT write `status: complete`. The workflow will be treated as partial on the next eval run.

```yaml
status: complete          # or "partial" if output guard failed — see above
current-step: step-auto
accumulated-context:
  # ... preserve all accumulated-context fields from the run ...
  narrative-path: "{path to output file, or null if missing}"
  output-guard: "{passed|failed}"
  working-memory-path: "{path to working memory file, or null if failed}"
  working-memory-status: "{written|failed}"
```

This write is mandatory. If `status: complete` is not written, the workflow will attempt to resume on the next run rather than starting fresh.

---
<!-- personal:start -->
<!-- personal:end -->
