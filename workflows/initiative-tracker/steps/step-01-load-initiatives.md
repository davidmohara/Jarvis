---
model: opus
---

<!-- system:start -->
# Step 01: Load All Initiatives

## MANDATORY EXECUTION RULES

1. You MUST read ALL files in `tasks/initiatives/` — no sampling, no skipping.
2. For each initiative, extract ALL metadata fields: status, owner, next action, blockers, dependencies, due date.
3. You MUST pull knowledge layer context for each initiative.
4. Do NOT analyze blockers or classify risks in this step. Load and inventory only.
5. Status values MUST conform to shared-definitions.md#Initiative Status.

---

## EXECUTION PROTOCOL

**Agent:** Quinn
**Input:** `tasks/initiatives/` directory, `memory/episodic/projects/` knowledge layer
**Output:** `initiative_registry` — full initiative list with metadata, stored in working memory for step 02

---

## YOUR TASK

### Sequence

1. **Read all files in `tasks/initiatives/`.**
   - For each initiative file, extract frontmatter fields:
     - `id` (auto-generated from filename)
     - `title`
     - `status`: planned | active | at-risk | blocked | completed | cancelled
     - `owner`
     - `due-date`
     - `tags` (check for `revenue-impact` tag)
     - `blockers` array
     - `next-action` (if in frontmatter or body)
     - Any dependency references to other initiative IDs
   - Capture body content summary (key context, recent activity, decisions)
   - Note `last-updated` date or infer from file modification date

2. **Pull knowledge layer context** for each initiative.
   - Search `memory/episodic/projects/` for entries whose subject, tags, or related-entities reference the initiative title
   - For each match capture: date, type, brief summary
   - Identify most recent knowledge layer entry per initiative

3. **Calculate stale status per initiative.**
   - Compare last_activity_date (max of last-updated and most recent KL entry) to today
   - Flag as stale if days_since_activity >= 14

4. **Identify revenue-impacting initiatives.**
   - Primary: flag any initiative with `revenue-impact: true` field or `revenue-impact` tag in frontmatter
   - Secondary (heuristic fallback): flag any initiative whose title or content references revenue, pipeline, ARR, accounts, or client engagements — mark these as `revenue_impact_source: heuristic` so step 03 can note the detection method
   - Store as list for step 03 escalation check

5. **Store results** in working memory:
   ```
   initiative_registry:
     total_count: N
     initiatives:
       - id: ...
         title: ...
         status: planned | active | at-risk | blocked | completed | cancelled
         owner: ...
         due_date: YYYY-MM-DD | null
         tags: [...]
         revenue_impact: true | false
         blockers: ["description", ...]
         next_action: ...
         dependencies: [initiative-id, ...]
         last_activity_date: YYYY-MM-DD | null
         days_since_activity: N
         stale: true | false
         kl_context: "brief summary of relevant knowledge layer entries"
   revenue_impacting_initiatives: [initiative-id, ...]
   ```

---

## SUCCESS METRICS

- All initiative files read with complete metadata
- Knowledge layer context pulled for each initiative
- Stale status calculated for every initiative
- Revenue-impacting initiatives identified

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `tasks/initiatives/` directory does not exist or is empty | Report: "No initiatives found in tasks/initiatives/. Strategic initiative tracking requires initiative files. Create initiatives in tasks/initiatives/ to begin tracking." End workflow. |
| Initiative file has invalid status value | Note the invalid status. Set status to `active` as default. Flag in report: "Initiative '[title]' has unrecognized status '[value]' — defaulted to active." |
| Knowledge layer unavailable | Note: "Knowledge layer unavailable — initiative context will use task file data only." Proceed. |

---

## NEXT STEP

Read fully and follow: `step-02-blocker-analysis.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
