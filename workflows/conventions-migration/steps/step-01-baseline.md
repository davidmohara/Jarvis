---
status: not-started
started-at: ~
completed-at: ~
---

<!-- system:start -->
# Step 01: Baseline

1. Read `reference/capability-conventions.md` fully. The sweep applies those rules; do not improvise equivalents.
2. Run the linter in report mode over the whole repo and save the JSON findings to `workflows/conventions-migration/state-baseline-findings.json`:
   `python3 systems/eval-harness/validate-conventions.py > findings.jsonl` (each line is one finding).
3. Run the census: `python3 skills/rigby-skill-audit/scripts/audit.py --census --json` — save to state.yaml `accumulated-context.census_baseline`.
4. Bucket the findings into three lists in state.yaml:
   - `mechanical` — FAIL-class rules plus unambiguous WARNs (missing frontmatter, unregistered library skills, interactive `input(` in bundled scripts)
   - `judgment` — description rewording (imperative, intent-not-mechanics), pointer when-to-load phrasing, Gotchas sections
   - `size` — every `size.*` finding
5. Acknowledged findings (already excused in `conventions-exceptions.json`) are out of scope — never re-fix them.

Write the bucket counts to state.yaml. Do not fix anything in this step.
<!-- system:end -->
