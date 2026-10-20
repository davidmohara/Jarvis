<!-- personal:start -->
# DIGEST FORMAT

The Watchtower workflow (and David directly) posts structured content digests to #content. These are the primary input for the digest drafting path.

## What a digest looks like

```
# Post Title

## Hook
2-4 sentences — the opening move

## Story Angle
David's personal vantage point, first-person

## Core Insight
The distilled truth

## Challenge / CTA
The closing ask/challenge

## Sources
- Source name — URL
- Source name — URL
```

Section header variations are valid: `## Challenge / CTA` and `## Challenge/CTA` are both acceptable. Other section names may vary slightly — match by keyword (see detection rule below).

## Detection rule

A message (bot or user) is a **digest** if it contains BOTH:
- `# ` (an H1 header — the post title)
- At least one `## ` (an H2 section header)

Watchtower bot messages sometimes use `*Bold*` section headers instead of `## ` markdown — those are ALSO digests and must never be skipped as noise (see step-01's MESSAGE ROUTER).

## Section mapping

| Digest section | Post arc role |
|---------------|--------------|
| `## Hook` | Post hook (opening) |
| `## Story Angle` / `## Story` | Body — David's personal angle |
| `## Core Insight` / `## Insight` | Insight — the distilled truth |
| `## Challenge / CTA` / `## Challenge/CTA` / `## Challenge` | Closing challenge/CTA |
| `## Sources` | Reference context only — not cited in the post body |

Match sections by keyword presence in the header, not exact string match.

## Missing sections

If a digest is missing any of the four post-arc sections (Hook, Story, Insight, Challenge), Harper fills them using `identity/CONTENT-VOICE.md`. Sources are always optional. QUALITY GATE 2 (Content Schema Validation) in step-01-discover.md checks the four-arc requirement before Ghost draft creation.

## Bot message skip rule

Skip bot messages UNLESS they contain `# ` AND `## ` (digest signal) OR the Watchtower bold-header digest signal. Bot messages with either digest signal are processed on the DIGEST PATH, not skipped.
<!-- personal:end -->
