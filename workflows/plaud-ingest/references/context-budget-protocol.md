# Context Budget Protocol — plaud-ingest non-no-op runs

Loaded by step-03 and step-05 on any run where `new-recordings` is non-empty.
If the no-op preflight exited early, this protocol never runs and costs nothing.

## Why this exists

On ingest days (2026-10-27, 2026-10-28) the Knox agent spent ~10.4M input
tokens, with late steps re-carrying ~8.8M: transcripts read in step-03 (self-ID
scans) and step-05 (parse + note composition) stayed in conversation context and
were re-sent on every subsequent turn (boot token analysis, 2026-10-28,
follow-up 5). The invariant below removes the driver, not the symptom.

## The invariant

**No transcript body ever enters the Knox agent's conversation context.**
A transcript body is:

- a staged `plaud_*.md` read in full (Read, Bash cat, MCP file read)
- a vault note's `<details>` transcript block (vault notes carry the full
  transcript — reading a zzPlaud note raw loads it)
- transcript text pasted into prompts, reports, or state.yaml

**Allowed bounded reads:** the staged file's metadata header (everything above
the `## Transcript` heading — title, date, duration, the AI summary's first
~900 chars) may be inspected directly when a field is needed that the broker
does not surface (e.g. hunting for a recording start time). Transcript
segments below that heading are never read directly, by any tool.

Everything the agent needs to judge (speaker identity, action items, summary
style, routing) is available as bounded evidence from the broker script:
`skills/plaud-transcripts/scripts/context_tools.py` (stdlib, run with
`/usr/bin/python3`).

## Broker commands

| Need | Command |
|------|---------|
| Speaker self-ID evidence + calendar context (step-03) | `context_tools.py speaker-evidence <staged.md> [--max-bytes 12000]` |
| Action-item candidates, all speakers (step-05) | `context_tools.py action-candidates <staged.md> [--max-bytes 8000]` |
| Write vault note (transcript verbatim + renames) + transcript-free digest | `context_tools.py assemble-note <staged.md> --target <vault path> --file-id <id> [--speakers '<JSON>'] [--tags '<JSON>'] [--force] [--dry-run]` |
| Re-read a vault note without its transcript (Gate 5, 7-day cross-ref) | `context_tools.py note-digest <note path(s) or glob> [--max-bytes 6000]` |

Outputs are bounded JSON/text to stdout; diagnostics go to stderr. The agent
runs each command once, reads the bounded output, and moves on. Evidence
outputs need not be persisted — resolutions and candidates land in
`state.yaml` `accumulated-context` and the note itself.

## What each step does with it

- **step-03:** self-ID scan = `speaker-evidence` output (self-ID candidates,
  opening/closing utterances, addressed-name mentions, topic context). The
  script scans every segment mechanically; `scan.segments_scanned ==
  scan.total_segments` is the proof the full transcript was searched. The
  scan mandate from the error log (lazy speaker-ID escalations,
  err-20260909T010719-0BCW7C et al.) is satisfied by the script's full pass —
  a bounded excerpt skim by the agent does NOT satisfy it, and neither does
  skipping the script and eyeballing `sample_text`.
- **step-05:** per recording — `action-candidates`, then `assemble-note`
  (speaker renames applied at assembly), then fill the `<!--FILL:...-->`
  placeholders via bounded Edits using the digest, then Gate 5 re-read via
  `note-digest`, then daily-note link, then Monday routing from the
  candidates list. The 7-day calendar cross-ref scans recent `zzPlaud/`
  notes via `note-digest`, never raw Reads.

## Fallback ladder (never blocks ingestion)

The broker is new; treat its failure like any tool failure, not a workflow
blocker:

1. Retry the command once (transient error).
2. If it still fails: for that single recording you MAY fall back to the
   pre-protocol path (read the staged file, compose the note in context).
   Required when you do: increment
   `accumulated-context.context-budget.transcript-body-reads`, write the
   reason into `context-budget.fallback-reasons`, log an error-log entry
   (category `tool-failure`, related_skill `plaud-transcripts`), and surface
   the overage in the final report. A silent fallback is a protocol violation.
3. Process remaining recordings through the broker normally.

## State schema addition

```yaml
accumulated-context:
  context-budget:            # initialized at step-01 on non-no-op runs
    evidence-extractions: 0   # count of broker evidence runs (speaker-evidence + action-candidates)
    transcript-body-reads: 0  # full transcript bodies read into conversation; target 0
    fallback-reasons: []      # one string per fallback read
```

## Gotchas

- **Degraded Plaud rename mode** (2026-10-28): PATCH + `is_reload`
  regeneration can return 200 yet leave generic `Speaker N` labels in the
  staged file. Real names must come from `speaker-mappings` and be applied by
  `assemble-note --speakers`, not expected in the staged text.
- **List-endpoint duration bug**: some staged files carry milliseconds in
  `**Duration:** NNNNs`. The broker normalizes values > 7200 to seconds; do not
  hand-correct.
- **Vault notes are transcript carriers.** Gate 5 and any cross-reference read
  must go through `note-digest` — a raw re-read of a just-written note reloads
  the transcript and defeats the budget.
- **AI summaries can be multi-KB.** The digest caps the excerpt (~900 chars);
  the full summary stays in the staged file for the note transform, where
  `assemble-note` already carries it.

## Verification loop

- After step-03/05, confirm `context-budget.transcript-body-reads: 0` in
  state.yaml (non-zero means a fallback ran — check `fallback-reasons`).
- Gate 5 must still pass per note; `verify/ingest-reconcile.py` must still
  exit 0 on the run.
- Expected shape on the next non-no-op day: main-agent input well under half
  the 10.4M baseline, windowed late steps no longer flat at ~8.8M. If
  late-step re-carriage still exceeds ~2M after this ships, the queued
  follow-up is a per-recording subagent split for step-05 (each ingest
  subagent loads one transcript and returns a compact result), which is a
  redesign — do not attempt it inline in a run.
