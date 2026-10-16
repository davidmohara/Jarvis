---
agent: harper
prompt-definition: agents/harper.md
artifact-date: 2026-10-08
status: draft
---

# Stage 3 Artifact: Harper

Harper is the communication and content agent: presentation/deck building, email
drafting, talking points, content calendar, podcast prep, and thought-leadership
authoring.

## Prompt Definition

**Path:** `agents/harper.md`. Title: "Storyteller: Communication, Content &
Thought Leadership." Capabilities: presentation creation, email drafting, talking
points, content calendar, social media.

**Summary:** Harper owns external communication and content. It builds decks,
drafts emails calibrated to recipient and relationship, generates talking points
for events and media, manages the content calendar, and produces podcast prep
(detailed reference sheet plus studio PDF, merging the Episode Prep Generator
output with Janine's SharePoint questions doc). Harper also runs the
Podcast-to-Pipeline content system.

## Quality Criteria

| # | Criterion | Measurable pass/fail threshold |
|---|-----------|-------------------------------|
| P1 | Voice calibration | Drafted content matches the recipient/relationship tone profile; pass = >= 90% of drafts |
| P2 | Source merge completeness (podcast prep) | Podcast prep merges both sources (Episode Prep Generator deep prep and Janine's SharePoint doc) when both exist, deduped; pass = 100% of preps |
| P3 | Structural assertion pass rate | >= 90% of harness structural assertions pass across Harper's runs |
| P4 | Tier 3 grade | Grade B or better on graded runs; pass = >= 80% of graded runs |

## Measured Results

Recomputed from `systems/eval-harness/runs/*.json` on 2026-10-16 using the
attribution layer (`step_audit.resolve_record_agent` + `merge_reporting_agent`),
which recovers records whose workflow/name resolves to a harper-owned workflow.
Repro:

```
python3 -c "import json,glob,sys;sys.path.insert(0,'systems/eval-harness');from step_audit import resolve_record_agent,merge_reporting_agent as M;r=[json.load(open(f)) for f in glob.glob('systems/eval-harness/runs/*.json')];print(len([d for d in r if M(resolve_record_agent(d))=='harper']))"
```

- **Total records: 23** (raw labels: `general-purpose` 9, `harper` 6, `claude` 4,
  `unknown` 2, `Explore` 1, `master` 1; 14 recovered by the 2026-10-16
  transcript-attribution fix). Status distribution: success 10, aborted 13.
  Strict success rate = 10/23 = 43.5%; mech = 10/23 = 43.5%.
- **Workflows:** content-pipeline 3, obsidian-source-note 1, talking-points 1,
  podcast-prep 1, content-discovery 1, harper-podcast-prep 1, content-approval 1.
- **Structural assertions:** 34/49 passed = 69.4% across 23 records. Below the P3
  threshold.
- **Tier 3 grades:** 7 graded (A 4, B 1, C 1, F 1) = 5/7 = 71.4% grade-pass
  (A/B). Below the P4 threshold.
- **Assertion trend:** 2026-05 100% (n=2), 2026-08 57.1% (n=2), 2026-09 52.6%
  (n=6), 2026-10 n/a (n=13, no assertions recorded). Small samples.
- **Error log:** 48 entries canonicalize to `harper` (`harper` 37 + `Harper` 6 +
  three descriptive `Harper (content-approval ...)` labels), 27 with an applied
  systemic fix, 18 proposed. Harper has the second-highest applied-fix count,
  indicating a well-exercised correction loop.

**Honesty note:** 23 records is still too few for a stable rate. P3 (69.4%) is
below threshold and P4 (71.4%) is below threshold on small samples. P1 and P2 are
not directly asserted by existing records. What is required: a fresh instrumented
window of podcast-prep and email-drafting runs (target >= 10 each) scored against
P1-P2, including at least one prep where only one source exists to test P2's
"when both exist" branch.

## Iteration History

**Iteration 1: MCP tag rejection on post creation.**
Baseline: `err-20260519T145656-T8EAEV` (2026-05-19, process-skip) post creation
did not handle MCP rejecting tag objects and skipped verification. Hypothesis:
tagging and verification were not enforced. Change: step-01 updated to omit tags
if the MCP rejects tag objects, plus a mandatory `get_post` verification before
Slack notification. Measured: applied.

**Iteration 2: inferring a theme instead of using the stated thesis.**
Baseline: `err-20260608T051800-H4R2PX` (2026-06-08, assumption-error) when the
controller's message included a detailed POV, Harper inferred a theme from the
headline instead. Hypothesis: the frame was being derived rather than taken from
the controller. Change: use the controller's stated thesis as the frame when
provided. Measured: applied; directly supports P1 (voice calibration).

**Iteration 3: Unsplash aspect-ratio failures.**
Baseline: `err-20260626T142721-T01MZL` (2026-06-26, format-violation) portrait
silhouette images were selected for landscape slots. Hypothesis: aspect ratio was
not verified before committing to an image. Change: verify aspect ratio from
og:image dimensions or photo-page metadata before committing; flag
silhouette/person photos as high-risk for portrait crops. Measured: applied.

**Gap:** no before/after pass rate isolating a single Harper change. The run
needed is a paired podcast-prep set (single-source vs. dual-source) scored on P2,
plus an email-drafting set scored on P1.
