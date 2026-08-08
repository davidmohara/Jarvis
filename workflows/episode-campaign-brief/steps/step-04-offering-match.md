---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 04: Offering Match + Brief Assembly

## MANDATORY EXECUTION RULES

1. Before executing, write `status: in-progress` and `started-at` to this
   file's frontmatter.
2. Load `accumulated-context.pain_points` from `state.yaml`.
3. You MUST query the live SharePoint sources named in
   `skills/offering-match/SKILL.md` — never a cached offerings list from a
   prior run, even a prior run in this same episode's history.
4. This is the final step. It also assembles and writes the Episode Campaign
   Brief document.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** Pain points from `accumulated-context`
**Output:** Offering matches + the assembled Episode Campaign Brief markdown
document

---

## YOUR TASK

1. Read and execute `skills/offering-match/SKILL.md` in full, passing the
   pain points list. This queries live SharePoint sources — do not skip or
   shortcut this call.

2. Capture the returned `offering_matches` list (including any `no_match`
   entries — these belong in the brief too, as honest gaps).

3. Assemble the Episode Campaign Brief markdown document with this structure:

   ```markdown
   # Episode Campaign Brief — {episode.title}

   **Episode:** {episode_number, if known} | **Date:** {date} | **Guest:** {guest, if any}
   **Source:** {source_url or obsidian_note_path}

   ## Pain Points

   ### {pain_point.id}: {pain_point.statement}
   > "{pain_point.quote}" — {speaker}
   {context}

   [repeat per pain point]

   ## Audience Profile

   **Industries:** {...}
   **Company size band:** {...} — {size_rationale}
   **Buyer roles:** {...}
   **Buying-trigger signals:** {...}

   ## Offering Matches

   ### {pain_point.id} → {offering_name}
   **Category:** {category} | **Duration:** {duration} | **Price:** {price}
   **Source:** [{source_doc}]({link})
   {fit_rationale}

   [or, for gaps:]

   ### {pain_point.id} → No current offering match
   {reason}
   ```

4. Save the brief to `content/podcast-campaigns/{episode-slug}-campaign-brief.md`
   (create the directory if it doesn't exist).

5. Write outputs to this file's frontmatter:
   ```yaml
   outputs:
     offering_matches_count: <int>
     unmatched_pain_points: [pp-0X, ...]
     brief_path: "content/podcast-campaigns/{episode-slug}-campaign-brief.md"
   ```

6. Update `state.yaml`:
   - `accumulated-context.offering_matches`: the full match list
   - `accumulated-context.brief_path`: the saved brief path
   - `status: complete`

7. Mark this file's frontmatter `status: complete` and `completed-at`.

8. Present the brief to the controller and note explicitly: "This brief can
   feed `audience-target-outreach` directly — want me to start account/contact
   targeting from this audience profile?"

---

## SUCCESS METRICS

- SharePoint sources were queried live this run (not answered from memory)
- Every offering match cites a real source document with duration/price
- Unmatched pain points are stated plainly, not hidden or force-fit
- Brief document saved and presented

## FAILURE MODES

| Failure | Action |
|---------|--------|
| SharePoint unreachable | Do not fabricate offering matches. Save the brief with pain points + audience profile only, and flag: "Offering matching could not run — SharePoint sources unreachable. Retry offering-match once connectivity is restored." Set workflow `status` to `aborted` if the controller wants a complete brief before proceeding, or `complete` with the gap noted if a partial brief is acceptable. |

## NEXT STEP

This is the final step of `episode-campaign-brief`. If the controller wants to
continue into outreach, hand off to `workflows/audience-target-outreach/workflow.md`
using this run's `audience_profile` as input.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
