<!-- system:start -->
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
(This is the canonical location for unpublished Improving-blog drafts. Do not use or recreate any other drafts/ path.)

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
<!-- system:end -->
