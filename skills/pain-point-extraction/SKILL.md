---
name: pain-point-extraction
owning_agent: harper
model: sonnet
trigger_keywords: [pain points, extract pain points, episode pain points]
trigger_agents: [harper]
description: >
  Second step of the Podcast-to-Pipeline pipeline. Reads a podcast transcript and
  extracts structured pain points, each grounded in a supporting quote. Feeds
  audience-profile-builder and offering-match. Called by
  workflows/episode-campaign-brief/workflow.md step 02.
---

<!-- system:start -->
# Pain Point Extraction

## Purpose

Read a transcript and pull out the real business/operational pain points discussed —
not generic industry problems, but the specific frustrations, failures, or friction
points the guest or host actually described. Every pain point must be traceable to
a quote. This skill does not match pain points to offerings or audiences — that is
`offering-match` and `audience-profile-builder`'s job, each working from this output.

## Input

The transcript + episode metadata object produced by `episode-transcript-intake`.

## Output

```yaml
pain_points:
  - id: pp-01
    statement: "Plain-language restatement of the pain point"
    quote: "The exact supporting quote from the transcript"
    speaker: "Guest name" | "Host"
    timestamp: "00:14:32" (if timestamps are present in the source; omit if not)
    severity_signal: "How strongly this was expressed — offhand mention vs. repeated/emphasized theme"
    context: "One sentence on the situation that produced this pain point (industry, team size, trigger event, etc., if stated)"
  - id: pp-02
    ...
```

## Process

1. **Read the full transcript.** Do not skim or sample — pain points can appear
   anywhere, including asides.

2. **Identify candidate pain points.** Look for:
   - Explicit statements of frustration, failure, cost, or risk ("the thing that
     kills us is...", "we lost six months to...", "nobody talks about how hard...")
   - Described symptoms even without an explicit "this is a problem" framing
     (e.g., a guest describing a workaround implies an underlying pain point)
   - Repeated themes — if the same friction comes up twice in different words,
     that is a stronger signal than a single offhand mention

3. **For each candidate, extract:**
   - The verbatim supporting quote (do not paraphrase the quote itself — only the
     `statement` field is a restatement)
   - Who said it
   - A plain-language restatement any salesperson could use without re-listening
     to the episode
   - A severity signal, using the language actually used (do not invent a numeric
     score — "mentioned once in passing" and "returned to three times unprompted"
     are both valid, honest signals)

4. **Deduplicate.** If the same underlying pain point is described multiple times,
   merge into one entry and cite the strongest quote, noting in `severity_signal`
   that it recurred.

5. **Do not invent pain points that aren't in the transcript**, even if they seem
   like an obvious fit for Improving's services. This skill's entire value is that
   every downstream pitch traces back to something a real person actually said.

## Failure Modes

| Failure | Action |
|---------|--------|
| Transcript has no clear pain points (pure technical explainer, no complaints/friction) | Report this honestly: "No distinct pain points surfaced in this transcript — it reads as [descriptive/technical], not a discussion of a problem." Do not force-fit generic pain points to make the pipeline continue. |
| Transcript is garbled/low-quality (per intake's quality flag) | Extract what is legible, flag any quote pulled from a low-confidence passage. |
| Guest and host disagree on whether something is a real problem | Capture both framings; note the disagreement in `context`. |

## SKILL COMPLETE

After the pain point list is returned to the caller, write the skill-run signal
file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/pain-point-extraction-latest.json
```

Content:
```json
{
  "skill": "pain-point-extraction",
  "agent": "harper",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

**Eval-harness exception:** if this invocation is an eval-harness executor run (simulating this skill for grading, benchmarking, or testing rather than a genuine Harper-invoked production run), do NOT write this signal file. Writing it from a simulation would falsely register a live skill run in the production eval-harness tracking system. Only write it when this is an actual production invocation.

Set `trigger` to `"boot"` if called from a boot workflow, `"scheduled"` if called
from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if
extraction found few/weak pain points and flagged that honestly, `"failure"` if
the transcript could not be processed at all. Use the actual start time for
`started`. This write is always the final action.
<!-- system:end -->

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill pain-point-extraction
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/pain-point-extraction.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->
