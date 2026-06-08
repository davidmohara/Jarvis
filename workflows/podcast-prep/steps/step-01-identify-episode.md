---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- personal:start -->
# Step 01: Identify Episode

## MANDATORY EXECUTION RULES

1. You MUST parse the input to determine whether the user provided an episode number or a guest name.
2. You MUST search SharePoint for Janine's episode doc first — this is the authoritative source. Obsidian notes are secondary and should only be used if SharePoint yields nothing.
3. You MUST search the calendar for the filming event to get date, time, location, and attendees.
4. You MUST store all episode details in working memory before proceeding.
5. Do NOT proceed to step 02 without a confirmed episode match.
6. If no match is found, ask the user to clarify.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** User's request — episode number (e.g., "Episode 5") or guest name (e.g., "Robyn Fuentes")
**Output:** Episode details stored in working memory for subsequent steps

---

## YOUR TASK

### Sequence

1. **Parse the input.** Determine what the user provided:

   | Input Type | Examples | How to Match |
   |------------|----------|-------------|
   | Episode number | "Episode 5", "Ep 5", "5" | Direct match on episode number in the map |
   | Guest name | "Robyn Fuentes", "Robyn", "John Ruzick" | Match against primary or secondary guest columns |
   | Topic | "agent orchestration", "AI business model" | Match against topic/title column |

2. **Search SharePoint for Janine's episode doc (primary source).**
   - Use M365 MCP: `sharepoint_search` with the guest name and/or episode number as search terms — e.g., `"{Guest Name} podcast episode"` or `"episode {N} podcast topics"`
   - Do not assume a specific filename or folder path — search broadly and read whatever doc surfaces that contains the episode's title, topic framing, and interview questions
   - Read the full doc via `read_resource` and extract: episode title, season/episode number (if stated), topic framing, and the complete question list — use all of it verbatim in the prep sheet
   - If multiple docs match, prefer the most recently modified one and note the others
   - If Janine's doc is not found on SharePoint: fall back to Obsidian (`search_vault_simple` for "podcast episode {N}" or guest name) and flag: "Janine's SharePoint doc not found — using Obsidian notes as fallback. Content may be incomplete."
   - Do NOT use the old Obsidian sync doc (`zzClaude/Cowork/Podcast Sync Prep - 2026-02-13.md`) — it only covers Episodes 1-7 and is out of date.

3. **Search the calendar for the filming event.**
   - Use M365 MCP: `outlook_calendar_search` for "Improving Edge" or "MarketScale" or "podcast" near the expected date
   - Extract: date, time, location, attendees (host, guest, producer, video/marketing)
   - If no calendar event found, use the date from the episode map and flag it

4. **Store episode details in working memory:**
   ```
   episode:
     number: {N}
     title: "{Episode Title}"
     season: 1
     primary_guest:
       name: "{Full Name}"
       title: "{Title/Role}"
     secondary_guest: "{Name}" or null
     filming:
       date: YYYY-MM-DD
       time: "{Time range}"
       location: "{Location}"
     attendees:
       host: "David O'Hara"
       producer: "{Name}"
       video: "{Name}"
     status: "{from episode map}"
   ```

5. **Confirm the match to the user.** Brief summary:
   ```
   Found: Season 1, Episode {N} — "{Title}"
   Guest: {Name}, {Title}
   Filming: {Date} at {Time}, MarketScale Dallas
   ```

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Janine's doc not found on SharePoint | Fall back to Obsidian `search_vault_simple` for "podcast episode {N}". Flag: "Janine's doc not found on SharePoint — using Obsidian notes as fallback." |
| No match anywhere | Ask: "I couldn't find an episode matching '{input}'. Can you give me the episode number or the guest's full name?" |
| Multiple matches | Present options: "Found multiple matches: Episode {N} ({Title}) and Episode {M} ({Title}). Which one?" |
| Calendar event not found | Proceed with date from Janine's doc or Obsidian. Flag: "No calendar event found — using episode doc schedule." |

---


## STEP COMPLETION TRACKING

Record step completion for eval harness:

```bash
python3 systems/eval-harness/record-step.py podcast-prep step-01-identify-episode complete "${{frontmatter.started-at}}" "${{frontmatter.completed-at}}"
```

## NEXT STEP

Read fully and follow: `step-02-gather-data.md`
<!-- personal:end -->
