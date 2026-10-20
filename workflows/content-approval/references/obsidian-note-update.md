<!-- system:start -->
## Obsidian Note Update Protocol (for all publish operations)

**This protocol applies when publishing a post (Step 6a) or when manually updating a published post. Run this BEFORE Ghost publish to ensure vault sync on success.**

> **Note for content-discovery:** When discovery creates a pending-drafts.json entry, it sets a `content_type` field on that entry — either `"post"` or `"article"`. Harper uses this field here to route to the correct vault folder. If `content_type` is absent, Harper defaults to `"post"`.

### Obsidian Update Steps:

1. **Determine the vault folder** from the `content_type` field on the pending-drafts.json entry:
   - If `content_type == "article"`: vault folder is `Mind/Articles/`
   - If `content_type == "post"`, is absent, or is null: vault folder is `Mind/Posts/`

2. **Build the filename and find the note:**
   - If the pending-drafts.json entry has an `obsidian_slug` field that is non-null and non-empty: use it as the filename slug.
   - If `obsidian_slug` is absent or null: derive from the `title` field — lowercase, hyphens for spaces, strip punctuation.
   - **Expected filename pattern:** `_{slug}.md` (with leading underscore, indicating draft status)
   - Example: title "The Corrections Are the Leak" → expected filename `_the-corrections-are-the-leak.md`

3. **Find the note** using `mcp__obsidian-mcp-tools__get_vault_file` with the path `{vault_folder}/_{slug}.md`. If not found, surface a hard failure to David.

4. **If the note is NOT found:** Do NOT skip silently. Stop all processing immediately:
   - Log the missing file
   - Prepend this warning to any Slack notification:
   ```
   [WARNING] Obsidian note not found — expected {vault_folder}/_{slug}.md. Cannot proceed with publication.
   ```
   - Do NOT proceed to Ghost publish if the note is missing. This prevents publishing without vault sync.

5. **If found, update the note in this exact order:**

   **Step 5a: Update frontmatter fields:**
   - Set `status: "Posted"` (changed from "Draft" or similar)
   - Set `published_url: "{url from Ghost response}"` (add the live URL)
   - Set `published_date: "{ISO 8601 timestamp from Ghost response}"` (when published)

   **Step 5b: Update tags in frontmatter:**
   - Add tag: `status: Posted` (indicates publication status)
   - Remove tag: `status: Draft` (if present, old draft tag)
   - Keep all other tags unchanged

   **Step 5c: Rename the file:**
   - Strip the leading `_` from the filename
   - New filename pattern: `{slug}.md` (no leading underscore)
   - Example: `_the-corrections-are-the-leak.md` → `the-corrections-are-the-leak.md`
   - Use `mcp__obsidian-mcp-tools__rename_vault_file` for the rename

6. **If any step in 5a/5b/5c fails:**
   - Log the failure with specific error details
   - Prepend a warning to the Slack notification: `[WARNING] Could not update Obsidian vault — {specific error}. Post is live but vault is out of sync. Update manually.`
   - Continue to Ghost publish — the post must still be published even if vault sync fails
   - But note that the vault is now out of sync and will need manual correction

7. **Verify the update succeeded:**
   - Re-fetch the file from Obsidian to confirm all changes: frontmatter updated, filename renamed, tags changed
   - If verification fails, note it but continue — the important part (vault update) was attempted

---
<!-- system:end -->
