---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 02: Guest Research (parallel with Step 01)

## MANDATORY EXECUTION RULES

1. Before executing, write `status: in-progress` to this file's frontmatter
   and set `accumulated-context.prep_status: research-in-progress` in
   `state.yaml`.
2. This step runs in parallel with `step-01-transcript-search.md` — launch
   both at workflow start, do not sequence one before the other.
3. This research is **secondary** to a prior conversation transcript if one
   exists. It enriches the guest research brief (accomplishments, speaking
   history, background) and backstops the questions when no transcript is
   found. It never overrides what the guest actually said in a real
   conversation.
4. Do not invent guest biographical facts if research comes back thin —
   an honest gap is far more useful to the host than a fabricated credential.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** `guest_name`, `guest_title`, `guest_company`, `industry_domain`
**Output:** A "guest context brief" object, stored in `state.yaml`'s
`accumulated-context.guest_research`

---

## YOUR TASK

1. Spawn a research subagent (general-purpose, fresh context — it does not
   need this workflow's history) with a self-contained prompt covering:
   - Who to research: `guest_name`, `guest_title` at `guest_company`,
     operating in `industry_domain`.
   - Tools to use: WebSearch, WebFetch (LinkedIn if a public profile is
     reachable, Google/news mentions, company site, press/interview
     coverage, conference talks).
   - What to return, as a single structured "guest context brief":
     - **Professional accomplishments** — verifiable career highlights
     - **Notable projects** — specific work tied to their name, not generic
       company achievements
     - **Speaking history** — talks, articles, podcasts, panels they've done
       before
     - **Personal/background details** — anything publicly shared that
       humanizes them (hometown, hobbies, non-work interests, career-path
       origin story), useful as icebreaker material only if no transcript
       fills that role instead
   - Explicit instruction: this brief needs to compress to **one page max**
     in the final prep sheet — prioritize the 5-8 facts most worth including,
     don't return an exhaustive biography for step 3 to have to trim.
   - Explicit instruction: cite where each fact came from (source name or
     URL) so Harper can judge reliability, and state plainly if a fact can't
     be verified rather than inferring or guessing.

2. Do not block on the subagent's completion before step 1 proceeds. Note
   the subagent's identifier/handle so step 3 can check on or await it later.

3. When the subagent's result arrives (whenever that happens relative to
   step 1's progress):
   - If it returned a usable brief: write it to `state.yaml`'s
     `accumulated-context.guest_research` verbatim (structured object above).
   - If it returned empty, inconclusive, or clearly thin results (fewer than
     3 verifiable facts, or the guest has little to no public footprint):
     set `accumulated-context.research_gaps_flagged: true` and record a
     one-line reason in `accumulated-context.research_gap_note`. This is
     non-blocking — do not stop the workflow or step 3 for it. (This matters
     less when step 1 found a real transcript — note in the flag whether a
     transcript is covering the gap.)
   - Set `accumulated-context.step2_research_done: true`.
   - Mark this file's frontmatter `status: complete` and `completed-at`.

4. Update `state.yaml`'s `current-step` only once *both* step-01 and step-02
   have reached `status: complete` in their own frontmatter — whichever step
   finishes second is responsible for advancing `current-step: step-03`.

---

## SUCCESS METRICS

- Research subagent launched without blocking step 1's start
- Guest context brief captured with sourced facts, compressed to what will
  fit in a one-page brief, or gap explicitly flagged
- 5-8 facts surfaced when the guest has any public footprint, ranked so
  step 3 can trim to the best 3-5 if no transcript exists to lean on instead

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Guest has little to no public footprint | Flag `research_gaps_flagged: true` with a reason, proceed. Note whether step 1's transcript search covers the gap. |
| WebSearch/WebFetch unreachable | Retry once. If still unreachable, flag the gap the same way as above — do not stall the workflow waiting on connectivity. |
| Research subagent returns unverifiable or contradictory claims | Include only sourced facts; drop unsourced ones rather than presenting them as fact. |

## NEXT STEP

Runs in parallel with `step-01-transcript-search.md`. Once both are
complete, continue to `step-03-generate-prep.md`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
