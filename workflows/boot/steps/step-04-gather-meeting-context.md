---
status: complete
completed-at: '2026-10-29T14:04:21Z'
---

<!-- system:start -->
# Step 04: Gather Meeting Context (Phase 3)

## MANDATORY EXECUTION RULES

1. You MUST gather context for every meeting flagged `needs_prep` in step-02's `calendar_data` (in state.yaml `accumulated-context`). Do not synthesize the briefing without meeting context.
2. You MUST check Clay reminders and birthdays. This is not optional — it is a standing controller requirement.
3. Clay data comes from `data/clay-reminders-unified.json` (pulled by step-01.2 Pull C, next-7-days window). Do NOT call Clay MCP again — the unified pull already covers this step's 7-day range.
4. Record compact results via the **Edit tool, never Bash** — the eval harness's per-step attribution keys on Edit/Write tool calls.
5. This step never loads the master persona (`agents/master.md`) or `SYSTEM.md`, never runs STATE CHECK, and never walks other steps. The next-step chain was removed on 2026-10-22 because it let one long-lived boot subagent carry ~531k input tokens into this step for a 1,354-token output (eval-20261021T151330-QNQLC5).

---

## CONTEXT BUDGET (hard limits)

The 2026-10-29 run cost **2,099,878 input tokens in 31 turns** — 4x the 2026-10-28 run (505,639) for the same compact `phase3` output. The driver was not search payload size; it was five **full-body `vault_read` calls** on long transcript notes (13K, 9K, 10K and 5K tokens apiece) that permanently inflated the context every later turn re-sent. Three of those notes were then re-read a second time with `limit: 1` after the first read had already blown the budget. Enforce all of the following:

- **Never `vault_read` a full note body.** Pass `target` + `targetType: heading` (e.g. `"Summary"`) or `limit` (≤ 60 lines). A `vault_read` with no `target`/`limit` is a protocol violation in this step.
- **`search_simple` `contextLength` ≤ 40.** Use `search_query` with a path/`regexp` filter to narrow before reading. Treat a result set larger than ~10 hits as a signal to tighten the query, not to read wider.
- **At most 2 notes per meeting**, most-recent-first. The goal is "is there anything here?", not "summarize the history".
- **No duplicate reads.** If a read already returned a body, extract the line you need from what you have. Do not re-read the same path with a different `limit`/`target` in the same run.
- **Off-mandate reads are forbidden:** `systems/eval-harness/**`, `~/.claude/projects/**` transcripts, `.jsonl` files, and anything under `runs/`. On 2026-10-29 this executor spent turns inspecting harness transcripts for no output.
- **Working context ceiling: ~45K tokens.** If the accumulated conversation is approaching it, stop reading and write what you have. A partly-informed `prep_status: needs-prep` flag is a better outcome than a complete one that costs 2M tokens.

---

## EXECUTION PROTOCOL

**Agent:** dedicated meeting-context subagent, spawned by the coordinator (Master) with a tight single-purpose brief.
**Input:** `accumulated-context` from state.yaml (step-02's calendar_data with `needs_prep` flags), `data/clay-reminders-unified.json`, identity files, knowledge base
**Output:** Meeting prep context and Clay reminders/birthdays added to `accumulated-context`

---

## CONTEXT BOUNDARIES

- Morning-briefing step-03 is borrowed here as a **mechanical gather pass** — its rules are fully written in its step file, so this executor applies them directly. This is NOT a morning-briefing workflow run: no Watchtower invocation (Watchtower no longer runs as part of boot; it runs via the standalone morning-briefing workflow or on demand), no step-03b guardrail, no Ralph verification. Those belong to a standalone morning-briefing run.
- The morning-briefing step says "store results in working memory" — overridden here: results go into `state.yaml` `accumulated-context` (compact form) because your working memory evaporates when you exit.
- Context gathering is read-only: do not create, update, or modify any files (state.yaml accumulated-context is the only write).
- For client meetings pull account/person context but do not do full Chase-level prep; for 1:1s pull recent notes but not full Shep-level prep. Flag that Chase/Shep should run if deep prep is needed.
- Spend at most ~30 seconds of processing per meeting. Grab what is available and move on.
- Do not surface Clay data to the controller in this step — it is incorporated into the briefing in step-05.

---

## YOUR TASK

1. **Read the flagged meetings.** Open `workflows/boot/state.yaml` and read `accumulated-context.phase2.morning-briefing-steps-01-02.calendar_data`. Every meeting with `needs_prep: true` gets a context lookup.

2. **Run morning-briefing step-03's gather rules directly.** Read `workflows/morning-briefing/steps/step-03-gather-context.md` and apply its sequence:
   - Read identity context: `identity/MEMORY.md`, `identity/RESPONSIBILITIES.md`, `identity/MISSION_CONTROL.md` (key people, relationship map, active projects).
   - For each `needs_prep` meeting: search the knowledge base (Obsidian MCP) by attendee names and by meeting subject/account — pull the most recent relevant note, not all history; check `delegations/tracker.md` for open items involving attendees; classify prep urgency `ready | needs-prep | low-context`. Apply the CONTEXT BUDGET limits above: `search_simple` `contextLength` ≤ 40, `vault_read` only with `target`/`targetType: heading` or `limit` ≤ 60, at most 2 notes per meeting, no duplicate reads.
   - Check yesterday's daily review: `reviews/daily/{yesterday}.md` — completed or missing; if present, pull tomorrow's top 3 if listed.

3. **Check Clay from the unified file.** Read `data/clay-reminders-unified.json`:
   - Upcoming reminders (next 7 days): name/date/description
   - Upcoming birthdays (next 7 days): name/date, relationship context
   - If the pull reported Clay unavailable: record "Clay unavailable — carried from step-01.2". Do not re-pull and do not treat it as a fresh failure.

4. **Record results in accumulated-context** (Edit tool):
   ```yaml
   accumulated-context:
     phase3:
       meeting_context:
         - meeting: ...
           attendees: [...]
           context_found: [one-line summaries]
           open_items: [...]
           prep_status: ready | needs-prep | low-context
       system_status:
         yesterday_review: completed | missing
         yesterday_top_3: [...] | null
       morning-briefing-step-03: completed ([N meetings with context]) | nothing-to-surface | failed — [reason]
       clay-reminders: [compact list or "none"]
       clay-birthdays: [compact list or "none"]
     meetings_found: "N events today — context gathered for [meeting subjects]"
   ```

5. **Update step frontmatter:** Set `status: complete` and `completed-at` to the real UTC clock time from `date -u +%Y-%m-%dT%H:%M:%SZ` (paste the exact output; never estimate or round) — Edit tool.

6. **Update state.yaml:** Set `current-step: step-05-synthesize-briefing.md` — Edit tool.

---

## SUCCESS METRICS

- Every `needs_prep` meeting has at least a context lookup attempted
- Prep urgency classified for each important meeting
- Clay reminders and birthdays read from the unified file (or absence confirmed)
- Yesterday's review status known
- Compact results recorded in accumulated-context — zero raw payloads
- Zero API calls (calendar and Clay already on disk; knowledge-base reads are searches, not pulls)
- Subagent exited immediately after the state update — zero other step files read

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Morning-briefing step-03 file missing | Note the failure. Proceed without meeting-specific prep context. Surface in briefing: "Meeting prep context unavailable." |
| No `needs_prep` meetings | Record "nothing-to-surface" and proceed. A clear calendar is a valid outcome. |
| Knowledge base (Obsidian MCP) unavailable | Proceed without knowledge-layer context. Note: "Meeting context limited — knowledge base unavailable." |
| Clay unified file missing or pull failed | Record: "Clay unavailable — carried from step-01.2". Do not re-pull. Note in briefing that reminders/birthdays could not be checked. |
| Clay returns no results | Record: "Clay: nothing to surface." This is a valid outcome. |
| Identity files missing | Report it and proceed with whatever data is available. |

---

## RETURN TO COORDINATOR

This is the END of your mandate. Do not read any other step file — the coordinator spawns the briefing subagent (steps 05 through 08) after you return. Your final message is a short status report: meetings with context (or none), Clay outcome, yesterday's review status, and any failure. Then stop.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
