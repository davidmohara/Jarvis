---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` to this file's frontmatter before doing anything else.
2. Read `identity/VOICE.md` BEFORE writing any tweet. Voice alignment is non-negotiable.
3. You MUST read the blog post angles drafted in step-02 before generating tweets. Tweets must NOT overlap with those angles.
4. Generate exactly 10 tweets. No fewer. No more.
5. Each tweet must be 280 characters or fewer — hard limit, no exceptions. Count carefully.
6. Each tweet must stand alone. No "read more" links, no "thread below," no cliffhangers requiring a URL.
7. Tweets must approach distinct angles — no two tweets covering the same idea from the same direction.
8. The intent URL for each tweet uses `https://twitter.com/intent/tweet?text=` + URL-encoded tweet text. Encode spaces as `%20`. Encode `#` as `%23`. Encode `&` as `%26`. Encode `?` as `%3F`. Encode `"` as `%22`. Encode `'` as `%27`.
9. Store results in `accumulated-context.weekly_tweets` before marking complete.
10. Write `status: complete`, `completed-at`, and `outputs` when done.

---

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Knox |
| Model | sonnet |
| Input | `accumulated-context.weekly_themes` (from step-01), step-02 `draft_paths` and `content_angles` (to define covered territory), `identity/VOICE.md` |
| Output | `accumulated-context.weekly_tweets` — array of 10 tweet objects |

---

## CONTEXT BOUNDARIES

- Scope: generate tweets only. No Obsidian writes. No blog-ideas.md updates. No source proposals.
- These tweets are ready-to-post material, not drafts. Each should be worth sending as-is.
- Tweets are David's voice — Regional Director, IT consulting, AI/agentic systems practitioner. Not a media brand. Not a thought leader performing thought leadership. A real person with opinions.
- Tweet diversity is required: some provocative, some data-driven, some experiential, some question-format. Aim for a mix across the 10.

---

## YOUR TASK

1. Read `identity/VOICE.md`. Internalize David's voice: direct, personal, punchy, occasionally sarcastic, never corporate.

2. Collect covered territory from step-02:
   - Read `accumulated-context.weekly_themes` — specifically the `content_angles` added by step-02 to each theme entry. These are the blog post angles already claimed.
   - Note the titles and angles of all draft files created in step-02 (from `accumulated-context.weekly_themes[*].content_angles` and the step-02 outputs `draft_paths`).
   - Treat all blog post angles as OFF LIMITS for tweets. A tweet must NOT summarize, preview, or recycle any of these angles. It must approach the same underlying topic (if used at all) from a genuinely different direction.

3. Generate 10 tweets. For each:

   - Pick an angle NOT covered by any blog draft. This can be:
     - A sharp observation from the week's signals that didn't make it into a blog angle
     - A practitioner-level take on a theme (what you'd actually do / what you've seen in the field)
     - A provocative question the signal raises
     - A contrarian read on a consensus narrative in the news
     - A short story or moment from David's week that the signal triggered
     - A stat or number from the signal re-framed with a "so what"

   - Format variety target across the 10:
     - 2-3 **Provocative/contrarian** — challenge an assumption, name something others dance around
     - 2-3 **Practitioner/experiential** — "Here's what I'm actually seeing in the field..." or first-person observation
     - 2 **Question-format** — genuine question that opens a conversation (not rhetorical hand-wringing)
     - 2-3 **Data/signal-driven** — anchor to a specific signal, stat, or development; add the "so what"

   - Constraints per tweet:
     - 280 characters max (count carefully — include spaces and punctuation)
     - No hashtags unless they add genuine value (limit to 1 max if used)
     - No "Read more:" or link placeholders
     - No "Thread:" or numbered continuations
     - Must stand alone — assume no other context
     - Sound like David texted it, not like a content team scheduled it

4. For each tweet, build the intent URL:
   - Base: `https://twitter.com/intent/tweet?text=`
   - Append URL-encoded tweet text
   - Key encoding rules: space → `%20`, `#` → `%23`, `&` → `%26`, `?` → `%3F`, `"` → `%22`, `'` → `%27`, newline → `%0A`

5. Store in `accumulated-context.weekly_tweets` as an array of objects:
   ```yaml
   weekly_tweets:
     - text: "<tweet text, plain>"
       intent_url: "https://twitter.com/intent/tweet?text=<url-encoded-text>"
       angle_type: "provocative|practitioner|question|data"
     - ...
   ```

6. Write `outputs` to this file's frontmatter:
   ```yaml
   outputs:
     tweets_generated: 10
     angle_types:
       provocative: <int>
       practitioner: <int>
       question: <int>
       data: <int>
     blog_angles_avoided: <int>   # count of step-02 angles read and excluded
   ```

---

## SUCCESS METRICS

- Exactly 10 tweets stored in `accumulated-context.weekly_tweets`.
- No tweet exceeds 280 characters.
- No tweet overlaps in angle with any blog draft from step-02.
- All 4 angle types represented across the set.
- Each tweet has a valid, properly encoded intent URL.
- Voice matches David's register — direct, personal, not corporate.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `weekly_themes` empty | Generate 0 tweets; write `tweets_generated: 0` to outputs; continue to step-03 |
| Step-02 `content_angles` not available | Proceed without overlap check; note in outputs: `overlap_check: skipped` |
| Tweet exceeds 280 chars after generation | Trim — cut filler words, tighten; do not truncate mid-thought |
| Fewer than 10 viable angles found | Extract additional angles from raw signal items in `weekly_themes`; do not pad with weak takes |
| URL encoding error | Use plain spaces as `%20` and skip encoding edge cases rather than generating a broken URL |

---

## NEXT STEP

`workflows/watchtower/steps/weekly-step-03-suggest-sources.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
