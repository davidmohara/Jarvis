---
status: complete
started-at: "2026-09-18T17:04:30Z"
completed-at: "2026-09-18T17:08:00Z"
outputs:
  phase2_status: "complete — 5/5 tasks executed (morning-briefing 01-02, G, H, I, J), 0 degraded sources. record-step.py for morning-briefing declined (no standalone in-progress eval record; covered by boot's turn-level record)."
  completed_tasks: ["morning-briefing-01-02", "task-g-72hr-lookahead", "task-h-email-triage", "task-i-jarvis-inbox", "task-j-reminders"]
  morning-briefing-steps-01-02: "completed — calendar live (data/calendar-unified.json; today 09-18 = Houston retreat day 1, GEHC AI routing architecture discussion 12-1pm CT is the only client touch, rest tentative/personal); task data LIVE (data/omnifocus-unified.json status:available, 42 active tasks, 11 inbox, 5 due today, 0 overdue, 0 flagged); delegation tracker has 1 ACTIVE delegation (Steve Hall follow up -> Derek Nwamadi, due 2026-09-25, Waiting); Q3 rocks still draft pending David's review (last-updated 2026-07-30, ~7 weeks unsigned)"
  task-g-72hr-lookahead: "completed — 09-19 retreat (no timed events); 09-20 Texans vs Bengals Suite 870 (doors 10am CT, kickoff 12pm CT) then AA2438 IAH->DFW 7:03pm CT; 09-21 Monday packed: Prayer Call 8am, Sales & Recruiting 9:15am, Employee AI Usage policy sync (Amber Robinson) 9:30am OVERLAPS Sales Scrum 9:30am, Eagles Challenge golf 10:30am-4pm, GEHC internal check-in 3:30pm, dinner with Makena 6:30pm"
  task-h-email-triage: "completed — 17 messages in window, 10 actionable (Ashford & Remington Hotels escalation HIGH from Diana Stevens, UTB board book comments due TODAY, amazing race retreat list, Solace Texans suite ticket push, DCC Sigma Genetics breakfast 9/30, Fortium SIM Enclave follow-up, BofA AI session partnership fwd, World Affairs Council dinner 10/13, Legacy Club 4-member intake replies received, YPO nominee intake forms deadline)"
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
