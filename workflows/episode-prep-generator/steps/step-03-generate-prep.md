---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 03: Generate Episode Prep

## MANDATORY EXECUTION RULES

1. Before executing, write `status: in-progress` to this file's frontmatter
   and set `accumulated-context.prep_status: prep-generating` in
   `state.yaml`.
2. This step waits for **both** step 1 (transcript search) and step 2
   (guest research) to reach `status: complete` before it starts — unlike
   the old workflow, this is not something step 3 can partially begin early.
   The transcript, if one exists, drives the entire structure of the output,
   so there is nothing useful to produce before both inputs are in.
3. **Do not build David's actual 2026-07-14-kapil-dabi.md prep sheet
   (`meetings/podcast-prep/2026-07-14-kapil-dabi.md`) as your literal
   reference for section structure, tone, and length before generating
   anything.** This is the format bar — match it, don't approximate it.
4. Output is always **2-3 pages max, scannable in under 2 minutes**. This is
   a hard constraint, not a suggestion. If you find yourself writing 10
   formal sections or abstract discussion threads instead of concrete
   questions pulled from a real conversation, stop and cut.
5. No em dashes anywhere in the output.
6. Never invent a quote or a line of dialogue and present it as something
   the guest actually said. If the transcript has it verbatim, quote it. If
   you're inferring what the guest will likely say based on research, say so
   plainly ("Based on his public talks, expect him to frame this as...").

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** `topic`, `guest_name`, `guest_title`, `guest_company`,
`industry_domain`, `specific_angle`, `internal_context` (optional);
`accumulated-context.prior_transcript` from step 1;
`accumulated-context.guest_research` from step 2
**Output:** The complete prep sheet body, stored in `state.yaml`'s
`accumulated-context.prep_sheet_body`

---

## YOUR TASK

### 1. Decide which path you're on

Check `accumulated-context.prior_transcript.found`:

- **`true` (transcript path)** — the transcript is your primary source.
  Build questions directly from what was actually discussed. Go to 2a.
- **`false` (research-inference path)** — no transcript exists. Build
  questions from `accumulated-context.guest_research` plus the stated
  `topic`, `industry_domain`, and `specific_angle`. Go to 2b.

### 2a. Building from a transcript (primary path)

1. Read `accumulated-context.prior_transcript.raw_content` and
   `conversation_flow_notes` in full.
2. Identify the conversational arc: the topics the guest actually raised,
   in the order they came up, and where the guest opened a door for a
   follow-up that wasn't taken in the original conversation but should be
   pursued on-air.
3. Group related exchanges into 3-5 thematic clusters (mirroring the
   `## 1. [Cluster Title]` / `## 2. [Cluster Title]` structure of the
   reference prep sheet) — these become the numbered sections of the
   questions block. Cluster titles should be concrete and specific to what
   was actually discussed, not generic ("Retail's Agentic Commerce Shift,"
   not "Industry Trends").
4. Within each cluster, write the main questions the host should ask,
   numbered continuously across the whole document (1, 2, 3...), with
   lettered follow-ups (a, b) only where the transcript shows a natural
   follow-up opening or where a follow-up sharpens a point the guest made.
   Target **7-10 total main questions** across all clusters.
5. Questions should read as things a host actually asks out loud, framed to
   let the guest continue in the direction the transcript shows they're
   comfortable going. Where useful, reference specific things the guest said
   ("You mentioned X — walk us through...") rather than asking in the
   abstract.
6. Where `internal_context` was provided, weave one question that connects
   the conversation to that context naturally (see the reference sheet's
   question 6, which ties the guest's point to Improving's trip-concierge
   work) — do not force it if there's no natural connection point.
7. End the questions block with a wrap-up question (e.g., "what's the one
   thing you want listeners to do differently because of this
   conversation").
8. Build the **Suggested Flow** section: pull 3-5 verbatim or near-verbatim
   quotes from the transcript that show what the guest will likely say when
   asked the above, organized by the same clusters. Label it clearly as
   grounded in the actual prior conversation (see reference sheet's "from
   [date] conversation" framing) — this is not speculation, it's a memory
   aid pulled from what already happened.

### 2b. Building from research inference (fallback path)

1. Read `accumulated-context.guest_research` in full.
2. Using `topic`, `industry_domain`, and `specific_angle`, build 3-5
   thematic clusters the conversation should move through, same structure
   as 2a step 3.
3. Write 7-10 main questions with lettered follow-ups where they sharpen a
   point, grounded in the guest's actual research profile (their real
   projects, their real speaking history) rather than generic industry
   questions that could apply to any guest in the space.
4. Weave `internal_context` in the same way as 2a step 6, if provided.
5. End with a wrap-up question, same as 2a step 7.
6. Build the **Suggested Flow** section using research-based inference
   instead of verbatim quotes: state plainly this is inferred from the
   guest's public talks/writing/interviews, not something they've actually
   said to David ("Based on his conference talks on X, expect him to
   frame..."). Do not present an inferred line as a quote.

### 3. Assemble the remaining sections (both paths)

Build the full document with these sections, in this order:

1. **Title and metadata** (2-3 lines) — episode title (topic-driven, punchy,
   matching the reference sheet's style: "Episode N: [Topic] — [Subtitle]"),
   guest name/title, one status/note line if relevant (e.g., sign-off
   needed, first external guest, numbering TBD).
2. **Questions and Talking Points** — the numbered clusters and questions
   from step 2a/2b. This is the main content.
3. **Guest Research Brief** (1 page max) — accomplishments, notable
   projects, speaking history, relevant background from
   `accumulated-context.guest_research`. If `research_gaps_flagged: true`,
   state that plainly rather than presenting a thin brief as complete.
4. **Suggested Flow** — from step 2a/2b above.
5. **Internal Context** — only include this section if `internal_context`
   was provided as an input. Weave the supplied text into how it connects
   to the conversation (Improving's work, angle, constraints). If not
   provided, omit the section entirely rather than leaving an empty
   placeholder.
6. **Closing** — a short, concrete closing beat (thank the guest, any
   milestone/tease/subscribe reminder appropriate to the episode).
7. **Notes** — metadata block: source of the conversation transcript (vault
   path + description) or "No prior transcript found; questions built from
   research-based inference," episode numbering status (provisional unless
   confirmed), and any required sign-offs or scheduling caveats surfaced
   during research or in the transcript.

### 4. Enforce length and format

- Total length: 2-3 pages, scannable in under 2 minutes. If it's running
  long, cut abstract framing and restate questions more directly — do not
  pad with extra formal sections.
- No em dashes.
- Questions only in the main content block — never write out imagined guest
  dialogue as if it already happened, except where quoting the transcript
  verbatim in the Suggested Flow section.
- Use markdown headers and numbered lists matching the reference sheet's
  visual structure (`##` for major sections, numbered questions with
  lettered sub-questions, `---` dividers between major blocks).

### 5. Write outputs

Write to this file's frontmatter:
```yaml
outputs:
  path_used: transcript | research-inference
  question_count: <int, target 7-10>
  internal_context_included: true | false
  research_gap_noted: true | false
```

Update `state.yaml`:
- `accumulated-context.prep_sheet_body`: the full assembled document body
  from step 3 above (everything except the final file header — step 4
  handles the outer wrapper)
- `accumulated-context.step3_prep_generated: true`

Mark this file's frontmatter `status: complete` and `completed-at`, and
advance `state.yaml`'s `current-step: step-04`.

---

## SUCCESS METRICS

- Questions are concrete, follow the conversational flow of a real prior
  conversation when one exists, and are not abstract industry-generic
  threads
- 7-10 main questions, with follow-ups only where earned
- Suggested Flow section grounded in the transcript when available, clearly
  labeled as inference when not
- Total output 2-3 pages, scannable in under 2 minutes
- No em dashes; no fabricated quotes presented as verbatim

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Neither step 1 nor step 2 produced usable material (no transcript, thin/no research) | Proceed anyway using only `topic`, `industry_domain`, and `specific_angle` to build questions. State plainly in Notes that both the transcript search and guest research came back empty, and that questions are built from the stated inputs alone. Do not stall the workflow. |
| Transcript found but mostly personal/social with little professional substance | Use what professional substance exists, backstop the rest with guest research, and note in Notes that the transcript leaned personal/social and content was supplemented. |
| Output creeping past 3 pages | Cut before finalizing — remove redundant follow-ups, tighten the research brief, do not ship an oversized document. |
| `internal_context` doesn't naturally fit any question | Place it in the Internal Context section only; do not force an awkward tie-in into the numbered questions. |

## NEXT STEP

Once complete, continue to `step-04-assemble-output.md`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
