---
status: not-started
started-at: ~
completed-at: ~
---

<!-- system:start -->
# Step 04: Size Triage

Every `size.*` finding gets exactly one of three outcomes, decided with David:

1. **Fix** — split detail into `references/` and leave a when-to-load pointer behind. Preferred for: files whose bulk is reference material, tables, or long examples. Rigby drafts the split.
2. **Except** — record in `systems/eval-harness/conventions-exceptions.json` with a reason and a `review_after` date (default: +3 months). Rigby records; David approves; nothing enters the manifest approved without David.
3. **Accept as WARN** — allowed only when David explicitly declines both fix and exception. The finding stays visible in every lint run. Surface the running count in the close report.

Order the conversation by blast radius: step files first (29+, mostly mechanical splits), then workflows, then skills, then agents, then scripts. Exceptions that already exist and no longer apply (from the census) get retired in this step.
<!-- system:end -->
