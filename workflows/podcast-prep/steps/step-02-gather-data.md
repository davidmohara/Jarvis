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

1. You MUST pull BOTH question sources unconditionally, every run: the `episode-prep-generator` output (if one exists for this guest) AND Janine's SharePoint question doc. Neither is a fallback for the other — both are always attempted, and step 03 merges whatever came back.
2. You MUST look up the guest in Clay for background and relationship context.
3. You MUST check for existing prep sheets in `meetings/podcast-prep/` to avoid duplicating work.
4. You MUST flag any missing data sources clearly — do not silently skip.
5. Do NOT build any documents in this step. This step is data gathering only.
6. You MUST write `sources_used` to `state.yaml` as a list before finishing this step — populate it with whichever of `episode-prep` / `sharepoint` actually returned usable content for this run (omit a source entirely if it had nothing, rather than failing the step).

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** Episode details from step 01
**Output:** All gathered data stored in working memory for steps 03 and 04; `sources_used` written to `state.yaml`

---

## YOUR TASK

### Sequence

1. **Pull the episode-prep-generator output, if one exists.**
   - Glob `meetings/podcast-prep/*{guest-last-name-slug}*.md` (and, if the episode's original booking date is known, try `meetings/podcast-prep/{that-date}-{guest-last-name-slug}.md` directly first).
   - If found: read the full file via Read. Extract the questions block (with clusters and follow-ups), the Suggested Flow section, the guest research brief, and the Notes section (transcript source, sign-off caveats).
   - If NOT found: note it — "No episode-prep-generator output found for {guest_name} in `meetings/podcast-prep/`." This is not a failure; proceed to the SharePoint pull below regardless.

2. **Pull Janine's SharePoint question doc — always, regardless of whether episode-prep output was found.**
   - Use M365 MCP: `sharepoint_search` for `Season 1_Episode {N}_Topics and Questions`
   - If found, use `read_resource` to pull the full content
   - Extract: all questions, topic groupings, any notes from Janine
   - If NOT found: flag it — "No SharePoint question doc for Episode {N}." This is not a failure either; step 03 works with whatever combination of sources actually returned content.

3. **Populate `sources_used`.** After both pulls above, set `state.yaml`'s `sources_used` to a list containing `episode-prep` if step 1 found a file, `sharepoint` if step 2 found a doc, both if both did, or an empty list if neither did (in which case step 03 falls through to its own suggested-questions generation — see step-03's failure modes).

4. **Search SharePoint for the Podcast Guide.**
   - Use M365 MCP: `sharepoint_search` for `Podcast Guide`
   - This contains tone/format reference from Janine
   - If already cached from a previous run, skip. Key reminders:
     - Conversational, light, casual tone
     - 40% host / 60% guest speaking split
     - ~1 hour filming, 25-35 min final cut
     - Unscripted, key topics as guide not script

5. **Look up the guest in Clay.**
   - Use Clay MCP: `searchContacts` by guest name
   - Then `getContact` for the full profile
   - Extract: full name, title, company, background, relationship notes, last interaction date
   - If guest not in Clay: note it, proceed with whatever is available from the episode map and web search

6. **Search email for recent threads with the guest.**
   - Use M365 MCP: `outlook_email_search` for the guest's name
   - Look for: logistics emails, topic confirmations, scheduling details, any context changes
   - Extract key context: confirmed topics, special requests, schedule changes

7. **Check for existing prep sheets.**
   - Use Glob: `meetings/podcast-prep/*{guest-name-slug}*` and `meetings/podcast-prep/*Episode*{N}*`
   - If detailed prep sheet already exists: flag it — "Found existing prep sheet at {path}. Want me to rebuild or update?"
   - If PDF-format sheet already exists: flag similarly

8. **Store all gathered data in working memory:**
   ```
   gathered_data:
     sources_used: [episode-prep, sharepoint]  # list — either, both, or empty; never a binary either/or flag
     episode_prep_source:
       found: true/false
       source_path: "reviews/episode-prep/{file}.md" or null
       questions_block: "..." or null
       suggested_flow: "..." or null
       guest_research_brief: "..." or null
       notes_section: "..." or null
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
| No episode-prep-generator output exists for this guest | Not a failure — note it, set `sources_used` without `episode-prep`, and proceed using SharePoint (and/or step-03's suggested-question generation if SharePoint also has nothing). |
| SharePoint search fails or returns no results | Not a failure — note it, set `sources_used` without `sharepoint`, and proceed using episode-prep output (and/or step-03's suggested-question generation if episode-prep also has nothing). Flag: "No question doc found on SharePoint for Episode {N}." |
| Neither source returns anything | Flag clearly: "No episode-prep-generator output and no SharePoint question doc found for Episode {N}. Step 03 will generate suggested questions." Set `sources_used: []`. Proceed — do not stall the workflow. |
| Guest not in Clay | Flag: "Guest not found in Clay. Using episode map and web search for background." Do a quick WebSearch for the guest's name + company for bio context. |
| Email search returns nothing | Proceed. Not all guests have prior email threads. |
| Existing prep sheet found | Ask user: "Found existing prep at {path}. Rebuild from scratch, or update the existing one?" |
| SharePoint/M365 MCP unavailable | Flag: "M365 connection unavailable. Proceeding with Obsidian and Clay data only. SharePoint questions will need manual input." |

---


## STEP COMPLETION TRACKING

Record step completion for eval harness:

```bash
python3 systems/eval-harness/record-step.py podcast-prep step-02-gather-data complete "${{frontmatter.started-at}}" "${{frontmatter.completed-at}}"
```

## NEXT STEP

Read fully and follow: `step-03-build-prep-sheet.md`
<!-- personal:end -->
