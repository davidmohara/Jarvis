<!-- system:start -->
# Prep Document Section Order (episode-prep-generator step-03)

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
<!-- system:end -->
