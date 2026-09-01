---
name: audience-profile-builder
owning_agent: harper
model: sonnet
trigger_keywords: [audience profile, ICP for this episode, who is this episode for]
trigger_agents: [harper]
description: >
  Third step of the Podcast-to-Pipeline pipeline. Reads extracted pain points and
  builds a target audience profile (ICP) for the episode - industry, company size,
  buyer role, and buying-trigger signals. Feeds account-targeting and
  contact-targeting. Called by workflows/episode-campaign-brief/workflow.md step 03.
---

<!-- system:start -->
# Audience Profile Builder

## Purpose

Turn a set of extracted pain points into a concrete target audience profile - the
ICP for this specific episode. This is what `account-targeting` and
`contact-targeting` use to find real companies and people, so it must be specific
enough to search on, not a generic "mid-market companies" statement.

## Input

The `pain_points` list produced by `pain-point-extraction`, plus the episode
metadata (industry context of the guest/host, if any, informs but does not
substitute for pain-point-derived signals).

## Output

```yaml
audience_profile:
  industries:
    - name: "..."
      rationale: "Why this industry, tied to a specific pain point id"
  company_size_band: "e.g. 500-5,000 employees, or $50M-$500M revenue"
  size_rationale: "Why this band - what about the pain point implies this scale (e.g. 'the guest describes a problem that only emerges once you have multiple regional teams, implying mid-to-large size')"
  buyer_roles:
    - title: "e.g. VP of Engineering, Director of Supply Chain"
      why: "Why this role owns this pain point"
      seniority_band: "Director+ | VP+ | C-suite"
  buying_trigger_signals:
    - signal: "e.g. recent reorg, new ERP rollout, funding round, leadership change"
      linked_pain_point: "pp-0X"
  pain_point_coverage:
    - pain_point_id: "pp-0X"
      addressed_by: "which part of the profile above traces to this pain point"
```

## Process

1. **Read every pain point.** For each one, ask: who, specifically, owns this
   problem inside a company? What size/maturity of company would even have this
   problem (a 20-person startup and a 5,000-person enterprise rarely share the
   same operational pain points)?

2. **Derive industries.** Only name an industry if the transcript gives a real
   signal (the guest's own industry, an example they used, a vertical-specific
   term). Do not default to "all industries" - if the transcript is genuinely
   industry-agnostic, say so explicitly rather than listing every vertical.

3. **Derive company size band.** Use operational cues in the pain points
   themselves (team structure, tooling maturity, scale of the described failure)
   rather than guessing. State the reasoning, not just the number.

4. **Derive buyer roles.** The role that would feel this pain point directly and
   have budget/authority to fix it - not every possible title, just the ones the
   pain points actually point to.

5. **Derive buying-trigger signals.** Signals a real account-targeting search
   could look for (recent funding, leadership change, tech-stack change, public
   incident) that would indicate a company is *currently* experiencing this pain
   point, not just theoretically could.

6. **Confirm full pain-point coverage.** Every pain point from the input should
   map to at least one part of the profile. If a pain point doesn't cleanly map
   to an audience segment, say so rather than forcing a fit - not every pain
   point extracted from an episode is commercially targetable.

## Failure Modes

| Failure | Action |
|---------|--------|
| Pain points are too generic to derive a specific ICP | Report this: "These pain points don't point to a specific industry or role - they read as universal. Recommend a broad audience profile or skipping targeted outreach for this episode." Do not invent specificity that isn't there. |
| Only one pain point provided | Proceed - a single strong pain point can still anchor a profile, just note the profile rests on one signal. |
| Conflicting signals (pain point implies enterprise, guest is a solo founder) | Note the tension explicitly and default to what the *pain point itself* implies, not the guest's own profile. |

## SKILL COMPLETE

After the audience profile is returned to the caller, write the skill-run signal
file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/audience-profile-builder-latest.json
```

Content:
```json
{
  "skill": "audience-profile-builder",
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
from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the
profile is thin/low-confidence and flagged as such, `"failure"` if no usable
profile could be derived. Use the actual start time for `started`. This write is
always the final action.
<!-- system:end -->

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill audience-profile-builder
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/audience-profile-builder.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->
