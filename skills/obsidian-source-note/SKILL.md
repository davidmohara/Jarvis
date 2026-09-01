---
name: obsidian-source-note
owning_agent: harper
model: sonnet
trigger_keywords: [save to obsidian, obsidian note, source note, save research, save podcast notes, save article notes, talk research, reference note]
trigger_agents: [harper, knox, chief]
description: >
  Write a structured Source Note to Obsidian from any content type (podcast, article, video,
  book). Applies the Source Note template (Tags block at bottom), writes verbatim transcript
  or raw content, and appends a Key Concept Summary section. Use when David asks to save
  a podcast, article, or source for future reference — especially when building toward a
  talk, post, or deliverable. NOT for Plaud or Teams meeting transcripts (use those skills).
---

<!-- system:start -->
# Obsidian Source Note

Save any researched content to Obsidian as a structured Source Note. The output is a
reference file David can return to when building a talk, post, or deliverable.

## Output Structure

Every Source Note has three sections, in this order:

1. **Header block** — source metadata (title, URL, guest/author, date, purpose)
2. **Verbatim content** — full transcript or raw article text, as close to verbatim as
   extraction allows. Label auto-generated transcripts as such. Speaker labels preserved.
3. **Key Concept Summary** — extracted concepts, frameworks, metaphors, and talk angles.
   Each concept gets: a name, a 2–4 sentence explanation, and a "talk angle" note if
   the content was captured for a talk or deliverable.
4. **Tags block** — Source Note template tags (see below). Always last.

---

## Tags Block (mandatory, always at bottom)

Read the template at `Templates/Source Note.md` before writing any note. The tags block
must match this structure exactly:

```
#### Tags
Source Type: {Book | Post | Video | Podcast}
Author: [[{Author Name}]]
Domain(s): [[{Domain 1}]], [[{Domain 2}]], ...
Note Type: [[Source Notes]]
Link: {URL}
Status: {Captured | In Progress | Processed}
Recommendation: {strength and relevance note}
Motive: {why David captured this — what he's building toward}
Rediscovery: [[{Topic 1}]], [[{Topic 2}]], ...
Date Created: [[{YYYY-MM-DD}]]
```

**Domain(s):** Pick 2–5 from David's actual knowledge domains. Common ones:
AI, Financial Services, Leadership, Technology Consulting, Business, Speaking,
Health, Personal Development, Improving, Systems Thinking, Culture

**Rediscovery:** WikiLink to topics this note should surface under. Think: what will
David be working on when he needs to find this? Use project names, talk topics,
domain areas, and agent names where relevant.

---

## File Location and Naming

**Default vault location:** `Research/Talks/` for talk-building content,
`Podcasts/` for general podcast captures, `Mind/` for reading/thinking notes.

Ask David or infer from the stated motive (e.g., "building a talk" → `Research/Talks/`).

**Filename:** `{Topic} - {Guest/Author} {Source Type}.md`
Examples:
- `AI in Financial Services - Shectman Podcast.md`
- `Context Singularity - Elephant Ventures Article.md`

---

## Execution

### Step 1: Gather the content

Use the appropriate extraction method for the source type:
- **Podcast (Spotify):** Follow `skills/podcast-transcript-extract/SKILL.md` → Step 3d
- **Podcast (YouTube):** Follow `skills/podcast-transcript-extract/SKILL.md` → Step 3a
- **Podcast (Apple):** Follow `skills/podcast-transcript-extract/SKILL.md` → Step 3b
- **Article/Post:** `mcp__workspace__web_fetch(url="{url}")`. If blocked, try WebSearch
  for mirroring sites (Archive.org, cached versions, RSS feeds, Substack reader).
- **Video (non-podcast):** YouTube transcript method from podcast-transcript-extract.

**Self-recovery for blocked URLs:**
1. Try direct web_fetch
2. Search for transcript/summary on mirror sites: `site:podscribe.app`, `site:listennotes.com`,
   `site:podchaser.com`, `site:buzzsprout.com`, transcript aggregators
3. Search for the title + "transcript" or "summary"
4. Open in Chrome via Claude in Chrome tools
5. Only ask David for help if all four methods fail

### Step 2: Extract Key Concepts

Read `identity/CONTENT-VOICE.md` before writing the Key Concept Summary — it governs
what David finds useful vs. generic. Then extract:

- **Frameworks** — named models, rubrics, decision tools the source introduces
- **Metaphors** — vivid analogies worth borrowing for a talk or post
- **Statistics/data points** — concrete numbers that anchor arguments
- **Contrarian claims** — positions that challenge consensus
- **Terminology** — new or precise language worth adopting
- **Talk angles** — how each concept connects to David's delivery context

Each concept entry:
```
### {N}. {Concept Name}

{2–4 sentences: what the concept is, why it matters, what makes it useful}

**Talk angle:** {How David might use this in a FS+AI talk, post, or conversation}
```

### Step 3: Write the Obsidian note

```
mcp__obsidian-local__create_vault_file(
  filename="{vault_location}/{filename}.md",
  content="{full note content}"
)
```

### Step 4: Append the Tags block

Use `mcp__obsidian-local__patch_vault_file` to append the tags block after the last
heading in the file:

```
mcp__obsidian-local__patch_vault_file(
  filename="{vault_location}/{filename}.md",
  target="{last heading in the file}",
  targetType="heading",
  operation="append",
  content="\n\n---\n\n#### Tags\n..."
)
```

### Step 5: Verify

```
mcp__obsidian-local__get_vault_file(filename="{vault_location}/{filename}.md")
```

Confirm: file exists, transcript is non-empty, Key Concept Summary has at least 3 entries,
Tags block is present at the bottom with all fields populated.

---

## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file:

```
systems/eval-harness/skill-runs/obsidian-source-note-latest.json
```

Content:
```json
{
  "skill": "obsidian-source-note",
  "agent": "harper",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"scheduled"` if called from content-pipeline, `"manual"` otherwise.
<!-- system:end -->

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill obsidian-source-note
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/obsidian-source-note.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
