---
name: podcast-prep
description: Generate episode prep documents for The Improving Edge — detailed reference sheet + single-page studio PDF
agent: harper
model: sonnet
---

<!-- personal:start -->
# Podcast Prep Workflow

**Goal:** Produce two documents for each episode of "The Improving Edge" podcast: (1) a detailed reference prep sheet with logistics, guest background, questions, talking points, and checklist, and (2) a single-page styled PDF for the studio — printed and brought to filming.

**Agent:** Harper — Storyteller, Communication, Content & Thought Leadership

**Architecture:** Sequential 5-step workflow. Identify the episode from input, gather all data sources, build the detailed prep sheet, distill into the single-page PDF format, then generate the styled PDF and offer delivery. Minimal user interaction — this runs end-to-end and presents results.

**Additive upstream input — `episode-prep-generator`:** This workflow does not merge with or get replaced by `workflows/episode-prep-generator/workflow.md`. That workflow produces a deep, 2-3 page transcript-first (or research-based) prep document — the thinking layer, usable as soon as a guest is booked, before a filming date/studio sheet exists. This workflow (`podcast-prep`) remains the *studio floor sheet* layer, and always pulls **both** the episode-prep-generator output (when one exists for the guest) **and** Janine's SharePoint questions doc — neither is a fallback for the other. Step 02 gathers whichever of the two actually return content; step 03 merges and dedupes questions from both into the single combined document. See the Inputs and Data Sources tables below.

---

## INITIALIZATION

### Why This Exists

David films "The Improving Edge" at MarketScale in Dallas. Each episode requires cross-referencing the Obsidian episode map, pulling Janine's questions from SharePoint, checking for a prior `episode-prep-generator` deep prep, looking up the guest, merging and distilling questions from whatever sources exist, and formatting a studio-ready PDF. This workflow automates the entire pipeline into a single invocation.

### Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Episode number or guest name | Yes | Identifies which episode to build the prep sheet for (see step 01) |

No flag is needed to opt into the episode-prep-generator source — step 02 always checks `meetings/podcast-prep/` for a matching file and always pulls Janine's SharePoint doc, every run. Whichever of the two actually has content feeds step 03; when both do, step 03 merges and dedupes them into one combined question set rather than picking one and discarding the other.

### Data Sources

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Obsidian episode map | Episode number, topic, guests, schedule | Obsidian MCP — `zzClaude/Cowork/Podcast Sync Prep - 2026-02-13.md` |
| `meetings/podcast-prep/` | Deep prep document from `episode-prep-generator` (questions, Suggested Flow, guest research brief), if one exists for this guest | Glob, Read tools — always checked |
| SharePoint | Janine's question docs (`Season 1_Episode {N}_Topics and Questions.docx`), Podcast Guide | M365 MCP (sharepoint_search, read_resource) — always pulled, not a fallback |
| Clay | Guest background, title, company, relationship context | Clay MCP (searchContacts, getContact) |
| M365 Calendar | Filming date, time, location, attendees | M365 MCP (outlook_calendar_search) |
| M365 Email | Recent threads with guest for logistics/context | M365 MCP (outlook_email_search) |
| Existing prep files | Check for duplicates in `meetings/podcast-prep/` | Glob, Read tools |

### Outputs

1. **Detailed prep sheet:** `meetings/podcast-prep/YYYY-MM-DD-guest-name.md` — logistics, guest background, questions, talking points, checklist
2. **PDF-format markdown:** `meetings/podcast-prep/Episode {N}.md` — single-page studio reference
3. **Styled PDF:** `meetings/podcast-prep/Episode {N}.pdf` — print-ready, styled with `reference/podcast-prep-pdf.css`
4. **reMarkable upload:** Automatically uploaded to `/Improving/Podcast` via `rmapi put`

### Key References

- **PDF template format:** `reference/podcast-prep-pdf-template.md` — defines the single-page layout
- **CSS stylesheet:** `reference/podcast-prep-pdf.css` — styles the PDF output
- **Existing examples:** `meetings/podcast-prep/` — past prep sheets for pattern reference

---

## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.

2. If `status: in-progress`:
   - You are resuming a previous run. Do NOT start over.
   - Read `current-step` to find where to continue.
   - Load `accumulated-context` — this is the data already gathered. Do not re-gather it.
   - Check that step's frontmatter:
     - If `status: in-progress`: the step was interrupted mid-execution — re-execute it.
     - If `status: not-started`: begin it fresh.
   - Notify the controller: "[Agent]: Resuming [workflow-name] from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`,
     set `current-step: step-01`, leave `sources_used: []` until step 02 populates it.
   - Begin at step-01.

4. If `status: aborted`:
   - Do not resume automatically. Surface to controller:
     "[Agent]: [workflow-name] was previously aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.

## CORRECTION MODE

If `state.yaml` shows `status: complete` for this episode AND the user's request is a targeted fix (e.g., "fix Don's title", "adjust PDF margins") rather than a full re-run, apply corrections without re-running the full pipeline:

1. Load the existing output files (`meetings/podcast-prep/*.md` and `.pdf`).
2. Identify which step(s) need to change:
   - **Guest data errors** (title, company, background) → fix in step-02 output, regenerate step-03/04/05.
   - **Prep sheet content** (talking points, questions) → fix in step-03 output, regenerate step-04/05.
   - **PDF formatting/layout** (single-page PDF only) → fix in step-04/05 output only.
3. Skip `step-02-gather-data.md` (the expensive SharePoint/Clay/Outlook/WebSearch pass) and instead use the cached data already in `accumulated-context` from the previous run. Start directly at the affected downstream step.
4. Regenerate only the affected outputs and downstream steps, then upload to reMarkable.

This avoids re-running the expensive multi-connector data-gather step for single-field corrections, reducing token waste.

## EXECUTION

Read fully and follow: `steps/step-01-identify-episode.md` to begin the workflow.
<!-- personal:end -->
