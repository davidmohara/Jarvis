---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 02: Gather Data (Phase 2)

## MANDATORY EXECUTION RULES

1. Fire ALL tasks simultaneously — this is a parallel phase. Do not run them sequentially.
2. Task E (Plaud ingest) MUST spawn Knox as a background Agent running the full workflow. A manual directory listing of `~/Downloads/transcript-staging/` is NOT a substitute and does NOT satisfy this task.
3. Every task must report one of three outcomes: **completed**, **nothing to surface**, or **failed — [reason]**. Silence is not an option.
4. Do NOT proceed to step-03 until all tasks have returned a status.
5. Do NOT wait for Knox (Task E) — it is fire-and-forget. Record its spawn as completed and move on.

---

## EXECUTION PROTOCOL

**Agent:** Master
**Input:** Session context loaded in step-01, live data sources
**Output:** Gathered data from all Phase 2 tasks, recorded in accumulated-context

---

## CONTEXT BOUNDARIES

- Pull only what each task specifies. Do not expand scope mid-task.
- Task H (email triage) pulls flagged and time-sensitive messages only — not full inbox.
- Task G (72-hour look-ahead) covers the next 3 calendar days — not today (today is covered by morning briefing step-01).

---

## YOUR TASK

Fire all of the following simultaneously:

### Morning Briefing Steps 01-02

Run `workflows/morning-briefing/workflow.md` through step-02 (calendar gather + task gather). These two steps provide today's calendar data and task inbox status for the briefing synthesized in step-05.

### Task E: Plaud Ingest (fire-and-forget)

Spawn Knox as a background Agent with the following directive:

> "Knox — run `workflows/plaud-ingest/workflow.md` in full. Read the workflow, run the STATE CHECK, and execute all steps as written. This is a background task — do not wait for confirmation before starting."

Do NOT wait for Knox to return. Record outcome as: `Task E: spawned Knox — fire-and-forget`.

### Task G: 72-Hour Look-Ahead

Pull calendar events for the next 3 days via M365 MCP (`outlook_calendar_search`). Capture:
- Meeting subjects, times, attendees
- Any client or partner meetings that will need prep
- Back-to-back blocks or heavy meeting days

### Task H: Email Triage (flagged/time-sensitive only)

Pull email via M365 MCP (`outlook_email_search`). Filter for:
- Flagged messages
- Unread messages from the last 24 hours marked high priority
- Any message with an explicit deadline or time-sensitive subject line

Do NOT pull full inbox. Surface only what needs action today.

### Task I: Jarvis Inbox

Run `skills/jarvis-inbox/SKILL.md` — read the skill file and execute as written. Surface any items requiring David's attention.

---

## RECORDING RESULTS

After all tasks complete (except Knox, which is fire-and-forget), record outcomes in state.yaml `accumulated-context`:

```yaml
accumulated-context:
  phase2:
    morning-briefing-steps-01-02: completed | nothing-to-surface | failed — [reason]
    task-e-plaud: spawned Knox — fire-and-forget
    task-g-72hr-lookahead: completed | nothing-to-surface | failed — [reason]
    task-h-email-triage: completed | nothing-to-surface | failed — [reason]
    task-i-jarvis-inbox: completed | nothing-to-surface | failed — [reason]
```

Update step frontmatter: Set `status: complete` and `completed-at` with current timestamp.

Update state.yaml: Set `current-step: step-03-verify-phase2.md`.

---

## SUCCESS METRICS

- All tasks fired simultaneously (not sequentially)
- Knox spawned as a background Agent (not substituted with a directory listing)
- Every task returned a status — no silent failures
- Results recorded in accumulated-context

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Knox spawn fails | Record: "Task E: failed — Knox spawn error [reason]". Surface in step-03 manifest for Ralph to flag. |
| Morning briefing steps unavailable | Record failure. Proceed — briefing will be degraded but boot continues. |
| M365 calendar unavailable (Task G) | Record: "Task G: failed — M365 unavailable". Surface in briefing as "72-hour look-ahead unavailable." |
| M365 email unavailable (Task H) | Record: "Task H: failed — M365 unavailable". Note in briefing. |
| Jarvis inbox fails | Record: "Task I: failed — [reason]". Continue. |

---

## NEXT STEP

Read fully and follow: `step-03-verify-phase2.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
