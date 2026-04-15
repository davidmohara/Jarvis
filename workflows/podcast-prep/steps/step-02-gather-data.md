---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- personal:start -->
# Step 02: Gather Data

## MANDATORY EXECUTION RULES

1. You MUST search SharePoint for the episode's question document before proceeding.
2. You MUST look up the guest in Clay for background and relationship context.
3. You MUST check for existing prep sheets in `meetings/podcast-prep/` to avoid duplicating work.
4. You MUST flag any missing data sources clearly — do not silently skip.
5. Do NOT build any documents in this step. This step is data gathering only.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** Episode details from step 01
**Output:** All gathered data stored in working memory for steps 03 and 04

---

## YOUR TASK

### Sequence

1. **Search SharePoint for the question document.**
   - Use M365 MCP: `sharepoint_search` for `Season 1_Episode {N}_Topics and Questions`
   - If found, use `read_resource` to pull the full content
   - Extract: all questions, topic groupings, any notes from Janine
   - If NOT found: flag it — "No SharePoint question doc for Episode {N}. Will generate suggested questions."

2. **Search SharePoint for the Podcast Guide.**
   - Use M365 MCP: `sharepoint_search` for `Podcast Guide`
   - This contains tone/format reference from Janine
   - If already cached from a previous run, skip. Key reminders:
     - Conversational, light, casual tone
     - 40% host / 60% guest speaking split
     - ~1 hour filming, 25-35 min final cut
     - Unscripted, key topics as guide not script

3. **Look up the guest in Clay.**
   - Use Clay MCP: `searchContacts` by guest name
   - Then `getContact` for the full profile
   - Extract: full name, title, company, background, relationship notes, last interaction date
   - If guest not in Clay: note it, proceed with whatever is available from the episode map and web search

4. **Search email for recent threads with the guest.**
   - Use M365 MCP: `outlook_email_search` for the guest's name
   - Look for: logistics emails, topic confirmations, scheduling details, any context changes
   - Extract key context: confirmed topics, special requests, schedule changes

5. **Check for existing prep sheets.**
   - Use Glob: `meetings/podcast-prep/*{guest-name-slug}*` and `meetings/podcast-prep/*Episode*{N}*`
   - If detailed prep sheet already exists: flag it — "Found existing prep sheet at {path}. Want me to rebuild or update?"
   - If PDF-format sheet already exists: flag similarly

6. **Store all gathered data in working memory:**
   ```
   gathered_data:
     sharepoint_questions:
       found: true/false
       questions: [...] or null
       source_file: "{filename}" or null
     podcast_guide:
       found: true/false
       key_reminders: [...]
     guest_clay:
       found: true/false
       full_name: "..."
       title: "..."
       company: "..."
       background: "..."
       relationship_notes: "..."
       last_interaction: "..."
     email_context:
       found: true/false
       key_threads: [...] or null
     existing_prep:
       detailed_sheet: "{path}" or null
       pdf_sheet: "{path}" or null
     flags: [list of any missing or noteworthy items]
   ```

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| SharePoint search fails or returns no results | Flag: "No question doc found on SharePoint for Episode {N}. Will generate suggested questions in step 03." Proceed. |
| Guest not in Clay | Flag: "Guest not found in Clay. Using episode map and web search for background." Do a quick WebSearch for the guest's name + company for bio context. |
| Email search returns nothing | Proceed. Not all guests have prior email threads. |
| Existing prep sheet found | Ask user: "Found existing prep at {path}. Rebuild from scratch, or update the existing one?" |
| SharePoint/M365 MCP unavailable | Flag: "M365 connection unavailable. Proceeding with Obsidian and Clay data only. SharePoint questions will need manual input." |

---

## NEXT STEP

Read fully and follow: `step-03-build-prep-sheet.md`
<!-- personal:end -->
