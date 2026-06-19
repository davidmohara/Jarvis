# Skill: LinkedIn Post from Blog Release

## Agent
Harper

## Trigger

"Draft a LinkedIn post for my new blog: [title] [URL]"

Variations:
- "Write a LinkedIn post for this blog post: [URL]"
- "LinkedIn share for [title]: [URL]"

---

## Standing Permissions

- Read Ghost blog posts via `mcp__ghost-blog__get_post` and `mcp__ghost-blog__get_post_by_slug`
- No write permissions required. Harper drafts. David posts manually.

---

## Before You Write Anything

Read both of these in full before generating any output:

- `identity/CONTENT-VOICE.md` — governs David's voice, structure, and what separates his perspective from generic thought leadership
- `identity/writing-rules.md` — universal rules including the em-dash prohibition (no `—`, no `–`, no `--`), parenthetical asides, and warmth

These are not optional background reads. They are the operating spec for this skill.

---

## Workflow

### Step 1: Fetch the Blog Post

If a URL is provided, extract the slug from the URL path and call:

```
mcp__ghost-blog__get_post_by_slug(slug)
```

If a post ID is provided directly, call:

```
mcp__ghost-blog__get_post(id)
```

Extract the following fields:
- `title`
- `excerpt` (custom excerpt if present; otherwise the meta description)
- `plaintext` or `html` (full body — used to identify the core tension)
- `tags` (topic signals)
- `published_at`
- `url` (canonical URL to include in the post)

If Ghost returns an error or the post is not found, tell David and ask him to confirm the slug or post ID.

### Step 2: Identify the Core Tension

Read the post body. The LinkedIn hook is built on tension, not summary. Before drafting, identify:

1. **The contradiction or counterintuitive claim** — what does this post say that is surprising, uncomfortable, or cuts against the default assumption?
2. **The real-world stakes** — who is affected? What breaks if you get this wrong? What changes if you get it right?
3. **The consulting vantage point** — where does David's lived proximity to the work sharpen the observation? His teams are in client environments. Use that. Do not abstract it away.

Write these three elements down internally before drafting. If you cannot identify a genuine tension in the post, flag it to David before proceeding. A post without real tension will produce a generic LinkedIn share. That is worse than no post at all.

### Step 3: Draft the LinkedIn Post

Apply the contrast-hook structure. Every LinkedIn post must follow this arc:

1. **Hook (1-2 sentences):** A tension statement. A contradiction. A counterintuitive claim. Something that earns the next line by creating friction. Not a rhetorical question with an obvious answer. Not a summary of the post. An observation that makes the reader stop.

2. **Expansion (1-2 sentences):** Widen the gap. Show the two sides of the tension. Make the stakes concrete. Draw on the consulting vantage point when the topic connects to it.

3. **Distillation (1-2 sentences):** The single clean truth the post arrives at. This should feel earned by the two lines before it, not dropped in from outside.

4. **Challenge or question (1 sentence):** A direct ask or provocation. David's signature move. Not "I hope this resonates." Not "What do you think?" Something with enough specificity that a reader feels like David is in the room with them, expecting an answer.

5. **URL:** The canonical post URL on its own line. No anchor text. No "click here." Just the URL.

**Format constraints:**
- Under 120 words total (not counting the URL)
- No headers, no bullets, no bold
- No em-dashes. Not `—`, not `–`, not `--`. Use commas, periods, or parentheses instead.
- No hashtags unless David explicitly asks
- No "I wrote about this" or "My latest post" constructions. Get to the tension immediately.
- Parenthetical asides are fine when they carry dry wit or inner monologue. Do not strip them.

### Step 4: Quality Gate

Before returning the draft, run these checks:

| Check | Pass Condition | Required |
|-------|---------------|----------|
| Em-dash scan | Regex `—\|–` returns zero matches | Required |
| Grammarly check | No critical grammar/spelling errors. Tone suggestions reviewed (Harper decides). | Required |
| Word count | Body is under 120 words (URL excluded) | Required |
| Hook clarity | First sentence creates friction or contradiction. Does not summarize the post. Does not start with "I" or "My." | Required |
| Consulting lens | If the topic connects to delivery, deployment, or client work, that vantage point appears somewhere in the post | Required |
| Challenge present | Final line before URL is a direct question or provocation, not a close or a summary | Required |
| No generic closes | "I hope this helps," "share your thoughts," "thanks for reading" are not present anywhere | Required |
| Voice check | Read the draft aloud. If it sounds like a LinkedIn carousel or a generic thought leadership post, rewrite it. | Required |

If any check fails, fix it before returning the draft. Do not return a draft that fails the em-dash, Grammarly, or generic-close checks. Those are non-negotiable.

### Grammarly Quality Gate (Step 4a)

This step runs immediately after the em-dash scan and before word count is reported. The post does not return until it passes.

**Integration: MCP connector**

Call `mcp__grammarly__check` if it is available in the session. If it is not listed in the available tools, fall through to the manual path below.

```
mcp__grammarly__check(
  text: <drafted post body, URL excluded>,
  goals: {
    audience: "general",
    formality: "informal",
    domain: "general",
    tone: "confident"
  }
)
```

**What to do with the response:**

The Grammarly API returns a list of alerts. Each alert has a `category` and an `impact` level. Handle them as follows:

| Alert type | Action |
|------------|--------|
| Spelling errors | Auto-fix. These are objective. Apply without flagging. |
| Grammar errors (subject-verb agreement, tense, punctuation) | Auto-fix if the correction is unambiguous. If the original was intentional (e.g., fragment for stylistic effect), leave it and note it. |
| Clarity / conciseness suggestions | Review. Apply if the suggestion does not flatten the voice. Skip if it makes the line generic. |
| Tone suggestions | Do not auto-apply. Flag for Harper to review. Harper owns the voice. A Grammarly tone flag is information, not an instruction. |
| Style suggestions | Do not auto-apply. Same reason. |

Critical errors (spelling, hard grammar breaks) block the post from returning. Tone and style suggestions do not block the post, but they must be surfaced to Harper as a note in the output.

**Before/after example:**

Before Grammarly pass:
```
Most teams dont know they've already lost the leverage they think there negotiating with.
```

After Grammarly pass (auto-fixed spelling and apostrophe):
```
Most teams don't know they've already lost the leverage they think they're negotiating with.
```

Tone suggestion (flagged, not applied):
> Grammarly flagged "lost the leverage" as potentially negative in tone. Harper reviewed and kept it. The negativity is the point.

**If `mcp__grammarly__check` is not available:**

Document the gap and ask Harper to run the check manually before posting. Include this block in the output:

```
---
GRAMMARLY GATE: MCP connector not available in this session.
Before posting, paste the draft into grammarly.com or the Grammarly desktop app.
Fix any critical grammar/spelling errors. Review tone suggestions and decide whether to apply them.
Do not post until this step is complete. David can configure the MCP token in Global IT Services.
---
```

The Grammarly API endpoint for direct integration is `https://api.grammarly.com/api/check` (OAuth 2.0, requires a Grammarly Developer token). David can request access and configure the token through IT or directly at developer.grammarly.com.

---

## Output Format

Return exactly this and nothing else:

```
---
LINKEDIN DRAFT
---

[the post]

---
Word count: [n] words (URL excluded)
---
```

Do not include explanations, commentary, or rationale unless David asks. He wants copy-paste ready output.

---

## Example That Works

This is the canonical reference for what the output should look and feel like. Study the structure: the hook creates a genuine contrast (burning budget vs. underwriting outcomes), the expansion sharpens the gap (hoping vs. proving), the distillation lands a single clean truth (spend is no longer the signal), and the challenge asks something specific (projections or receipts).

```
Uber spent their entire 2026 AI budget in four months. Can't prove it moved the needle.

Cognition just put $10 million on the table guaranteeing theirs does.

One vendor burned cash hoping. The other is underwriting outcomes.

That's the shift. Spend is no longer the signal. Proof is.

Read the full post. Then tell me: are your AI conversations built on projections or receipts?

[URL]
```

Notice what is absent: no em-dashes, no hashtags, no "check out my latest post," no summary of what the article covers, no "I hope this sparks a conversation." The post does not explain itself. It earns the click by creating a gap the reader wants to close.

---

## Edge Cases

**Post is opinion-heavy but lacks a clear tension.** Flag it before drafting: "I'm reading the post and the core argument is [X]. The best tension I can find is [Y]. Is that the angle you want, or is there a sharper one I'm missing?"

**Post is a personal story without a clear professional application.** Still find the tension. Personal posts often have the sharpest hooks because the stakes are real. "I made this mistake. Here's what it cost" is tension.

**The excerpt and the body tell different stories.** Use the body. The excerpt is often written for SEO. The body is where the actual observation lives.

**David provides a title and URL but the URL 404s or the Ghost MCP returns an error.** Do not hallucinate the content. Tell David: "I can't pull the post from Ghost. Paste the body or the key argument and I'll draft from that."

**David says the draft doesn't sound like him.** Ask one question: "What's the line in the post that matters most to you?" Rebuild from that anchor. Do not ask for a full briefing. One line is enough.

---

## Voice Reminders (from CONTENT-VOICE.md)

These are the rules most likely to fail in LinkedIn drafts:

- **The consulting vantage point is the differentiator.** Generic leadership commentary is noise. David's voice is grounded in the fact that his teams are building and deploying the things he writes about. Use that proximity whenever the topic connects to it. Not as a credential drop. As the ground the observation stands on.
- **Reflective, not prescriptive.** He does not tell readers what to do. He arrives at a conclusion and then asks something of them.
- **Direct without being cold.** The tone is a senior colleague over coffee, not a speaker with slides.
- **Specificity over abstraction.** Abstract insight without a real anchor reads like a carousel. Names, numbers, and real situations are what make it his.
