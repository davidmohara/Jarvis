# Podcast Prep PDF Template — "The Improving Edge"

Reference format derived from Episode 2 PDF (John Ruzick). Use this to generate all future episode prep sheets.

---

## Format Specification

### 1. Header Banner
`THE IMPROVING EDGE | {Guest Full Name}, {Guest Title}`

- Blue background, white/gold text
- Full width across top of page

### 2. Intro Script (standard — same every episode)
```
INTRO SCRIPT
Welcome to The Improving Edge. This is where we talk about how AI and technology actually
show up in real organizations; what works, what doesn't, and what we're learning along the
way. I'll be sharing conversations with people doing the work, turning innovation into outcomes.
```

### 3. Season & Episode
Centered: `Season 1, Episode {N}`

### 4. Episode Title
Centered, bold, large font: `{Episode Title}`

### 5. Episode Overview
Subheading: **Episode Overview** (orange/gold)

2-3 sentence paragraph summarizing the episode's focus. Written in first-person plural ("We'll discuss..."). Should cover the key themes without being exhaustive.

### 6. Key Discussion Topics
Subheading: **Key Discussion Topics** (orange/gold)

Table format:

| # | TOPIC | FOCUS |
|---|-------|-------|
| 1 | {Topic Name} | {1-2 sentence description of what this topic covers} |
| 2 | ... | ... |

- Typically 5 rows
- Topic names are bold, concise (2-4 words)
- Focus descriptions are brief — one to two sentences max

### 7. Prompting Questions
Subheading: **Prompting Questions** (orange/gold)

Numbered list, each with:
- **Bold label**: `{N}. On {Topic}`
- *Italicized question in quotes* — the actual question to ask on air
- Combine related questions into a single prompt where natural
- Typically 5 topic questions + 1 standard wrap-up
- **Last question is always the wrap-up:**

```
6. Wrap-Up
"What are a couple of takeaways you'd like the listeners to walk away with?"
```

### 8. Remember Bar
Blue background bar, centered text:
```
REMEMBER: Keep it conversational (60% guest / 40% host) • Share personal stories • Have fun!
```

### 9. Sportcoat Line
```
Sportcoat: _______________________________
```
Fill-in blank for wardrobe choice before filming.

---

## Design Notes

- **One page.** The entire prep sheet fits on a single page. This is a quick-reference for filming, not a deep-dive document.
- **Questions are distilled.** Janine's full SharePoint question docs have 10+ questions. The PDF condenses these into 5-6 focused prompts that guide the conversation without scripting it.
- **Tone matches the podcast.** Casual, direct, no jargon. Questions are phrased the way David would actually ask them.
- **Printed for studio.** This gets printed and brought to the recording — hence the sportcoat line and clean single-page layout.

---

## PDF Generation

The prep sheet .md files use a **hybrid markdown/HTML format** — some elements are raw HTML (`div.banner`, `h4`, `center`, `div.remember`) and others are standard markdown (`##` headings, `###` headings, `**bold**`, `*italic*`, `> blockquotes`, pipe tables).

**Generator:** `generate_pdfs.py` (project root) converts these to clean HTML and renders PDFs via weasyprint.

**Key rules for the generator:**
- Convert `###` → `<h3>` (episode title), `##` → `<h2>` (section headings) before checking for HTML pass-through
- Convert `**bold**` → `<strong>` and `*italic*` → `<em>` inside all content including table cells and blockquotes
- Blockquote text must render in `#000000` black (not gray) — enforced with `!important` in the CSS
- The sportcoat line uses class `.sportcoat` (not `p:last-child`) to avoid graying out other text
- HTML elements in the .md file pass through unchanged (with inline markdown still converted)

**CSS:** `reference/podcast-prep-pdf.css`

**To regenerate:** `python3 generate_pdfs.py` — update the `EPISODES` list in the script to include new episodes.

---

## Source Files

- **Episode question docs (Janine):** SharePoint > Podcast Planning > Season 1_Episode {N}_Topics and Questions.docx
- **Podcast Guide (tone/format):** SharePoint > Janine's OneDrive > Podcast Planning > Podcast Guide.docx
- **Episode map:** Obsidian > zzClaude/Cowork/Podcast Sync Prep - 2026-02-13.md
- **Existing PDFs:** reMarkable > Improving > Podcast > Episode {NN}.pdf
