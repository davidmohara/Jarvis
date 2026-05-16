# Error Tracking Schema

<!-- system:start -->
## Storage Layout

```
systems/error-tracking/
  _meta.json              # log-level metadata (version, description)
  entries/
    err-<id>.json         # one file per entry — see ID Format below
  schema.md               # this file
  new-entry.py            # generate a new id and skeleton entry file
  rebuild-log.py          # aggregate entries into a single view for analysis
```

One file per entry is the canonical form. The previous monolithic `error-log.json` was retired because it produced unresolvable merge conflicts when the same vault was written from two machines via GitHub.

## ID Format

New entries use:

```
err-YYYYMMDDTHHMMSS-XXXXXX
```

Where `XXXXXX` is a random 6-character alphanumeric suffix (`[A-Z0-9]`). The timestamp is UTC. Generate the id with `python3 systems/error-tracking/new-entry.py --id-only` so the format and randomness stay consistent.

Why this format: the old `err-YYYYMMDD-NNN` scheme collided across machines (both would pick `-001` on the same day) and forced sequential numbering, which required reading the whole log to know the next id. Timestamp plus random suffix is collision-free across machines and append-only.

Older entries created under the legacy `err-YYYYMMDD-NNN` scheme keep their original ids and are not renamed; cross-references in `related_entries` remain stable.

## Entry Structure

Each file in `entries/` contains a single JSON object:

```json
{
  "id": "err-YYYYMMDDTHHMMSS-XXXXXX",
  "timestamp": "ISO 8601",
  "session": "session identifier or date",
  "source": "explicit | self-detected",
  "agent": "which agent was active when the error occurred",
  "category": "see categories below",
  "description": "what went wrong — factual, concise",
  "correction": "what the right answer/action was",
  "failure_mode": "root cause classification",
  "systemic_fix": "proposed or applied fix (null if pending analysis)",
  "fix_status": "proposed | applied | deferred | not-applicable",
  "severity": "minor | moderate | major",
  "related_entries": ["err-..."]
}
```

The filename must match the `id` field exactly: `entries/<id>.json`.

## Writing a New Entry

1. Generate the id and skeleton: `python3 systems/error-tracking/new-entry.py` prints the new file path.
2. Fill in the fields.
3. Commit only the new file. No other file in `systems/error-tracking/` needs to change for a new entry.

Agents writing entries programmatically should follow the same id format and write to `entries/<id>.json` directly. Never edit other entries or `_meta.json` when recording a new correction.

## Reading the Log

For one-off lookups, read individual files in `entries/`. For analysis across the full log (Rigby's pattern detection, weekly review), use:

```
python3 systems/error-tracking/rebuild-log.py --out /tmp/log.json
```

This emits a single aggregated JSON object with `metadata` and `entries[]` (sorted by id), structurally identical to the retired monolithic log.

## Error Categories

| Category | Description | Examples |
|----------|-------------|---------|
| `data-accuracy` | Wrong facts, numbers, dates, or stale information | Incorrect meeting time, wrong person's title |
| `tool-misuse` | Used the wrong tool, wrong parameters, or skipped a better tool | Searched wrong calendar, missed an MCP server |
| `routing-error` | Routed to wrong agent or handled work that should have been delegated | Chase question handled by Chief |
| `format-violation` | Output didn't follow IES conventions or style rules | Wrong file naming, prose instead of bullets |
| `missed-context` | Failed to read or incorporate available context | Didn't check delegation tracker, skipped identity file |
| `assumption-error` | Made an incorrect assumption instead of checking | Guessed a date, assumed a preference |
| `process-skip` | Skipped a required step in a workflow or protocol | Didn't snapshot before evolution, skipped pre-brief |
| `hallucination` | Generated information that doesn't exist in any source | Made up a meeting, invented a contact |
| `over-engineering` | Did more than asked, added unnecessary complexity | Added features not requested, over-explained |
| `under-delivery` | Incomplete response, missing pieces the executive expected | Answered half the question, forgot follow-ups |

## Failure Modes

Reusable root cause labels (used in `failure_mode` field):

- `lazy-search` — didn't look hard enough before answering
- `stale-cache` — relied on old information instead of re-reading
- `wrong-assumption` — guessed instead of checking
- `sloppy-read` — misread or skimmed a source
- `bad-conversion` — math, date, or unit error
- `tool-ignorance` — didn't know or forgot a tool existed
- `context-blindness` — available context was ignored
- `pattern-mismatch` — applied a wrong mental model to the situation
- `scope-creep` — expanded beyond what was asked
- `protocol-skip` — knew the step, skipped it anyway

## Severity Levels

| Level | Criteria |
|-------|----------|
| `minor` | No impact on executive's decisions or time; caught immediately |
| `moderate` | Required executive intervention to correct; wasted some time |
| `major` | Could have led to wrong decisions, missed commitments, or external impact if not caught |

## Pattern Structure

When Rigby analyzes the log, recurring patterns are stored separately (not in `entries/`):

```json
{
  "pattern_id": "pat-NNN",
  "category": "error category",
  "failure_mode": "root cause",
  "occurrences": 3,
  "entry_ids": ["err-...", "err-...", "err-..."],
  "first_seen": "ISO date",
  "last_seen": "ISO date",
  "proposed_fix": "description of systemic fix",
  "fix_type": "rule | skill-update | workflow-update | agent-update | training-module",
  "fix_status": "proposed | approved | applied | deferred"
}
```
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
