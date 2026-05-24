---
name: reddit-monitor
description: >
  Builds a live Reddit post monitor as an interactive HTML artifact. Use this skill whenever the user wants to monitor Reddit communities for posts worth engaging with — for outreach, community management, competitor tracking, lead generation, or brand listening. Triggers on requests like "show me Reddit posts to respond to", "monitor Reddit for [topic]", "find posts I should engage with on Reddit", "what's being said on Reddit about [topic]", "update my subreddit list", "add [subreddit] to my monitor", or any request involving Reddit community tracking or engagement queues. Also triggers when the user asks to refresh, update, or modify an existing Reddit monitor.
---

# Reddit Monitor Skill

Build a self-contained HTML artifact that pulls live data from Reddit's public JSON API, filters for recent and relevant posts, and surfaces a prioritized engagement queue. The artifact runs entirely in the browser — no server, no API key required.

**Output location:** All files produced by this skill (artifacts, config snapshots) go in `systems/reddit-monitor/` within the workspace.

**Agent:** Harper — personal evolution. Registered in `agents/harper.md` task portfolio.

---

## When to use this skill

- User wants to find Reddit posts worth responding to for a product, service, or topic
- User wants to add or remove subreddits from an existing monitor
- User wants to tune the keywords or lookback window on an existing monitor
- User wants to understand what's being discussed in specific communities

---

## Core behavior

### Step 1: Gather configuration from context

Before building anything, extract the following from the conversation:

- **Subreddits to monitor** — look for any prior outreach plan, strategy doc, or explicit list the user has mentioned. Default to what you find in context; ask only if nothing is available.
- **Keywords to match** — what topics, pain points, or product names should trigger a match? Pull from any product/strategy docs in context. Make these specific and community-appropriate (e.g., "skin irritation", "Grip-Lok", "tube securement" — not just "Kare").
- **Lookback window** — default 10 days unless the user specifies otherwise.
- **Reddit usernames to track** — any account names the user posts from. These are used to auto-detect threads the user has already responded to. Leave empty if not provided; the settings panel always allows adding them later.
- **Purpose** — who this is for and what kind of engagement is intended (affects how the UI is labeled and framed).

If any of these are missing and can't be inferred, ask one focused question before proceeding. Don't ask for information you can derive from context.

### Step 2: Build the artifact

Call `mcp__cowork__create_artifact` with a complete, self-contained HTML page.

The artifact must:

1. **Fetch posts from Reddit's public JSON API** — `https://www.reddit.com/r/{subreddit}/new.json?limit=100` for each subreddit. Reddit's API accepts browser fetch requests without auth. Use `User-Agent: "Mozilla/5.0"` headers and handle rate limiting gracefully (stagger requests with a short delay between subreddits).

2. **Filter by recency** — only show posts where `created_utc` is within the lookback window (default: past 10 days). Convert epoch timestamps correctly.

3. **Score posts** — assign a priority score based on:
   - Keyword match in title or selftext (primary signal, weighted by number of matches)
   - Comment count (engagement signal — more comments = more eyes on the thread)
   - Recency (newer posts get a small boost since the engagement window is still open)
   - Flair/tag match if relevant
   
   Surface the highest-scoring posts first.

4. **Display a clean two-section engagement queue:**

   **Active queue** — posts needing a response, sorted by priority score:
   - Subreddit badge
   - Post title (linked to the actual Reddit post)
   - Age (e.g., "3 days ago")
   - Comment count
   - Matched keywords highlighted
   - Priority score indicator (high / medium / low)
   - A "Mark responded" button that moves the post to the Responded section (persisted in localStorage)

   **Responded section** — collapsed by default, expandable. Shows posts that were either manually marked responded OR auto-detected as responded via username matching. Each entry shows a "You responded" badge and the date responded. Posts can be moved back to the active queue if marked by mistake.

5. **Auto-detect responded posts via username tracking:**

   On each data refresh, for every tracked username, fetch `https://www.reddit.com/user/{username}/comments.json?limit=100`. This returns the user's recent comments including the `link_id` field (the post ID they commented on). Cross-reference these post IDs against posts in the monitor — any match is automatically moved to the Responded section with a "You responded" badge.

   This is far more efficient than fetching comment trees per post. One API call per username covers ~100 recent comments.

   - Stagger these fetches after the subreddit fetches complete, with the same rate-limit delay
   - If a username fetch fails (private account, rate limit), fail silently — don't block the rest of the page
   - Auto-detected responses take priority over manual marks — if both exist, show "You responded" badge

6. **Editable settings panel** — collapsible panel at the top where the user can:
   - Add/remove monitored subreddits (text input + tag × buttons)
   - Add/remove keywords (same pattern)
   - Add/remove Reddit usernames to track for auto-detection (same pattern, labeled "My Reddit accounts")
   - All changes persist to localStorage and take effect on next reload

   The initial values for all three lists come from the configuration gathered in Step 1. localStorage overrides them once the user makes changes.

7. **Lookback window control** — a simple dropdown (7 days / 10 days / 14 days / 30 days) that re-filters without re-fetching.

8. **Loading and error states** — show a spinner while fetching, a clear error message if a subreddit 404s or rate-limits, and a "Reload" button to refresh all data.

9. **Summary stats at the top** — total posts fetched, posts matching keywords, subreddits checked, responded count (manual + auto-detected), last refreshed timestamp.

### Step 3: Handle "update my subreddit list" requests

When the user wants to add, remove, or swap subreddits from an existing monitor, use `mcp__cowork__update_artifact` to modify the hardcoded default list in the artifact's JS. This ensures new browsers / cleared localStorage get the right defaults.

Tell the user: "I've updated the default list in the artifact. Changes are live — open the monitor and it'll reflect the new subreddits."

---

## Artifact design guidelines

Keep the UI practical and information-dense. This is a work tool, not a marketing page.

- **Color coding:** High priority = red/orange badge, Medium = yellow, Low = gray
- **Layout:** Full-width table or card list; settings in a collapsible panel at the top
- **Font:** System font stack — no external dependencies
- **No CDN dependencies** — the artifact must work offline after initial load (except for the Reddit API calls themselves)
- **Dark-mode friendly** — use CSS variables for colors so system dark mode works

---

## localStorage keys

Use consistent key names so multiple refreshes/sessions share state:

- `reddit_monitor_subreddits` — JSON array of subreddit names (without r/ prefix)
- `reddit_monitor_keywords` — JSON array of keyword strings
- `reddit_monitor_usernames` — JSON array of Reddit usernames to track (without u/ prefix)
- `reddit_monitor_responded` — JSON array of post IDs manually marked as responded
- `reddit_monitor_auto_responded` — JSON array of post IDs auto-detected as responded via username matching (kept separate so auto-detection can re-run cleanly on refresh)
- `reddit_monitor_lookback_days` — integer

---

## Example subreddit and keyword defaults (Kare Devices context)

If you detect this is for Kare Devices / Kare Patch / tube securement outreach, use these defaults unless the user specifies otherwise:

**Subreddits:**
- feedingtube
- Gastroparesis
- nursing
- ChronicIllness
- spinalcordinjury
- neurogenicbladder
- caregiving

**Keywords:**
- catheter, tube securement, skin irritation, Grip-Lok, adhesive, dislodge, tape, GJ tube, NG tube, PEG tube, feeding tube, stoma, tubie, MCAS, skin breakdown

These are starting defaults — the user can tune them in the settings panel.

---

## What not to do

- Don't use Reddit's OAuth API or ask for credentials — the public JSON endpoint is sufficient for read access
- Don't build a server component — the artifact is entirely client-side
- Don't hardcode post data — it should fetch live on every load
- Don't skip the settings panel — the ability to update subreddits, keywords, and usernames interactively is a core requirement
- Don't show posts older than the lookback window even if they match keywords — recency is the gating filter, not an optional boost
- Don't fetch per-post comment trees to detect user responses — use the user's `/comments.json` feed instead; it's one call per username and covers ~100 recent comments
- Don't let a failed username fetch block the page — username tracking is a convenience feature, not a critical path
