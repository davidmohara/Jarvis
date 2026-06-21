# Watchtower — Requirements Spec

**Status:** Draft for Rigby to build. Master (Jarvis) wrote this spec after a clarifying-question pass with David on 2026-06-19. Master must NOT build this; Rigby owns the scaffold.

**Owning agent:** Knox (Knowledge & Vault) owns the information-gathering, scoring, tagging, and vault-capture effort. Knox HANDS OFF to specialists, mirroring the morning-briefing delegation pattern: daily top items → Chief (morning briefing section); weekly content candidates → Harper (hook/outline drafting in David's voice). Rigby builds and maintains the workflow infrastructure. (Superseded by Revision 2 §10 — earlier text named Chief as owner; ownership moved to Knox per David 2026-06-19.)

---

## 1. Purpose

A standing intelligence system that monitors news and happenings across David's areas of interest, digests each item into a one-paragraph "what you should be aware of" summary, captures surfaced knowledge into the Obsidian vault, and flags highly relevant items as content candidates — feeding the EXISTING content pipeline, not a parallel one.

David approves or rejects proposed new sources on a recurring basis. Nothing gets auto-added.

## 2. Confirmed scope (from David)

- **Topics:** AI / agentic systems; IT consulting & services; Texas / regional business.
- **Cadence — split:**
  - **Daily:** items David should be aware of. One-paragraph summary each.
  - **Weekly:** content candidates (with drafted hook + outline) AND proposed new sources for approval.
- **Outputs — combination:**
  - Config + data files live in the workspace (`workflows/watchtower/`).
  - Surfaced knowledge captured to Obsidian, properly tagged for future reference.
  - Content drafts live in Obsidian (`Mind/Posts/`, underscore-prefix = draft).
  - A live dashboard of daily items for async review after the morning briefing.
- **Content flagging:** highly relevant item → collect into the content register WITH an auto-drafted rough hook + outline tagged for blog / LinkedIn / Forbes.
- **Gathering:** mix of web search (discovery) + direct RSS feeds (trusted sources).
- **Seed sources:** combination — David names some, Watchtower proposes the rest for his approval.

## 3. Integration constraints (do not duplicate existing capability)

| Existing thing | Watchtower relationship |
|----------------|------------------------|
| `workflows/content-pipeline/` (Harper, Slack→Ghost) | Watchtower FEEDS this. Content candidates land in `reference/blog-ideas.md` and `Mind/Posts/` as drafts; Harper's pipeline handles drafting-to-publish. Do not rebuild publishing. |
| `reference/blog-ideas.md` | Append content candidates here under a Watchtower-sourced marker. This is the content idea register. |
| `workflows/knowledge-ingest/` (Knox) | Reuse vault tagging/frontmatter conventions for Obsidian capture. Watchtower's daily capture should match Knox's normalize/file conventions. |
| `workflows/morning-briefing/` (Chief) | Daily dashboard is reviewed async AFTER the morning briefing. Optionally surface a Watchtower one-liner in the briefing; do not merge the two. |
| Obsidian `Mind/Posts/` | Content drafts. `__Post Ideas.md` is the master idea list. |

## 4. Files to build under `workflows/watchtower/`

1. **`config.yaml`** — ALREADY DRAFTED by Master at `workflows/watchtower/config.yaml`. Rigby: review, bring under ownership, correct anything that doesn't match conventions. Holds cadence, relevance thresholds, dedupe window, output paths, source-suggestion settings, and David's relevance profile.
2. **`sources.yaml`** — the source registry. Per topic: named web sources + RSS feed URLs. Seeded from the approved starter set (see §6). Each source: `name`, `url`, `rss` (nullable), `topic`, `trust` (high/med), `added` date, `status` (active/paused).
3. **`workflow.md`** — standard IES workflow file with STATE CHECK protocol, step table, source registry pointer. Match the structure of `workflows/knowledge-ingest/workflow.md`. Frontmatter: `name`, `description`, `agent: chief`, `model: sonnet` (scoring/synthesis needs reasoning; daily fetch steps may note `model: haiku`).
4. **`state.yaml`** — standard schema (`workflow`, `agent`, `status`, `session-started`, `session-id`, `current-step`, `original-request`, `accumulated-context`).
5. **`steps/`** — see §5.
6. **`proposed-sources.md`** — staging file where the weekly run writes proposed new sources for David's yes/no. Approved ones move to `sources.yaml`.

## 5. Step design

### Daily run (awareness)
- `step-01-gather.md` — pull RSS feeds in `sources.yaml`; run targeted web searches per topic against David's lenses. Collect candidate items (title, url, source, published date, raw snippet).
- `step-02-dedupe.md` — drop items seen within `dedupe.lookback_days` (match on url + normalized title). Maintain a seen-items ledger (e.g., `workflows/watchtower/seen.jsonl`).
- `step-03-score.md` — score each item 0–100 against David's profile/lenses (`config.yaml profile`). Drop below `awareness_floor`. Mark items ≥ `content_flag` as content-worthy.
- `step-04-summarize.md` — write a one-paragraph "what you should be aware of" summary per surviving item. Plain prose, lead with the takeaway.
- `step-05-capture.md` — write the daily note to Obsidian `Watchtower/Daily/YYYY-MM-DD.md` with `#watchtower` + per-topic tags; build/update the live dashboard artifact (`watchtower_daily`).
- `step-06-report.md` — short summary of what was surfaced; hand content-worthy items to the weekly queue.

### Weekly run (content + sources)
- `step-01-synthesize.md` — pull the week's content-worthy items; synthesize themes.
- `step-02-draft-angles.md` — for each content-worthy item, draft a rough HOOK + OUTLINE tagged blog/LinkedIn/Forbes. Use David's voice (`identity/VOICE.md`) and blog style (`reference/blog-ideas.md`). Write drafts to `Mind/Posts/_<slug>.md` and append a candidate row to `reference/blog-ideas.md`. (Harper consulted for voice.)
- `step-03-suggest-sources.md` — propose up to `source_suggestions.max_per_week` NEW sources adjacent to David's topics. Write to `proposed-sources.md` with name, url, rss, why-relevant. Never auto-add.
- `step-04-weekly-note.md` — write `Watchtower/Weekly/YYYY-Www.md` summarizing themes, content candidates, and the source proposals awaiting approval.
- `step-05-report.md` — surface to David: content candidates ready, sources awaiting yes/no.

## 6. Seed sources — APPROVAL PENDING

David said "both": he'll name some, Master proposes the rest. Master's proposed starter set is in §7 below as a separate approval list. **Rigby: do NOT hardcode these into `sources.yaml` until David approves them.** Build `sources.yaml` with structure + any David-named sources; leave proposed ones in `proposed-sources.md` pending the first approval pass.

## 7. Scheduling

After the scaffold passes review, wire two scheduled tasks (these ARE system evolution, so Rigby's domain):
- Daily 6am local (`0 6 * * *`) — runs the daily/awareness workflow.
- Weekly Monday 7am local (`0 7 * * 1`) — runs the weekly/content+sources workflow.
Leave `enabled: false` in config until David confirms the first manual run looks right.

## 8. Acceptance criteria

- `workflows/watchtower/` contains config.yaml, sources.yaml, workflow.md, state.yaml, steps/ (per §5), proposed-sources.md.
- A manual daily run produces: an Obsidian daily note (tagged), a live dashboard, and one-paragraph summaries.
- A manual weekly run produces: content drafts in `Mind/Posts/`, candidate rows in `reference/blog-ideas.md`, and source proposals in `proposed-sources.md`.
- No duplication of content-pipeline publishing or knowledge-ingest filing — Watchtower feeds them.
- Nothing auto-adds a source; all source additions gate on David's yes/no.
- Files follow IES naming + frontmatter conventions; snapshot taken before any structural change.

---

## 9. REVISION 1 — David's changes (2026-06-19, post-scaffold)

These supersede the relevant parts above. Rigby implements all three.

### 9a. Source approvals — Batch 0 approved + additions

David approved all 10 of Batch 0. **Move all 10 from `proposed-sources.md` to `sources.yaml` with `status: active`, `added: 2026-06-19`.**

ALSO add these David-named sources to `sources.yaml` (active):

| Name | URL | RSS (find/verify the real feed URL; null if none) | Topic | Trust |
|------|-----|-----|-------|-------|
| Superhuman AI | https://www.superhuman.ai | (find feed) | ai-agentic | med |
| The Rundown AI | https://www.therundown.ai | (find feed) | ai-agentic | med |
| NVIDIA Newsroom (press releases) | https://nvidianews.nvidia.com | https://nvidianews.nvidia.com/releases.xml (verify) | ai-agentic | high |
| OpenAI News | https://openai.com/news/ | (find feed; may need scrape fallback) | ai-agentic | high |
| Anthropic News | https://www.anthropic.com/news | (find feed; may need scrape fallback) | ai-agentic | high |
| xAI News | https://x.ai/news | (find feed; may need scrape fallback) | ai-agentic | high |
| Google DeepMind / Google AI blog | https://blog.google/technology/ai/ | https://blog.google/technology/ai/rss/ (verify) | ai-agentic | high |
| Meta AI blog | https://ai.meta.com/blog/ | (find feed) | ai-agentic | med |
| Microsoft AI blog | https://blogs.microsoft.com/ai/ | https://blogs.microsoft.com/ai/feed/ (verify) | ai-agentic | high |

Notes for Rigby:
- "Top model providers (xAI, OpenAI, Anthropic, etc.)" — the "etc." is interpreted as the major frontier labs above (Google DeepMind, Meta, Microsoft). If David wants to trim, he'll say so. Mark the less-central ones (Meta) `trust: med` so scoring can weight them.
- Several of these publish via web pages, not clean RSS. Where no feed exists, the gather step should fall back to a targeted site-scoped web search (e.g., `site:openai.com/news`) rather than RSS. Record `rss: null` and a `gather_method: search` field on those entries so step-01 knows to search instead of poll.
- Verify each RSS URL actually resolves at build time where you can; where you can't verify, set `rss: null`, `gather_method: search`, and note "feed unverified" so the first run confirms.

### 9b. Auto-retire dormant sources (3-week rule)

New lifecycle rule. A source that surfaces **no item clearing `awareness_floor`** for 21 consecutive days is automatically retired.

Implementation:
- Track per-source last-surfaced date in a ledger (e.g., `workflows/watchtower/source-activity.json`): for each active source, `last_surfaced` (date an item from it last cleared awareness_floor) and `added`.
- The daily gather/score steps update `last_surfaced` whenever a source contributes a surviving item.
- A maintenance check (run in the daily step-06 report, or a dedicated `daily-step-07-prune.md`) moves any source where `today - max(last_surfaced, added) >= 21 days` out of `sources.yaml` into a new **`dormant-sources.yaml`** with `retired: <date>` and `reason: "no item cleared awareness_floor in 21 days"`.
- Dormant sources are NOT polled. They are not deleted — kept in `dormant-sources.yaml` for the record and possible manual revival.
- Surface retirements in the weekly report so David sees what dropped off and can revive if he disagrees.
- Trigger is "no item SURFACED" (cleared awareness_floor), not "no item at all" — this catches noisy-but-low-signal sources, per David.

### 9c. Daily morning piece folds into existing morning boot-up

The daily/awareness run is NOT a standalone 6am scheduled task. Instead it becomes part of the existing morning boot-up workflow.

Implementation:
- Identify the existing morning workflow (`workflows/morning-briefing/` — confirm it's the boot-up David means; it's Chief's). The Watchtower daily run should be invoked as a step within (or immediately before) the morning briefing so its output is fresh when David reviews.
- Output format: **inline section + dashboard.** Add a "Watchtower" section to the morning briefing containing the top surfaced items (David picks how many feels right; default top 5 by score). The FULL set of one-paragraph summaries lives on the live dashboard (`watchtower_daily`) for async deep-dive, linked from the briefing section.
- Do NOT wire a separate daily scheduled task. Remove/disable the standalone daily cadence in `config.yaml` (set daily `enabled: false` and add a note that daily runs via morning-briefing). The WEEKLY run remains a candidate for its own Monday schedule (still leave `enabled: false` until David confirms).
- Coordinate with Chief's morning-briefing workflow conventions; do not duplicate calendar/inbox logic — just add the Watchtower section + invocation.

### 9d. Scheduling status after Revision 1

- Daily: runs via morning-briefing, NOT its own scheduled task.
- Weekly: still unscheduled, `enabled: false`, pending David's confirmation after a clean manual run.
- Master will not wire the weekly schedule until David says go.

---

## 10. REVISION 2 — Ownership moved to Knox (2026-06-19)

David: "Morning brief hands off to sub-agents, this workflow should be the same. Identify which agent should manage this information gathering effort." Decision: **Knox** owns it.

Rigby implements:

### 10a. Reassign owning agent Chief → Knox
- `workflow.md` frontmatter: change `agent: chief` to `agent: knox`. Update any `owner:` field to `knox`.
- `state.yaml`: change `agent: chief` to `agent: knox`.
- `config.yaml` header comment: "Owned by Chief (daily awareness)..." → "Owned by Knox (information gathering + vault capture); hands daily digest to Chief, weekly content candidates to Harper."
- Every step file's voice/attribution: the gathering, dedupe, scoring, summarizing, capture, and prune steps run AS Knox. Update any "[Chief]:" agent self-references in those step files to "[Knox]:". Leave Harper's consult on the weekly content step intact.

### 10b. Preserve the hand-off pattern (this is the point of the change)
Knox does NOT run inline as a silent part of Chief's briefing. It is a distinct gathering effort that hands results off, mirroring how morning-briefing delegates to specialists:
- **Daily:** Knox executes the gather→dedupe→score→summarize→capture→prune chain, writes the Obsidian daily note + dashboard, then HANDS the top-N scored items to Chief. Chief's morning-briefing renders the Watchtower section from Knox's output. In `workflows/morning-briefing/`, the WATCHTOWER INVOCATION should be framed as a hand-off to Knox (Knox runs the daily Watchtower workflow and returns `watchtower_output`), not as Chief doing the gathering. Adjust the invocation wording/spawn so Chief delegates to Knox rather than executing the gather steps itself. Keep failure non-blocking.
- **Weekly:** Knox runs synthesis + source suggestions; HANDS content candidates to Harper for the hook/outline drafting step (Harper owns voice). Source-approval staging stays as-is.

### 10c. Constraints
- Match IES spawn/handoff conventions (see agents/master.md spawn protocol and agents/knox.md). Respect system:/personal: markers in any edited file.
- No behavioral change to gathering logic, dormancy rule, sources, or scheduling — this revision is purely ownership + handoff framing.
- Still no scheduled tasks wired. Weekly still `enabled: false`. Not committed until David signs off.

### 10d. Weekly scheduled brief is also Knox's (David, 2026-06-19)

David: "Knox should also be the agent who handles the scheduled weekly brief too."

When the weekly scheduled task IS eventually wired (Monday 7am local, `0 7 * * 1` — still pending David's go after a clean manual run), its scheduled-task prompt MUST invoke the Watchtower WEEKLY workflow AS KNOX. Knox runs synthesis + source suggestions, then hands content candidates to Harper for hook/outline drafting (per §10b). The scheduled task does not assign the run to Chief, Harper, or anyone else — Knox is the executing agent; Harper is a consult on the draft-angles step only. Master will write the scheduled-task prompt accordingly when David approves wiring. Until then: no schedule wired, `enabled: false`.
