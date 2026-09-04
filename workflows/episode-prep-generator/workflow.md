---
name: episode-prep-generator
description: Generate a scannable, 2-3 page Improving Edge podcast episode prep sheet with concrete questions built from a prior conversation transcript when one exists, enriched by parallel guest research
agent: harper
model: sonnet
fairness:
  applicable: false
  reason: "generates prep content for a single named podcast guest ahead of a scheduled recording, not a decision about eligibility, access, or resources applied across a population"
---

<!-- system:start -->
# Episode Prep Generator Workflow

**Goal:** Turn a guest name (plus topic, title, company, industry/domain,
specific angle, and an optional internal-context note) into one scannable,
2-3 page episode prep document David can read in under 2 minutes. When a
prior recorded conversation with the guest exists (Plaud transcription,
meeting notes, lunch conversation record), the questions are built directly
from that real conversation, not from abstract industry threads. When no
transcript exists, questions fall back to research-based inference.

**Agent:** Harper — Storyteller, Communication, Content & Thought Leadership

**Architecture:** 4-step workflow with a parallel fan-out at the start:

1. `step-01-transcript-search.md` — search the Obsidian vault (via
   `mcp__obsidian-mcp-tools__search_vault`) for a prior recorded conversation
   with this guest: Plaud transcriptions, meeting notes, lunch conversation
   records. If found, this becomes the primary source for step 3's
   questions. If not, flag it and continue.
2. `step-02-guest-research.md` — runs in parallel with step 1: research the
   guest (LinkedIn, Google, news mentions) for professional accomplishments,
   speaking history, and notable projects. Secondary to the transcript when
   one exists; the primary source when one doesn't.
3. `step-03-generate-prep.md` — waits for both step 1 and step 2 to
   complete, then builds the prep sheet: 7-10 concrete questions with
   follow-ups (from the transcript when available, from research inference
   otherwise), a 1-page guest research brief, a Suggested Flow section
   capturing what the guest will actually say, an optional Internal Context
   section, a closing beat, and a Notes section documenting the transcript
   source and any sign-off/scheduling caveats.
4. `step-04-assemble-output.md` — save the assembled document to
   `meetings/podcast-prep/`. Each guest/episode has exactly one prep file at
   a fixed filename pattern; re-running this workflow for the same guest on
   the same date updates that file in place rather than creating a second,
   differently-named file.

Unlike the previous version of this workflow, step 3 does **not** start
producing content before both step 1 and step 2 finish — the transcript, if
one exists, determines the entire structure and content of the prep sheet,
so there's nothing useful to generate ahead of that input landing.

**Format bar:** The output must match David's actual prep format, exemplified
by `meetings/podcast-prep/2026-07-14-kapil-dabi.md` — concrete numbered
questions with lettered follow-ups grouped into a handful of named clusters,
a Suggested Flow section grounded in a real (or clearly-labeled inferred)
conversation, and a short Notes section. This is **not** the old 10-section,
8-10 page format built from `reference/improving-edge-prep-sheet-generator-prompt.md`
— that template is no longer used by this workflow.

**Relationship to `podcast-prep`:** This workflow is the *deep research and
thinking layer*, usable as soon as a guest is booked, before the studio floor
sheet exists. `workflows/podcast-prep` is the *studio floor sheet* — it pulls
the already-scheduled episode from the Obsidian episode map, Janine's
SharePoint questions doc, Clay, and calendar, and produces the condensed
single-page PDF for filming day. This workflow's output is meant to feed and
sharpen that one-pager, not replace it. Do not merge the two workflows — they
run at different points in an episode's lifecycle and pull from different
sources.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Why This Exists

David's actual prep sheets are short, concrete, and built from real prior
conversations with guests whenever one exists — a lunch, a call, a Plaud
recording. The previous version of this workflow generated a formal
10-section, 8-10 page document built purely from role/domain inference, which
didn't match how David actually preps for an episode. This rebuild makes
"check whether we've already talked to this guest" the first move, not an
afterthought, and constrains the output to something scannable in the two
minutes before David walks into a recording.

### Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `topic` | Yes | The episode topic |
| `guest_name` | Yes | Guest's full name |
| `guest_title` | Yes | Guest's title |
| `guest_company` | Yes | Guest's company |
| `industry_domain` | Yes | Industry or domain the guest operates in |
| `specific_angle` | Yes | What makes this conversation worth having now, or what's unresolved/contested that this guest can speak to |
| `internal_context` | No | Text connecting the conversation to Improving's work (e.g., "Improving has trip concierge work; connect agentic commerce to that") — woven into an Internal Context section if provided |

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Obsidian vault | Prior conversation transcript with this guest (Plaud, meeting notes, lunch records) | `mcp__obsidian-mcp-tools__search_vault` + `get_vault_file` — via step-01 |
| Web | Guest professional background, speaking history, notable projects | WebSearch, WebFetch — via step-02's research subagent |
| LinkedIn (if reachable) | Career history, recent posts/activity | WebSearch/WebFetch — via step-02's research subagent |

### Output

- One markdown document at
  `meetings/podcast-prep/[episode-date]-[guest-last-name].md`, 2-3 pages,
  scannable in under 2 minutes, containing:
  (this filename pattern is fixed; if it already exists for this
  guest/date, the run updates it in place rather than creating a second
  file)
  1. Episode title and metadata (2-3 lines)
  2. 7-10 concrete questions with follow-ups, grouped into named clusters
     (main content)
  3. Guest research brief (1 page max)
  4. Suggested Flow section (what the guest will actually say, from
     transcript or research)
  5. Internal Context section (only if `internal_context` was provided)
  6. Closing beat
  7. Notes: transcript source (or its absence), episode numbering status,
     any required sign-offs
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.

2. If `status: in-progress`:
   - You are resuming a previous run. Do NOT start over.
   - Read `current-step` to find where to continue.
   - Load `accumulated-context` — data already gathered (including any
     `prior_transcript` or `guest_research` already captured). Do not re-pull
     it.
   - Check that step's frontmatter: if `status: in-progress`, re-execute it;
     if `status: not-started`, begin it fresh.
   - Notify the controller: "[Harper]: Resuming episode-prep-generator from
     [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate
     `session-id`, write `session-started` and `original-request` (all
     inputs including `internal_context` if given), set
     `current-step: step-01`.
   - Begin steps 01 and 02 together per the EXECUTION note below.

4. If `status: aborted`:
   - Surface to controller: "[Harper]: episode-prep-generator was previously
     aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.

## EXECUTION

Read fully and follow `steps/step-01-transcript-search.md` and
`steps/step-02-guest-research.md` **together, not sequentially**: launch
both at workflow start. Both must reach `status: complete` in their own
frontmatter before `steps/step-03-generate-prep.md` begins — step 3 does not
start early, because the transcript (if found) determines the structure of
the entire output. Once step 3 reaches `status: complete`, continue to
`steps/step-04-assemble-output.md`.

Target total runtime: 15-25 minutes end to end (shorter than the previous
version — the output is a fraction of the length).
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
