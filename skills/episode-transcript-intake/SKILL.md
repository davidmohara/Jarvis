---
name: episode-transcript-intake
owning_agent: harper
model: sonnet
trigger_keywords: [episode intake, podcast to pipeline, turn this episode into a campaign, campaign brief, ingest episode]
trigger_agents: [harper]
description: >
  First step of the Podcast-to-Pipeline pipeline. Takes a podcast episode reference
  (public URL or internal Improving Edge episode already in Obsidian) and produces a
  clean transcript plus episode metadata for downstream pain-point extraction. Never
  called standalone in normal use — invoked by workflows/episode-campaign-brief/workflow.md
  step 01, but callable directly for testing or re-intake.
---

<!-- system:start -->
# Episode Transcript Intake

## Purpose

Turn a podcast episode reference into a clean transcript and structured episode
metadata that `pain-point-extraction` can consume. This skill does not analyze
content — it only retrieves and normalizes it.

## Input

One of:
- A public URL (YouTube, Apple Podcasts, Spotify, RSS/show website)
- An internal reference to an already-captured Improving Edge episode (episode number,
  title, or a pointer to an existing Obsidian note under `Podcasts/`)

## Output

A structured object (held in working memory / passed to the caller, not necessarily
written to disk unless requested):

```yaml
episode:
  title: ...
  episode_number: ... (if known, e.g. "EP047")
  guest: ... (if any)
  date: ...
  source: "public-url" | "internal-improving-edge"
  source_url: ... (if public)
  obsidian_note_path: ... (if internal or if a new Source Note was created)
transcript: |
  {full transcript text, speaker labels preserved if present}
```

## Process

1. **Determine source type.**
   - If given a URL → public source path.
   - If given an episode number, title, or explicit reference to an internal
     Improving Edge episode → internal source path.
   - If ambiguous, ask: "Is this a public episode URL, or an Improving Edge episode
     already recorded internally?"

2. **Public URL path.** Reuse the exact retrieval mechanics from
   `skills/podcast-transcript-extract/SKILL.md` (YouTube transcript panel, Apple
   Podcasts episode page, Spotify transcript tab, RSS/show site scraping via
   `mcp__Control_Chrome__*`). Do not duplicate that logic — read and follow that
   skill's Execution section to retrieve the raw transcript and episode metadata.
   Do not write the Obsidian Source Note that `podcast-transcript-extract` normally
   writes unless the controller explicitly wants one archived — this skill's job
   ends at "clean transcript in hand," not "vault entry created."

3. **Internal Improving Edge path.** Search `Podcasts/` in Obsidian
   (`mcp__obsidian-mcp-tools__search_vault` or `list_vault_files`) for a note matching
   the episode reference. If found, read it and extract:
   - Transcript body (verbatim content section, per the Source Note structure used by
     `obsidian-source-note`)
   - Metadata: title, guest, date, episode number (parse from filename/header if not
     in a dedicated field)
   If the episode was recorded but not yet transcribed/captured to Obsidian, check
   Plaud staging per `plaud-discover`/`plaud-transcripts` conventions before giving up.

4. **Normalize.** Strip any HTML/markdown artifacts from the transcript. Preserve
   speaker labels where present. Do not summarize or truncate — pain-point-extraction
   needs the full text.

5. **Return the structured object** above to the caller (typically
   `workflows/episode-campaign-brief/workflow.md` step 01).

## Failure Modes

| Failure | Action |
|---------|--------|
| URL unreachable / paywalled | Report which step failed (fetch, transcript panel, RSS lookup) and stop. Do not fabricate a transcript. |
| Internal episode not found in Obsidian or Plaud | Ask the controller for the correct episode reference or a direct URL/upload. |
| Transcript exists but is auto-generated and low quality (garbled names, no punctuation) | Proceed but flag: "This transcript is auto-generated and may have transcription errors — pain-point extraction quotes should be spot-checked against source." |
| Episode has no guest / is a solo episode | Fine — `guest` field is optional, proceed normally. |

## SKILL COMPLETE

After the transcript + metadata object is returned to the caller, write the
skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/episode-transcript-intake-latest.json
```

Content:
```json
{
  "skill": "episode-transcript-intake",
  "agent": "harper",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

**Eval-harness exception:** if this invocation is an eval-harness executor run (simulating this skill for grading, benchmarking, or testing rather than a genuine Harper-invoked production run), do NOT write this signal file. Writing it from a simulation would falsely register a live skill run in the production eval-harness tracking system. Only write it when this is an actual production invocation.

Set `trigger` to `"boot"` if called from a boot workflow, `"scheduled"` if called
from a scheduled task, `"manual"` otherwise (including when called as a workflow
step — the workflow itself is manually or explicitly triggered). Set `status` to
`"partial"` if the transcript was retrieved with quality caveats, `"failure"` if
retrieval failed entirely. Use the actual start time for `started`. This write is
always the final action.
<!-- system:end -->
