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

---

## INITIALIZATION

### Why This Exists

David films "The Improving Edge" at MarketScale in Dallas. Each episode requires cross-referencing the Obsidian episode map, pulling Janine's questions from SharePoint, looking up the guest, distilling questions, and formatting a studio-ready PDF. This workflow automates the entire pipeline into a single invocation.

### Data Sources

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Obsidian episode map | Episode number, topic, guests, schedule | Obsidian MCP — `zzClaude/Cowork/Podcast Sync Prep - 2026-02-13.md` |
| SharePoint | Janine's question docs (`Season 1_Episode {N}_Topics and Questions.docx`), Podcast Guide | M365 MCP (sharepoint_search, read_resource) |
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
     write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

4. If `status: aborted`:
   - Do not resume automatically. Surface to controller:
     "[Agent]: [workflow-name] was previously aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.

## EXECUTION

Read fully and follow: `steps/step-01-identify-episode.md` to begin the workflow.
<!-- personal:end -->
