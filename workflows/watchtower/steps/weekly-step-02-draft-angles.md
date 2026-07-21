---
status: complete
started-at: "2026-07-20T07:10:00Z"
completed-at: "2026-07-20T07:20:00Z"
outputs:
  themes_processed: 4
  drafts_created: 4
  draft_paths:
    - "Mind/Posts/_your-saas-stack-was-priced-for-humans.md"
    - "Mind/Posts/_the-safe-bet-isnt-safe-anymore.md"
    - "Mind/Posts/_governance-isnt-your-problem-uniform-governance-is.md"
    - "Mind/Posts/_abbott-just-changed-the-rules-texas-ai-clients.md"
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
   ```markdown
   ---
   source: watchtower
   date: YYYY-MM-DD
   topic: <theme_title>
   channels: [blog|linkedin|forbes]
   status: draft
   tags: [watchtower, <relevant topic tags>]
   ---

   # <Post Title (working)>

   ## Hook
   <1-2 sentence hook. Lead with tension or surprise. Sound like David, not a press release.>

   ## Story Angle
   <2-3 sentences. What experience or observation does David bring to this? First person.>

   ## Core Insight
   <The "so what" — the one thing the reader should take away.>

   ## Challenge / CTA
   <Optional. A question or provocation to close with.>

   ## Sources
   - <item title> — <url>
   ```

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
