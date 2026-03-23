<!-- system:start -->
# Step 03: Update System — Write Review and Close the Day

## MANDATORY EXECUTION RULES

1. You MUST write the daily review file to `{project-root}/reviews/daily/YYYY-MM-DD.md`. The review is not done until it's persisted.
2. You MUST write a narrative journal entry to the knowledge system. Read `references/vault-conventions.md` for routing, format, and tagging. This is non-negotiable — the narrative write happens every session.
3. You MUST update the delegation tracker if any delegations were completed or if new blockers surfaced that should become delegations.
4. You MUST include the inbox count in the review file.
5. You MUST close with a summary. Short and sharp — Chief's style.
6. Do NOT ask the controller any more questions in this step. This is automated execution based on data from steps 01 and 02.
7. Do NOT modify quarterly objectives. If rock status needs updating, note it in the review file and flag it for the next weekly review.

---

## EXECUTION PROTOCOL

**Agent:** Chief
**Mode:** Automated — no controller interaction required
**Input:** Capture data from step 01, tomorrow data from step 02
**Output:** Daily review file written, delegation tracker updated, closing summary delivered

---

## CONTEXT BOUNDARIES

- All data needed is in working memory from steps 01 and 02.
- The daily review template at `{project-root}/reviews/daily/_template.md` is the target format. If the template exists, use it. If not, use the structure defined below.
- Write to the file system. This is the permanent record.

---

## YOUR TASK

### Sequence

1. **Build the daily review file content:**

   Use the template if it exists, otherwise use this structure:

   ```markdown
   # Daily Review — YYYY-MM-DD

   ## What Got Done
   - [item] (source: task-system/controller/meeting) [rock: Rock Name]
   - [item] ...

   ## What Didn't Get To
   - [item] — carry-forward | drop [rock: Rock Name]
   - [item] ...

   ## Blockers & Waiting On
   - [item] — waiting on [person] — action: delegation/nudge/escalation
   - [item] ...

   ## Morning Priority Scorecard
   - Priority 1: [hit/miss]
   - Priority 2: [hit/miss]
   - Priority 3: [hit/miss]
   - Score: X/3

   ## Tomorrow's Top 3
   1. [Priority] — [rock alignment]
   2. [Priority] — [rock alignment]
   3. [Priority] — [rock alignment]

   ## Calendar Prep Needed (Tomorrow)
   - [Meeting] — [type] — agent: [Chase/Shep/Chief]

   ## System State
   - Inbox: X items
   - Overdue delegations: X
   - Delegations due tomorrow: X
   - Corrections logged today: X (explicit: X, self-detected: X)

   ---
   *Review completed by Chief at HH:MM*
   ```

2. **Write the review file:**
   - Path: `{project-root}/reviews/daily/YYYY-MM-DD.md`
   - Create the `reviews/daily/` directory if it doesn't exist
   - If a file already exists for today (e.g., from a morning briefing), append the review sections — do not overwrite

3. **Update the delegation tracker:**
   - Read `{project-root}/delegations/tracker.md`
   - For any delegations the controller confirmed as completed in step 01: update status to "Done" and add completion date
   - For any new blockers from step 01 that should become delegations: add a new row with status "Waiting", today's date, and appropriate due date
   - Write the updated tracker back

4. **Pull error tracking count:**
   - Read `systems/error-tracking/error-log.json`
   - Count entries with today's date
   - Include the count in the System State section of the review file
   - If any threshold patterns were detected today, add a one-line note under Handoffs: "Rigby flagged a recurring [category] pattern — review at weekly."

5. **Check for handoffs:**
   - If any carry-forwards or blockers relate to goal drift → note: "Flag for Quinn at next review"
   - If any delegations went cold (overdue > 7 days) → note: "Flag for Shep to nudge"
   - If any content deadlines slipped → note: "Flag for Harper"
   - Record handoff notes in the review file under a `## Handoffs` section (only if there are handoffs)

6. **Write narrative journal entry to the knowledge system:**

   Read `references/vault-conventions.md` for the target folder, frontmatter format, tag taxonomy, and filename convention. Follow those conventions exactly.

   **Title:** Generate a descriptive title that captures the defining theme of the day — what this day was actually about. Do not use generic titles like "Daily Review" or "End of Day". Format: `YYYY-MM-DD <Descriptive Title>` (e.g., `2026-03-22 The Day the Pipeline Moved`, `2026-03-22 Three Meetings and a Decision That Changed the Quarter`).

   **Narrative:** Write a first-person prose account of the day. 3-5 paragraphs. Source from `capture_data` and `tomorrow_data` but do NOT list items — synthesize them into a coherent story of what happened and why it mattered. Cover:
   - What kind of day it actually was, as distinct from what was planned
   - What moved, what stalled, what surprised — and the why behind each
   - What is carrying forward and what that means for the current quarter
   - The emotional or strategic texture of the day: what does this day mean in context?

   Write in first person, past tense. Direct, honest, occasionally sharp. This entry is a permanent record, not a status report.

7. **Deliver the closing summary to the controller:**

   ```
   Day closed.

   [X] completed | [Y] carried forward | [Z] blocked
   Morning priorities: [X]/3
   Tomorrow's top 3 locked.
   Inbox: [N] items.
   [Any handoff flags, one line each]

   Get some rest. Tomorrow starts with [first meeting time or "a clear morning"].
   ```

---

## SUCCESS METRICS

- Daily review file written to `reviews/daily/YYYY-MM-DD.md`
- Narrative journal entry written to the knowledge system with descriptive title and first-person prose
- Delegation tracker updated for any completed or new delegations
- Inbox count recorded
- Morning priority scorecard included (if morning briefing existed)
- Tomorrow's top 3 persisted in the review file
- Closing summary delivered — concise, Chief's style

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Cannot write to file system | Deliver the review content to the controller inline. Note: "Could not write review file — printing here instead. Copy this to reviews/daily/ manually." |
| Delegation tracker missing or malformed | Skip delegation updates. Note: "Delegation tracker not found — skipping updates." |
| No data from step 01 or 02 | This should not happen. If it does: "Missing capture data. Run the daily review workflow from the beginning." Halt. |
| Template file doesn't exist | Use the built-in structure defined in this step. Proceed normally. |

---

## NEXT STEP

Load and execute `steps/step-04-root-audit.md` to complete the daily shutdown sequence.

The daily review file is now the input artifact for tomorrow's morning briefing workflow (step 01 of morning-briefing will look for it).
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
