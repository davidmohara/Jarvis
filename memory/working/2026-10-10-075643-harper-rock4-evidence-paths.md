# Working Memory — Rock 4 Publishing Evidence Paths (Harper)

**Date:** 2026-10-10 07:56
**Agent:** Harper
**Request:** David, 2026-10-10, on committing Q4 Rock 4 (Thought Leadership): "Rock 4 can be seen by using the Ghost MCP to see published articles or the GA for the blog to see stats. Additionally, figure out if there's a way to see LinkedIn analytics." Establish standing evidence paths so future rock reviews pull real numbers instead of grading the workstream as invisible.

## 1. Ghost published articles — PATH CONFIRMED, LIVE PULL DONE

**How it is wired today:**

- The "Ghost MCP" David referenced is the `ghost-blog` server (`npx -y @densh/ghost-mcp-server`) configured in **Claude Desktop's config** (`~/Library/Application Support/Claude/claude_desktop_config.json`), not in Claude Code's `~/.claude.json`. So `mcp__ghost-blog__get_posts` / `get_post` / `update_post` work in Desktop/Cowork sessions but are NOT available in Code sessions. This is a real gap: `skills/delivery-router/SKILL.md`, `skills/harper-blog-linkedin-post/SKILL.md`, and the content-pipeline/content-approval workflows all call `mcp__ghost-blog__*` tools, which silently fail in Code.
- **Code-side fallback that works:** the Ghost Admin API key embedded in `workflows/content-pipeline/ghost_update_v2.py` (same key as the Desktop MCP env: `GHOST_API_URL=https://driventodevelop.com`, key id `69b084ee2fa72d02909ce5b9`). Auth is a short-lived HS256 JWT (`aud: /admin/`), endpoint `GET /ghost/api/admin/posts/?filter=status:published`. Read-only listing verified working from this session.

**Live evidence (read-only pull, 2026-10-10):**

- **100 published posts total; 77 published in 2026; 5 already published in Q4** (Oct 1-10 window).
- Most recent 3:
  1. 2026-10-08 — "DFW Is Now #4 and the Capital Layer Is the Real Story" — https://driventodevelop.com/2026/10/08/dfw-is-now-4-and-the-capital-layer-is-the-real-story/
  2. 2026-10-07 — "DFW's Innovation Economy Is Wider Than You Think" — https://driventodevelop.com/2026/10/07/dfws-innovation-economy-is-wider-than-you-think/
  3. 2026-10-06 — "Uniform Governance Is How Agents Die" — https://driventodevelop.com/2026/10/06/uniform-governance-is-how-agents-die/
- Also Q4: 2026-10-05 "The Restructuring Is Not Coming. It's Here." and 2026-10-02 "Reversibility Is the Governing Criterion."
- **Verdict: David's "publishing via Alice is running and moving well" is confirmed by the record.** Near-daily cadence in the first 10 days of Q4. The Q3 "publishing stalled since Aug 20" reading was IES-file blindness, not reality.

**Rigby recommendation:** add `ghost-blog` to Claude Code's MCP config (global `~/.claude.json` or IES `.mcp.json`) pointing at the same `@densh/ghost-mcp-server` with the same env vars, so Code sessions get `mcp__ghost-blog__*` natively and every existing skill/workflow reference resolves. Zero new code needed.

## 2. Blog stats via GA — PATH CONFIRMED, LIVE PULL DONE

**How it is wired today:**

- A **`ga4-driven-to-develop` MCP server already exists in Claude Desktop's config**: `/opt/homebrew/bin/ga4-mcp-server` (a `ga4_mcp` Python package wrapper) with `GA4_PROPERTY_ID=324164215` and `GOOGLE_APPLICATION_CREDENTIALS=/Users/davidohara/.config/google/ga4-service-account.json`. Sibling servers exist for kare-devices, cigartrack, doughdiary.
- The service account + `google-analytics-data` Python lib also work **directly from Code** (no MCP needed): verified with a read-only `run_report` against property `324164215` this session.
- GA4 measurement ID on the live site: **G-D4LHZS6VKQ** (confirmed in the homepage gtag snippet). Property 324164215. Blog platform: Ghost 6.10 on Fly.io (`/Users/davidohara/develop/driventodevelop/ghost-blog/fly.toml`, app `d2d-blog`).

**Live evidence (read-only pull, 2026-10-10):**

- Last 28 days: **597 sessions, 531 users, 664 pageviews, 47s avg session duration**.
- Q4 to date (Oct 1-10): **179 sessions, 196 pageviews**.
- Top pages (28d): homepage 250; "Madman, Architect, Carpenter, and Judge" (2024) 106; "A Snake and Kindness" (2023) 33; **"The Restructuring Is Not Coming. It's Here." (Oct 5) already at 20**, "Your Manager Is the AI Strategy" (Sep 15) 13, "What Happens to an Expert When AI Knows Everything They Know" (Sep 24) 12. New Q4 posts are attracting traffic within days of publishing.
- Historical context from `projects/driven-to-develop/seo-audit-feb2026.md`: roughly 150 real organic users/month; "Direct" traffic is heavily bot-polluted (trafficheap.com filtered from March 1, 2026 onward). Rock reviews should report organic/search and per-post pageviews, not raw "Direct."

**Rigby recommendation:** register `ga4-driven-to-develop` in Code's MCP config the same way as ghost-blog, or standardize on the direct Python call (service account already on disk, lib installed). Either makes blog stats a one-call pull for Quinn's rock review.

## 3. LinkedIn analytics — NO EXISTING PATH; RECOMMENDATION BELOW

**What exists:** nothing. No LinkedIn or Metricool server in Desktop or Code MCP configs. The only prior attempt (episodic memory `2026-07-30-205917-session-wrapup.md`) used the Claude-in-Chrome extension against the analytics page; the connection was persistently flaky and the pull failed. David was offered a manual CSV export instead; it never landed.

**Options assessed:**

1. **LinkedIn API:** Impractical. Personal post analytics sit behind the Community Management API / Marketing Developer Platform, which require a vetted LinkedIn developer app and OAuth consent from David, and member-level analytics access is restricted. Weeks of setup for marginal data. Not recommended.
2. **Playwright/browser automation against `linkedin.com/analytics/creator/content/`:** Feasible but with a catch. Code's Playwright MCP (`npx @playwright/mcp@latest`) launches a fresh profile with no LinkedIn session, so it hits a login wall. It works only if (a) run through Desktop/Cowork browser tooling with David's logged-in session, or (b) the Playwright MCP is reconfigured with a persistent `--user-data-dir` that David logs into once (Rigby build). LinkedIn session cookies expire and 2FA challenges recur, so this path needs an explicit "confirm login and retry" protocol like the Dynamics one (CBRE-session precedent already encoded in `agents/harper.md`).
3. **Metricool connector:** A `Metricool Social Media Management` connector exists in claude.ai's connector catalog (currently unauthenticated). Metricool aggregates LinkedIn personal-profile analytics (impressions, engagement, follower growth) into a dashboard and API. Requires David to authenticate the connector and connect his LinkedIn account; historical depth is limited on lower tiers. Cleanest hands-off option once connected.
4. **Manual:** David screenshots `linkedin.com/analytics/creator/content/` or exports per-post analytics monthly, drops them in a folder, Harper reads them. Zero setup, but depends on David remembering; this is exactly the class of manual step that produced Q3's invisible-workstream problem.

**Recommendation:** Option 2 first, with Option 3 as the upgrade path. Concretely:

- **Now (needs David, 5 minutes, one time):** Rigby reconfigures the Playwright MCP (or adds a second browser server) with a persistent user-data-dir; David logs into LinkedIn once in that profile. After that, any agent can read-only pull the creator analytics dashboard and per-post analytics on a cadence, with a login-wall check that asks David to re-auth rather than fabricating numbers.
- **Alternative if David prefers a dashboard:** authenticate the Metricool connector in claude.ai settings and connect LinkedIn. Then LinkedIn stats become an MCP call with no browser fragility.
- **Standing fallback either way:** monthly manual export from David, dated, into `data/linkedin-analytics/`, so the rock review never goes dark again.

## Rock 4 evidence path summary (for Quinn's reviews)

| Metric | Path | Status |
|--------|------|--------|
| Published articles (count, titles, dates, URLs) | Ghost Admin API (key in ghost_update_v2.py) or `mcp__ghost-blog__get_posts` on Desktop | Working today, proven 2026-10-10: 100 total, 5 in Q4 |
| Blog traffic (sessions, users, pageviews, top pages) | GA4 property 324164215 via service account (`~/.config/google/ga4-service-account.json`) or `mcp__ga4-driven-to-develop__*` on Desktop | Working today, proven 2026-10-10: 597 sessions/28d, 179 in Q4 |
| LinkedIn post analytics | None today. Recommended: Playwright with persistent logged-in profile, or Metricool connector | Needs one-time David action |

**Constraints honored:** all external access read-only (one GET to Ghost Admin API, three `run_report` reads to GA4 Data API). No writes to workflows/, skills/, agents/, systems/. No git operations. Ghost/GA MCP config changes flagged to Rigby rather than built here.
