---
name: plaud-discover
owning_agent: knox
model: haiku
description: >
  Query the Plaud API to enumerate recent recordings and cross-reference against the
  Obsidian vault to identify which ones have not yet been ingested. Returns a list of
  new recording objects with their transcription status. Use this skill when you need
  to know what Plaud recordings exist but haven't been processed yet, or when starting
  the plaud-ingest workflow. Also triggered by "what recordings do I have", "check
  Plaud for new recordings", "any new Plaud notes", or similar.
trigger_keywords: [plaud discover, find recordings, plaud scan]
trigger_agents: [knox]
---

# Plaud Discover

Identify Plaud recordings that exist in the API but have not yet been ingested into
the Obsidian vault. Output is a structured list of new recordings with transcription
status for each.

## ⛔ HARD GATE — DEDUP IS MANDATORY, NOT ADVISORY, IN ANY EXECUTION CONTEXT

**No file or recording may be reported as "unprocessed"/"new" without evidence that it
was actually checked against the vault.** This applies identically whether this skill
runs inline or as a background/forked subagent (see `.claude/skills/plaud-discover/SKILL.md`,
which launches this skill with `context: fork`, `model: haiku`) — fork execution is
**not** an exemption from steps 3-4 below, and a shorter/cheaper run is never an
acceptable reason to skip them.

This gate exists because the same failure has now recurred three times under forked
execution specifically — `err-20260826T190948-QQMBTP`, `err-20260828T140747-814VN9`,
and again on 2026-08-31 (`err-20260831T144849-LDEIJS`, `err-20260831T145746-29X2M7`) —
each time reporting 120-129 already-ingested staging files as "unprocessed" when a
manual re-check (calling `fetch_plaud.py` directly and cross-referencing live vault
frontmatter) found only 1-2 genuinely new recordings. The 2026-08-28 fix (see
`memory/working/rigby-plaud-discover-fix-2026-08-28.md`) corrected real bugs in the
dedup *logic* (archive-folder exclusion, Tier 3's filename assumption, silent
proceed-without-dedup) but did not stop the recurrence — the logic was fine, there was
just nothing forcing a fork to actually execute it instead of guessing. The following
is that enforcement:

1. **Build and persist a dedup ledger before writing any output.** For every candidate
   — every API recording AND every top-level staged file — write one entry to
   `systems/eval-harness/skill-runs/plaud-discover-ledger-latest.json`:
   ```json
   {"id_or_title": "...", "tiers_checked": [1, 2, 3], "vault_match": true, "decision": "skip"}
   ```
   A candidate with no ledger entry, or an entry whose `tiers_checked` is empty, must
   not appear in `new_recordings`. The ledger is what distinguishes "checked and found
   no match" from "didn't check" — a final list with no ledger behind it is exactly the
   failure this gate closes off. Overwrite this file each run (it's a per-run artifact,
   not history).
2. **Circuit breaker against the known false-positive signature.** Before finalizing,
   compare your `new_recordings` count against the most recent confirmed baseline in
   `workflows/plaud-ingest/steps/step-01-discover.md` frontmatter
   (`outputs.previous-run-results`). If your count is more than double the last
   confirmed count **and** more than 10% of total candidates scanned, do not report it
   as a real finding — that ratio is the known signature of a skipped dedup pass.
   Instead: re-run vault enumeration
   (`mcp__obsidian-mcp-tools__list_vault_files(path="zzPlaud")`) once, confirm the
   returned count is at or above the previous run's `confirmed-in-vault`, and redo the
   diff. If the anomaly persists after a clean re-enumeration, treat it as a genuine
   vault-read problem and follow the "Vault enumeration fails" path under Error
   Handling below — abort and report the discrepancy explicitly rather than letting a
   large "new" count pass through unexamined.
3. **No volume-based shortcut.** "There are too many staged files to check
   individually" is never a valid reason to default them all to `new`. If tool-call
   budget is a real constraint under fork execution, batch the checks (parallel
   `get_vault_file` calls, or one `list_vault_files` pass plus bulk frontmatter
   parsing) rather than skipping candidates — but every candidate must resolve to an
   explicit ledger entry with at least one tier actually checked.

## How this works

The Plaud API's `/file/simple/web` endpoint returns a paginated list of all recordings.
The vault stores ingested recordings under `zzPlaud/` with filenames in `YYYY-MM-DD Title.md`
format. By comparing these two sets, we can identify exactly what is new.

This skill does NOT download transcripts — it only enumerates what exists and what's new.
Downloading happens in step-04 of the plaud-ingest workflow.

## Prerequisites

- Valid Plaud API token cached at `~/.config/plaud/token.json`
- Read access to the Obsidian vault (via Obsidian MCP)
- If token is missing or expired: run Chrome login flow per `skills/plaud-transcripts/SKILL.md`

## Execution

### 1. Get token and API base

Load token from `~/.config/plaud/token.json`. Extract `access_token` and check `expires_at`.
If within 30 days of expiry, the fetch script will auto-refresh — proceed normally.
If expired, run Chrome login flow before continuing.

Determine API base from `~/.config/plaud/credentials.json` region field:
- `"us"` → `https://api.plaud.ai`
- `"eu"` → `https://api-euc1.plaud.ai`

### 2. Enumerate recordings from Plaud API

Use the fetch script's listing behavior — or call the API directly:

```
GET /file/simple/web
Headers: Authorization: Bearer <token>
         app-platform: web
         edit-from: web
         Origin: https://web.plaud.ai
         Referer: https://web.plaud.ai/
Params: skip=0, limit=50, is_trash=0, sort_by=create_time, is_desc=1
```

**Default behavior is full enumeration (catch-up mode).** Paginate through ALL pages until no more results are returned. Do not apply a date filter unless a specific `target-date` was explicitly set in `state.yaml accumulated-context.target-date` for a targeted reprocess run.

For each recording, capture:

```json
{
  "file_id": "...",
  "name": "Recording Title",
  "create_time": "2026-04-15T14:23:00Z",
  "duration": 3421,
  "is_trans": 0 | 1,
  "trans_status": 0 | 1
}
```

Where:
- `is_trans: 0` = no transcription exists (status: `missing`)
- `is_trans: 1` + `trans_status: 0` = transcription in progress (status: `pending`)
- `is_trans: 1` + `trans_status: 1` = transcription ready (status: `ready`)

**Date filtering (targeted reprocess only):**
- Only filter by `create_time` matching `target-date` if that field is explicitly set in state.
- For all normal runs: no date filter — get all recordings and dedup against vault.

### 3. Enumerate already-ingested vault notes

Via Obsidian MCP, list all files under `zzPlaud/` recursively:

```
mcp__obsidian-mcp-tools__list_vault_files(path="zzPlaud")
```

For each `.md` file returned, read its frontmatter and extract the `file_id` field (if present).
Build two lookup structures:

1. **file_id set** — a set of all `file_id` values found in vault note frontmatter. This is the
   primary dedup mechanism. Notes written after this fix was applied (2026-08-10) will have this field.
2. **title set** — a set of normalized filenames (date stripped, `.md` stripped, lowercased,
   punctuation removed, whitespace collapsed). This is the fallback for older notes that predate
   file_id tracking.

Reading frontmatter: use `mcp__obsidian-local__get_vault_file` for each note, then parse the
YAML block between the `---` delimiters. If a note has `file_id: <value>`, add it to the
file_id set. Always add the normalized title to the title set regardless.

Also check staging: list `~/Downloads/transcript-staging/plaud_*.md` at the **top level only**.

**Exclude `_not_new_archive/` and any other subfolder entirely.** Files under
`_not_new_archive/` (or any archive/excluded subfolder) have already been triaged as not-new
by a prior run. Never scan them, never count them, never let them influence the diff. If you
are enumerating with `find` or a recursive glob, explicitly prune `_not_new_archive` (e.g.
`find ~/Downloads/transcript-staging -maxdepth 1 -name 'plaud_*.md'`) — a recursive scan that
picks up the archive is the single most common cause of massive false-positive "new" counts,
since that folder alone can hold hundreds of old files.

For each remaining top-level staged file, extract its title (strip the `plaud_` prefix and
extension) and **run it through the same Tier 1 / Tier 2 dedup checks used for API recordings
in step 4 before doing anything else with it.** A staged file is never automatically "new" —
staging is a work-in-progress area, not a source of truth about what's ingested. Concretely:

1. Try to resolve the staged file's `file_id` (check for a sibling `_raw.json` with a `file_id`
   field, or frontmatter if the `.md` has any). If resolved and it's in the vault's file_id set
   → this recording is **already ingested**. Skip it, and flag it for cleanup (it's a leftover
   that should have been moved to `_not_new_archive/` or deleted after ingestion — note this in
   your report, do not silently re-queue it).
2. If no file_id is resolvable, fuzzy-match the staged title against vault titles (same 85%
   threshold as Tier 2). A match → already ingested. Skip it and flag for cleanup as above.
3. Only if neither check matches does the staleness rule apply:
   - Modification time **within the last 24 hours**: treat as in progress — it will be picked
     up by step-04 without re-fetching.
   - Modification time **older than 24 hours**: treat as genuinely stale/orphaned. Re-queue the
     associated recording as new so it gets reprocessed.

Check mtime using `stat -f "%m" <file>` (macOS) or `stat -c "%Y" <file>` (Linux) and compare
against current epoch time minus 86400 seconds.

If genuinely stale/orphaned files are found (i.e. they passed both dedup checks above), add
their file IDs to `state.yaml accumulated-context.stale-staged-files` so the next run has an
explicit list of files that need reprocessing. Do not add a file to this list until it has
cleared the file_id and title dedup checks — an unresolved-but-already-ingested staged file is
a cleanup problem, not a reprocessing problem.

### 4. Compute the diff

**Two-tier deduplication — check in this order for every API recording:**

**Tier 1 — file_id exact match (primary):**
If the recording's `file_id` is present in the vault's file_id set, it is already ingested.
Skip it. This is authoritative — no further check needed.

**Tier 2 — title fuzzy match (fallback for pre-2026-08-10 notes):**
Only reach this tier if the file_id was NOT found in tier 1. Normalize the API recording's
`name` field (lowercase, strip punctuation, collapse whitespace). Compare against each
normalized vault title using sequence similarity. A match threshold of **85%** is required.
A match at this tier means already ingested — skip it.

**Tier 3 — staged file check:**
If neither tier 1 nor tier 2 matched, check whether a staged file already exists for this
recording. **Staged filenames are title-based (`plaud_<title>.md`), not file_id-based** —
do not assume a `plaud_<file_id>*.md` pattern, it will never match real files. Resolve the
staged file's `file_id` via its sibling `_raw.json` if present, or fuzzy-match its title
(strip `plaud_` prefix and extension) against the recording's `name` at the same 85% threshold
used in Tier 2. If a match is found and the file is not stale (see step 3's staging rules),
skip it — it's in progress.

If no tier matched: this recording is **new**.

```
Decision logic (pseudocode):
  if recording.file_id in vault_file_id_set:               → SKIP (already ingested, exact match)
  elif fuzzy_match(recording.name, vault_titles) >= 0.85:  → SKIP (ingested, title match)
  elif staged_file_exists(recording.file_id) and not stale: → SKIP (in progress)
  else:                                                      → NEW (add to output list)
```

**Important:** The 85% fuzzy threshold is intentionally strict. Knox substantially rewrites
Plaud's auto-generated titles when creating vault notes (adds speaker names, cleans punctuation,
reorganizes). Notes written before file_id tracking began will rely on this tier. If a vault
title scores below 85% but you have strong contextual reason to believe it's the same recording
(same date + duration match within 5%), treat it as ingested and log your reasoning. When
genuinely uncertain, default to NEW — a duplicate note is recoverable; a missed recording
requires a full reprocess.

### 5. Return the new-recordings list

Structured as:

```yaml
new_recordings:
  - file_id: abc123
    name: "Meeting with Todd Wynne"
    date: 2026-04-15
    duration_seconds: 3421
    has_transcript: true
    transcript_status: ready   # ready | pending | missing
  - file_id: def456
    name: "One Texas Strategy Call"
    date: 2026-04-15
    duration_seconds: 1820
    has_transcript: false
    transcript_status: missing
```

**This full per-recording list is the required output of this skill — not a summary count.**
When this skill is run as part of `workflows/plaud-ingest/workflow.md` step-01, the calling
step MUST write this exact list into `state.yaml accumulated-context.new-recordings` before
proceeding. A count-only report (e.g. "127 ready for vault ingestion") with no list behind it
is an incomplete run — do not let it be treated as satisfying step-01's requirement, and do not
advance `current-step` past `step-01` until the list is actually written to state. If for any
reason only a summary can be produced (e.g. truncated output), that is a failure, not a
shortcut — report it as such rather than writing a count into a field that expects a list.

**Every entry in `new_recordings` must trace back to a ledger entry from the HARD GATE above**
with at least one tier checked and `decision: new`. If you cannot produce the ledger file, you
cannot produce this list — that is the failure mode to report, not a reason to fall back to an
unchecked guess.

Also do not invent ad hoc output shapes (e.g. a `findings` block with just totals) for the
skill-run signal file below — the schema in "SKILL COMPLETE" is the only one that's tracked by
the eval harness; deviating from it hides exactly the kind of incomplete-run problem this fix
addresses.

## Running via the fetch script

As an alternative to direct API calls, you can invoke `fetch_plaud.py` with discovery
intent using osascript:

```
do shell script "cd <skill-scripts-dir> && /usr/bin/python3 fetch_plaud.py <YYYY-MM-DD> 2>&1"
```

Read the output to identify which recordings were found, their statuses, and which ones
ended up in the pending queue. The script handles pagination, token refresh, and status
detection automatically.

## Error handling

- **API returns 401**: Token expired. Run Chrome login flow. Retry once.
- **API returns 429**: Rate limited. Wait 5 seconds and retry.
- **Empty result set**: Either no recordings for the date, or wrong date/timezone. Try ±1 day.
- **Vault enumeration fails** (Obsidian MCP `list_vault_files` errors, times out, or returns an
  empty/partial result): Do **not** proceed without dedup — a silent fallback here has already
  caused two false-positive incidents (`err-20260826T190948-QQMBTP`, `err-20260828T140747-814VN9`)
  where 100+ already-ingested recordings were reported as "new." Instead: retry the vault
  enumeration once. If it still fails or returns a file_id count that is dramatically lower than
  the previous run's confirmed-in-vault count for an overlapping recording set, **abort this
  skill run** and report the vault-read failure explicitly (do not write a `new_recordings` list,
  do not let the caller treat a partial/empty vault read as "vault is actually empty"). Surfacing
  a blocked run is always better than fabricating a new-recordings count on broken dedup data.

## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/plaud-discover-latest.json
```

Content:
```json
{
  "skill": "plaud-discover",
  "agent": "knox",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from the morning briefing or a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output, `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action.

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill plaud-discover
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/plaud-discover.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

