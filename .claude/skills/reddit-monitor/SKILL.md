---
name: reddit-monitor
description: >
  Builds a live Reddit post monitor served locally (a small Node server at http://localhost:7429, NOT a published Claude Artifact — Artifacts run under a CSP that blocks external fetches, so a Reddit-fetching artifact can never work). Use this skill whenever the user wants to monitor Reddit communities for posts worth engaging with — for outreach, community management, competitor tracking, lead generation, or brand listening. Triggers on requests like "show me Reddit posts to respond to", "monitor Reddit for [topic]", "find posts I should engage with on Reddit", "what's being said on Reddit about [topic]", "update my subreddit list", "add [subreddit] to my monitor", or any request involving Reddit community tracking or engagement queues. Also triggers when the user asks to refresh, update, or modify an existing Reddit monitor.
model: sonnet
---

# Reddit Monitor Skill

Build a live Reddit post monitor that filters for recent and relevant posts and surfaces a prioritized engagement queue.

**Delivery mechanism — read this before building anything:** This tool CANNOT be delivered as a published Claude Artifact. Published Artifacts run inside a sandboxed iframe under a strict Content-Security-Policy that blocks all `fetch`/`XHR`/`WebSocket` requests to third-party hosts, including `reddit.com` and any Reddit API mirror. Every subreddit fetch from a published artifact fails with "Load failed" — always, for every subreddit, with no exceptions. This is documented, structural behavior of the Artifact publishing tool, not a fixable bug in the page.

The correct delivery mechanism is a **local Node server** that (a) serves the monitor's HTML/JS/CSS directly over `http://localhost` — a normal same-origin page, not a sandboxed iframe, so the CSP restriction doesn't apply — and (b) proxies Reddit data server-side, since server-to-server requests aren't subject to browser CSP either. See `systems/reddit-monitor/proxy.js` for the canonical implementation: it serves the UI at `http://localhost:7429/` and proxies Reddit data through Arctic Shift (`arctic-shift.photon-reddit.com`, a free public mirror of Reddit's search API) via `/api/posts` and `/api/comments` endpoints.

**Output location:** All files produced by this skill (the local server, config snapshots) go in `systems/reddit-monitor/` within the workspace.

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

### Step 2: Build (or update) the local server

Do not call `mcp__cowork__create_artifact` / the Artifact tool for this skill — see the CSP explanation above. Instead, write (or edit) a single Node script at `systems/reddit-monitor/proxy.js` that both serves the UI and proxies Reddit data. It needs no dependencies beyond Node's built-in `http`/`https` modules.

The script must implement two things:

**A. An HTTP server** (plain `http.createServer`, no framework needed) that:
- Serves the monitor's HTML/CSS/JS (as a template string is fine) at `/` and `/index.html`
- Proxies subreddit post search through Arctic Shift at `GET /api/posts?subreddit={sub}&limit={n}&after={date}`, forwarding to `https://arctic-shift.photon-reddit.com/api/posts/search?subreddit={sub}&limit={n}&after={date}`. `after` accepts an ISO date (`YYYY-MM-DD`), epoch seconds, or a relative string.
- Proxies per-user comment history through Arctic Shift at `GET /api/comments?author={user}&limit={n}&after={date}`, forwarding to `https://arctic-shift.photon-reddit.com/api/comments/search?author={user}&limit={n}&after={date}` — this is what powers auto-detection of responded threads (see item 5 below).
- Validates the `subreddit`/`author` params against a safe character allowlist before proxying (no path injection).
- Sets `Access-Control-Allow-Origin: *` on proxied responses so the page's own-origin fetches always succeed.

**B. The client-side HTML/JS app**, served by that same process, which does everything described below. Because it's served from `http://localhost:7429` (a normal origin, not a sandboxed iframe), it can freely call its own `/api/*` endpoints — there is no CSP restriction on same-origin or server-side requests.

The app must:

1. **Fetch posts via the local proxy** — call `/api/posts?subreddit={sub}&limit=100&after={lookback-date}` for each monitored subreddit (never call `reddit.com` or any Reddit API directly from the browser — that's what triggers the CSP failure when this ever gets treated as a hosted artifact instead of a locally-served page). Stagger requests with a short delay between subreddits to be polite to the upstream API.

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

   On each data refresh, for every tracked username, fetch `/api/comments?author={username}&limit=100&after={lookback-date}` (the local proxy endpoint, which forwards to Arctic Shift server-side). This returns the user's recent comments including the `link_id` field (the post ID they commented on). Cross-reference these post IDs against posts in the monitor — any match is automatically moved to the Responded section with a "You responded" badge.

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

When the user wants to add, remove, or swap subreddits from an existing monitor, edit the hardcoded `DEFAULTS` object in `systems/reddit-monitor/proxy.js` directly (use the Edit tool — this is a local file, not a published artifact). This ensures new browsers / cleared localStorage get the right defaults. If the server is currently running, the change takes effect on the next server restart (or immediately for anyone who clears localStorage and reloads, since the new `DEFAULTS` are baked into the HTML the server emits — but a running process is still holding the old template string in memory until it restarts).

Tell the user: "I've updated the default list in `proxy.js`. Restart the monitor (or just reload if you're relying on the settings panel rather than a fresh browser) and it'll reflect the new subreddits."

### Step 4: Running the monitor

Start it with:

```
node systems/reddit-monitor/proxy.js
```

Then open `http://localhost:7429/` in any browser. The server proxies Reddit data through Arctic Shift server-side, so no browser-side CSP or CORS issue ever comes up.

Check first whether it's already running as a persistent `launchd` service (`com.davidohara.reddit-monitor`, see `~/Library/LaunchAgents/com.davidohara.reddit-monitor.plist`) before starting a second instance — a `KeepAlive`/`RunAtLoad` launchd job will already keep it up and auto-restart it, in which case just tell the user to open `http://localhost:7429/`. If no such job exists and the user wants it running continuously, offer to set one up; otherwise starting it manually per session is fine — the script has its own 30-minute idle auto-shutdown if you do run it as a one-off foreground/background process rather than under launchd.

---

## UI design guidelines

Keep the UI practical and information-dense. This is a work tool, not a marketing page.

- **Color coding:** High priority = red/orange badge, Medium = yellow, Low = gray
- **Layout:** Full-width table or card list; settings in a collapsible panel at the top
- **Font:** System font stack — no external dependencies
- **No CDN dependencies** — the page must work with only the local server's own `/api/*` calls, no other network access
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
- spinalcordinjury
- neurogenicbladder
- CysticFibrosis
- HomeHealth
- ostomy
- IBD
- CNA

**Keywords:**
- catheter, Foley, leg bag, drainage bag, self-cath, intermittent catheterization, external catheter, condom catheter, StatLock, tube securement, skin irritation, Grip-Lok, adhesive, dislodge, tape, GJ tube, NG tube, PEG tube, feeding tube, stoma, wafer, appliance leak, skin barrier, tubie, MCAS, skin breakdown, PICC line, central line, port-a-cath, IV infiltration, TPN, home infusion

These are starting defaults — the user can tune them in the settings panel.

---

## What not to do

- Don't use Reddit's OAuth API or ask for credentials — the public search API is sufficient for read access
- Don't publish this as a Claude Artifact (`mcp__cowork__create_artifact` / `update_artifact`) — published Artifacts run under a CSP that blocks every external fetch, so a Reddit-fetching artifact fails 100% of the time, for every subreddit. This is the exact bug this skill was rewritten to prevent. Always deliver via the local `proxy.js` server instead.
- Don't have the browser-side JS call `reddit.com` or any external Reddit API directly — always go through the local server's own `/api/*` endpoints, even though this same-origin page isn't sandboxed and technically could reach external hosts. Keeping fetches server-side keeps the User-Agent/rate-limit handling in one place and matches the proxy contract.
- Don't hardcode post data — it should fetch live on every load
- Don't skip the settings panel — the ability to update subreddits, keywords, and usernames interactively is a core requirement
- Don't show posts older than the lookback window even if they match keywords — recency is the gating filter, not an optional boost
- Don't fetch per-post comment trees to detect user responses — use the user's comment-search endpoint instead; it's one call per username and covers ~100 recent comments
- Don't let a failed username fetch block the page — username tracking is a convenience feature, not a critical path

## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/reddit-monitor-latest.json
```

Content:
```json
{
  "skill": "reddit-monitor",
  "agent": "chief",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from the morning briefing or a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output, `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action.

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill reddit-monitor
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/reddit-monitor.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

