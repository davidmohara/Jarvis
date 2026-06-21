---
name: watchtower
description: Standing intelligence monitor — scans news and sources across David's topic areas, delivers daily awareness summaries, and surfaces weekly content candidates feeding the existing content pipeline.
agent: knox
owner: knox
evolution: personal
model: sonnet
---

<!-- system:start -->
# Watchtower Workflow

Standing intelligence system. Monitors AI/agentic systems, IT consulting, and Texas/regional business. Two entry modes with distinct outputs.

**Harper is consulted during the weekly content-flagging step (step-02 of weekly run) for voice alignment.**

---

## Entry Modes

| Mode | Trigger | Cadence | Steps |
|------|---------|---------|-------|
| **Daily / Awareness** | Invoked by `workflows/morning-briefing/` before step-01-gather-calendar | Every day (via morning briefing) | daily-step-01 through daily-step-07-prune, then daily-step-06 |
| **Weekly / Content + Sources** | "run watchtower weekly" or scheduled Monday 7am (pending) | Every Monday | weekly-step-01 through weekly-step-05 |

**Daily cadence note:** The daily run does NOT run as a standalone scheduled task. It is invoked by the morning-briefing workflow. See `config.yaml cadence.daily.enabled: false` and the WATCHTOWER INVOCATION section in `workflows/morning-briefing/workflow.md`.

Both modes share `state.yaml` and `config.yaml`. Sources live in `sources.yaml`.

---

## Data Sources Required

| Source | Purpose | Path / Connector |
|--------|---------|-----------------|
| `sources.yaml` | Active RSS feeds + trusted web sources | `workflows/watchtower/sources.yaml` |
| `config.yaml` | Thresholds, paths, cadence, profile | `workflows/watchtower/config.yaml` |
| `state.yaml` | Run state and accumulated context | `workflows/watchtower/state.yaml` |
| `seen.jsonl` | Dedupe ledger | `workflows/watchtower/seen.jsonl` (created on first run) |
| `source-activity.json` | Per-source last_surfaced ledger for dormancy tracking | `workflows/watchtower/source-activity.json` |
| `dormant-sources.yaml` | Retired sources (not polled, not deleted) | `workflows/watchtower/dormant-sources.yaml` |
| David's profile | Lenses for scoring | `identity/VOICE.md`, `identity/MEMORY.md` |
| Content register | Append content candidates | `reference/blog-ideas.md` |
| Obsidian vault | Daily notes + content drafts | Obsidian MCP (`Watchtower/Daily/`, `Mind/Posts/`) |

---

## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.

2. If `status: in-progress`:
   - You are resuming a previous run. Do NOT start over.
   - Read `current-step` to determine where to continue.
   - Load `accumulated-context` — do not re-gather data already collected.
   - Check that step's frontmatter:
     - `status: in-progress` → step was interrupted; re-execute it from the beginning.
     - `status: not-started` → begin it fresh.
   - Notify: "[Knox]: Resuming watchtower from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01`.
   - Determine entry mode from trigger (daily vs. weekly). Begin at step-01 for that mode.

4. If `status: aborted`:
   - Do not resume automatically. Surface to David:
     "[Knox]: Watchtower was previously aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.

---

## EXECUTION

Run STATE CHECK above, then begin at step-01 for the appropriate mode.

---

## Daily Run — Steps (Awareness)

| Step | File | Model | Description |
|------|------|-------|-------------|
| 01 | `steps/daily-step-01-gather.md` | haiku | Pull RSS feeds + web searches per topic; collect candidate items |
| 02 | `steps/daily-step-02-dedupe.md` | haiku | Drop items seen within dedupe window; update seen.jsonl |
| 03 | `steps/daily-step-03-score.md` | sonnet | Score items 0-100 against David's profile; drop below awareness_floor; update source-activity.json |
| 04 | `steps/daily-step-04-summarize.md` | sonnet | Write one-paragraph "what you should be aware of" per surviving item |
| 04b | `steps/daily-step-04b-synthesize.md` | sonnet | Generate through_line (synthesizing pattern) and consulting_read (editorial callout) from summarized items |
| 05 | `steps/daily-step-05-capture.md` | haiku | Write Obsidian daily note (with through-line); build/update dashboard artifact (with through-line banner + consulting-read callout) |
| 07 | `steps/daily-step-07-prune.md` | haiku | Dormancy check: retire sources silent >= 21d to dormant-sources.yaml |
| 06 | `steps/daily-step-06-report.md` | haiku | Summary of what was surfaced (includes retirements); hand content-worthy items to weekly queue |

**Step order note:** step-04b-synthesize runs between step-04-summarize and step-05-capture. Step-07-prune runs between step-05 and step-06. Step-06 reads retirements_today that step-07 writes.

## Weekly Run — Steps (Content + Sources)

| Step | File | Model | Description |
|------|------|-------|-------------|
| 01 | `steps/weekly-step-01-synthesize.md` | sonnet | Pull week's content-worthy items; synthesize themes |
| 02 | `steps/weekly-step-02-draft-angles.md` | sonnet | Draft HOOK + OUTLINE per content item; write to Obsidian + blog-ideas.md |
| 03 | `steps/weekly-step-03-suggest-sources.md` | sonnet | Propose up to max_per_week new sources; write to proposed-sources.md |
| 04 | `steps/weekly-step-04-weekly-note.md` | haiku | Write Obsidian weekly note summarizing themes, candidates, proposals |
| 05 | `steps/weekly-step-05-report.md` | haiku | Surface content candidates ready + sources awaiting yes/no |

---

## Source Registry

Active sources: `workflows/watchtower/sources.yaml`
Dormant sources (auto-retired, not polled): `workflows/watchtower/dormant-sources.yaml`
Proposed sources awaiting approval: `workflows/watchtower/proposed-sources.md`
Source activity ledger: `workflows/watchtower/source-activity.json`

Source approval gate: David explicitly approves or rejects each entry in `proposed-sources.md`. Approved entries are moved to `sources.yaml` by Rigby. Nothing auto-adds.

Dormancy rule: a source that surfaces no item clearing `awareness_floor` for 21 consecutive days is automatically moved from `sources.yaml` to `dormant-sources.yaml` by `daily-step-07-prune`. Retirements surface in the weekly report.

---

## Integration Contracts

| Downstream system | How Watchtower feeds it |
|-------------------|------------------------|
| `reference/blog-ideas.md` | Weekly step-02 appends candidate rows under `[watchtower]` marker |
| `Mind/Posts/` (Obsidian) | Weekly step-02 writes `_<slug>.md` draft files |
| `Watchtower/Daily/` (Obsidian) | Daily step-05 writes `YYYY-MM-DD.md` with `#watchtower` tag |
| `Watchtower/Weekly/` (Obsidian) | Weekly step-04 writes `YYYY-Www.md` |
| Morning briefing | Daily run is invoked by morning-briefing before its step-01; top 5 items by score rendered inline as a Watchtower section with link to full dashboard; content candidate count noted |

Watchtower does NOT publish. It does NOT file vault notes outside its own folders. It feeds Harper's content pipeline and Knox's vault — it does not rebuild either.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
