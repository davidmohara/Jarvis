---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- personal:start -->
# Step 05: Generate PDF & Deliver

## MANDATORY EXECUTION RULES

1. You MUST generate the PDF using **Python/weasyprint** — NOT `npx md-to-pdf`. The md-to-pdf approach does not apply the stylesheet correctly in the sandbox.
2. You MUST visually verify the rendered PDF using `mcp__PDF_Tools_-_Fill__Sign__Merge__Split__Extract__render_pdf_page` before presenting it to David.
3. The PDF MUST pass the visual format checklist (see below) before it is considered done.
4. Once the PDF passes all 15 visual checks, push to reMarkable immediately — no approval needed.
5. Present the PDF link and reMarkable upload confirmation together in the final summary.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** PDF-format markdown from step 04
**Output:** Styled single-page PDF presented for approval, then reMarkable upload on David's go-ahead

---

## YOUR TASK

### 1. Generate the PDF with Python/weasyprint

Write a Python script that renders the episode content as a self-contained HTML string and outputs it to PDF using weasyprint. Do NOT use md-to-pdf or any markdown-to-HTML converter — build the HTML directly so CSS is guaranteed to apply.

Install weasyprint if needed:
```bash
pip install weasyprint --break-system-packages
```

Output path: `meetings/podcast-prep/Episode {N}.pdf` (in the IES OneDrive folder)

The Python script must produce HTML with **all styles inlined in a `<style>` block** (no external CSS file references). Use the color palette and element structure from `reference/podcast-prep-pdf.css`:

- `.banner` — `background-color: #005495`, `color: #ffffff`, `border-bottom: 3px solid #FF9200`, centered, 13pt bold
- `.pipe` inside banner — `color: #FF9200`
- `.intro-label` (INTRO SCRIPT) — `color: #4496D2`, 8.5pt bold
- `.intro-text` — plain paragraph, `color: #000000`
- `.season-line` — centered, `color: #666666`
- `.episode-title` — centered, `color: #005495`, 12pt bold
- `.section-heading` — `color: #4496D2`, `border-bottom: 1.5px solid #4496D2`
- `table thead` — `background-color: #005495`, white text
- `td.num` — `color: #FF9200`, centered, bold
- `tr.even-row td` — `background-color: #F4F7F9`
- `.q-label` — bold, `color: #000000`
- `.q-text` — italic, indented 16px, `color: #000000`
- `.remember` — `background-color: #5AC1A6`, white text, centered
- `.sportcoat` — `color: #999999`, 7.5pt

All text elements must have `color: #000000 !important` or their explicit color set. Do NOT rely on CSS inheritance for text color — weasyprint may not propagate it correctly.

Page size: Letter, margins: 0.45in top/bottom, 0.6in left/right.

Target: **single page**. If content overflows, reduce font sizes (body: 9pt → 8.5pt, table: 8pt → 7.5pt, questions: 8.5pt → 8pt) and tighten margins before any content cuts.

### 2. Copy to Desktop for visual verification

The PDF Tools MCP can only access `/Users/davidohara/Desktop`. After writing the PDF to OneDrive, copy it:

```bash
# Via osascript (host Mac):
do shell script "cp 'FULL_ONEDRIVE_PATH/Episode {N}.pdf' '/Users/davidohara/Desktop/Episode{N}_check.pdf'"
```

### 3. MANDATORY Visual Verification

Use `mcp__PDF_Tools_-_Fill__Sign__Merge__Split__Extract__render_pdf_page` to render page 1 of `/Users/davidohara/Desktop/Episode{N}_check.pdf`.

**Visual Format Checklist — ALL items must pass before presenting to David:**

| # | Check | Pass Criteria |
|---|-------|---------------|
| 1 | **Banner** | Dark blue background (#005495), white text, orange bottom border, guest name visible |
| 2 | **Orange pipe** | The `|` separator between show name and guest is orange (#FF9200) |
| 3 | **INTRO SCRIPT label** | Blue text, small, above the intro paragraph |
| 4 | **Intro text** | Black, readable, NOT italic, NOT a blockquote |
| 5 | **Season/Episode line** | Centered, gray text |
| 6 | **Episode title** | Centered, dark blue, bold |
| 7 | **Section headings** | Blue with blue underline |
| 8 | **Table header** | Dark blue background, white text |
| 9 | **# column** | Orange numbers |
| 10 | **Alternating rows** | Even rows have light blue-gray background |
| 11 | **Question labels** | Bold black (e.g., "1. On Financial Risk") |
| 12 | **Question text** | Italic, indented |
| 13 | **REMEMBER bar** | Teal background (#5AC1A6), white text |
| 14 | **Sportcoat line** | Gray, small, at bottom |
| 15 | **Single page** | `total_pages` = 1 in the render response |

If ANY check fails: fix the Python script and re-render. Do NOT present a broken PDF to David. Do NOT report "looks correct" based on code inspection alone — you must see the rendered image.

If the PDF is 2 pages: reduce font sizes and/or tighten spacing, then re-render. Repeat until single page.

### 5. reMarkable Upload (immediately after visual verification passes)

Only after David approves, route to Knox for the reMarkable upload:

- File: `meetings/podcast-prep/Episode {N}.pdf`
- Destination: `/Improving/Podcast`
- Label: `Season 1, Episode {N} — {Guest Last Name}`

Knox executes the upload using the reMarkable upload skill. Refer to `.claude/skills/remarkable-upload/SKILL.md` for the Finder bridge pattern.

### 6. Present Final Summary

```
## Podcast Prep Complete — Episode {N}

**Episode:** Season 1, Episode {N} — "{Title}"
**Guest:** {Guest Name}, {Guest Title}
**Filming:** {Date} at {Time}

### Documents Created
1. **Detailed prep sheet:** `meetings/podcast-prep/YYYY-MM-DD-guest-name.md`
2. **Studio PDF (markdown source):** `meetings/podcast-prep/Episode {N}.md`
3. **Studio PDF (rendered):** `meetings/podcast-prep/Episode {N}.pdf`

### Flags
{List any flags from the workflow}

### reMarkable
{Uploaded to /Improving/Podcast as "Season 1, Episode {N} — {Guest Last Name}" | Awaiting approval}
```

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| weasyprint not installed | `pip install weasyprint --break-system-packages` then retry |
| Text invisible (white on white) | Add `color: #000000 !important` to every text element explicitly — do not rely on inheritance |
| PDF is 2 pages | Reduce font sizes: body 8.5pt, table 7.5pt, questions 8pt. Tighten margins. Re-render. |
| Visual check fails on any item | Fix the Python script. Re-render. Do not present until all 15 checks pass. |
| PDF Tools MCP path error | Copy file to `/Users/davidohara/Desktop/` via osascript first |
| reMarkable upload fails | Flag: "reMarkable upload failed — rmapi may need re-authentication." PDF is already approved and local. |

---

## WORKFLOW COMPLETE

The podcast prep workflow is done when: (1) the PDF passes all 15 visual checks, (2) David has approved it, and (3) it is on the reMarkable. Harper stands by for revisions.

---

## STEP COMPLETION TRACKING

Record step completion for eval harness:

```bash
python3 systems/eval-harness/record-step.py podcast-prep step-05-generate-pdf complete "${{frontmatter.started-at}}" "${{frontmatter.completed-at}}"
```
<!-- personal:end -->
