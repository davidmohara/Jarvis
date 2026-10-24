---
status: complete
started-at: '2026-10-23T13:26:00Z'
completed-at: '2026-10-23T13:29:29Z'
---

<!-- system:start -->
# Step 01.2: Unified Data Pull (Consolidate All External Data)

## MANDATORY EXECUTION RULES

1. You MUST pull ALL external data sources in a single phase — no repeated calls.
2. You MUST write each data source to a separate file in `data/` directory.
3. You MUST execute all pulls in parallel (fire simultaneously, do NOT wait sequentially).
4. You MUST report status for each pull (completed, nothing-to-surface, or failed — [reason]).
5. Clay MCP MUST ALWAYS attempt to pull, even if marked unavailable — this checks current state, not assumed stale data.
6. You MUST NOT proceed until all pulls have status reported.

---

## EXECUTION PROTOCOL

**Agent:** dedicated unified-data-pull subagent, spawned by the coordinator (Master) with a tight single-purpose brief (see `workflow.md`). This step is a plain data-pull phase: it never loads the master persona (`agents/master.md`) or `SYSTEM.md`, never runs STATE CHECK, and never walks other steps.
**Input:** M365 MCP, Clay MCP, OmniFocus access, Jarvis folder
**Output:** Consolidated data files written to `data/` directory

---

## CONTEXT BOUNDARIES

- This step consolidates all external data pulls BEFORE phase 2 data gathering
- All downstream steps will read from these files instead of calling APIs
- Fire all pulls in parallel (non-blocking)
- No raw API responses stored in accumulated-context — only file paths and summaries

---

## YOUR TASK

Fire all pulls simultaneously. Each pull writes to disk and reports status.

### Pull A: Email (Flagged & Time-Sensitive)

**Source:** M365 MCP (`outlook_email_search`)
**Output file:** `data/email-unified.json`
**What to pull:**
- All flagged messages
- Unread messages from last 24 hours marked high priority
- Messages with explicit deadline or time-sensitive subject line
- Do NOT pull full inbox — only actionable items

**File format:** use the exact schema in `references/pull-file-formats.md` (read it before writing the output file).

**Status reporting:** use the yaml shape in `references/pull-file-formats.md` for this pull.

---

### Pull B: OmniFocus Inbox

**Source:** OmniFocus.

**Run the `omnifocus-data` skill.** Do NOT hand-write OmniFocus queries in this step:

```bash
python3 skills/omnifocus-data/scripts/omnifocus_data.py pull
```

That command writes `data/omnifocus-unified.json` and is the single writer for it. Read the file back and report `status` and `task_count`. A `status: failed` pull is a degraded source to surface, never something to pass over as an empty day.

For ad-hoc reads inside this step, use the same skill: `list --kind inbox`, `list --kind due`, `counts`. Prefer the script over the MCP for every read here, because it does not depend on MCP session state and boot runs unattended. If the MCP does happen to be connected, the two agree on counts, tags and projects — and note that its `query_omnifocus` returns a display rendering that omits notes, so it cannot stand in for the pull.

(Why delegated: see `references/pull-file-formats.md`.)
**Output file:** `data/omnifocus-unified.json`
**What to pull:**
- All active (non-completed) tasks in inbox
- Due today, overdue, or flagged
- Include: task name, due date, project, tags, flags

**File format:** use the exact schema in `references/pull-file-formats.md` (read it before writing the output file).

This shape is produced by `skills/omnifocus-data/scripts/omnifocus_data.py`; treat that script as the definition of record if the two ever disagree.

**`completed` MUST be present and false on every task.** The inbox holds roughly 247 completed tasks alongside the ~8 incomplete ones, and OmniFocus "Clean Up" does NOT remove them. Filtering is part of the query, never a cleanup step. Recording the field is what lets the eval harness assert that no completed task leaked into the pull.

**Status reporting:** use the yaml shape in `references/pull-file-formats.md` for this pull.

`status: available` with `task_count: 0` is a real empty result (nothing in the inbox, nothing due, nothing flagged). Report it as `nothing-to-surface`, not as a failure. `status: failed` is a degraded source and must be surfaced as such.

---

### Pull C: Clay Reminders (Next 7 Days) — MANDATORY ALWAYS

**Source:** Clay MCP
**Output file:** `data/clay-reminders-unified.json`
**MANDATORY:** This pull MUST ALWAYS attempt to fetch from Clay, even if Clay MCP is previously marked unavailable. This checks current state rather than assuming stale data.

**What to pull:**
- Upcoming reminders (next 7 days)
- Upcoming birthdays (next 7 days)
- Include: date, description, attendee/contact, relationship context

**File format:** use the exact schema in `references/pull-file-formats.md` (read it before writing the output file).

**Status reporting:** use the yaml shape in `references/pull-file-formats.md` for this pull.

**Note:** Even if Clay appears unavailable, the attempt itself is valuable — it confirms current state and ensures we're not using stale cached assumptions.

---

### Pull D: Jarvis Inbox

**Source:** `/Jarvis` email folder
**Output file:** `data/jarvis-inbox-unified.json`
**What to pull:**
- All unread messages in /Jarvis folder
- Emails requiring David's direct attention
- Include: sender, subject, received date, summary

**File format:** use the exact schema in `references/pull-file-formats.md` (read it before writing the output file).

**Status reporting:** use the yaml shape in `references/pull-file-formats.md` for this pull.

### Pull E: YNAB Spend

**Source:** YNAB (MCP connector where available; REST API fallback)
**Output file:** `data/ynab-unified.json`

Run the canonical pull:

```bash
python3 skills/ynab-data/scripts/ynab_data.py pull
```

That command writes `data/ynab-unified.json` and is the single writer for it. Read the file back and report `status` and the payee counts. A `status` other than `available` is a degraded source to surface (dead token, API error), never something to pass over as a quiet month.

(Why delegated: see `references/pull-file-formats.md`.)
**Output file:** `data/ynab-unified.json`

**Consumers:** card-offer filtering (`chase-card-offers-*`, `card-walkthrough` step-02), spend reviews, budget questions.

---

## Recording Results

After ALL pulls complete, record outcomes in `accumulated-context`:

```yaml
accumulated-context:
  phase1-point5:
    unified-data-pulls:
      email: "completed — N messages" | "nothing-to-surface" | "failed — [reason]"
      omnifocus: "completed — N tasks" | "nothing-to-surface" | "failed — [reason]"
      clay: "completed — N reminders, M birthdays" | "nothing-to-surface" | "failed — [reason]"
      jarvis-inbox: "completed — N messages" | "nothing-to-surface" | "failed — [reason]"
      ynab: "completed — N payees" | "nothing-to-surface" | "failed — [reason]"
    files-created:
      - "data/email-unified.json"
      - "data/omnifocus-unified.json"
      - "data/clay-reminders-unified.json"
      - "data/jarvis-inbox-unified.json"
      - "data/ynab-unified.json"
    total_data_on_disk_kb: N
```

---

## Execution Guidelines

Read `references/execution-guidelines.md` before firing the pulls: parallel-execution rules (fire all pulls simultaneously) and the status-reporting format.

## Success Metrics

- All 4 pulls fire simultaneously (not sequentially)
- All 4 pulls report status (no silent failures)
- Files written to disk: 5 JSON files in `data/` directory
- Total data on disk: < 500 KB combined
- No raw data stored in accumulated-context (only file paths and summaries)
- Estimated context savings: 80-90% vs. storing raw data in context

---

## Failure Modes

| Failure | Action |
|---------|--------|
| M365 email API unavailable | Record: "email: failed — M365 unavailable". Continue. |
| OmniFocus connection fails | Record: "omnifocus: failed — [reason]". Continue. |
| Clay MCP unavailable | Record: "clay: nothing-to-surface — Clay unavailable". Continue. |
| Jarvis folder missing | Record: "jarvis-inbox: nothing-to-surface — folder not found". Continue. |
| File write fails for any pull | Record failure. Continue. Downstream steps handle missing files. |
| Multiple pulls fail | Record all failures. Continue to step 02. Boot will degrade gracefully. |

---

## Update State

1. **Update step frontmatter:** Set `status: complete` and `completed-at` with current timestamp — with the Edit tool, never Bash (the eval harness's per-step attribution keys on Edit/Write tool calls).
2. **Update state.yaml:** Set `current-step: step-02-gather-data.md`.

---

## RETURN TO COORDINATOR

This is the END of your mandate. Do not read `step-02-gather-data.md` or any other step file — the coordinator spawns the dedicated gather subagent for step-02 after you return. The calendar pull (step-01.5) already ran as its own dedicated subagent before this one — never re-pull the calendar here. All downstream steps (phase 2 through phase 5) read from these consolidated files instead of calling APIs.

Your final message is a short status report: one line per pull (A through E) with its outcome, files written, and any failure. Then stop.

<!-- system:end -->
