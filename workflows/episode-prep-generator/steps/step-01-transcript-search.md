---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 01: Search for Prior Conversation Transcript

## MANDATORY EXECUTION RULES

1. Before executing, write `status: in-progress` to this file's frontmatter
   and set `accumulated-context.prep_status: transcript-search-in-progress`
   in `state.yaml`.
2. This step runs in parallel with `step-02-guest-research.md` — launch
   both at workflow start, do not sequence one before the other.
3. A found transcript is the primary source for step 3's questions. Guest
   research (step 2) enriches it but never overrides it — if the transcript
   says something, that's what goes in the prep sheet, not an inference from
   a LinkedIn bio.
4. Do not fabricate or paraphrase a transcript that wasn't actually found.
   If nothing turns up, flag the gap plainly and move on — the workflow
   falls back to research-based inference in step 3, it does not stall here.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** `guest_name` (also try `guest_company` and known nicknames/short
forms as secondary search terms)
**Output:** A transcript object (or an explicit not-found flag), stored in
`state.yaml`'s `accumulated-context.prior_transcript`

---

## YOUR TASK

1. Search the Obsidian vault via `mcp__obsidian-mcp-tools__search_vault` for
   a prior recorded conversation with this guest. Run more than one query if
   the first comes back empty — try the full name, last name only, and
   `guest_name` + `guest_company`.

2. What counts as a hit — any of these, in priority order:
   - **Plaud transcriptions** (typically under a `zzPlaud/` path or tagged
     `#plaud`) — meeting or lunch recordings with this guest as an attendee
   - **Meeting notes** referencing a call, lunch, or coffee with this guest
   - Any other recorded/transcribed conversation record naming this guest as
     a participant

   Do not count a note that merely *mentions* the guest's name in passing
   (e.g., a CRM note, a LinkedIn post copy) — this step is looking for an
   actual conversation record, not any reference to the person.

3. If one or more hits are found:
   - Prefer the most recent and most substantive transcript if there are
     multiple.
   - Read the full transcript via `mcp__obsidian-mcp-tools__get_vault_file`.
   - Extract and store in `accumulated-context.prior_transcript`:
     - `found: true`
     - `source_path`: the vault file path
     - `source_description`: one line, e.g. "Transcript of 2026-07-13 lunch
       with Kapil Dabi (Seasons 52, Plano)"
     - `raw_content`: the transcript text (or the substantive excerpt if the
       file is very long — keep everything relevant to the episode topic and
       professional/product substance)
     - `conversation_flow_notes`: a short list of the natural topic
       transitions and follow-up openings you noticed while reading, for
       step 3 to build the question sequence and "Suggested Flow" section
       from

4. If no hit is found after trying multiple search terms:
   - Set `accumulated-context.prior_transcript.found: false`
   - Set `accumulated-context.research_gaps_flagged: true` (or leave it as
     already set by step 2 if that also flagged something — both steps can
     contribute to the same flag) and append a note: "No prior conversation
     transcript found for [guest_name] — building questions from research-
     based inference instead."
   - This is non-blocking. Proceed to mark this step complete.

5. Set `accumulated-context.step1_transcript_search_done: true`.

6. Mark this file's frontmatter `status: complete` and `completed-at`.

7. Update `state.yaml`'s `current-step` only once *both* step-01 and step-02
   have reached `status: complete` — whichever finishes second advances
   `current-step: step-03`.

---

## SUCCESS METRICS

- Vault searched with at least two query variants before concluding "not
  found"
- If found: transcript captured in full (or full substantive excerpt), with
  source path and description recorded for step 4's Notes section
- If not found: gap flagged plainly, no invented transcript content
- Step 2 not blocked waiting on this step

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `mcp__obsidian-mcp-tools__search_vault` unreachable | Retry once. If still unreachable, flag `research_gaps_flagged: true` with reason "Obsidian vault unreachable — could not search for prior transcript," proceed to research-based fallback. |
| Multiple transcripts found with this guest | Use the most recent and most substantive one as primary; note the others' paths in `conversation_flow_notes` in case step 3 wants supplementary detail. |
| Transcript found but almost entirely off-topic (e.g., purely personal/social) | Still capture it — step 3 decides what's usable. Note in `source_description` that the content is largely personal/social so step 3 knows to lean more on research for professional substance. |

## NEXT STEP

Runs in parallel with `step-02-guest-research.md`. Once both are complete,
continue to `step-03-generate-prep.md`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
