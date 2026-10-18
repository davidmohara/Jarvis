---
status: not-started
started-at: ~
completed-at: ~
---

<!-- system:start -->
# Step 03: Judgment Fixes

For the `judgment` bucket, draft each fix and present it for approval before applying — these change meaning, not structure.

Group by fix shape to keep review short:

- **Descriptions not imperative** (the big bucket): draft the rewritten description per skill — imperative verb, intent not mechanics, pushy, under 1024 chars. Present the top 20 by eval-run frequency first; the long tail follows.
- **Pointer when-to-load phrasing**: show each pointer and the sentence that adds the trigger condition.
- **Gotchas sections**: for each skill with error-log `related_skill` entries, list the candidate gotcha lines (one per recurring entry, phrased as a rule).
- **`--help` gaps**: scripts parsing `sys.argv` by hand get an argparse retrofit draft.

Apply approved items only. Record every rejection verbatim in state.yaml — rejected drafts are negative feedback for the next sweep.
<!-- system:end -->
