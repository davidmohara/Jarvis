<!-- system:start -->
# HUB REGISTRY & HUB PAGE SYNC

Hub pages are undated Ghost **pages** (not posts) that collect clusters of dated posts around a theme. This file is the source of truth: which hubs exist, how a post maps to a hub, and how hub pages stay updated. Adding a new hub never requires a workflow edit: add a registry entry below and the daily run picks it up.

## How mapping works

A post maps to a hub when its Ghost tags (read live from Ghost, never from memory) satisfy the hub's match rule. Rules are expressed as:

- `tags_all`: every listed tag must be present on the post
- `tags_any`: at least one listed tag must be present
- `title_keywords_any`: optional additional filter; at least one keyword (case-insensitive) must appear in the post title. Use sparingly: tag-only rules are cleaner.

Tag names refer to the locked tag list in `ghost-conventions.md`. The locked-list rule still holds: hub mapping never creates new tags.

## Publish-time behavior (two directions)

1. **Post → hub link (draft time).** When a drafted post's selected tags map to a hub whose `page_status` is `live`, the draft body gains a lexical link node to the hub page URL. Gate 2 checks this as `has_hub_link_if_mapped`. Hubs with `page_status: pending` are skipped: the link rule activates automatically once the page exists and the entry flips to `live`.
2. **Hub → post entry (publish time).** On every daily run, step-01 Step 1c reconciles each live hub page against Ghost: any post with status `published` or `scheduled` that matches the hub's rule but is not already linked in the hub page body gets appended. **Drafts are never added to hub pages. Only `published` and `scheduled` posts qualify.**

## Hub page sync protocol (step-01 Step 1c)

For each registry entry with `page_status: live`:

1. **Resolve the page.** `mcp__ghost-blog__get_page_by_slug(slug)`. If 404: the registry claims `live` but the page does not exist: log it, surface it in the run outcome line, and skip this hub. Never create the page programmatically: page bodies are drafted separately and approved by David before the page exists.
2. **Collect candidate posts.** `mcp__ghost-blog__get_posts` (published and scheduled only, including tags). Also include any post that transitioned to `published` or `scheduled` in the same run's Step 1a resync. Filter to posts matching the hub's rule by their live Ghost tags (and title keywords when the rule has them). Exclude anything with status `draft`.
2b. **Backfill guard (tightened 2026-10-26).** Hub pages are David-curated narratives, not tag dumps. Every hub rule now requires BOTH the tag match AND a title keyword, and only posts with `published_at` on or after the hub's go-live date (2026-10-21) are candidates. Older posts are never auto-added: if one belongs on a hub, David or a quarterly refresh adds it with a narrative sentence. Candidates that pass are **appended only when the title keyword match is unambiguous**; anything borderline is listed in the run outcome as "hub candidate for David" and is not written to the page.
3. **Diff against the page body.** Extract linked URLs from the page's current lexical body. A post already linked (canonical URL match) is skipped: the sync is idempotent and safe to run every day.
4. **Append missing entries.** For each missing post, newest first, append a list item to the page's post-list section: the post title hyperlinked to its canonical URL, plus the publish date. Do not rewrite the hub's framing copy: that is David-approved text.
5. **PUT the page.** Immediately before the PUT, GET the page again and take the **server-issued `updated_at`** from that response: send that exact string in the PUT body. Do not cache it from an earlier read and do not construct it client-side (optimistic lock; same corrected rule as `ghost-draft-creation.md`). The endpoint is the **pages** API, not posts:
   ```
   PUT https://driventodevelop.com/ghost/api/admin/pages/{page_id}
   Authorization: Ghost {jwt}
   Content-Type: application/json

   {"pages": [{"lexical": "{updated_lexical_json_string}", "updated_at": "{server_issued_updated_at}"}]}
   ```
   JWT generation is the same pattern as Step 7 in `ghost-draft-creation.md` (Admin API key from the `ghost-blog` env block, HS256, `aud: "/admin/"`).
6. **Record** `hub_synced` (count of post entries appended across all hubs) in the step's frontmatter outputs and in `state.yaml` `accumulated-context`.

If nothing is missing, no PUT is made.

## Quarterly hub refresh (manual, on demand, not scheduled)

Once a quarter, Harper re-reads each live hub's framing (intro and section copy) against the posts the hub now collects, drafts a refreshed framing, and presents it to David for approval before applying anything. Approved changes are applied with the same pages PUT and server-issued `updated_at` rule above. Do not create a scheduled task for this: run it when David asks ("quarterly hub refresh").

## Adding a new hub

1. Add an entry to the registry table below: slug, title, cluster description, match rule, `page_status: pending`.
2. Draft the hub page body and get David's approval, then create and publish the Ghost page at `https://driventodevelop.com/{slug}/`. Page creation is deliberately manual: the framing copy is David-approved before it exists, and the workflow must never create hub pages itself.
3. Flip the entry to `page_status: live` (fill in `ghost_page_id` if known).
4. Done. The next daily run's Step 1c backfills all matching published posts, Gate 2 starts requiring the hub link in newly drafted matching posts, and the quarterly refresh picks the hub up. No workflow file changes needed.
<!-- system:end -->

<!-- personal:start -->
## Hub registry (David's hubs)

| Slug | Title | Cluster description | Match rule | Hub URL | page_status | ghost_page_id |
|------|-------|---------------------|------------|---------|-------------|----------------|
| agent-governance-guide | Agent Governance: A Practical Guide for Enterprise Leaders | Posts on governing enterprise AI agents: oversight, guardrails, accountability, rollout discipline. | `tags_all`: ai + leadership; AND `title_keywords_any`: agent, agents, governance, govern, insider, insiders, identity, inventory, owner, ownership, access, credential, credentials, permission, permissions, guardrail, guardrails, oversight, ai lead | https://driventodevelop.com/agent-governance-guide/ | live | 6ad90869608cfe028219634f |
| ai-consulting-business-model | How AI Is Changing the Consulting Business Model | Posts on AI's impact on consulting economics: pricing, delivery models, leverage, talent. | `tags_all`: ai + business; AND `title_keywords_any`: consulting, consultant, consultants, delivery, billing, fde, service line, margin, utilization, restructuring, reskilling | https://driventodevelop.com/ai-consulting-business-model/ | live | 6ad90869608cfe0282196354 |
| ai-economics | AI Economics: Pricing, Platforms, and the Capital Layer | Posts on AI pricing and economics broadly: seat pricing, platform wars, bubbles. The DFW/Texas capital-layer and talent-market posts (the retired dfw-ai-economy scope) fold in as sections of this hub. | `tags_any`: ai, business; AND `title_keywords_any`: pricing, seats, saas, bubble, valuation, capital, economy, economics, dfw, dallas, texas, data center | https://driventodevelop.com/ai-economics/ | live | 6ad90869608cfe0282196359 |

**Go-live date (all three hubs): 2026-10-21.** See the backfill guard below.

### Rule tightening (2026-10-26, David's request)

The first sync diff (2026-10-26) flagged 35 posts as missing across the three hubs, mostly pre-go-live posts that do not fit the curated narrative (for example "Your Next Browser May Come from Dallas" against the governance guide). Fixes: all three hubs now require tag match AND title keyword; the noisy keywords platform, rate, and gap were dropped from ai-economics; and the go-live backfill guard above blocks historic posts. The flags below describe the pre-tightening rules and are kept for history.

### Tag-signal flags (reviewed 2026-10-21)

- **agent-governance-guide**: weak signal. The locked tag list has no governance tag; `ai + leadership` is a proxy. It will over-match (generic AI leadership posts) and under-match (governance posts tagged ai + business, which land in the consulting hub instead). Acceptable to start. If mismatch noise shows up, the clean fix is a dedicated tag, which requires David's explicit approval, since the workflow never creates tags.
- **ai-consulting-business-model**: moderate signal. `ai + business` is the natural combination but will also catch AI posts about other industries' business models, not just consulting. Watch and tighten if needed.
- **ai-economics** (replaces the retired dfw-ai-economy hub, 2026-10-21): weak-to-moderate signal. No economics or geo tag exists in the locked list, so the rule leans on title keywords. The broader keyword set (pricing, seats, saas, platform, rate, bubble, gap, dfw, dallas, texas, data center) fixes the old rule's geo-only blind spot, but keywords like "platform" and "rate" are common in AI posts generally, so expect some over-match. Posts on AI economics whose titles carry none of the keywords will still be missed. A dedicated tag would tighten this but needs David's approval first.

All three hubs went `live` on 2026-10-21: David approved the draft bodies (from `projects/hub-drafts/`), published the Ghost pages, and the entries above carry their page IDs. Gate 2's hub-link check and Step 1c's backfill are active for all three from the next run onward. For any future hub, keep the entry at `page_status: pending` until David approves the page body and the page is published; the workflow never creates hub pages itself.
<!-- personal:end -->
