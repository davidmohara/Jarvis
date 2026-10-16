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
though the raw label is `general-purpose`, plus a further 35 recovered from the
spawn transcript by the 2026-10-16 attribution fix. Repro:

```
python3 -c "import json,glob,sys;sys.path.insert(0,'systems/eval-harness');from step_audit import resolve_record_agent,merge_reporting_agent as M;r=[json.load(open(f)) for f in glob.glob('systems/eval-harness/runs/*.json')];print(len([d for d in r if M(resolve_record_agent(d))=='knox']))"
```

- **Total records: 101** (raw labels: `general-purpose` 51, `knox` 45, `Explore`
  3, `master` 1, `claude` 1). Status distribution: success 52, aborted 25,
  partial 15, failure 6, incomplete 2, complete 1. Strict success rate = 53/101 =
  52.5%; mech (strict + partial, session-exit aborts excluded) = 68/99 = 68.7%.
- **Workflows:** plaud-ingest 34, plaud-transcripts 7, plaud-discover 6,
  plaud-speaker-id 6, remarkable-upload 3, plaud-trigger 3, watchtower 2,
  watchtower-weekly 2, omnifocus-tasks 1, delivery-router 1, teams-transcripts 1.
- **Structural assertions (K3):** 176/238 passed = **73.9%** across 101 records.
  Still below the 90% threshold. The 35 transcript-recovered records carry no
  assertions, so the rate is unchanged by the fix. The 18 recovered `plaud-ingest`
  records pass at 51/56 = 91.1%, but the pre-existing records pass at 125/182 =
  68.7% and dominate the denominator, so K3 does not close.
- **Tier 3 grades (K4):** 31 graded (A 13, B 10, C 4, D 1, F 3) = 23/31 = **74.2%**
  grade-pass (A/B). Below the K4 threshold — the transcript fix surfaced 15
  previously-unattributed graded records whose grades pull the rate under the bar.
- **Assertion trend:** 2026-07 83.3% (n=2), 2026-08 70.3% (n=30), 2026-09 74.5%
  (n=47), 2026-10 87.5% (n=21). Record volume concentrated in August-September.
- **Error log:** 53 entries canonicalize to `knox` (`knox` 47 + `Knox` 5 +
  `knox (plaud-ingest, ...)` + `knox-plaud-ingest-step-01`), 25 with an applied
  systemic fix, 17 proposed.

**Honesty note:** K4 is measured directly (74.2% grade-pass) and is **below** its
threshold — the 2026-10-16 transcript fix surfaced 15 previously-unattributed
graded records that pull the rate from 81.2% (on the 16 previously-attributed
grades) under the 80% bar. K3 is also below its 90% threshold (73.9%): the
recovered `plaud-ingest` records pass at 91.1%, but the older records' 68.7%
keeps the combined rate under the bar. K1 and K2 are only partially measured:
assertion sets check note existence and tagging for some runs, not full
accounting of every staged recording. A fresh plaud-ingest run over a known
staged set is required to score K1/K2 directly.

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
