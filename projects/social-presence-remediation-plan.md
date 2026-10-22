# Social Presence Remediation Plan

**Status**: Draft for review and approval. No changes made yet.
**Source audit**: `/Users/davidohara/Downloads/social report.md` (Oct 21, 2026)
**Scope**: driventodevelop.com (Ghost), @davidmohara on X, cross-profile identity.

## Access Inventory (what Jarvis can execute directly)

| Access | Path | What it enables |
|---|---|---|
| Ghost blog (admin) | ghost-blog MCP: get/update/create posts and pages | About/Speaking/Writing rewrites, broken-link fixes, meta descriptions, pillar pages, llms.txt page, post restructure, newsletter CTA, retagging |
| GA4 (blog analytics) | ga4-driven-to-develop MCP | Referral measurement, UTM validation, monthly reporting baseline |
| X account | No API in this session. The audit used an X API workspace (separate). Posting requires either that workspace's x MCP or manual execution | Bio rewrite, pinned post, native posting, replies |
| LinkedIn | No connector | Manual by David |
| Improving.com profile | No access | Request to Improving web team |
| Old WordPress blog | No verified access | Verify control, then 301/redirect or rel=canonical |

## Execution Constraints

- Content edits (About bio, bio wording, X posts) are drafted for David's approval; never published without sign-off. Writing rules apply (no em-dashes, human voice).
- Canonical title: **Regional Director** (decided Oct 21). Longer versions may add "co-founder of Improving" and "leads Improving's AI practice" in prose contexts where space allows, but the title itself is Regional Director everywhere.
- GA4 measurement (Phase 5) is deferred; not in scope for this pass.

---

## Phase 1: Identity and E-E-A-T (highest leverage, ~1 hour of David's time total)

**1.1 Canonical identity decision.** Resolved Oct 21: Regional Director. May 2 prose extensions in bio contexts: "co-founder of Improving" and "leads Improving's AI practice."

**1.2 About page rewrite.** COMPLETE Oct 21 (David pasted approved content: Regional Director + co-founder + AI practice lead, podcast, social links).

**1.3 Site-wide metadata (Jarvis via Ghost).** Homepage title to include name and AI positioning; homepage description updated (currently silent on AI despite 75% of 2026 posts tagged AI); twitter:description (currently "President of Improving", stale since 2024). If Ghost MCP exposes site settings/code injection: add Person JSON-LD with jobTitle, worksFor: Improving, and sameAs [x.com/davidmohara, linkedin.com/in/davidmohara, improving.com/profile/david-ohara]. If not exposed, provide the code-injection snippet for David to paste into Ghost admin (5 min).

**1.4 Author page (Jarvis via Ghost).** Fill author bio, add social URLs so sameAs populates from the author object.

**1.5 X bio (David or via X-access workspace).** "Regional Director at Improving, leading the AI practice. Dallas. Writing daily at Driven To Develop." Pin a post (see Phase 3).

**1.5b Improving profile cross-links (external request).** Email Improving web team: link David's improving.com profile to the blog and X. Provide exact link targets.

**1.6 Old WordPress blog (David verifies control first).** If controlled: redirect to driventodevelop.com or at minimum a "moved to" post. Removes a competing indexed source for "Driven to Develop".

## Phase 2: Blog technical and structural repairs (Jarvis-executed, low approval burden)

**2.1 Fix 4 broken internal links.** COMPLETE Oct 21 (David, Ghost admin; verified live: old URLs absent, dated URLs present on all 4 posts).

**2.2 Fill missing meta descriptions.** COMPLETE Oct 21. True missing set was 120 (recount), all pre-2026 and older; the 3 July 2026 posts already had metas (audit count was stale). 120/120 backfilled via David-authorized Admin API batch, zero failures, zero remaining empty, verified by 12-post sample + spot-checks. 3 recent metas pasted by David (verified live). Love With Your Presence (scheduled for 10-22): verify meta at publish. Run report: memory/working/2026-10-21-meta-backfill-run.md. Operational note: this Ghost version REQUIRES updated_at on PUT, using the current server-issued value (fresh client timestamps fail the optimistic lock).

**2.2b Pipeline meta enforcement (Rigby build).** COMPLETE Oct 21. Gate 2 non-empty enforcement on metas (format_rules non_empty_string, validator-native); step-7 verify includes both meta fields before Slack unlock; pending-drafts schema records metas + resync drift detection; citation-friendly draft format live across all 6 files (bottom-line opening, 2-4 H2 subheads, takeaway close, mandatory outbound primary-source link, 300-700 words). Follow-up candidate: teach skills/schema-validator a native must_be_non_empty rule.

**2.3 Add /llms.txt.** SKIPPED Oct 21, per David. No native Ghost path; viable via an Express route on the self-hosted server. AI crawlers already allowed; About page + author profile + pillar pages cover the same signal with more authority. Revisit only if the value is proven.

**2.4 Newsletter capture (Ghost post template).** End-of-post signup card. Requires theme edit or a code-injection snippet; if the MCP path can't reach the theme, provide the snippet for Ghost admin (code injection, post template).

**2.5 Smaller items (Ghost, batched):** lazy-load headshot, homepage publisher Person, branded OG images (Jarvis generates templates; Unsplash stock replaced over time), BlogPosting schema (optional, low priority).

## Phase 3: Content restructure for citation (AEO/GEO)

**3.1 Restructure new posts going forward (standard).** Every post: 2-4 H2 subheads, one-sentence bottom line at top, linked primary sources, "What to do Monday" list. Apply as a post-publish pass Jarvis runs before each new post goes out.

**3.2 Backfill priority posts (David approves rewrites).** The 10 highest-value 2026 posts (5 Percent Problem, Reversibility, Uniform Governance, Agent Governance Stack, Billing Model, FDE Model, DFW hubs' anchors) restructured with headings and source links. 2/week. Original text preserved; structure and links added.

**3.3 Three pillar/hub pages (Ghost pages, undated URLs).** COMPLETE Oct 21: all three live (agent-governance-guide, ai-consulting-business-model, ai-economics, broadened from DFW-only per David). Bodies drafted, link-host defects caught and corrected, feature images sourced per pipeline rules, published by David, registry flipped live, automation armed (Gate 2 hub-link check + Step 1c backfill active from next daily run). Hub #3 scope change recorded; future hubs (e.g., health) are one registry entry. Follow-up candidate: add hubs to Ghost primary nav.
- Agent Governance: A Practical Guide for Enterprise Leaders
- How AI Is Changing the Consulting Business Model
- DFW's AI Economy (living guide, quarterly refresh)

Each links its 10-15 cluster posts; each post links back. Jarvis builds scaffolds + internal links, David approves framing.

**3.4 Retag by cluster.** Replace the generic "thoughts" tag (86 uses) with cluster tags matching the hubs. Batched, Ghost.

**3.5 Speaking and Writing pages (Jarvis drafts, David approves).** Populate with 2026 talks: Convergence AI Dallas (Mar 31), Improving AI Executive Workshops, Microsoft AI Tour Houston, Principled Business Austin Summit, The Improving Edge podcast. These pages already rank for name searches; currently near-empty.

## Phase 4: X repositioning and growth (OUT OF SCOPE, per David Oct 21: X handled elsewhere)

**4.1 Profile (needs X access).** Bio (1.5), pinned post, banner stating focus. X Premium optional; measure before renewing.

**4.2 Posting model change.** Kill auto-shares permanently (median 21.5 impressions; stopped July anyway). Every blog post feeds 2-3 native posts: thesis, stat + source, the question it raises. Link in reply, not in the main post. Jarvis drafts these alongside each post (workflow: each publish generates the X drafts in the same pass).

**4.3 Cadence target.** 1-2 originals per weekday from the blog pipeline (already producing ~5 posts/week, so the material exists).

**4.4 Reply program.** 15-20 min/day, targets: @bgadoci, @hkarthik, @jasona, @DevlinLiles, Improving accounts; @levie/@emollick when the consulting-operator view adds something. Replies drew 7 of 22 total likes; highest ROI per minute.

**4.5 Dallas niche.** Own the DFW AI economy story; tag Dallas Innovates / Convergence AI Dallas when there's a real take.

**4.6 Visuals.** Simple 2x2 / 3-tier framework images (reversibility tiers, value quadrant) for the strongest posts.

**4.7 Cut list.** Off-topic retweets (watches, cows); reduce brand-complaint share. Keep deliberate personality, not filler.

**4.8 X access gap (blocking).** This session has no X write path. Options: (a) run posting from the workspace with the x API (same one the audit used), (b) David posts natively from Jarvis-drafted queues, (c) browser automation (not recommended for posting; approval friction on every post makes it slower than option b).

## Phase 5: Measurement (DEFERRED, per David Oct 21)

**5.1 Baseline capture (GA4 MCP).** Deferred. Do not build the baseline until the measurement pass is reactivated.

**5.2 Monthly scorecard.** Followers, profile visits, link clicks (X), blog referral sessions from t.co (GA4), pillar page sessions, newsletter signups. All posts linking the blog use UTM tags. GA4 property G-D4LHZS6VKQ already installed.

---

## Sequencing and Effort

| Order | Item | Executor | David time |
|---|---|---|---|
| 1 | Canonical identity wording (1.1) | David | 10 min |
| 2 | About page + metadata + author page (1.2-1.4) | Jarvis | 15 min review |
| 3 | Broken links + 2026 meta descriptions (2.1-2.2 first batch) | Jarvis | none (batch spot-check) |
| 4 | Speaking/Writing page drafts (3.5) | Jarvis | 15 min review |
| 5 | X bio + pinned post (needs 4.1 decision on access path) | David or x-workspace | 10 min |
| 6 | Pillar page scaffolds (3.3) | Jarvis | 20 min review |
| 7 | Post-restructure standard (3.1) applied to next posts | Jarvis | none after approval |
| 8 | Backfill meta descriptions + retag (2.2 remainder, 3.4) | Jarvis, batched weekly | none |
| 9 | llms.txt, newsletter snippet, small items (2.3-2.5) | Jarvis + snippets | 10 min paste if needed |
| 10 | Improving web team request + WordPress blog (1.5b, 1.6) | David | 15 min |

## Open Decisions for David

1. ~~Canonical title~~ Resolved Oct 21: Regional Director (prose extensions: co-founder of Improving, leads the AI practice).
2. ~~X access path~~ Resolved Oct 21: X posting handled outside this plan.
3. Pillar page set: the three proposed, or a different three.
4. ~~Backfill vs archive-only~~ Resolved Oct 21: full backfill via David-authorized Admin API batch.
5. X Premium: yes/no.
