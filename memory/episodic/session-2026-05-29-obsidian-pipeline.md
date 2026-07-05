---
type: working-archive
task_id: obsidian-pipeline-build
created: 2026-05-29
archived-from: memory/working/session-2026-05-29-obsidian-pipeline.md
context: obsidian-source-note skill build, Spotify transcript extraction, content-pipeline
  routing, eval harness assertions
salience:
  score: 0
  last_scored: 2026-07-05
  last-promoted-check: 2026-07-05
  promoted: false
---

# Session Working Memory — 2026-05-29 (Evening)

## What Was Built

### 1. obsidian-source-note skill (`skills/obsidian-source-note/SKILL.md`)
New skill for saving any content (podcast, article, video, book) as a structured Obsidian Source Note. Output format: header block → verbatim transcript → Key Concept Summary with talk angles → Tags block matching `Templates/Source Note.md`. Owned by harper. Not for Plaud/Teams transcripts (those have their own skills).

### 2. podcast-transcript-extract skill — Spotify support added
Added Step 3d for Spotify extraction. Requires logged-in Chrome. Method:
1. `select_browser` + `tabs_context_mcp` to get active Spotify tab
2. `javascript_tool`: `document.querySelector('[data-testid="transcript-tab"]').click()`
3. Start local Python HTTP server on port 9876: `python3 -c "import http.server..."`
4. Browser JS: `fetch('http://127.0.0.1:9876', {method: 'POST', body: fullText})`
5. Read `/tmp/spotify_transcript.txt`, kill server
- **Known issue:** Chrome extension context expires between JS calls on Spotify's heavy JS page. Fix: call `select_browser` + `tabs_context_mcp` before each tool call sequence.
- **Known issue:** Spotify may show a permission popup on first load. Re-run after dismissing.

### 3. content-pipeline step-01-discover.md — routing table
Added routing logic before blog processing. Key signals:
- "save to obsidian" / "source note" / "for a talk" / "reference" → obsidian-source-note skill
- "PowerPoint" / "slides" / "deck" → Flag for manual handling, notify in #content
- Default / "draft a post" → standard blog pipeline
Also added URL normalization rule: strip `?si=`, `?mod=`, `?ref=` tracking params before dedup checks.

### 4. Eval harness — obsidian-source-note assertions
New assertion file: `systems/eval-harness/assertions/obsidian-source-note.json`
15 assertions covering: file-exists, file-min-bytes, transcript present + non-empty, Key Concept Summary with numbered concepts and talk angles, Tags block with all required fields (Source Type, Author wikilink, Domain wikilinks, Link URL, Motive, Date Created).

### 5. read.py — retry on silent empty
`systems/slack-bot/read.py` now retries with 2x time window when Slack API returns `ok: true, messages: []`. Emits a warning in stderr and surfaces a warning key in the JSON payload if retry also returns empty. Fixes the critical silent failure observed at ~8pm this session (err-20260529T200913-OZ7D7N).

## Key Eval Run
`systems/eval-harness/runs/eval-20260529T224500-ypo001.json` — 15/15 assertions passed for YPO ep 74 note.

## Obsidian Note Written
`Research/Talks/AI Agent Accountability - YPO Tech Network Podcast.md`
Source: YPO Technology Network AI Brief Ep. 74, host Stephen Forte
Key themes: agent misbehavior (Pocket OS, Replit incidents), academic study showing systematic deception, Yoshua Bengio Singapore speech, enterprise governance framework.

## Deck Built
`presentations/agent-receipts.pptx` — 5-slide dark-theme deck on AI agent accountability incidents. For use in YPO/Improving talks. Not in Obsidian — local presentations/ directory only.

## Patch Pitfall — patch_vault_file
`patch_vault_file` with `targetType="heading"` appends inside the section but will create duplicate headings if the section already has content at the end. Workaround: use `create_vault_file` (which overwrites) when restructuring an existing note rather than patching repeatedly.

## pptxgenjs Pitfalls Encountered
- Shadow objects must be created fresh per shape — pptxgenjs mutates option objects in-place, corrupting second+ uses of the same object. Use a factory function: `const mkShadow = () => ({...})`.
- No `#` in hex colors — causes file corruption.
- `ROUNDED_RECTANGLE` breaks with rectangular accent overlays — use `RECTANGLE`.

## Manifest
`skills/_manifest.jsonl` — obsidian-source-note entry added 2026-05-29 (was missing at time of session close).
