---
status: complete
started-at: "2026-08-27T20:05:00Z"
completed-at: "2026-08-27T20:10:00Z"
outputs:
  deliverables_checked: 0
  renamed: []
  moved:
    - from: "drafts/improving-blog/2026-08-22-the-twenty-percent-nobody-budgeted.md"
      to: "content/improving-blog/2026-08-22-the-twenty-percent-nobody-budgeted.md"
      reason: "David's decision (relayed by controller) to retire the non-canonical drafts/ root directory; content/improving-blog/ is the canonical location per workflows/content-pipeline/steps/step-01-discover.md. Filename already followed YYYY-MM-DD-slug.md convention, no rename needed."
  verified_clean: 1
  no_pdf_docx_pptx_epub_in_diff: true
model: sonnet
---

<!-- system:start -->
# Step 02: Organize Deliverables

## MANDATORY EXECUTION RULES

1. You MUST check every generated deliverable (PDF, Word, PPTX, EPUB) created or modified during the session.
2. You MUST verify each deliverable's name follows the output naming conventions defined in the controller's system config.
3. You MUST verify each deliverable is in the correct directory.
4. Do NOT rename or move files without recording the action. If a convention conflict exists, note it and move on.

---

## EXECUTION PROTOCOL

**Agent:** Master
**Mode:** Automated — no controller interaction needed
**Input:** Git status (new and modified files), output naming conventions from system config
**Output:** List of verified, renamed, or moved files

---

## YOUR TASK

### Naming Convention Reference

Deliverables follow two tracks:

**Source files (markdown — for the system):**
- Date-based slug format: `YYYY-MM-DD-slug.md`
- Exception: Grouped outputs (e.g., podcast episodes) use descriptive names within their subfolder

**Deliverable files (PDF, Word, PPTX — for reading/distribution):**
- Human-readable names optimized for consumption
- No date prefixes unless the date is part of the document's identity
- Short, clear — the way you'd label a folder on a desk

### Sequence

1. **List all new/modified non-markdown files** from git status:
   - Filter for: `.pdf`, `.docx`, `.pptx`, `.epub`
   - These are the deliverables to check

2. **For every PDF anywhere in the repo, apply the build artifact rule first:**

   > **RULE:** If a PDF has a corresponding markdown source file covering the same content — regardless of directory — it is a **build artifact, not a deliverable.** The markdown is canonical. Delete the PDF before staging. Do not commit it.

   This applies repo-wide: `meetings/`, `projects/`, `identity/`, or any other directory. PDF and markdown filenames will often differ — the PDF uses a short human-readable name (e.g., `Tim Brackney.pdf`) while the markdown uses a date-slug (e.g., `2026-06-16-tim-brackney-springline.md`). Do not rely on filename matching. Instead, for each `**/*.pdf` found in git diff output:

   - Read the PDF filename and any `.md` files created or modified this session in the same directory or elsewhere in the repo
   - Ask: does any markdown file cover the same content, person, project, or topic as this PDF? Match on subject matter — not filename
   - If a corresponding markdown exists anywhere in the repo: **delete the PDF**
   - If no corresponding markdown exists anywhere in the repo for this PDF: treat as standalone deliverable and proceed to the checks below

3. **For each remaining deliverable (no corresponding markdown source), verify:**

   | Check | Pass | Fail Action |
   |-------|------|-------------|
   | Name follows human-readable convention | Name is clear, no unnecessary date prefix | Rename to match convention |
   | Located in correct directory | Next to source markdown, or in `meetings/` | Move to correct location |
   | Source markdown exists | Deliverable has a corresponding `.md` source | Note as standalone — may be intentional |

3. **For each source markdown created this session, verify:**

   | Check | Pass | Fail Action |
   |-------|------|-------------|
   | Follows `YYYY-MM-DD-slug.md` pattern | Correct | Rename to match convention |
   | Located in correct directory per file map | Correct | Move to correct location |

4. **Store results** in working memory:
   ```
   organize_results:
     deliverables_checked: N
     renamed:
       - from: ...
         to: ...
         reason: ...
     moved:
       - from: ...
         to: ...
         reason: ...
     verified_clean: N
   ```

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Ambiguous naming — could be intentional | Leave as-is. Note in summary. |
| No clear target directory | Leave in current location. Note in summary. |
| Rename would conflict with existing file | Do not rename. Flag for controller review. |

---


## STEP COMPLETION TRACKING

Record step completion for eval harness:

```bash
python3 systems/eval-harness/record-step.py shutdown-cleanup step-02-organize-deliverables complete "${{frontmatter.started-at}}" "${{frontmatter.completed-at}}"
```

## NEXT STEP

Read fully and follow: `step-03-gitignore-check.md`
<!-- system:end -->

<!-- personal:start -->
### Known Deliverable Destinations

Use this routing table when a deliverable is found in the wrong location. Match on file type and name pattern, then move to the correct destination.

| Pattern | Type | Correct Destination |
|---------|------|---------------------|
| `One Texas * Monthly Update.pptx` | PPTX | `/Users/davidohara/Library/CloudStorage/OneDrive-Improving/Presentations/One Texas/Monthly Meetings/` |
| `One Texas * Scorecard.pptx` | PPTX | `/Users/davidohara/Library/CloudStorage/OneDrive-Improving/Presentations/One Texas/Monthly Meetings/` |

**Note:** If any One Texas PPTX is found in `meetings/` or anywhere in the IES repo, move it to the OneDrive Presentations path above. The IES `meetings/` directory is for markdown source files only.
<!-- personal:end -->
