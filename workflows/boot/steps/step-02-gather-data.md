---
status: complete
started-at: "2026-09-02T16:05:00Z"
completed-at: "2026-09-02T16:08:00Z"
outputs:
  phase2_status: "complete — all Phase 2 tasks executed. Calendar fresh (live re-pull, 33 events across 4-day window), OmniFocus fresh (live re-pull, 9 uncompleted), email fresh (live re-pull, 5 actionable). No blocking failures; Clay available (0 reminders/birthdays)."
  morning-briefing-steps-01-02: "completed — calendar and task data read from unified files (data/calendar-unified.json, data/omnifocus-unified.json)"
  task-g-72hr-lookahead: "completed — Sep 3-5 from calendar-unified.json: Sales & Recruiting Meeting / Sales Scrum (daily recurring), David/Robyn 1:1, Podcast Filming, Future Innovation Fal.Con keynotes, Golf Lesson (Sep 3); Dallas Virtual Coffee Chat, 1st Friday Executive Meeting, Friday Weekly Wrap-Up (Sep 4); Golf, Monthly Credit Card Reporting Reminder (Sep 5). Today (Sep 2) is the heaviest day of the window: external breakfast + Dallas Executive Huddle + AI Leaders Weekly + personal doctor appt + podcast topic discussion + YPO yDeep Dive + UTB call + haircut + Systemic Compliance scoping call + evening Cigars with the Stars."
  task-h-email-triage: "completed — 5 actionable messages from data/email-unified.json: Tomorrow's meeting (now today) from Systemic Compliance — Matt scored the document, ties directly to today's 3:30pm CDT Scoping call; Interviews in Dallas - Curtis availability? (Lee Carlson resume, awaiting go/no-go); Re: YPO Request (Jerry Jones Jr declined); YPO GOLD REX commitment form reminder; YPO Vision & Values Naples registration forward."
  task-i-jarvis-inbox: "nothing-to-surface — Jarvis folder empty (confirmed via live search)"
  task-j-reminders: "nothing-to-surface — data/reminders.json present but reminders array empty (0 due items)"
  omnifocus-status: "9 inbox items, all uncompleted/unassigned, none dated or flagged. Live re-pull via osascript."
  data-freshness: "Calendar fresh (live re-pull 16:05Z), OmniFocus fresh (live re-pull 16:06Z), Email fresh (live re-pull 16:00Z), Clay available (live re-pull 16:03Z, 0 reminders/birthdays)."
---

<!-- system:start -->
# Step 02: Gather Data (Phase 2)

## MANDATORY EXECUTION RULES

1. Fire ALL tasks simultaneously — this is a parallel phase. Do not run them sequentially.
2. Every task must report one of three outcomes: **completed**, **nothing to surface**, or **failed — [reason]**. Silence is not an option.
3. Do NOT proceed to step-03 until all tasks have returned a status.
4. Task J (Boot Reminders) always runs — even if `data/reminders.json` is empty, record `nothing-to-surface`.

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

### Task G: 72-Hour Look-Ahead

Read calendar data from `data/calendar-unified.json` (already pulled in step-01.5). Filter for days+1 to day+3. Capture:
- Meeting subjects, times, attendees
- Any client or partner meetings that will need prep
- Back-to-back blocks or heavy meeting days

**NOTE:** Do NOT call M365 directly. The unified pull in step-01.5 provides all calendar data for the 4-day window.

### Task H: Email Triage (flagged/time-sensitive only)

Read email from `data/email-unified.json` (already pulled by step-01.2). Filter for:
- Flagged messages
- Unread messages from the last 24 hours marked high priority
- Any message with an explicit deadline or time-sensitive subject line

Do NOT call M365 directly. The unified pull in step-01.2 provides all flagged/time-sensitive data.

### Task I: Jarvis Inbox

Run `skills/jarvis-inbox/SKILL.md` — read the skill file and execute as written. Surface any items requiring David's attention.

### Task J: Boot Reminders

Read `data/reminders.json`. Filter for entries where `trigger_date <= today`.

For each due reminder, capture:
- `id`
- `trigger_prompt` — the question to surface to David
- `routing.agent` — who handles the yes response
- `routing.action_prompt` — the self-contained execution prompt (store, don't execute yet)
- `on_no.snooze_days` and `on_no.message`

**Do NOT execute any action_prompt during data gather.** Just load the due reminders into accumulated-context. Execution happens in step-04 after David responds.

If the file is missing or empty: record `nothing-to-surface`.

---

## RECORDING RESULTS

After all tasks complete, record outcomes in state.yaml `accumulated-context`:

```yaml
accumulated-context:
  phase2:
    morning-briefing-steps-01-02: completed | nothing-to-surface | failed — [reason]
    task-g-72hr-lookahead: completed | nothing-to-surface | failed — [reason]
    task-h-email-triage: completed | nothing-to-surface | failed — [reason]
    task-i-jarvis-inbox: completed | nothing-to-surface | failed — [reason]
    task-j-reminders: completed ([N] due) | nothing-to-surface | failed — [reason]
```

Update step frontmatter: Set `status: complete`, `completed-at` with current timestamp, and `outputs.phase2_status` with a summary line (e.g. "complete — all 5 tasks executed, 0 failures" or "complete — 4 tasks completed, 1 skipped, 0 failures").

Update state.yaml: 
- Set `current-step: step-02.5-measure-phase2.md` (proceed to instrumentation/measurement step).
- Append Phase 2 outcomes to `accumulated-context.phase2`.

---

## SUCCESS METRICS

- All tasks fired simultaneously (not sequentially)
- Every task returned a status — no silent failures
- Results recorded in accumulated-context

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Morning briefing steps unavailable | Record failure. Proceed — briefing will be degraded but boot continues. |
| M365 calendar unavailable (Task G) | Record: "Task G: failed — M365 unavailable". Surface in briefing as "72-hour look-ahead unavailable." |
| M365 email unavailable (Task H) | Record: "Task H: failed — M365 unavailable". Note in briefing. |
| Jarvis inbox fails | Record: "Task I: failed — [reason]". Continue. |
| `data/reminders.json` missing | Record: "Task J: nothing-to-surface — file not found". Continue. Do not halt boot. |
| Reminders file malformed JSON | Record: "Task J: failed — JSON parse error". Continue. Do not halt boot. |

---

## NEXT STEP

Read fully and follow: `step-03-verify-phase2.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
