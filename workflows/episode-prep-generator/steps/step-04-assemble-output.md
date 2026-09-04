---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 04: Assemble Final Output

## MANDATORY EXECUTION RULES

1. Before executing, write `status: in-progress` to this file's frontmatter.
2. Do not begin this step until `step-03-generate-prep.md` shows
   `status: complete` in its own frontmatter.
3. This step assembles and saves — it does not regenerate or re-derive
   content from step 3. If the assembled document is running long, that's a
   step 3 problem to revisit, not something to trim silently here.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** `accumulated-context.prep_sheet_body`,
`accumulated-context.prior_transcript`, `accumulated-context.guest_research`
**Output:** One saved markdown file, path recorded in
`accumulated-context.output_path`

---

## YOUR TASK

1. Take `accumulated-context.prep_sheet_body` from step 3 as-is — it already
   contains title/metadata, questions, guest research brief, suggested
   flow, internal context (if applicable), closing, and notes in the order
   step 3 assembled them. Do not reorder or add sections here.

2. Determine the filename: `[episode-date]-[guest-last-name].md`.
   - `episode-date`: today's date (`YYYY-MM-DD`) unless the controller
     supplied an actual scheduled recording date as part of the original
     request — use that if given.
   - `guest-last-name`: lowercase, hyphenated if multi-word (e.g.,
     `van-der-berg`).

3. Save to `meetings/podcast-prep/[episode-date]-[guest-last-name].md`.
   - This filename pattern is fixed and does not vary. Never append a
     suffix (`-2`, `-updated`, `-final`, etc.) under any circumstance.
   - Check whether a file already exists at that exact path.
     - If it exists: OVERWRITE it in place. A prior run's prep sheet for
       this guest on this date is superseded by the current run, not
       preserved alongside it.
     - If it doesn't exist: create it.
   - Each guest/date combination has exactly one prep file, always the
     latest version. There is never more than one file for the same
     guest/episode.

4. Sanity-check the saved file before reporting done:
   - Total length reads as 2-3 pages, scannable in under 2 minutes (not the
     old 8-10 page format)
   - No em dashes
   - Notes section states the transcript source (or explicitly that none was
     found) so a future reader knows where the questions came from

5. Update `state.yaml`:
   - `accumulated-context.output_path`: the saved file path
   - `accumulated-context.prep_status: complete`
   - `status: complete`

6. Mark this file's frontmatter `status: complete` and `completed-at`.

7. Present the complete document to the controller and note explicitly:
   - The output path
   - Which path was used (transcript-driven or research-inference), from
     step 3's `outputs.path_used`
   - Whether `research_gaps_flagged` was set, and if so, what was missing
   - If a transcript was used: the source (vault path + description) so
     David can go back to the original conversation if he wants more detail

---

## SUCCESS METRICS

- Single assembled markdown file saved to
  `meetings/podcast-prep/[episode-date]-[guest-last-name].md` — exactly one
  file per guest/episode, updated in place on re-runs, never duplicated
  under a suffixed name
- Document reads 2-3 pages, matches the format of
  `meetings/podcast-prep/2026-07-14-kapil-dabi.md` (concrete questions,
  Suggested Flow, Notes with source attribution) rather than the old
  10-section abstract format
- Transcript source (or its absence) stated plainly in Notes
- Delivered promptly — no unnecessary re-derivation of step 3's content

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `meetings/podcast-prep/` directory doesn't exist | Create it — this is a normal first-run condition, not a failure. |
| Step 3 never reached `status: complete` | Do not assemble a partial document silently. Report that step 3 is incomplete and why, set workflow `status: aborted`, and ask the controller whether to proceed with a partial document or wait. |
| A file already exists at the target path (a prior run for this guest/date) | Overwrite it. Never append a numeric or descriptive suffix (`-2`, `-updated`, `-final`, ...) — the filename pattern is fixed, and each guest/episode has exactly one current prep file. |
| Assembled document from step 3 is clearly over 3 pages | Flag this to the controller rather than silently trimming — trimming here risks cutting content step 3 deliberately included. Note it as a quality issue for the next run. |

## NEXT STEP

This is the final step of `episode-prep-generator`. No automatic handoff —
the episode hasn't recorded yet. Once it has, and David wants to turn it
into a pipeline campaign, that's a separate invocation of
`workflows/episode-campaign-brief/workflow.md` starting from a transcript.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
