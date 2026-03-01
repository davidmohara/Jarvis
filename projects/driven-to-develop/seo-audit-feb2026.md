# Driven to Develop — SEO Audit
**Date**: February 28, 2026 (updated March 1, 2026) | **Domain**: driventodevelop.com | **Platform**: Ghost CMS on Fly.io

> **Update Log (March 1, 2026):**
> - ✅ Switched theme from Liebling (unmaintained since 2019) to **Solo** (official Ghost theme)
> - ✅ Added related posts via code injection (Content API, falls back to recent posts when tag has < 2 matches)
> - ✅ Noindexed tag archive pages via code injection (DOMContentLoaded script in Site Header)
> - ✅ Filtered referral spam — added trafficheap.com to unwanted referrals in GA4
> - ✅ Meta description applied to Madman post
> - Solo theme resolved: homepage alt text (0 missing vs 14 before), native search, proper structured data, current Ghost 6.10 compatibility

---

## Executive Summary

Driven to Develop has a real audience — about 822 organic search users over the past 6 months — but the numbers are heavily obscured by bot traffic and referral spam. Two posts account for the vast majority of organic performance: "Madman, Architect, Carpenter, and Judge" and "A Snake and Kindness." The site's biggest strength is that those two articles genuinely rank and engage readers (131s and 87s average session duration respectively). The biggest problems are thin content across most posts, missing meta descriptions, images without alt text, and tag pages that waste crawl budget with zero user value. Fix the on-page basics, bulk up the winning content, and noindex the tag pages — that's 80% of the upside.

**Top 3 priorities:**
1. Add meta descriptions to every post and fix image alt text sitewide
2. Expand the two top-performing posts from ~400 words to 1,500+ words
3. Noindex tag archive pages that are generating 100% bounce rates

---

## Traffic Reality Check (Sep 2025 – Feb 2026)

Before the audit details, let's separate real humans from noise.

**Raw numbers**: 5,192 users / 5,620 sessions

**After removing spam and bots**:

| Channel | Users | Sessions | Bounce Rate | Avg Duration |
|---------|-------|----------|-------------|--------------|
| Organic Search | 822 | 1,066 | 56.4% | 117s |
| Organic Social | 50 | 53 | 56.6% | 56s |
| Referral (legit) | ~40 | ~90 | — | — |
| **Real total** | **~912** | **~1,209** | — | — |

**What's fake**: 3,745 "Direct" users with 92.7% bounce rate and 7s avg session — overwhelmingly bot traffic. Plus 501 sessions from trafficheap.com (known referral spam). The site's real human traffic is roughly **150 users/month from organic search**, plus a trickle from LinkedIn and social.

**Legitimate referral sources**: LinkedIn (37 users), Teams link previews (15), Facebook (4), Twitter/X (4), Instagram (3), ChatGPT (2).

---

## Top Performing Content

| Post | Organic Users | Page Views | Avg Duration | Bounce |
|------|-------------|------------|-------------|--------|
| Madman, Architect, Carpenter, and Judge | 402 | 555 | 131s | 63.5% |
| A Snake and Kindness | 359 | 456 | 87s | 53.0% |
| Razors | 46 | 58 | 97s | 68.3% |
| Media Room Riser with LED Lights | 29 | 36 | 119s | 53.1% |
| Path of Least Resistance | 20 | 19 | 55s | 60.0% |
| It's Simple, Right? | 55 | 56 | 42s | 57.9% |

Everything else gets fewer than 25 organic users over 6 months. The "Madman" article alone drives 49% of all organic traffic. That's both the good news (it ranks) and the risk (one article carries the site).

---

## Keyword Opportunity Table

| Keyword | Est. Difficulty | Opportunity | Current Status | Intent | Recommended Action |
|---------|----------------|-------------|----------------|--------|--------------------|
| madman architect carpenter judge | Moderate | **High** | Ranking page 1-2 | Informational | Expand post to 1,500+ words, add original framework |
| madman architect carpenter judge writing process | Low | **High** | Likely ranking | Informational | Target as H2 within existing post |
| betty sue flowers writing | Low | **High** | Not targeted | Informational | Add section crediting original framework |
| snake kindness story leadership | Low | **High** | Ranking | Informational | Expand post, add meta description |
| conscious capitalism blog | Moderate | **Medium** | Not covered | Informational | Write pillar post — you have Improving's CC content |
| conscious leadership personal development | Moderate | **Medium** | Not covered | Informational | New post — directly aligned with your brand |
| leadership mental models | Moderate | **Medium** | Partially (Razors post) | Informational | Expand Razors post, retitle for search intent |
| optimal stopping secretary problem | Moderate | **Medium** | Have a post | Informational | Expand and optimize existing post |
| leadership starts with me | Low | **Medium** | Have a post, thin | Informational | Rewrite with 1,000+ words and personal stories |
| what is culture leadership | Moderate | **Medium** | Have a post, thin | Informational | Expand with frameworks and examples |
| happiness vs joy | Moderate | **Medium** | Have a post | Informational | Expand — high-search-volume topic |
| finding your passion myth | Moderate | **Medium** | Have a post | Informational | Expand, add original perspective |
| how to handle being wrong leadership | Low | **Medium** | Have a post | Informational | Expand — strong personal brand topic |
| compelling narratives leadership | Low | **Low** | Have a post | Informational | Minor optimization |
| operational visions goal setting | Low | **Low** | Have a post | Informational | Add meta description, minor expansion |
| DIY media room riser | Low | **Low** | Ranking well (119s duration!) | Informational | Different audience — leave as-is, optimize title tag |

---

## On-Page Issues

| Page | Issue | Severity | Fix |
|------|-------|----------|-----|
| Homepage | ~~14 of 18 images missing alt text~~ | ~~High~~ ✅ **Fixed** | Solo theme resolved — 0 missing alt text now |
| Homepage | No Open Graph image | **Medium** | Add og:image meta tag for social sharing |
| Homepage | ~~Meta description is generic~~ | ~~Medium~~ ✅ **Fixed** | Applied March 1: "Leadership, growth, and the messy middle of building things worth building. Thoughts from David O'Hara." |
| Madman article | ~~No meta description~~ | ~~Critical~~ ✅ **Fixed** | Applied March 1: "Betty Flowers' four roles of writing — Madman, Architect, Carpenter, and Judge — and how using them intentionally transforms your creative process." |
| Madman article | Only 445 words | **High** | Expand to 1,500+ words — you're ranking on thin content, imagine what depth would do |
| Snake article | 308 words (very thin) | **High** | Expand to 1,000+ words |
| Snake article | 3 images missing alt text | **Medium** | Add descriptive alt text |
| Multiple posts | ~90% bounce on older posts | **Medium** | Add internal links, related posts, CTAs to keep readers on site |
| All posts | ~~No structured "Related Posts" section~~ | ~~Medium~~ ✅ **Fixed** | Added via code injection — tag-filtered with fallback to recent posts |
| Sitewide | No author schema | **Low** | Add Person schema for David O'Hara — helps E-E-A-T |
| /about/ page | Decent engagement (25s, 58% bounce) | **Low** | Optimize — this is where organic visitors go to learn about you |

---

## Content Gap Analysis

**Topics competitors cover that you don't:**

1. **Conscious Capitalism / Conscious Leadership** — You literally speak on this and Improving publishes content about it. There's no pillar post on driventodevelop.com about conscious capitalism. This is a glaring gap given your professional positioning. **Priority: High. Effort: Half day.**

2. **Writing process / creative process deep-dives** — Your "Madman" post ranks well but it's 445 words. Ed Batista's version of this topic is much deeper. The Flowers Paradigm has a whole Substack breakdown. You have room to own this topic with a definitive, longer piece. **Priority: High. Effort: 2-3 hours (expand existing post).**

3. **Leadership frameworks / mental models** — Your "Razors" post touches this but the keyword "leadership mental models" has real search volume and you're not explicitly targeting it. **Priority: Medium. Effort: Half day for a new pillar post.**

4. **Personal development through adversity / growth stories** — You write personal essays but they're short. Longer-form storytelling with frameworks would rank better and build authority. **Priority: Medium. Effort: Ongoing.**

5. **Speaking / thought leadership positioning** — Your /speaking/ page gets 27 users with great engagement (61s, 26% bounce) but has no SEO optimization. A "hire me to speak" page optimized for "leadership speaker Texas" or "conscious capitalism speaker" could drive inbound leads. **Priority: Medium. Effort: 2 hours.**

**Content types to consider**: The site is all short essays. Adding one comparison post ("X vs Y"), one listicle-style framework post, or one comprehensive guide would diversify content formats and capture different search intents.

**Funnel gap**: There's no email capture, newsletter signup, or any conversion mechanism. Readers arrive, read, and leave. Even a simple "Subscribe for new posts" would build an owned audience.

---

## Technical SEO Checklist

| Check | Status | Details |
|-------|--------|---------|
| HTTPS | ✅ Pass | Active, no mixed content |
| Sitemap | ✅ Pass | /sitemap.xml exists with 4 sub-sitemaps |
| robots.txt | ✅ Pass | Clean, no issues |
| Canonical tags | ✅ Pass | Present on pages checked |
| Article schema | ✅ Pass | Ghost auto-generates Article structured data |
| Mobile responsive | ✅ Pass | Ghost default theme is responsive |
| Tag page indexation | ✅ **Fixed** | Noindex applied via code injection (DOMContentLoaded in Site Header). Verified on /tag/leadership/ and /tag/business/. |
| Pagination pages indexed | ✅ **Fixed** | Same script catches `.paged` body class — all paginated archives noindexed |
| Author/Person schema | ⚠️ Warning | No Person schema for David — hurts E-E-A-T signals |
| Open Graph tags | ⚠️ Warning | Missing og:image on homepage |
| Page speed | ⚠️ Warning | Not tested directly — Solo theme is lighter than Liebling (7 images vs 18 on homepage), likely improved |
| Referral spam | ✅ **Fixed** | trafficheap.com added to unwanted referrals in GA4 (March 1, 2026). Historical data still polluted; going forward is clean. |
| DoughDiary privacy policy | ⚠️ Warning | /doughdiary-privacy-policy/ is indexed on driventodevelop.com — unrelated content dilutes site topical focus |

---

## Competitor Landscape

For the "madman architect carpenter judge" keyword (your top performer):

| Dimension | driventodevelop.com | edbatista.com | consultantsmind.com |
|-----------|-------------------|---------------|---------------------|
| Content depth | 445 words (thin) | ~1,200 words (deep) | ~800 words |
| Original framework | References Flowers | References Flowers + adds coaching lens | References Flowers + business application |
| Publishing frequency | ~Monthly | ~Monthly | ~Weekly |
| Internal linking | Minimal | Strong | Strong |
| Schema markup | Article (auto) | Article | Article |

Ed Batista's version is more comprehensive and adds a coaching/leadership application layer. Your post ranks alongside his but with far less depth — which means Google is rewarding your domain for something else (probably freshness or click-through rate). Adding depth would likely push you ahead.

For general leadership blog competition: The space is dominated by organizations (BetterUp, HBR, Forbes) for generic leadership keywords. Your opportunity is in **long-tail, personal, framework-driven content** where individual bloggers outperform corporate content farms.

---

## Prioritized Action Plan

### Quick Wins (This Week)

1. ~~**Write meta description for "Madman, Architect, Carpenter, and Judge"**~~ ✅ **Done March 1** — Applied: "Betty Flowers' four roles of writing — Madman, Architect, Carpenter, and Judge — and how using them intentionally transforms your creative process."

2. ~~**Add alt text to all homepage images**~~ ✅ **Resolved** — Solo theme handles image alt text properly. 0 of 7 images missing alt text (was 14 of 18 with Liebling).

3. ~~**Noindex tag archive pages**~~ ✅ **Done March 1** — Code injection in Site Header using DOMContentLoaded script. Verified on /tag/leadership/ and /tag/business/.

4. ~~**Filter referral spam in GA4**~~ ✅ **Done March 1** — trafficheap.com added to unwanted referrals in GA4 data stream settings. Clean data going forward.

5. **Add og:image to homepage** — Set a default social sharing image in Ghost settings. Expected impact: **Low**. Effort: 5 minutes.

### Strategic Investments (This Quarter)

6. **Expand "Madman" post to 1,500+ words** — Add your own framework overlay, practical application steps, and examples from your leadership experience. Reference Betty Sue Flowers properly. Add internal links to related posts. This is your best-performing asset — invest in it. Expected impact: **High**. Effort: 2-3 hours.

7. **Expand "A Snake and Kindness" to 1,000+ words** — Same approach. It's your #2 performer at 308 words. More depth = better rankings = more traffic. Expected impact: **High**. Effort: 2 hours.

8. **Write a Conscious Capitalism pillar post** — You speak on this, Improving is aligned with it, and there's no content on your blog about it. Target "conscious capitalism," "conscious leadership," and related keywords. 2,000+ words. Expected impact: **High**. Effort: Half day.

9. **Optimize the /speaking/ page for search** — Target "leadership speaker Dallas" or "conscious capitalism keynote speaker." Add testimonials, topic list, booking CTA. Expected impact: **Medium**. Effort: 2 hours.

10. ~~**Enable Ghost's related posts feature**~~ ✅ **Done March 1** — Added via Content API code injection in Site Footer. Tag-filtered with fallback to recent posts when tag has fewer than 2 matches.

11. **Add email signup / newsletter CTA** — You're getting readers but not capturing them. Even Ghost's built-in Members feature would work. Expected impact: **Medium** (long-term audience building). Effort: 1-2 hours.

12. **Move /doughdiary-privacy-policy/ off the blog** — Host it on a separate domain or subdomain. It dilutes your site's topical authority around leadership content. Expected impact: **Low**. Effort: 30 minutes.

---

## Theme Migration: Liebling → Solo (March 1, 2026)

**Previous theme**: Liebling v2.1.6 (eddiesigner/liebling) — last updated ~2019, built for Ghost 3-5 era.

**New theme**: Solo (official Ghost team theme) — actively maintained, built for personal blogs/individual writers.

**SEO improvements from theme switch:**
- Homepage images: 14 missing alt → 0 missing alt
- Native Ghost search: now available
- Fewer assets loaded (7 images vs 18 on homepage)
- Current Ghost 6.10 feature support (cards, bookmarks, toggles, email blocks)
- Proper structured data generation aligned with latest Ghost standards
- Clean, modern markup

**Code injections added:**
- **Site Header**: DOMContentLoaded script to noindex tag-template and paged body classes
- **Site Footer**: Related posts script (Content API with tag filter, fallback to recent) + CSS

**Note on blog format**: This is a personal thought leadership blog with short-form essays (300-600 words typically). The two-track content strategy is: short posts distributed via social/LinkedIn (don't need SEO optimization), and occasional "searchable" posts targeting keywords with proven demand (these get depth treatment). Not every post needs to be 1,500 words.

---

## Bottom Line

The blog has organic traction — real people finding you through Google for the "Madman" framework and the "Snake and Kindness" story. That's a foundation most personal blogs never achieve. But you're leaving a lot on the table with thin content, missing meta descriptions, and no conversion mechanism. The quick wins are genuinely quick (under 2 hours total) and the strategic investments align with content you already think about and speak on. The biggest single-action ROI move is expanding the Madman post — it's already ranking with 445 words, and depth would likely push it from page 2 to a solid page 1 position.
