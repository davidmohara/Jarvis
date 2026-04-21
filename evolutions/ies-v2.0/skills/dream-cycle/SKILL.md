---
name: dream-cycle
owning_agent: knox
model: sonnet
trigger_keywords: [dream, memory consolidation, compress memory, promote semantic]
trigger_agents: [rigby, knox]
description: "Nightly memory consolidation. Runs automatically via scheduled task."
---

# Dream Cycle Skill

You are running the IES nightly dream cycle. Execute all five phases in order.
Log every action. Be conservative — when in doubt about whether to promote or
compress an entry, leave it and note it in the log. Preservation over aggression.

## Pre-flight

- Read `memory/dream.log` — confirm last run date. If last run was today, abort with log entry: `aborted: already ran today`.
- Get current local date/time via `osascript -e 'return (current date) as string'`.
- Record `session_id: dream-cycle-{YYYY-MM-DD-HHmmss}`.

---

## Phase 1: Working Memory Cleanup

1. List all files in `memory/working/` (exclude `README.md`).
2. For each file:
   a. Read the frontmatter. Parse `expires` date.
   b. If `expires` < today AND `status: active`:
      - Set `status: archived` in frontmatter.
      - If content body is non-trivial (>3 substantive lines):
        Move to `memory/episodic/` with `type: working-archive`, `salience.score: 0`
      - If content body is trivial (empty, placeholder, or <3 lines):
        Delete the file.
3. Log: `working_archived: N`, `working_deleted: N`

---

## Phase 2: Salience Scoring

1. Read ALL files in `memory/episodic/` (all subdirectories, excluding `digests/`).
   Build a list: `[{file_path, date, tags, related_people, salience}]`
2. For each episodic entry E:
   a. Find all other entries where:
      - Shares 2+ tags with E, AND
      - Was written within the last 30 days
   b. Set `E.salience.score` = count of matching entries (max 10)
   c. Set `E.salience.last-promoted-check` = today
   d. Write updated frontmatter back to the file.
3. Log: `episodic_scanned: N`, `score_updates: N`

**NOTE:** Do not read or score entries in `memory/episodic/digests/` — those are already compressed.

---

## Phase 3: Semantic Promotion

1. Identify promotion candidates:
   All episodic entries where:
   - `salience.score >= 3`, AND
   - `salience.promoted == false`, AND
   - `salience.last-promoted-check` within last 24 hours (just scored)

2. Group candidates into clusters by shared tags.
   Each cluster = 1 potential semantic entry.

3. For each cluster:
   a. Determine domain: `relationships | operational | domain-knowledge | pattern`
      (infer from tags: people/accounts → relationships; system/process → operational;
      industry/market → domain)
   b. Check `memory/semantic/{domain}/` for an existing entry with overlapping tags.
   c. **If existing entry found:**
      - Read it.
      - Synthesize new insights from the cluster not already present.
      - Append to the `## Evidence` and `## Implications` sections.
      - Update `last-updated` and `synthesized-from` in frontmatter.
      - Increment confidence: `low → medium → high` based on total evidence count.
   d. **If no existing entry:**
      - Create new semantic entry in `memory/semantic/{domain}/`
      - Filename: `YYYY-MM-DD-{tag-slug}-pattern.md`
      - Write frontmatter + synthesis with Pattern Summary, Evidence, Implications.
      - Set `confidence: low` (new entry always starts low).
   e. Set `salience.promoted: true` on all source episodic files.

4. Log: `clusters_found: N`, `semantic_created: N`, `semantic_updated: N`, `promoted_entries: N`

**HARD RULE:** Never delete or overwrite existing semantic entries. Only append. Semantic memory is append-only.

---

## Phase 4: Episodic Compression

1. Find compression candidates:
   All episodic entries where:
   - `date` < 90 days ago, AND
   - `salience.score < 2`, AND
   - `salience.promoted == false`

2. **CAUTION:** If compression candidates are fewer than 5, skip Phase 4 entirely.
   Not worth the risk of compressing something useful. Log: `compression_skipped: true`

3. Group by quarter (`YYYY-QN`).

4. For each quarter group:
   a. Check if `memory/episodic/digests/{YYYY-QN}-digest.md` already exists.
   b. If not: create it.
   c. Append a one-paragraph summary of each candidate entry to the digest.
      Format: `### {date} — {subject} ({type})\n{2-sentence summary}\n`
   d. Mark each source file for deletion (do not delete yet — batch at end).

5. After all digests are written: delete the compressed source files.

6. Log: `entries_compressed: N`, `digests_updated: N`

---

## Phase 5: Logging

Append the following block to `memory/dream.log`:

```
---
## {YYYY-MM-DD}T{HH:MM:SS} {TZ}
session_id: dream-cycle-{YYYY-MM-DD-HHmmss}
working_archived: N
working_deleted: N
episodic_scanned: N
score_updates: N
clusters_found: N
semantic_created: N
semantic_updated: N
promoted_entries: N
entries_compressed: N
digests_updated: N
errors: N
summary: "[One sentence. e.g.: Promoted 2 patterns to semantic/relationships/. Compressed 8 Q1 entries. No errors.]"
---
```

If any errors occurred during any phase, append:
```
errors_detail:
  - phase: N
    file: path/to/file.md
    error: "Description of what went wrong"
```

**Final action:** If `semantic_created > 0` OR `semantic_updated > 0` OR `errors > 0`:
Write a file `memory/working/dream-summary-{YYYY-MM-DD}.md` with
`type: working`, `expires: {today + 1 day}`
Content: the log entry above, formatted for Chief to read at boot.

---

## LESSONS.md Check

After Phase 3, scan `systems/error-tracking/error-log.json` for any error category
appearing 3+ times in the last 30 days. If found and not already in `memory/LESSONS.md`:

Add an entry to `memory/LESSONS.md`:
```
## {today} — {Pattern Title}
Detected: {N} occurrences over {X} days
Category: {error category}
Pattern: {What keeps happening}
Fix: {What agents should do differently}
Status: active
```
