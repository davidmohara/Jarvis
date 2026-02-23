<!-- personal:start -->
# Step 05: Generate PDF & Deliver

## MANDATORY EXECUTION RULES

1. You MUST generate the styled PDF using `npx md-to-pdf` with the custom CSS stylesheet.
2. You MUST verify the PDF was created successfully before reporting.
3. You MUST upload the PDF to reMarkable — this is not optional.
4. You MUST present a final summary with all outputs and any flags.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** PDF-format markdown from step 04
**Output:** Styled PDF, reMarkable upload, final summary

---

## YOUR TASK

### 1. Generate the PDF

Run via Bash:

```bash
cd /Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES
npx md-to-pdf "meetings/podcast-prep/Episode {N}.md" --stylesheet reference/podcast-prep-pdf.css
```

This will output: `meetings/podcast-prep/Episode {N}.pdf`

**If `md-to-pdf` is not installed or fails:**
- Try: `npx md-to-pdf@latest "meetings/podcast-prep/Episode {N}.md" --stylesheet reference/podcast-prep-pdf.css`
- If still failing, flag to the user: "PDF generation failed. The markdown is ready at {path} — you can convert it manually or I can troubleshoot."

### 2. Verify the PDF

Check that the file exists and has a reasonable size (should be 50KB+):

```bash
ls -la "meetings/podcast-prep/Episode {N}.pdf"
```

### 3. Upload to reMarkable

Upload automatically — no need to ask:

```bash
rmapi put "meetings/podcast-prep/Episode {N}.pdf" "/Improving/Podcast"
```

If `rmapi` fails or isn't authenticated:
- Flag: "reMarkable upload failed — rmapi may need re-authentication. The PDF is ready locally at {path}."
- This is a blocker — the workflow is not complete until the PDF is on the reMarkable.

### 4. Present Final Summary

```
## Podcast Prep Complete — Episode {N}

**Episode:** Season 1, Episode {N} — "{Title}"
**Guest:** {Guest Name}, {Guest Title}
**Filming:** {Date} at {Time}

### Documents Created
1. **Detailed prep sheet:** `meetings/podcast-prep/YYYY-MM-DD-guest-name.md`
2. **Studio PDF (markdown):** `meetings/podcast-prep/Episode {N}.md`
3. **Studio PDF (styled):** `meetings/podcast-prep/Episode {N}.pdf`

### Flags
{List any flags from the workflow:}
- {e.g., "No SharePoint question doc found — questions are suggested, not from Janine"}
- {e.g., "Guest not in Clay — background from web search"}
- {e.g., "Calendar event not found — date from episode map"}

### reMarkable
{Uploaded to /Improving/Podcast | Not uploaded (user declined) | Upload failed — PDF available locally}
```

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `md-to-pdf` not installed | Try `npx md-to-pdf@latest`. If that fails, flag and leave the markdown ready for manual conversion. |
| PDF renders poorly (wrong formatting) | The CSS might need adjustment. Flag: "PDF generated but may need formatting review. Check the styling and let me know if adjustments are needed." |
| `rmapi` not authenticated | Flag: "reMarkable upload requires authentication. Run `rmapi` manually to re-authenticate, then retry." |
| PDF is unexpectedly large or small | If <10KB, something went wrong. If >500KB, the CSS might be pulling external resources. Flag either case. |

---

## WORKFLOW COMPLETE

The podcast prep workflow is done. David has a detailed prep sheet for deep review, a single-page PDF for the studio, and the PDF on his reMarkable. Harper stands by for any revisions or follow-up tasks.
<!-- personal:end -->
