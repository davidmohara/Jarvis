# Error Tracking Schema

<!-- system:start -->
## Entry Structure

Each entry in `error-log.json` follows this schema:

```json
{
  "id": "err-YYYYMMDD-NNN",
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
  "related_entries": ["err-YYYYMMDD-NNN"]
}
```

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

When Rigby analyzes the log, recurring patterns are stored:

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
