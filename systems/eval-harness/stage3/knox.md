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

Mined from `systems/eval-harness/runs/*.json` on 2026-10-08. Repro:

```
python3 -c "import json,glob;r=[json.load(open(f)) for f in glob.glob('systems/eval-harness/runs/*.json')];print(len([d for d in r if d.get('agent')=='knox']))"
```

- **Total records: 48.** Status distribution: success 40, partial 6, incomplete
  2. Completion (success) rate = 40/48 = 83.3%.
- **Structural assertions:** 125/182 passed = 68.7% across 48 records.
- **Tier 3 grades:** 15 graded (A 7, B 6, C 2) = 13/15 = 86.7% grade-pass (A/B).
  This is above the K4 threshold.
- **Assertion trend:** 2026-07 83% (n=2), 2026-08 60% (n=12), 2026-09 68%
  (n=33). Record volume concentrated in September.
- **Error log:** 50 entries tagged `knox` (23 with an applied systemic fix,
  16 proposed), plus one entry tagged `knox (plaud-ingest, general-purpose
  subagent)` and one `knox-plaud-ingest-step-01`.

**Honesty note:** K4 is measured directly (86.7% grade-pass, threshold met). K3
is below its 90% threshold on the current data (68.7%). K1 and K2 are only
partially measured: assertion sets check note existence and tagging for some
runs, not full accounting of every staged recording. A fresh plaud-ingest run
over a known staged set is required to score K1/K2 directly. Note also that 18
`plaud-ingest` eval records are attributed to the harness label `general-purpose`
rather than `knox` (a sub-agent attribution gap), so Knox's true execution count
is higher than 48.

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
