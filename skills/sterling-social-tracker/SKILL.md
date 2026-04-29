---
name: sterling-social-tracker
owning_agent: sterling
model: sonnet
trigger_keywords: [social tracker, dfw events, what's happening, events this week, dfw social, social calendar]
trigger_agents: [sterling, chief]
description: >
  Scrapes dfw.msondo.com for upcoming DFW events, filters by personal interest profile, and
  presents a curated table covering the next 3-4 weeks. Auto-runs during the weekly review as
  a forward-looking social planning step. Captures feedback on presented events and updates
  filter preferences directly in this file over time.
---

<!-- system:start -->
# Sterling Social Tracker

Pull upcoming DFW events from dfw.msondo.com, filter for relevance, and surface a curated
table for the next 3-4 weeks. This is a planning tool — the goal is to surface things worth
knowing about before they sell out or require coordination, not to produce an exhaustive list.

---

## Interest Profile

These are the categories worth surfacing. Events that don't fit get dropped silently.

| Category | What Qualifies |
|----------|---------------|
| **Food & Dining** | Chef dinners, pop-up restaurants, food festivals, wine tastings, spirit tastings, culinary events, farm-to-table experiences |
| **Music & Live Performance** | Concerts (all genres), jazz nights, live music at quality venues, comedy shows worth the drive |
| **Arts & Culture** | Gallery openings, museum special exhibits, film premieres, theater productions, design events, cultural festivals |

### Learned Preferences

*(This section is updated by Sterling when David provides feedback on presented events. Each entry notes what was flagged as useful or not useful, and why — so the filter improves over time.)*

| Date Added | Feedback | Filter Update Applied |
|------------|----------|-----------------------|
| — | No feedback yet — baseline run | Using initial interest profile above |

---

## Execution

### Step 1: Fetch the page

Open dfw.msondo.com in Chrome:

```
mcp__Control_Chrome__open_url(url="https://dfw.msondo.com", new_tab=true)
```

Wait for load, then extract the full page content:

```javascript
document.body.innerText.substring(0, 15000)
```

If the first 15,000 characters don't cover all events, continue in 10,000-character chunks:

```javascript
document.body.innerText.substring(15000, 25000)
```

Continue until no new event content appears.

### Step 2: Parse events

From the raw text, extract every event entry. For each, capture:

- **Event name**
- **Date / time** (exact or approximate)
- **Venue / location**
- **Category** (assign from: Food & Dining, Music, Arts & Culture, Networking, Other)
- **Brief description** (1-2 sentences, from page copy)
- **URL or ticket link** if present on the page

Build a raw list before filtering — don't discard anything until Step 3.

### Step 3: Filter and curate

Apply the Interest Profile above. Keep events that match Food & Dining, Music & Live Performance,
or Arts & Culture. Drop everything else.

Also apply any Learned Preferences from the table above — if prior feedback flagged a venue,
price point, or event type as not worth surfacing, respect that here.

**Lookahead window:** Events from today through 4 weeks out. Drop anything beyond 4 weeks.
Drop anything already in the past.

If more than 12 events survive filtering, prioritize: higher-signal events (known venues,
notable artists, limited capacity indicators) over generic recurring listings.

### Step 4: Present the table

Output a markdown table with these columns:

| Date | Event | Venue | Category | Notes | Link |
|------|-------|-------|----------|-------|------|

Sort by date ascending. Keep it scannable — Notes column is max 1 sentence.

After the table, add a one-line count: *"X events surfaced across Y-Z date range."*

### Step 5: Early feedback loop

**For the first 8 weekly review runs** (tracked by the feedback count in Learned Preferences
above), append this prompt after the table:

---
*Quick feedback to tune the filter: anything here you'd never want to see again? Anything
missing that should be on the radar? A one-line response is enough — I'll update the skill.*

---

When David responds with feedback:
1. Parse the signal (e.g., "skip comedy shows", "include more wine events", "that venue is always good")
2. Update the **Learned Preferences** table in this SKILL.md with the date, feedback summary, and what filter rule was applied
3. Adjust future filtering accordingly — don't ask for confirmation, just apply and note it

Once 8 feedback rounds are complete, remove the feedback prompt. The filter is mature.

### Step 6: Append to weekly review file

Append the social tracker output to the current week's review file at
`reviews/weekly/YYYY-Wxx.md`:

```markdown
## Social Calendar — DFW Lookahead

{table from Step 4}
```

If the weekly review file doesn't exist yet, write the section to working memory instead:
`memory/working/YYYY-MM-DD-social-tracker.md`

---

## Error Handling

| Situation | Action |
|-----------|--------|
| Page fails to load in Chrome | Retry once. If still fails, report "dfw.msondo.com unavailable" and skip — do not block the weekly review. |
| Page loads but no events found | Report "No upcoming events found on dfw.msondo.com" — the site may be sparse. |
| All events fall outside lookahead window | Report "No events in the next 4 weeks" — nothing to surface. |
| Feedback is ambiguous | Apply the most conservative interpretation and note it in Learned Preferences. Ask for clarification only if the feedback could mean two opposite things. |

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
