<!-- personal:start -->
# Step 01: Identify Episode

## MANDATORY EXECUTION RULES

1. You MUST parse the input to determine whether the user provided an episode number or a guest name.
2. You MUST read the Obsidian episode map to match the input to a specific episode.
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

2. **Read the Obsidian episode map.**
   - Use Obsidian MCP: `get_vault_file` for `zzClaude/Cowork/Podcast Sync Prep - 2026-02-13.md`
   - This file contains the master episode table with: episode number, topic/title, primary guest, secondary guest, filming date, status
   - Find the matching row

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
| No match in episode map | Ask: "I couldn't find an episode matching '{input}'. Can you give me the episode number or the guest's full name?" |
| Multiple matches (e.g., guest on two episodes) | Present options: "Found multiple matches: Episode {N} ({Title}) and Episode {M} ({Title}). Which one?" |
| Episode map file not found in Obsidian | Search vault for alternative locations: `search_vault_simple` for "podcast" or "episode". Flag: "Episode map not at expected path — searching vault." |
| Calendar event not found | Proceed with episode map date. Flag: "No calendar event found for this filming date. Using the episode map schedule." |

---

## NEXT STEP

Read fully and follow: `step-02-gather-data.md`
<!-- personal:end -->
