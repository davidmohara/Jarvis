---
agent: knox
prompt-definition: agents/knox.md
artifact-date: 2026-10-08
status: draft
---

# Stage 3 Artifact: Knox

Knox is the Knowledge Manager agent: vault curation, transcript ingestion (Plaud
and Teams), reMarkable sync, search, archival, and knowledge-health auditing.
Knox owns the plaud-ingest candidate workflow.

## Prompt Definition

**Path:** `agents/knox.md`. Title: "Knowledge Manager: Vault Curator &
Information Architect." Capabilities: knowledge capture, vault curation, device
sync, transcript ingestion, cross-reference linking, search, archival, knowledge
health.

**Summary:** Knox converts raw capture into structured, tagged Obsidian notes.
It ingests pre-fetched Plaud transcripts and Teams transcripts, syncs reMarkable
handwritten notes via vision transcription, routes action items to OmniFocus, and
audits the vault for orphaned notes, broken links, stale content, and missing
tags. Its output feeds Chief (boot ingestion) and Harper/Chase (content routing).

## Quality Criteria

| # | Criterion | Measurable pass/fail threshold |
|---|-----------|-------------------------------|
| K1 | Ingestion completeness | Every staged recording is either converted to a tagged note or explicitly logged as skipped with a reason; pass = 100% accounted for, 0 silent drops |
| K2 | Tag compliance | Every produced note carries the required tags and correct folder routing; pass = >= 95% of notes |
| K3 | Structural assertion pass rate | >= 90% of harness structural assertions pass across plaud-ingest and vault runs |
| K4 | Tier 3 grade | Grade B or better on graded runs; pass = >= 80% of graded runs |

## Measured Results

Recomputed from `systems/eval-harness/runs/*.json` on 2026-10-16 using the
attribution layer (`step_audit.resolve_record_agent` + `merge_reporting_agent`),
which recovers the 18 `plaud-ingest` records whose workflow resolves to Knox even
though the raw label is `general-purpose`. Repro:

```
python3 -c "import json,glob,sys;sys.path.insert(0,'systems/eval-harness');from step_audit import resolve_record_agent,merge_reporting_agent as M;r=[json.load(open(f)) for f in glob.glob('systems/eval-harness/runs/*.json')];print(len([d for d in r if M(resolve_record_agent(d))=='knox']))"
```

- **Total records: 66** (raw labels: `knox` 45, `general-purpose` 19, `master` 1,
  `claude` 1). Status distribution: success 40, aborted 14, partial 7, failure 2,
  incomplete 2, complete 1. Strict success rate = 41/66 = 62.1%; mech (strict +
  partial, session-exit aborts excluded) = 48/64 = 75.0%.
- **Workflows:** plaud-ingest 34, plaud-transcripts 7, plaud-discover 6,
  plaud-speaker-id 6, remarkable-upload 3, plaud-trigger 3, watchtower 2,
  watchtower-weekly 2.
- **Structural assertions (K3):** 176/238 passed = **73.9%** across 66 records.
  Still below the 90% threshold. The 18 recovered `plaud-ingest` records pass at
  51/56 = 91.1%, but the pre-existing 48 records pass at 125/182 = 68.7% and
  dominate the denominator, so K3 does not close.
- **Tier 3 grades (K4):** 16 graded (A 7, B 6, C 3) = 13/16 = 81.2% grade-pass
  (A/B). Above the K4 threshold.
- **Assertion trend:** 2026-07 83% (n=2), 2026-08 70% (n=30), 2026-09 74% (n=29),
  2026-10 88% (n=4). Record volume concentrated in August-September.
- **Error log:** 53 entries canonicalize to `knox` (`knox` 47 + `Knox` 5 +
  `knox (plaud-ingest, ...)` + `knox-plaud-ingest-step-01`), 25 with an applied
  systemic fix, 17 proposed.

**Honesty note:** K4 is measured directly (81.2% grade-pass, threshold met). K3
is below its 90% threshold (73.9%) even after the attribution fix recovered the
18 mislabeled `plaud-ingest` records — the recovered records pass at 91.1%, but
the older records' 68.7% keeps the combined rate under the bar. K1 and K2 are
only partially measured: assertion sets check note existence and tagging for some
runs, not full accounting of every staged recording. A fresh plaud-ingest run
over a known staged set is required to score K1/K2 directly.

## Iteration History

**Iteration 1: skill not read before execution.**
Baseline: `err-20260512-005` (2026-05-12, process-skip) Knox executed steps
without reading the full skill file, missing failure-mode paths. Hypothesis:
failure modes were treated as optional reading. Change: rule added that the full
skill file is read before any step; failure modes are part of the spec. Measured:
applied.

**Iteration 2: speaker-identification edge cases.**
Baseline: `err-20260512-006` (Edge Case A, known speaker not assigned) and
`err-20260512-007` (Edge Case B, known speaker wrongly assigned). Hypothesis: the
speaker-ID logic had no documented handling for ambiguous matches. Change: both
edge cases documented in `skills/plaud-transcripts/SKILL.md` (section 4c) and
`workflows/plaud-ingest/steps/step-03-identify-speakers.md`. Measured: applied;
Tier 3 grade-pass rose to 86.7% across 15 graded runs.

**Iteration 3: reMarkable filename/folder routing.**
Baseline: two entries tagged `remarkable-wrong-filename` and
`remarkable-wrong-folder`. Hypothesis: naming convention was not enforced at
write time. Change: naming-convention enforcement in the reMarkable path.
Measured: applied; no recurrence in later entries.

**Gap:** K3 (assertion pass rate) sits at 68.7%, below threshold. The run needed
is a batch plaud-ingest over a fixed staged set with K1/K2 assertion hooks, plus
an A/B of the speaker-ID edge-case handling before and after the step-03 change.
