---
name: omnifocus-data
owning_agent: master
description: >
  Extract OmniFocus data: the canonical pull into `data/omnifocus-unified.json`
  plus shared read primitives (inbox, due/overdue, flagged, tags, active
  projects, counts). Use this skill whenever OmniFocus data is needed as input
  to something else, or when the user asks "what's on my plate", "check my
  tasks", "what's in my OmniFocus", "pull OmniFocus", or asks for inbox /
  flagged / due counts. Also the mandated path for boot step-01.2 Pull B and
  for any workflow that needs OmniFocus counts. For CREATING tasks, use
  `skills/omnifocus-tasks/SKILL.md` instead: that is a separate, gated skill.
model: sonnet
trigger_keywords: [omnifocus, tasks, inbox, flagged, due, counts]
trigger_agents: [master, chief, quinn, shep]
---

<!-- system:start -->
# OmniFocus Data

Canonical producer of `data/omnifocus-unified.json` and the single owner of
OmniFocus read logic. Every consumer reads the file this skill writes; no
consumer should hold its own OmniFocus query.

## Why this skill exists

Use this skill's script for every OmniFocus read: the invariants below live in code, not in prose each consumer re-implements.

## Two paths, and which to use

| Need | Path |
|------|------|
| Reading OmniFocus to decide or write something | **This skill's script** — one entry point, no hand-written queries. It picks the best backend itself |
| The canonical pull, counts, and anything unattended | **This skill's script** (AppleScript) |

The script fronts two backends and chooses per command:

| Command | Backend |
|---------|---------|
| `pull`, `list` | **AppleScript only.** The MCP's `query_omnifocus` returns a display rendering (`• name [id] (project) #status`) that omits `note`, so it cannot produce the canonical record shape |
| `counts`, `tags`, `projects` | **MCP when reachable, AppleScript otherwise.** These are the reads the MCP does better: it speaks OmniFocus's *effective* status, so archived work is excluded for free |

The MCP depends on session state: the server must be built, running, and
connected before the session starts. osascript has no such dependency. Boot
runs unattended, so the **pull** must never depend on MCP availability, and it
does not.

`--source {auto,mcp,apple}` forces the choice. `auto` (the default) falls back
to AppleScript and says so on stderr. `--source mcp` never falls back: a caller
that asked for the MCP wants to hear it is unavailable, not to be quietly
served something else.

## The script

```
skills/omnifocus-data/scripts/omnifocus_data.py
```

| Command | Purpose |
|---------|---------|
| `pull [--out PATH]` | Write the canonical data file. Never raises: on failure it writes `status: failed` and exits 1 |
| `counts [--json]` | `inbox_uncompleted`, `flagged_uncompleted`, `total_uncompleted`, `due_within_7`, `overdue_uncompleted`, `completed_today` |
| `tags [--json]` | All tag names, including inactive ones |
| `projects [--json]` | Active project names, excluding those inside archived folders |
| `list --kind inbox\|due\|flagged [--json]` | Tasks of one kind |

Run it with `python3`. `--days N` shifts the due window (default 7) and must
precede the subcommand.

Both backends are verified to return identical results for all six counts,
for `tags`, and for `projects`. If they ever disagree, that is a bug, not a
preference — the whole point of routing both through one skill is that the
answer does not depend on which backend happened to answer.

## Counts mean open work, not rows

`total_uncompleted` counts real open tasks: no project-root rows, and nothing inside an archived folder. A raw `flattened tasks` count inflates this badly (measured 258 vs. the honest 136). `projects` likewise excludes projects that sit inside the archive even when flagged active.

## The pull

```bash
python3 skills/omnifocus-data/scripts/omnifocus_data.py pull
```

Writes `data/omnifocus-unified.json`. Report the outcome honestly: read the file
back and state `status` and `task_count`. A `status: failed` pull must be
surfaced as a degraded source, never passed over as an empty one.

## Invariants (do not violate)

1. **Every query carries the completed filter.** The inbox permanently holds
   roughly 247 completed tasks alongside ~8 incomplete ones, and OmniFocus
   "Clean Up" does NOT remove them. The filter lives in the query, not in a
   cleanup step. The script enforces this; if you hand-write a query, you must
   enforce it yourself.
2. **A failed pull is distinguishable from an empty one.** Always write and read
   `status`. Never let a failure look like a quiet day.
3. **One writer.** Only this skill writes `data/omnifocus-unified.json`. If you
   find another writer, that is a bug: consolidate it here.
4. **A count of open work excludes archived work and project roots.** Do not
   reintroduce `count of (flattened tasks whose completed is false)` as a
   total. See "Counts mean open work" above.
5. **Do not hand-write OmniFocus queries.** Every read here has a command. The
   script picks its own backend precisely so callers never have to reason about
   which one is connected.

## Failure handling

| Failure | Action |
|---------|--------|
| Script exits 1 | Read `error` from the output file and report it as a degraded source |
| `osascript` missing or unrunnable | The pull already writes `status: failed`; do not retry blindly. Report it |
| MCP tools absent | Expected in unattended runs. Use this script; do not report OmniFocus unreachable on that basis |
| Tags or projects empty | Treat as a real empty result, not an error |

## Task creation

Not here. Creating tasks is gated on project and tag assignment and lives in
`skills/omnifocus-tasks/SKILL.md`. Use this skill's `tags` and `projects`
commands to satisfy that gate's Step 1 if the MCP is unavailable.

---

<!-- system:end -->

