---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 02: Harvest via WebSearch (Two Consecutive Passes)

## MANDATORY EXECUTION RULES

1. Fetch ONLY via the `WebSearch` tool with `allowed_domains`. RSS-from-sandbox 403s; never use it. Never `curl`/`requests` a blocked outlet.
2. Fetch only sources where `active` AND `accessible` are both true in `sources.json`.
3. Every source (and every beat search) is scanned twice, consecutively, every run. This happens before clustering or scoring; it is not a retry-on-failure, it always runs.

---

## EXECUTION PROTOCOL

**Agent:** Rigby, spawned by the coordinator, never executed inline in the coordinator's session.
**Input:** The fetch list from step-01
**Output:** Merged, deduped item set with `seen_passes` set per item

---

## YOUR TASK

**Pass 1.** For each fetch-list source, call:
`WebSearch(query="politics", allowed_domains=["<search_domain>"])`
Collect title, url, and a one-line raw snippet for recent items (last 48-72h). If a call returns `400 ... not accessible`, the site now blocks the crawler: flag it, set its `accessible:false` in `sources.json`, move it to muted, and continue.

Then run the four REQUIRED beat searches across the full accessible domain set (these are mandatory every run — they are how gap parity gets met):
`WebSearch(query="immigration policy <month year>", allowed_domains=[<all accessible domains>])`
`WebSearch(query="economy inflation jobs <month year>", allowed_domains=[...])`
`WebSearch(query="foreign policy <lead conflict> <month year>", allowed_domains=[...])`
`WebSearch(query="2026 midterm elections primaries campaign <month year>", allowed_domains=[...])`
Add 1-2 more seeds for the day's biggest stories as needed.

**Pass 2.** Immediately repeat the exact same sweep — same per-source queries, same beat searches, same candidate seeds. This is mandatory every run, not a fallback for a thin pass 1. Pages update between calls, so pass 2 catches new items and confirms the ones pass 1 already found.

**Merge.** Combine both passes, dedupe by `url`. For each surviving item, set `seen_passes: 2` if it appeared in both passes, `seen_passes: 1` if only one. Keep both; do not drop single-pass items.

## NEXT STEP

Read fully and follow: `step-03-write-harvest.md`
<!-- system:end -->
