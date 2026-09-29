---
status: complete
started-at: "2026-09-28T16:32:00Z"
completed-at: "2026-09-28T16:38:00Z"
outputs:
  phase2_status: "complete — 5/5 tasks executed (morning-briefing 01-02, G, H, I, J), 0 degraded sources. record-step.py for morning-briefing declined (no standalone in-progress eval record; covered by boot's turn-level record). jarvis-inbox skill graded 100% PASS deterministic."
  completed_tasks: ["morning-briefing-01-02", "task-g-72hr-lookahead", "task-h-email-triage", "task-i-jarvis-inbox", "task-j-reminders"]
  morning-briefing-steps-01-02: "completed — calendar live (data/calendar-unified.json, 43 events; today 09-28 Monday pre-retreat: Dr Walters 8:45am, 1:1 McMichael 10:30am, Lone Star Gold board 1:30-3pm, GEHC internal 3pm, CRM-Contacts w/ Dodds 3:40pm, Shelly Kaiser YPO 4pm, SMU Cox MSAIB panel 5-6:30pm); task data LIVE (26 active, 18 inbox, 0 due today, 1 overdue, 0 flagged); 1 active delegation overdue 3 days (Steve Hall follow up -> Derek Nwamadi, due 09-25); Q3 rocks unsigned since 2026-07-30, quarter ends 09-30"
  task-g-72hr-lookahead: "completed — 09-29 Tue: Improving Company Retreat begins (all-day through 10-04), AA1550 DFW to LAS 8:50am CT (res LCLFFF), GEHC AI Routing deep dive 11am (tent), RTP AI workshop 2pm (tent), Gordon Ramsay Steak dinner 7pm Vegas (tent); 09-30 Wed: retreat day 2, yWhales yDeep Dive 10:30am-12pm (busy), GEHC weekly sync 10:30am (tent, duplicate invites), Vegas Leadership Celebration 7pm Vegas at Alexxa's; 10-01 Thu: President's Meeting Global Summit 9:45am-3pm Vegas at The LOFT at Cabo Wabo (busy)"
  task-h-email-triage: "completed — 19 messages in window (09-25 to 09-28), 7 actionable (YPO Tech Network Vermeer 30-min ask, helpdesk CRM ticket 69244 error text before Monday meeting, Vegas Retreat CorpLanta dress code HIGH, LSYPO waiver ACTION, Windsor Court NOLA upcoming stay, USAM Tips v2.1 Artifact invite, HRSouthwest Oct 11-13 connect)"
  task-i-jarvis-inbox: "nothing-to-surface — Jarvis inbox is empty (0 messages); skill-run signal written, deterministic grade 100% PASS"
  task-j-reminders: "nothing-to-surface — data/reminders.json empty (reminders array [])"
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
