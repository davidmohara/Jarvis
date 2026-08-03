---
status: complete
started-at: "2026-08-03T07:12:00Z"
completed-at: "2026-08-03T07:22:00Z"
outputs:
  themes_processed: 4
  drafts_created: 4
  draft_paths:
    - "Mind/Posts/_your-vendor-checked-the-box-you-still-havent.md"
    - "Mind/Posts/_nobody-owns-the-agent.md"
    - "Mind/Posts/_the-premium-you-charged-was-for-knowing-things.md"
    - "Mind/Posts/_texas-is-building-the-chips-now.md"
  blog_ideas_appended: 4
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` to this file's frontmatter before doing anything else.
2. Read `identity/VOICE.md` and `reference/blog-ideas.md` BEFORE writing any draft. Voice alignment is non-negotiable.
3. One draft file per content candidate, not per theme. Themes may yield multiple angles; that is expected.
4. All draft files go to Obsidian `Mind/Posts/` with underscore-prefix. Use Obsidian MCP (`mcp__obsidian-local__create_vault_file`) — do NOT write to filesystem paths inside the vault. Do NOT claim a file was written without calling this tool.
5. After writing each file, call `mcp__obsidian-local__get_vault_file` to verify it exists. Only log the path in outputs AFTER verification succeeds. If verification fails, retry once, then log failure.
6. Append candidate rows to `reference/blog-ideas.md` with `[watchtower]` source marker. Do NOT rewrite existing rows.
7. Drafts are starters — hook + outline only, not full posts. Keep them under 300 words total.
8. VERIFICATION GATE: Before writing `status: complete`, confirm that `outputs.draft_paths` contains only paths that were verified via `mcp__obsidian-local__get_vault_file`. A path that was written but not verified must be marked `unverified` in outputs.
9. Write `status: complete`, `completed-at`, and `outputs` when done.

---

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Knox (Harper consulted for voice) |
| Model | sonnet |
| Input | `accumulated-context.weekly_themes` (from step-01), `identity/VOICE.md`, `reference/blog-ideas.md` |
| Output | Draft files in Obsidian `Mind/Posts/`; candidate rows appended to `reference/blog-ideas.md` |

---

## CONTEXT BOUNDARIES

- Scope: draft hooks + outlines and register candidates. No full posts. No publishing.
- Watchtower feeds Harper's content pipeline — it does not replace it. These drafts are raw material.
- Channel tags: blog, linkedin, forbes — per `config.yaml relevance.content_channels`. Tag each draft with the best-fit channel(s).
- Blog style: short (1-3 min read), personal, reflective. Hook > story > insight > challenge. Refer to `reference/blog-ideas.md` header for style guidance.

---

## YOUR TASK

1. Read `identity/VOICE.md`. Internalize David's voice: direct, personal, reflective, not corporate.

2. Read `reference/blog-ideas.md`. Note the style guide in the header and the existing candidate rows to avoid duplicates.

3. For each theme in `accumulated-context.weekly_themes`:

   Identify 1-2 content angles. An angle is a specific post premise that ties the theme to David's experience, role, or perspective.

   For each angle:

   **a. Construct the draft file content:**

   **PRIOR STORY RULE — read before writing anything:**
   - If the delta check in step-01 flagged this theme as building on a prior published post (i.e., a prior week's content angle that was drafted and potentially published), add a `related_posts` field to frontmatter with a Ghost link placeholder for each related post.
   - The placeholder format is: `"[LINK: <prior post title>]"` — this is a signal to David to insert the actual Ghost URL when the post goes live. It is NOT visible prose in the body. Do NOT write sentences like "Last week I covered..." or "In W29 I wrote about..." or any reference to week numbers or prior Watchtower runs in the draft body. Ever.
   - If there is a natural place in the Story Angle or Core Insight where a link to a prior post would add value for the reader, use inline link syntax with the placeholder: `[prior post title]([LINK: <prior post title>])`. This reads naturally in the final post once the real URL is swapped in.

   ```markdown
   ---
   source: watchtower
   date: YYYY-MM-DD
   topic: <theme_title>
   channels: [blog|linkedin|forbes]
   status: draft
   tags: [watchtower, <relevant topic tags>]
   related_posts:
     - "[LINK: <prior post title if applicable>]"   # remove this line if no related posts
   ---

   # <Post Title in Title Case>

   ## Hook

   <1-2 sentence hook. Lead with tension or surprise. Sound like David, not a press release.>

   ## Story Angle

   <2-3 sentences. What experience or observation does David bring to this? First person.
   If referencing a prior post, use inline link placeholder: [post title]([LINK: post title])
   Use a colon to connect clauses mid-sentence, not an em-dash.>

   ## Core Insight

   <Structure the argument explicitly and sequentially when making a multi-part point.
   Use "Step one... Step two..." or similar scaffolding — do not compress a two-step argument into a summary paragraph.
   Always look for a "what is Improving actually doing about this" angle where it's genuinely true and relevant. David writes from inside the work, not as an outside observer. If Improving has real activity (certifications, client engagements, internal initiatives) that connects to the theme, include it. Do not manufacture it — only use what is real and specific.>

   ## Challenge / CTA

   <Optional. A question or provocation to close with.>

   ## Sources
   - <item title> — <url>
   ```

   **Formatting rules:**
   - Post titles are always in Title Case — every significant word capitalized.
   - Add a blank line between each `##` section header and the paragraph that follows.
   - Use colons, not em-dashes, to connect or extend a thought mid-sentence.

   **What NEVER appears in a draft body:** week numbers (W29, W30, etc.), phrases like "last week," "in a prior Watchtower run," "building on what I wrote," or any reference to the Watchtower system itself. Time references like "prior week" or "earlier this year" are fine when they read naturally. That context lives in the frontmatter and in Knox's notes only.

   **b. Write the file to Obsidian `Mind/Posts/_<slug>.md`** via Obsidian MCP.
   - Slug: lowercase, hyphens, derived from the post title. Keep it short.
   - Prefix with underscore: this marks it as a draft.

   **c. Append a candidate row to `reference/blog-ideas.md`** under `## Candidates`:
   ```markdown
   | "<Post Title>" | Watchtower ([DATE]) [watchtower] | <tags> | Draft at `Mind/Posts/_<slug>.md` |
   ```

4. Update `accumulated-context.weekly_themes` — add `content_angles` list to each theme entry (angle titles only).

5. Write `outputs` to this file's frontmatter:
   ```yaml
   outputs:
     themes_processed: <int>
     drafts_created: <int>
     draft_paths: []       # list of Obsidian paths written
     blog_ideas_appended: <int>
   ```

---

## SUCCESS METRICS

- At least one draft created per theme (unless theme set is empty from step-01).
- Each draft file is at correct Obsidian path with underscore prefix and correct frontmatter.
- Candidate rows appended to `reference/blog-ideas.md` — existing rows untouched.
- No full posts written — hook + outline only.
- Voice matches David's direct, first-person register.
- Every post title is in Title Case — verify each word is capitalized appropriately before writing the file.
- Draft bodies contain zero week-number references — scan each draft for the pattern `W\d{2}` (e.g. W29, W30) before writing; if found, remove and replace with natural prose or a Ghost link placeholder.
- Each `##` section header is followed by a blank line before the first paragraph — no exceptions.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `weekly_themes` empty | Write "No content candidates this week." to outputs; skip draft creation; continue to step-03 |
| Obsidian MCP unavailable | Write drafts to `workflows/watchtower/fallback/drafts/` as fallback; log path in outputs |
| Duplicate slug detected in Obsidian | Append `-2` to slug and retry once |
| `reference/blog-ideas.md` not found | Log error; still create Obsidian drafts; surface to David: "blog-ideas.md not found — candidate rows not appended." |

---

## NEXT STEP

`workflows/watchtower/steps/weekly-step-02b-draft-tweets.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
