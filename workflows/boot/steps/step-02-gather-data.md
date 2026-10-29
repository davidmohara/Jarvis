---
status: complete
started-at: '2026-10-28T17:19:30Z'
completed-at: '2026-10-28T17:22:37Z'
---

<!-- system:start -->
# Step 02: Gather Data (Phase 2)

## MANDATORY EXECUTION RULES

1. You are a single bounded gather pass: read the data files listed below, filter them, record compact results, exit. Nothing else.
2. Every task must report one of three outcomes: **completed**, **nothing to surface**, or **failed — [reason]**. Silence is not an option.
3. Record results in `state.yaml` `accumulated-context` via the **Edit tool, never Bash** — the eval harness's per-step attribution keys on Edit/Write tool calls (this is exactly how the 2026-10-22 run lost its per-step records).
4. Record **compact summaries only** — counts, itemized lists, one-line-per-item status. Never paste raw JSON payloads into accumulated-context.
5. Do NOT call M365, OmniFocus, or Clay. Every data source was already pulled to `data/` by step-01.5 and step-01.2. Re-pulling here is the recorded failure mode, not thoroughness.
6. When all six tasks have a status and the state is updated, your mandate is DONE. Exit and return to the coordinator. Do NOT read, follow, or execute any other step file — the next-step chains were removed from steps 02-04 on 2026-10-22 because they let one long-lived boot subagent accumulate 500-720k input tokens per step for outputs of a few hundred tokens (eval-20261021T151330-QNQLC5: step-02 545,309 in / 628 out; eval-20261013T114019-Q5UJLE: 719,033 in / 4,291 out attributed across steps).

---

## EXECUTION PROTOCOL

**Agent:** dedicated gather subagent, spawned by the coordinator (Master) with a tight single-purpose brief. This step is a plain file-read-and-filter pass: it never loads the master persona (`agents/master.md`) or `SYSTEM.md`, never runs STATE CHECK, and never walks other steps.
**Input:** the unified data files in `data/` (written by step-01.5 and step-01.2), `delegations/tracker.md`, `memory/personal/quarterly-objectives.md`
**Output:** compact Phase 2 gather results in `state.yaml` `accumulated-context`

---

## CONTEXT BOUNDARIES

- Pull once, share many: all reads go to the unified files on disk. Zero API calls in this step.
- Morning-briefing steps 01-02 are borrowed here as **mechanical file reads** — their classification and filter rules are fully written in their step files, so this executor applies them directly to the unified data files. This is NOT a morning-briefing workflow run: no Watchtower invocation here, no step-03b guardrail, no Ralph verification. Those belong to a standalone morning-briefing run.
- The morning-briefing steps say "store results in working memory" — that instruction is overridden here: your working memory evaporates when you exit, so the structured results go into `state.yaml` `accumulated-context` (compact form) for step-05's synthesis.
- Task H pulls flagged and time-sensitive messages only — not full inbox.
- Task G covers days+1 to day+3 — not today (today is covered by the morning-briefing step-01 borrow).

---

## YOUR TASK

### Task A: Morning Briefing Steps 01-02 (today's calendar + tasks)

Read `workflows/morning-briefing/steps/step-01-gather-calendar.md` and `workflows/morning-briefing/steps/step-02-gather-tasks.md`, then apply their rules directly:

- **Calendar (mb step-01):** filter `data/calendar-unified.json` (written by step-01.5) to today's events; classify each by type; flag `needs_prep` meetings, back-to-back blocks, zero-buffer clusters. Do not call M365.
- **Tasks (mb step-02):** read `data/omnifocus-unified.json` (written by step-01.2) — inbox items, due today, overdue, flagged; read `delegations/tracker.md` for overdue/due-today/due-this-week delegations; read `memory/personal/quarterly-objectives.md` for rock names and one-line status.

Record the combined result compactly under `accumulated-context.phase2.morning-briefing-steps-01-02` as:

```yaml
calendar_data:
  date: YYYY-MM-DD
  meeting_count: N
  meetings:
    - time: HH:MM-HH:MM
      subject: ...
      type: client | 1:1 | team | partner | external | personal | recurring-skip
      attendees: [names] (count only, if 5+)
      needs_prep: true/false
      flags: [...]
  open_blocks: [...]
  warnings: [...]
task_data:
  inbox_count: N
  due_today: [{task, project}, ...]
  overdue: [{task, project, due_date}, ...]
  flagged: [{task, project}, ...]
delegation_data:
  overdue: [{task, owner, due_date}, ...]
  due_today: [{task, owner}, ...]
rocks:
  - name: ... status: ...
```

### Task G: 72-Hour Look-Ahead

Filter `data/calendar-unified.json` for day+1 through day+3 (already in the 4-day window). Capture meeting subjects, times, attendees (counts for 5+), any client or partner meetings that will need prep, and back-to-back or heavy meeting days. Record under `task-g-72hr-lookahead`.

### Task H: Email Triage (flagged/time-sensitive only)

Read `data/email-unified.json` (written by step-01.2 Pull A). Surface flagged messages, unread high-priority from the last 24 hours, and anything with an explicit deadline. Record under `task-h-email-triage` with sender, subject, and why it is time-sensitive — one line each.

### Task I: Jarvis Inbox

Read `data/jarvis-inbox-unified.json` (written by step-01.2 Pull D).
- Zero unread items → record `task-i-jarvis-inbox: nothing-to-surface`. Do not spawn anything.
- N > 0 unread items → spawn ONE subagent with a tight brief: `Process only the items listed in data/jarvis-inbox-unified.json per skills/jarvis-inbox/SKILL.md; return a compact list of items requiring David's attention (sender, subject, routing). Do not expand scope beyond those items.` Its return is what you record under `task-i-jarvis-inbox`.

### Task J: Boot Reminders

Read `data/reminders.json`. Filter for entries where `trigger_date <= today`. For each due reminder, capture `id`, `trigger_prompt`, `routing.agent`, `routing.action_prompt`, and `on_no` (snooze_days, message).

**Do NOT execute any action_prompt during data gather.** Just load the due reminders into accumulated-context. Execution happens after David responds.

If the file is missing or empty: record `nothing-to-surface`. If it is malformed JSON: record `failed — JSON parse error`.

---

## RECORDING RESULTS

After all tasks complete, record outcomes in state.yaml `accumulated-context` (Edit tool):

```yaml
accumulated-context:
  phase2:
    morning-briefing-steps-01-02: completed (N meetings, M tasks) | nothing-to-surface | failed — [reason]
    task-g-72hr-lookahead: completed — [N events daterange] | nothing-to-surface | failed — [reason]
    task-h-email-triage: completed — [N flagged, M time-sensitive] | nothing-to-surface | failed — [reason]
    task-i-jarvis-inbox: [items or "nothing-to-surface"] | failed — [reason]
    task-j-reminders: completed ([N] due: [one-line list]) | nothing-to-surface | failed — [reason]
  phase2_status: "complete — all 6 tasks executed, 0 failures" (or the degraded variant)
```

Then:
- **Update step frontmatter:** Set `status: complete` and `completed-at` to the real UTC clock time from `date -u +%Y-%m-%dT%H:%M:%SZ` (paste the exact output; never estimate or round) — Edit tool.
- **Update state.yaml:** Set `current-step: step-03-verify-phase2.md`.

---

## TOOL DISCIPLINE

- File reads go through the Read tool; state and frontmatter updates go through Edit/Write — never Bash redirection or heredocs.
- The only authorized spawn is Task I's conditional jarvis-inbox processing, and only when the unified file shows unread items.
- A missing data file is a recorded failure for that task, never a reason to call the API yourself: record `failed — backing file missing (degraded source carried from step-01.2)` and move on.

## SUCCESS METRICS

- Zero M365 / OmniFocus / Clay API calls (all data from unified files)
- All 6 tasks returned a status — no silent failures
- Compact results recorded in accumulated-context (no raw payloads)
- Subagent exited immediately after the state update — zero other step files read
- Expected input cost: tens of thousands of tokens, not hundreds of thousands

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `data/calendar-unified.json` missing (Task A/G) | Record: "failed — calendar file missing (step-01.5 degraded)". Briefing surfaces "72-hour look-ahead unavailable." |
| `data/email-unified.json` missing (Task H) | Record: "Task H: failed — email file missing (step-01.2 degraded)". Note in briefing. |
| OmniFocus file missing or `status: failed` | Record: "Task A (tasks): degraded — OmniFocus pull failed". Not a quiet empty task day. |
| Jarvis inbox file missing | Record: "Task I: failed — file not found". Continue. |
| `data/reminders.json` missing | Record: "Task J: nothing-to-surface — file not found". Continue. Do not halt boot. |
| Reminders file malformed JSON | Record: "Task J: failed — JSON parse error". Continue. Do not halt boot. |
| Delegation tracker / quarterly objectives missing | Record the absence in `delegation_data`/`rocks`. Continue. |

---

## RETURN TO COORDINATOR

This is the END of your mandate. Do not read `step-03-verify-phase2.md` or any other step file — the coordinator spawns the dedicated verify subagent for step-03 after you return. Your final message is a short status report: one line per task (A, G, H, I, J) with its outcome, plus any failure worth surfacing. Then stop.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
