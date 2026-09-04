---
status: complete
started-at: "2026-09-04T18:00:00Z"
completed-at: "2026-09-04T18:15:00Z"
outputs:
  messages_scanned: 1
  new_urls: 0
  new_digests: 0
  posts_drafted: 0
  gate_1_result: "PASS"
  gate_2_result: "N/A"
  editorial_threads_checked: 13
  editorial_feedback_found: 0
model: sonnet
---

<!-- personal:start -->
# Step 01: Content Discovery & Draft

## MANDATORY EXECUTION RULES

0. You MUST use `mcp__Desktop_Commander__start_process` for read.py/post.py, never a sandboxed bash/shell tool (e.g. Cowork's `mcp__workspace__bash`). The sandbox has no general outbound network access and will fail Slack calls with a connection/tunnel error. If that happens, do not conclude Slack or the network is down, retry via Desktop Commander first. See err-20260715T134905-DAGK1T.
1. You MUST read the full workflow.md before executing — it contains Ghost conventions, tag IDs, voice rules, and channel IDs.
2. You MUST check pending-drafts.json (at `workflows/content-approval/pending-drafts.json` — see STATE TRACKING in workflow.md) and dedup against existing posts before drafting anything.
3. You MUST NOT create new Ghost tags. Only use tags from the locked list in workflow.md.
4. You MUST set status: draft on Ghost — never published.
5. You MUST upload the image to Ghost CDN before setting it on the post.
6. You MUST write the pending draft entry to pending-drafts.json after successful Ghost creation.
7. You MUST notify David via post.py (Jarvis bot) — not the Slack MCP connector.
8. You MUST set content_type on every pending-drafts.json entry — "post" or "article". Never omit it.
9. You MUST scan pending draft threads for editorial feedback before processing new content (Step 1b).
10. You MUST NOT proceed past GATE 1 or GATE 2 below if either fails its HARD criteria.

Before executing, write `status: in-progress` and `started-at` to this file's own frontmatter.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Trigger:** Runs daily at 6am via scheduled task
**Input:** #content Slack channel (last 24 hours)
**Output:** Ghost draft post + Slack notification with review instructions

---

## YOUR TASK

### 1. Read the channel

Use read.py via Desktop Commander to pull #content messages from the last 24 hours:

```
Tool: mcp__Desktop_Commander__start_process
Command: python3 "/Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES/systems/slack-bot/read.py" channel C0B160MA3EK 24 2>&1
Timeout: 15000
```

---

## QUALITY GATE 1 — Source Integrity (HARD, BLOCKING)

Run immediately after the read.py call above, before parsing or routing any message.

**Purpose:** Everything downstream — routing, drafting, dedup — depends on this pull actually having reached the right channel and returned real data. A silent tunnel failure or wrong-channel response must not be treated as "no new content."

| Check | Expected | On failure |
|-------|----------|------------|
| Command exit / stdout is non-empty | Non-empty JSON string returned | **STOP.** Do not conclude "no messages" — this looks like a tool/network failure. Retry via `mcp__Desktop_Commander__start_process` per MANDATORY EXECUTION RULE 0 before reporting. |
| Response parses as valid JSON | `json.loads` succeeds | **STOP.** Report the raw response and abort this run. Do not attempt to draft from unparseable output. |
| `ok` field is `true` | `{"ok": true, ...}` | **STOP.** If `ok: false`, capture the `error` field verbatim and report failure per FAILURE MODES below. Do not retry blindly more than once. |
| `messages` field is present and is a list (possibly empty) | `isinstance(messages, list)` | **STOP.** A missing or non-list `messages` field means the API contract broke or the wrong endpoint/channel was hit. |
| Channel ID in the request matches C0B160MA3EK | Literal string match against the command issued | **STOP.** If the channel ID was altered anywhere upstream, abort — do not draft from the wrong channel's content. |
| No garbage/binary payload in message `text` fields | Spot-check: at least the first message's `text` is printable UTF-8 | **STOP.** A garbled payload indicates a transport-layer problem (see err-20260715T182916-FSMOJK class of failures); do not attempt to parse it as content. |

An empty `messages` array (`{"ok": true, "messages": []}`) is a legitimate PASS — it means no new content in the last 24 hours, not a failure. Proceed to exit cleanly per the MESSAGE ROUTER's "no messages route" rule.

Log the result:
```
[Gate 1] Channel: C0B160MA3EK
[Gate 1] Response ok: true|false
[Gate 1] Messages returned: N
[Gate 1] PASS — proceeding to message routing.
```

If it fails, log `[Gate 1] FAIL — <check name>` and follow FAILURE MODES ("read.py fails") before any further processing.

Parse the JSON response — `{"ok": true, "messages": [...]}`. Each message has `ts`, `user`, `text`, `thread_ts`, and optionally `bot_id`.

Skip messages where `thread_ts != ts` — those are thread replies handled by content-approval.

For all remaining messages, apply the router below to each one before doing anything else.

---

### 1b. Scan pending draft threads for editorial feedback

After reading the channel, read `workflows/content-approval/pending-drafts.json`. For every entry with `status: pending` and a non-null `slack_thread_ts`, fetch the thread replies:

```
Tool: mcp__Desktop_Commander__start_process
Command: python3 "$(mdfind -name 'read.py' | grep 'systems/slack-bot/read.py' | head -1)" thread C0B160MA3EK {slack_thread_ts} 2>&1
Timeout: 15000
```

For each thread, examine the replies from human users (skip bot messages). Apply this router to each human reply:

**APPROVE/REJECT → skip** (keywords: "approve", "approved", "reject", "rejected", "looks good", "publish"). These are handled by content-approval. Do not process here.

**EDITORIAL FEEDBACK → execute the DRAFT EDIT PATH** (any reply that describes a change to make: "change X", "update X", "rewrite X", "fix X", "make it X", "add X", "remove X", "too long", "too short", "wrong tone", etc.)

Only process replies that arrived in the last 24 hours (compare reply `ts` to now). Skip older replies — they were either already handled or are stale.

If a reply has already been acted on, skip it. Track handled replies by adding an `editorial_edits` array to the pending-drafts.json entry (see DRAFT EDIT PATH below).

---

### DRAFT EDIT PATH

Execute this section when a pending draft thread contains editorial feedback.

**A. Fetch the current post from Ghost and verify draft status**

Use `mcp__ghost-blog__get_post(post_id="{ghost_post_id}")` to retrieve the post. Extract the `status`, `lexical` content, and `updated_at` timestamp.

If `status` is not `"draft"` (i.e., the post is published or scheduled), do NOT apply any edits. Reply in the thread:

```
"_Skipped — '{Post Title}' is already published. Edit it directly in Ghost._"
```

Then move on to the next pending draft. Only proceed with the edit if `status == "draft"`.

**B. Read the editorial instruction**

Parse what the reply is asking for. Categories:

| Instruction type | Action |
|-----------------|--------|
| Rewrite a specific section | Rewrite that section in David's voice (CONTENT-VOICE.md) |
| Change tone, length, or focus | Apply the change across the affected paragraphs |
| Add or remove specific content | Insert or delete the relevant text |
| Image swap | Follow the Step 6 image protocol, then update `feature_image` and `twitter_image` |
| Other structural change | Apply using best judgment; note what changed in the thread reply |

**C. Apply the edit**

Before writing: read `identity/CONTENT-VOICE.md` if the edit touches post body content.

Rebuild the affected lexical nodes. For full rewrites, rebuild the entire lexical body. For targeted edits, locate and replace only the affected paragraph nodes.

Use the Ghost Admin API PUT (same JWT pattern as Step 7) to update the post. Use PUT with no trailing slash — PATCH returns 404:

```
PUT https://driventodevelop.com/ghost/api/admin/posts/{ghost_post_id}
Authorization: Ghost {jwt}
Content-Type: application/json

{
  "posts": [{
    "lexical": "{updated_lexical_json_string}",
    "updated_at": "{current_updated_at}"
  }]
}
```

For image-only updates, PATCH `feature_image` and `twitter_image` (and `updated_at`) without touching `lexical`.

**D. Verify**

Call `mcp__ghost-blog__get_post` to confirm the edit landed. Check that `lexical` reflects the change and `updated_at` advanced.

**E. Reply in the thread**

Post a confirmation reply to the same Slack thread via post.py:

```
python3 "$(mdfind -name 'post.py' | grep 'systems/slack-bot/post.py' | head -1)" C0B160MA3EK "_Done — {brief description of what changed}. Draft updated._" {slack_thread_ts} 2>&1
```

**F. Update pending-drafts.json**

Add or append to the `editorial_edits` array on the entry:

```json
"editorial_edits": [
  {
    "reply_ts": "{ts of the feedback reply}",
    "instruction": "{brief summary of what was requested}",
    "applied_at": "{ISO timestamp}",
    "summary": "{brief description of what changed}"
  }
]
```

This prevents the same reply from being re-processed on the next run.

---

### MESSAGE ROUTER — apply in priority order

Evaluate each message against the following rules in sequence. Stop at the first match.

```
1. Bot message WITHOUT digest signal AND WITHOUT Watchtower section keywords  →  SKIP (operational noise)
2. Bot message WITH digest signal (# + ##) OR Watchtower section keywords (*Hook*, *Story Angle*/*Core Insight*, *Challenge*/*CTA*)  →  DIGEST PATH
   NOTE: Watchtower drafts ALWAYS route to DIGEST PATH. They use *bold* headers, not ## markdown. Never skip them. (err-20260727T201106-MOE539)
3. User message WITH routing keywords    →  OBSIDIAN ROUTE
   (keywords: "save to obsidian", "save as a note", "for a talk", "reference",
    "do not draft a post", "don't draft a post")
4. User message WITH (# + ##) headers   →  DIGEST PATH
4.5. User message WITH "article" keyword (case-insensitive) AND URL  →  URL PATH (content_type: "article")
4.6. User message WITH Improving blog keywords AND URL  →  IMPROVING BLOG PATH
   (keywords: "improving thoughts", "improving blog", "improving's blog", "improving thought leadership",
    "not one for my blog", "not my blog")
5. User message WITH URL, no routing keywords  →  URL PATH
6. User message with deck/slides/presentation/PowerPoint  →  MANUAL FLAG
7. User message referencing an existing post with editorial instructions (no URL, no digest signal)  →  EDITORIAL EDIT PATH
   (keywords: "change the image", "update the image", "add the link", "add a link", "change image",
    "swap image", "replace image", "fix the image", "update the post", "edit the post")
```

**Detection rule for digest signal:** A message matches ANY of these patterns:
- Has `# ` AND `## ` — an H1 title line and at least one H2 section header (standard markdown digest)
- Is a bot message containing all four Watchtower section keywords in bold: `*Hook*` (or `*Hook*\n`), `*Story Angle*` or `*Core Insight*`, and `*Challenge*` or `*CTA*` — these are Watchtower drafts and are ALWAYS processed, never skipped

> **CRITICAL — err-20260727T201106-MOE539:** Watchtower bot messages use `*Bold*` section headers, not `## ` markdown. The old detection rule missed them entirely and skipped them as "operational noise." This is wrong. Watchtower drafts are NEVER noise. If a bot message contains Hook + Story/Insight + Challenge in any header format, it is a digest and must be drafted.

**For SKIP:** Do nothing. Move to next message.

**For OBSIDIAN ROUTE:** Execute `skills/obsidian-source-note/SKILL.md` inline. Read the full skill before acting. Use Spotify extraction (Step 3d in podcast-transcript-extract) for Spotify URLs. After saving the note, notify David in #content:
```
"_Saved to Obsidian: [{Note Title}] — {vault_path}_"
```

**For MANUAL FLAG:** Post to #content:
```
"_@david — [{source title}] needs manual handling: {brief reason}. I can't process this automatically._"
```

**For IMPROVING BLOG PATH:** Draft an Improving thought-leadership post from the URL and save it locally. Do NOT post to Ghost. Do NOT add to pending-drafts.json. Execute the IMPROVING BLOG PATH section below.

**Prior-post linking (DIGEST PATH and URL PATH):** After drafting, scan the post body for references to prior posts, recurring themes, or named figures/numbers that appeared in a recent post. Check `pending-drafts.json` titles and Ghost published post slugs for thematic matches. If a clear callback exists, insert an inline hyperlink on the most natural anchor text before submitting to Ghost. Do not wait for David to ask. This is mandatory when the digest itself signals a "step two" or "prior week" relationship. (err-20260727T201700-2H2GW4)

> **CRITICAL — err-20260820T191921-BLD5R9:** Never strip or drop links. If a referenced post is published, resolve it to a real URL using the Ghost post list (url field, not tag URLs) and build a proper lexical link node. Only skip linking if the referenced post is still in draft status. Dropping a link and leaving plain text is always wrong. Use the `url` field from `get_posts` results — not the slug — as the canonical URL.

**For EDITORIAL EDIT PATH:** Execute the edit inline. Do not defer to Jarvis Master. Do not flag to #content. Handle it directly:

1. **Identify the target post.** Match the post name from the message to a Ghost draft or published post. Use `mcp__ghost-blog__get_posts` or search by slug if needed.
2. **Image swap:** If the instruction is to change the image, find a new Unsplash image following the Step 6 protocol (WebSearch → fetch photo page → extract ID → construct CDN URL). Upload via `mcp__ghost-blog__upload_image_from_url` if available; fall back to direct Unsplash URL if upload fails. Update the post via Ghost Admin API (same JWT pattern as Step 7) — PATCH to `/ghost/api/admin/posts/{id}/` with `{"posts": [{"feature_image": "{new_url}", "twitter_image": "{new_url}", "updated_at": "{current_updated_at}"}]}`.
3. **Link insertion:** If the instruction is to add a hyperlink to specific text, fetch the current post's `lexical` from Ghost, locate the target text node, wrap it in a link node, and PATCH the updated lexical back via Ghost Admin API.
4. **Confirm silently** by verifying the post via `mcp__ghost-blog__get_post` after the update. No Slack notification needed unless the edit fails.
5. **If the edit also includes a workflow update instruction** ("encode this in the workflow", "update the workflow"): apply the change to this file (step-01-discover.md) or workflow.md as appropriate, then confirm with a brief #content reply: `"_Workflow updated: {what changed}._"`

**For URL PATH and DIGEST PATH:** Continue to the relevant section below.

Do NOT treat non-blog messages as failed pipeline items. Route them correctly or flag them.

If no messages route to URL PATH or DIGEST PATH after evaluating all messages: exit cleanly. Do NOT post anything to #content.

---

### DIGEST PATH

Execute this section for any message (bot or user) that matched the digest signal.

**A. Parse the digest**

Extract the H1 line as the post title. Then extract content under each `##` section. Match sections by keyword — do not require exact header text:

| Keyword match | Maps to |
|--------------|---------|
| "hook" in header | Hook |
| "story" or "angle" in header | Story/Observation |
| "insight" in header | Insight |
| "challenge" or "cta" in header | Challenge/CTA |
| "source" in header | Sources (reference only) |

Strip leading/trailing whitespace from each section's content.

**B. Strip em-dashes**

Before drafting, replace all em-dashes (`—`, Unicode U+2014) in the extracted content with commas or periods, whichever reads more naturally in context. This is mandatory — Watchtower posts contain em-dashes and David's blog voice prohibits them.

**C. Handle Sources (if present)**

If a `## Sources` section exists, extract the URLs listed there. Fetch each URL with `mcp__workspace__web_fetch` for context only. Do not cite these sources in the post body. The source is a spark for context, not content to reference.

**D. Draft the post**

Before writing a single word: read `identity/CONTENT-VOICE.md` in full.

Map the parsed digest sections to the post arc:
- Hook section → post opening hook
- Story/Angle section → body (David's personal angle and observation)
- Insight section → insight paragraph
- Challenge/CTA section → closing challenge

For any section that is missing from the digest, Harper writes it from scratch using CONTENT-VOICE.md as the voice guide. The four post-arc elements (Hook, Story, Insight, Challenge) must all appear in the final post — no exceptions. **GATE 2 below checks this before Ghost creation.**

Apply all standard drafting rules from the URL PATH section:
- 300-500 words. No headers. No bullet points in body. Prose only.
- No em-dashes. Use commas, periods, or parentheses.
- The post must be David's voice and reaction — not a restatement of the digest content.
- End with a direct challenge or question to the reader.

Also draft at this stage: `meta_title`, `meta_description`, `twitter_title`, `twitter_description` (same rules as URL PATH).

**E. Continue with steps 5 onward (tag selection, image, GATE 2, Ghost creation, notify)**

After drafting from a digest, continue at **Step 5 (Select tags)** below. The digest path merges with the URL path at that point and follows the identical process through GATE 2, Ghost creation, pending-drafts.json write, and Slack notification.

In the pending-drafts.json entry, set:
```json
"source_type": "digest"
```

In the Slack notification teaser (Step 9), append `_(drafted from digest)_` on a new line after the teaser sentences.

---

### IMPROVING BLOG PATH

Execute this section when a message matched the IMPROVING BLOG PATH route (URL + Improving blog keywords).

This path runs the full improving-thought-leadership plugin workflow autonomously: topic-exploration logic → narrative-definition logic → blog-draft → smell-test → improving-guidance. The interactive steps (topic-exploration, narrative-definition) are executed inline by making autonomous choices from the source material — no clarifying questions are asked. The output is a publication-ready markdown file saved locally.

**Before any writing: read these three files in full:**
1. `/Users/davidohara/Library/Application Support/Claude/local-agent-mode-sessions/1f133084-7506-49f1-9119-507fb3342862/800e566d-bfe4-4a01-b24f-821196b81496/rpm/plugin_01LZNKsPzYFfeUaSpHEhXvAE/skills/blog-draft/references/voice.md` — Improving's credentialed authority voice (institutional "we", declarative, no personal "I")
2. `identity/CONTENT-VOICE.md` — David's personal blog voice (cadence, specificity, consulting vantage point, parenthetical asides, challenge-close structure)
3. The smell-test criteria from `skills/improving-thought-leadership:smell-test` — apply these actively while writing, not just as a later pass

**Voice synthesis rule:** The Improving institutional voice governs attribution ("we," "our teams," "across our engagements" — not "I"). David's CONTENT-VOICE.md governs everything else: sentence rhythm (short declarative kickers, longer builds), parenthetical asides, the consulting vantage point ("my teams build these things"), scene-setting specificity, warmth, and the challenge-close. The result should sound like David wrote it on behalf of Improving — not like a corporate press release and not like his personal diary. The clearest test: if you swapped the "we" to "I," would it read like one of his driventodevelop.com posts? If yes, the blend is right.

---

**A. Fetch and research the source (topic-exploration logic)**

1. Fetch the URL: `mcp__workspace__web_fetch(url="{url}")`. If it's a Spotify URL, run a WebSearch for the episode title to gather context — podcast pages don't yield transcripts via fetch.
2. Extract: core argument, key insight, memorable quote or verified stat, the "so what" for Improving's audience (technology leaders, engineering leaders, enterprise decision-makers).
3. Run a WebSearch for additional context if the source is thin — look for corroborating data, enterprise adoption patterns, or real-world consequences of the topic.
4. **Topic Brief (autonomous):** Derive the sharpest, most specific arguable claim from the source. Not "AI costs are rising" — something like "Organizations that skip human review in production agentic systems are treating a trust problem as a cost problem." This is the technical crux. Also determine: intended reader (enterprise tech or engineering leader), structural archetype (default: Problem → Diagnosis → Framework), and whether any Improving published case studies are relevant (check improving.com if the topic maps to a service line).

**B. Narrative Spec (narrative-definition logic)**

Derive autonomously — do not ask questions:

- **Locked thesis:** One declarative sentence that a smart, reasonable person could disagree with. Derived from the Topic Brief above.
- **Structural archetype:** Default to Problem → Diagnosis → Framework unless the source material clearly fits a different shape (postmortem, decision framework, pattern naming, false dichotomy correction).
- **H2 sequence:** 3-4 H2s that read as real questions or decisions the reader faces — never "Introduction" or "Conclusion." Derive from the thesis and source.
- **Real example:** Search Improving's published case studies (improving.com/case-studies or SharePoint if accessible) for a real anchor. If nothing matches, frame the illustrative scenario explicitly as illustrative — never dress up a hypothetical as real.
- **Closing action:** A concrete question or check the reader can bring to their own team. Derived from the thesis's implications.
- **Length:** 1,500-2,000 words.

**C. Write the draft (blog-draft)**

Write the full post to the locked Narrative Spec. Apply the blended voice throughout:

**From Improving's voice.md (non-negotiable):**
- Institutional first-person plural: "we," "our teams," "across our engagements" — never personal "I"
- Lead with the point, then support it. Short declarative kickers bracket longer builds.
- One idea per paragraph, fully landed (2-4 sentences). Let the real example breathe.
- H2s as real questions or decisions — not "Introduction" / "Conclusion"
- Include an executive bridge in every major technical section (what decision does this affect, what risk does it reduce, what does it cost if ignored)
- Numbers are precise and sourced. If a stat can't be verified, cut it or flag it as an estimate.

**From David's CONTENT-VOICE.md (applied to rhythm, texture, and structure):**
- Use David's Hook → Story/Observation → Insight → Challenge arc as the structural spine — even in a longer post, the opening earns the next sentence, the body carries the consulting vantage point, and the close asks something real of the reader.
- The consulting vantage point is the differentiator: "our teams build this" / "we see this in client environments" / "what the invoice doesn't say" — use it wherever the topic connects to Improving's delivery work. Not as a credential drop, as the ground the observation stands on.
- Parenthetical asides are natural and earned: "(and we've seen this kill timelines)" "(not the clean answer, but the honest one)" "(this one still stings a little)". They carry warmth and inner-voice texture. Don't force them, but don't scrub them.
- The close is a challenge or a direct question — never a summary, never "we hope this resonates." Ask something real of the reader.
- Warmth is present. Write to people, not at them. This is a senior colleague sharing something worth knowing, not a vendor white paper.

**Universal prohibitions (both voices):**
- No em-dashes. No contrast-negation scaffolding ("X is not Y. It is Z."). No filler transitions. No hollow affirmations. No mechanical parallel structure. No "y'all" in the Improving institutional voice (that's David's personal blog only).

Also write: `meta_title` (max 70 chars) and `meta_description` (max 155 chars).

**D. Self-check (smell-test logic)**

Before saving, scan the full draft against all ten smell-test categories:
1. Negation-template tic ("X is not Y. It is Z." and all variants) — highest priority
2. Mechanical parallel structure (3+ consecutive sentences/headers with identical shape)
3. Hollow affirmations
4. Over-qualification / throat-clearing ("It's worth noting that...")
5. Filler transitions ("Furthermore," "Moreover," "In conclusion")
6. Em dashes
7. Banned SEO clichés ("game-changer," "revolutionary," "unlocking," "delving into")
8. Fake-specific numbers (unverifiable statistics)
9. Generic triadic structures
10. Synonym sprawl

Grade the draft (A through F). If below B, remediate directly — rewrite flagged passages in Improving's voice, preserving the actual argument. Re-scan until B or better. Never pass a sub-B draft to the save step.

**E. Improving-guidance pass**

Attempt to fetch Improving's SharePoint framework docs via `mcp__b8c41a14-7a9b-4ea5-ab12-933ee04bc52f__sharepoint_search` (search for "Blog Writing Framework" and "SEO Writing Standards"). If accessible, apply the full checklist:
- Claims, Proof & Anonymization Rules
- Closing paragraph present and concrete
- Internal linking (one Improving service page, one sibling post if available)
- SEO / editorial structure (H1 present, stakes in first 250 words, no banned phrases)
- Voice attribution consistent (no stray personal "I")

If SharePoint is unreachable, apply the baseline checklist from memory (same rules) and note in frontmatter that improving-guidance SharePoint pass was skipped.

**F. Save locally**

Save the post-smell-test, post-guidance draft as a markdown file at:
```
/Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES/content/improving-blog/{YYYY-MM-DD}-{slug}.md
```
(This is the canonical location for unpublished Improving-blog drafts. A prior version of this step had a fallback path under a top-level `drafts/` directory at a stale, incorrect repo root — that directory has been retired; do not recreate it.)

Use `mcp__Desktop_Commander__write_file`. Frontmatter:
```yaml
---
title: "{Post Title}"
status: draft
audience: "Technology and engineering leaders in enterprise organizations"
source: "{source_url}"
meta_title: "{meta_title}"
meta_description: "{meta_description}"
created: {YYYY-MM-DD}
author: "Improving"
smell_test_grade: "{A/B/C...}"
pipeline_notes: |
  Drafted by Harper (content-discovery) from: {source_url}
  David's note: "{David's original message text}"
  Topic Brief: {one-sentence crux and intended reader}
  Narrative Spec: {thesis, structural archetype, real example note, closing action}
  Smell test: {grade} — {brief findings summary}
  Improving-guidance: {applied / SharePoint unavailable — baseline applied}
---
```

**G. Notify David in #content**

Post via post.py as a reply to the original message thread (use message `ts` as `thread_ts`):

```
*Improving Thoughts draft ready* ✍️

*"{Post Title}"*
_Smell test grade: {grade}_

{First 2-3 sentences of the draft as a teaser}

*Saved to:* {file_path}

_This ran through topic-exploration, narrative-definition, blog-draft, smell-test, and improving-guidance automatically. Review and publish when ready._
```

**H. Do NOT:**
- Create a Ghost draft
- Add to pending-drafts.json
- Post to driventodevelop.com
- Use David's personal blog voice (first-person "I")

---

### 2. Fetch and research each URL

For each new URL:

1. **Fetch the article:** `mcp__workspace__web_fetch(url="{url}")`
2. **If fetch fails or returns minimal content:** Run a web search for the article title or topic to gather context. The model should self-recover — proceed with search-gathered context.
3. **Extract:** Core argument, key insight, memorable quote or stat, the "so what" for David's audience.

### 3. Check deduplication

- Read `reference/blog-ideas.md` — Published section
- Call `mcp__ghost-blog__get_posts(limit=50)` and scan titles/slugs
- **Normalize URLs before dedup:** Strip tracking parameters before comparing. Spotify URLs include `?si=…` tokens; WSJ/NYT/others append `?mod=`, `?ref=`, `?campaign=`, etc. Compare base URLs only (scheme + host + path). Example: `https://open.spotify.com/episode/51IawJ6m9JcByFjLlzOwfV?si=xLu7qQ7g…` → `https://open.spotify.com/episode/51IawJ6m9JcByFjLlzOwfV`.
- Check `workflows/content-approval/pending-drafts.json` — if the normalized URL is already present in the `source_url` field (any status), skip it with note: "Skipped {url} — already in pipeline (status: {status})."
- **Digest title dedup:** For digest messages, also check `pending-drafts.json` by title. Extract the H1 from the digest and compare (case-insensitive) against all existing `title` fields. If a match exists (any status), skip with note: "Skipped digest '{title}' — already in pipeline (status: {status})." This prevents the 48h fallback from re-processing Watchtower digests that were already drafted in a prior run.
- If the source URL topic is already covered: skip with a note, don't draft.

### 4. Draft the post

**Before writing a single word: read `identity/CONTENT-VOICE.md` in full.** This is the blog-specific voice guide built from David's actual published posts. It is the source of truth for public content. Do not use `identity/VOICE.md` — that file governs Jarvis's internal communication style and is not appropriate for blog writing. Do not rely on memory or a summary of the rules. Read the file. This is mandatory on every run.

After reading CONTENT-VOICE.md, write a blog post in David's voice following the arc defined there:

- **Hook:** 1-2 sentences. A scene, a question, a contradiction. Something that earns the next sentence. Not "I read an article today." Not a rhetorical question that telegraphs the answer.
- **Story/Observation:** David's personal angle. What did this surface for him? A pattern from his consulting work, a real situation he has been in, something it confirmed or challenged. Be specific — real details, real friction.
- **Insight:** The distilled truth. One clean line of reasoning that arrives somewhere. Not a list of takeaways.
- **Challenge/Takeaway:** A direct question or provocation in the final paragraph. This is non-negotiable. It must appear in every post. It asks something of the reader.

**Length:** 300-500 words. No headers in posts under 500 words. Prose only. No bullet points in the body.

> ❌ **NO EM-DASHES. EVER.** Not `—`, not `–`, not `--`. Use commas, periods, or parentheses. No exceptions.

**Do not:** Summarize the article. Do not write "According to [source]..." David's reaction and angle is the post — the source is the spark, not the content.

Also draft at this stage:
- **meta_title:** Post title (same as title, or slight SEO variation — max 70 chars)
- **meta_description:** 1-2 sentence summary of the post's core insight — max 155 chars
- **twitter_title:** Same as meta_title
- **twitter_description:** Same as meta_description

### 5. Select tags

Choose 1-3 tags from the locked list in workflow.md. Match to the post's core themes. No new tags.

> **CRITICAL — Ghost API tag format:** Tags MUST be passed as an array of objects with an explicit `id` key. Passing bare ID strings causes Ghost to create new tags instead of linking existing ones.
>
> ✅ Correct: `tags=[{"id": "637ea17e92f3300211b1b23a"}, {"id": "68fbc4d89e3561027e745c91"}]`
> ❌ Wrong: `tags=["637ea17e92f3300211b1b23a", "68fbc4d89e3561027e745c91"]`
>
> **If the Ghost MCP rejects tag objects (returns an error about tag format):** Omit `tags` from the `create_post` call entirely. Apply tags via the Ghost Admin API PUT in Step 7b instead — the Admin API handles the object format correctly. Do NOT fall back to bare strings — that creates junk tags in the database.

### 6. Source the feature image

Identify the single most important high-level keyword from the post (e.g., "leadership", "resilience", "cost", "writing" — conceptual, not literal). Search Unsplash:

> **IMPORTANT:** `mcp__workspace__web_fetch` has a provenance restriction — it only fetches URLs that appeared in a prior user message or web_fetch result. Direct fetches to `unsplash.com/s/photos/...` will fail. Always use the two-step process below.

1. **Run a WebSearch** for: `unsplash {keyword} landscape photo site:unsplash.com/photos`
2. From the search results, pick a free (non-Unsplash+) photo URL — look for results where the title says "Free ... Image on Unsplash". Avoid results that mention "Unsplash+" or "premium".
3. **Fetch the photo page** with `mcp__workspace__web_fetch` using the exact URL returned by the search — this unlocks it for the provenance check.
4. From the fetched page, extract the photo ID from the `og:image` or `twitter:image` meta tag. The ID appears as `photo-{PHOTO_ID}` in the URL.
5. Construct the Unsplash CDN URL:
```
https://images.unsplash.com/photo-{PHOTO_ID}?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid={IXID}&ixlib=rb-4.1.0&q=80&w=2000
```
Use the ixid from the meta tag URL if available; omit the ixid parameter if not — it's optional.

**Image selection rules:**
- Must be landscape-oriented (wider than tall). No portrait-oriented images. Ever.
- Must be thematically aligned with the post's core concept — not just generically "professional." A post about auditing should show paperwork, spreadsheets, or financial review. A post about purpose/fulfillment should show open space, horizon, or journey imagery. A post about AI governance should show systems/infrastructure. Match the metaphor, not just the industry.
- Avoid portraits of people as the primary subject
- Must be free (no Unsplash+ license required)
- If the first candidate is premium (Unsplash+) or portrait, discard it and try the next search result — do not settle

> **MANDATORY — verify orientation from the actual pixels, never from the title, alt text, or search category.** Unsplash titles like "a long road with a mountain in the background" or category tags do not reliably indicate orientation — the same photo can be a portrait crop. (See err-20260715T195437-E6MUV6: a "long road / mountain" photo was used and turned out to be 2000x3000, portrait, because the title was trusted instead of the image.)
>
> Before accepting any candidate, fetch it and check real width vs. height via Desktop Commander:
> ```python
> import requests
> from io import BytesIO
> from PIL import Image
> r = requests.get(candidate_url, timeout=20)
> w, h = Image.open(BytesIO(r.content)).size
> assert w > h, f"portrait ({w}x{h}) — discard and try next candidate"
> ```
> If `w <= h`, discard the candidate and move to the next search result. Do not construct the final CDN URL or use the image in Ghost until this check passes.

Upload to Ghost CDN:
```
mcp__ghost-blog__upload_image_from_url(
  url="{unsplash_url}",
  filename="{post-slug}",
  purpose="image"
)
```

Use the returned Ghost CDN URL for both `feature_image` and `twitter_image`.

---

## QUALITY GATE 2 — Content Schema Validation (HARD, BLOCKING)

Run after Step 6 (image sourced) and before Step 7 (Ghost draft creation). This formalizes the DIGEST FORMAT / BLOG VOICE & FORMAT rules in workflow.md into an explicit checklist rather than leaving them as inline prose that's easy to skip under time pressure.

Applies to both the URL PATH and the DIGEST PATH (per DIGEST PATH Step E, the digest path merges in here).

**Two of these checks require judgment this gate does not delegate away:** whether the four
post-arc elements are actually present in the prose, and whether the draft reads as David's
own angle rather than a source recap. Make those calls yourself by reading the draft, set them
as plain booleans (`has_hook`, `has_story`, `has_insight`, `has_challenge`, `is_source_recap`),
then call `skills/schema-validator/SKILL.md` to mechanically check everything else against
those booleans plus the objective fields:

```yaml
data:
  word_count: <int>
  has_hook: <bool>
  has_story: <bool>
  has_insight: <bool>
  has_challenge: <bool>
  is_source_recap: <bool>          # your own read — true means FAIL
  body: "<full draft text>"
  tags: [{"id": "..."}, ...]
  meta_title: "<...>"
  meta_description: "<...>"
  feature_image_landscape: <bool>  # from Step 6's w > h check
  feature_image_set: <bool>
schema_spec:
  word_count: { min: 300, max: 500 }   # or {min: 1500, max: 2000} for IMPROVING BLOG PATH only
  tags: { field: "tags", allowed_list: [<locked-list tag ids from workflow.md>], format: "object_with_id" }
  em_dash_check: { field: "body", enabled: true }
  custom_checks:
    - { field: "has_hook", rule: "must_be_true" }
    - { field: "has_story", rule: "must_be_true" }
    - { field: "has_insight", rule: "must_be_true" }
    - { field: "has_challenge", rule: "must_be_true" }
    - { field: "is_source_recap", rule: "must_be_false" }
    - { field: "meta_title", rule: "max_length", value: 70 }
    - { field: "meta_description", rule: "max_length", value: 155 }
    - { field: "feature_image_landscape", rule: "must_be_true" }
    - { field: "feature_image_set", rule: "must_be_true" }
```

The "no bullet points / no headers in body" check for sub-500-word posts is a structural scan
of `body` this skill's generic rule set doesn't cover directly — run it yourself (or add it as
`format_rules`/`custom_checks` on a future edit if it recurs elsewhere) and fold the result
into `errors` manually if it fails, same STOP treatment as any other Gate 2 failure below.

| Check | Expected | On failure |
|-------|----------|------------|
| Word count | 300-500 words (URL/digest post path) or 1,500-2,000 words (IMPROVING BLOG PATH only) | **STOP.** Trim or expand before proceeding. Do not send an out-of-range draft to Ghost. |
| Four post-arc elements present | Hook, Story/Observation, Insight, Challenge/Takeaway all identifiable in the draft | **STOP.** If any is missing, write it now per DIGEST FORMAT's "Missing sections" rule (using CONTENT-VOICE.md), then re-check. |
| No em-dashes | Zero occurrences of `—`, `–` used as a dash, or `--` | **STOP.** Replace with commas, periods, or parentheses. Re-scan the full draft, not just the flagged sentence. |
| No bullet points / no headers in body (post under 500 words) | Prose only | **STOP.** Convert to prose. |
| Not a source recap | Draft reads as David's reaction/angle, not "According to [source]..." | **STOP.** Rewrite the offending passage from David's vantage point. |
| Tags are from the locked list | Every tag id in the draft's tag selection appears in workflow.md's LOCKED LIST table | **STOP.** Do not proceed with an off-list tag. Re-select from the locked list. |
| Tag format is object-with-id | Selected tags represented as `[{"id": "..."}]`, never bare strings | **STOP.** Fix format before the Ghost API call — bare strings create junk tags (see workflow.md's CRITICAL note). |
| meta_title ≤ 70 chars, meta_description ≤ 155 chars | Character counts checked | **STOP.** Trim before proceeding. |
| Feature image is landscape and CDN-uploaded (or verified fallback per FAILURE MODES) | `w > h` confirmed in Step 6; `feature_image` is set | **STOP.** Do not create the Ghost post without a validated image or an explicit, logged fallback. |

Log the result (reading `errors`/`warnings` back from the skill's response):
```
[Gate 2] Word count: N (limit: 300-500 or 1500-2000)
[Gate 2] Post-arc elements present: Hook ✓ Story ✓ Insight ✓ Challenge ✓
[Gate 2] Em-dash scan: clean
[Gate 2] Tags: {tag names} — all on locked list, object format confirmed
[Gate 2] Image: landscape confirmed, CDN url set
[Gate 2] PASS — proceeding to Ghost draft creation.
```

If `schema-validator` returns `valid: false`, log `[Gate 2] FAIL — <errors list>` and remediate
(fix the draft, or correct the boolean you fed in if your own judgment call was wrong on
re-read) before re-running the gate. Do not call the Ghost API with a draft that hasn't passed
Gate 2 (`valid: true`).

---

### 7. Create Ghost draft

> **CONFIRMED MCP LIMITATIONS (verified 2026-05-19):** The Ghost MCP silently drops `feature_image`, `twitter_image`, and `lexical` content on both `create_post` and `update_post`. Tags passed as bare ID strings create junk tags. **Do not use the Ghost MCP for post creation.** Use a single Admin API POST instead.

**Step 7 — Create post via Ghost Admin API (single call, replaces the old 7a/7b two-step):**

Use `mcp__Control_your_Mac__osascript` to run a Python script that:

1. **Get Admin API key:** Read `~/Library/Application Support/Claude/claude_desktop_config.json`. Find the server named `ghost-blog`. Read `GHOST_ADMIN_API_KEY` from its env block. The format is `{key_id}:{hex_secret}`.

2. **Generate JWT:**
   - Header: `{"alg": "HS256", "kid": "{key_id}", "typ": "JWT"}`
   - Payload: `{"exp": now + 300, "iat": now, "aud": "/admin/"}`
   - Sign using `hex_secret` decoded from hex to bytes (not base64)
   - Use PyJWT: `jwt.encode(payload, bytes.fromhex(hex_secret), algorithm="HS256", headers={"kid": key_id})`

3. **Build Lexical JSON** from the drafted post body. Structure: `{"root": {"children": [{paragraph nodes}], "direction": "ltr", "format": "", "indent": 0, "type": "root", "version": 1}}`. Each paragraph: `{"children": [{"detail": 0, "format": 0, "mode": "normal", "style": "", "text": "{paragraph text}", "type": "text", "version": 1}], "direction": "ltr", "format": "", "indent": 0, "type": "paragraph", "version": 1}`.

4. **POST to Ghost Admin API:**
   ```
   POST https://driventodevelop.com/ghost/api/admin/posts/
   Authorization: Ghost {jwt}
   Content-Type: application/json

   {
     "posts": [{
       "title": "{Post Title}",
       "status": "draft",
       "authors": [{"id": "68a3465b9e3561027e745c51"}],
       "feature_image": "{ghost_cdn_url}",
       "twitter_image": "{ghost_cdn_url}",
       "tags": [{"id": "{tag_id}"}, ...],
       "lexical": "{lexical_json_string}",
       "meta_title": "{meta_title}",
       "meta_description": "{meta_description}",
       "twitter_title": "{twitter_title}",
       "twitter_description": "{twitter_description}"
     }]
   }
   ```

5. **Capture returned post ID** from the response (`posts[0].id`).

**Step 7 verify — `mcp__ghost-blog__get_post`:**
- `lexical` is non-empty (has paragraph nodes)
- `feature_image` is set
- `tags` show real tag names (e.g., "leadership", "trust") not bare ID strings
- `excerpt` is populated (Ghost auto-generates from content)

**Do not send the Slack notification until ALL verification checks pass.** Report specific failures accurately — do not claim partial success:
- `lexical` empty or null: the POST failed to write content. Check the API response for errors and retry.
- Tags show ID strings: tag format was wrong. Retry with correct `{"id": "..."}` object format.
- `feature_image` null: the image upload failed. Retry Step 6 before proceeding.

Only a clean `get_post` response with content, image, and real tag names unlocks the Slack notification in Step 9.

Capture the returned `id` — this is the Ghost post ID needed for approval.

### 8. Write to pending-drafts.json

Read the current `workflows/content-approval/pending-drafts.json`, append the new entry, write it back:

```json
{
  "ghost_post_id": "{id from Ghost response}",
  "slack_thread_ts": null,
  "slack_channel": "C0B160MA3EK",
  "title": "{Post Title}",
  "source_url": "{original url or null for digest}",
  "created_at": "{ISO timestamp}",
  "status": "pending",
  "source_type": "url",
  "content_type": "post"
}
```

> Set `content_type` to `"article"` if the message contained the `article` keyword (detected in the router above). Otherwise use `"post"`. For digest entries, apply the same logic based on the digest message text or title.

Set `source_type` to `"url"` for the standard URL path, or `"digest"` for the digest path. For digest entries, `source_url` may be null or set to the first source URL from the digest's `## Sources` section if one exists.

`slack_thread_ts` starts as null — it gets filled in step 9 after posting.

### 9. Notify David in Slack

Use `master-slack` skill (post.py via Desktop Commander) to post to #content (C0B160MA3EK):

```
*New draft ready for review* ✍️

*"{Post Title}"*
_Source: {source_url}_

{First 2-3 sentences of the draft as a teaser}

*Review draft:* https://driventodevelop.com/ghost/#/editor/post/{ghost_post_id}/

*To review:* Reply to this thread with:
• `approve` — publishes to driventodevelop.com
• `reject` — discards the draft
• Anything else — I'll treat it as feedback and regenerate
```

**Capture the message timestamp:** Run post.py via Desktop Commander. Parse the stdout JSON response.
- If `ok` is true, extract the `ts` field and set `slack_thread_ts` in the pending draft entry.
- If `ok` is false or `ts` is missing, set `slack_thread_ts` to the current Unix timestamp as a fallback (close enough for content-approval to find replies).

Update `workflows/content-approval/pending-drafts.json` — set `slack_thread_ts` to this value for the entry you just created.

### 10. Update reference/blog-ideas.md

Add the new post to the Candidates table in `reference/blog-ideas.md`:

```
| "{Post Title}" | Content pipeline ({date}) | {tags} | Ghost draft — pending approval |
```

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| GATE 1 fails (read.py fails, script not found, token error, wrong-channel response) | Report failure via post.py to #jarvis: "Content discovery paused — read.py error: {error}". Exit. |
| URL fetch fails + web search returns nothing | Skip URL. Log: "Could not retrieve content for {url} — skipping." |
| GATE 2 fails and cannot be remediated after one retry | Notify David in #content: "Draft for '{title}' failed content schema validation ({failed check}) after one remediation attempt — needs manual review." Do not create the Ghost post. |
| Ghost API fails on post creation | Log error. Notify David in #content: "Draft creation failed for {url} — will retry tomorrow." |
| Image upload fails | Use a fallback Unsplash URL directly (without uploading) — Ghost accepts external URLs for feature_image. Note in Slack message: "(image not uploaded to CDN — using external URL)" |
| pending-drafts.json is malformed | Reset to `[]` and log the error. Do not halt. |

---

## YOUR TASK — Closing (state bookkeeping)

After Step 10 completes (or after an early clean exit with no new content):

1. Write `status: complete`, `completed-at`, and populated `outputs` (at minimum: `messages_scanned`, `new_urls`, `new_digests`, `posts_drafted`, `gate_1_result`, `gate_2_result`) to this file's own frontmatter.
2. Write those same output keys into `state.yaml`'s `accumulated-context`.
3. Set `state.yaml`'s `current-step: step-02`.

## NEXT STEP

After discovery completes:
1. Draft notification is posted to #content
2. Run `steps/step-02-git-finalize.md` to commit pending-drafts.json and state.yaml

`workflows/content-approval/steps/step-01-approve.md` runs independently on its own schedule, also followed by its own git-finalize step.
<!-- personal:end -->
