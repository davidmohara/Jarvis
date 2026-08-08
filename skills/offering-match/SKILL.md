---
name: offering-match
owning_agent: harper
model: sonnet
trigger_keywords: [offering match, match pain points to services, what do we sell for this]
trigger_agents: [harper]
description: >
  Fourth step of the Podcast-to-Pipeline pipeline. Matches extracted pain points to
  Improving's actual, current service offerings by searching live SharePoint sources
  - never a cached or invented offerings list. Refuses to fabricate a match if none
  exists. Called by workflows/episode-campaign-brief/workflow.md step 04, and reused
  standalone by prospect-message-draft for pitch grounding.
---

<!-- system:start -->
# Offering Match

## Purpose

Pair each extracted pain point with a real Improving service offering, pulled live
from SharePoint at the time this skill runs. This skill's entire value proposition
is that every pitch angle it produces is grounded in a real, currently-sold
offering with a real duration and price - never a plausible-sounding invented
service, and never a stale cached list from a prior run or a prior conversation's
memory.

**Hard rule: query the live SharePoint sources every time this skill runs.** Do not
rely on any previously-fetched offerings list, a summary from a prior session, or
general knowledge of "what Improving probably sells." If SharePoint is unreachable,
this skill fails rather than falling back to memory or invention (see Failure Modes).

## Input

The `pain_points` list from `pain-point-extraction`.

## Grounding Sources (query in this priority order, both if needed)

1. **Primary** — `OfficeoftheChiefConsultingOfficer/Shared Documents/General/Sales Support/Sales Offerings/`
   Structured per-offering documents organized by category (AI Offerings, DevOps
   Enablement, Data Enablement, Platform Engineering, Business Agility, etc.). Each
   doc includes Duration, Price, and Summary fields — pull all three verbatim.
2. **Secondary** — `https://improving.sharepoint.com/sites/Sales`
   Central Sales / SPARC site. Sales playbooks and regional service-offering decks
   (e.g. Pune capabilities). Use only to fill gaps not covered by the primary folder.

Use `mcp__claude_ai_Microsoft_365__sharepoint_search` and
`mcp__claude_ai_Microsoft_365__sharepoint_folder_search` to locate candidate
documents, then `mcp__claude_ai_Microsoft_365__read_resource` (or
`mcp__claude_ai_Microsoft_365__sharepoint_search` result content, whichever
surfaces the actual document text) to read the offering's Duration/Price/Summary.
Do not rely on the search result snippet alone if it doesn't clearly contain all
three fields — open the document.

**Do not use** the older third-party 2020 offerings PDF that may surface in a
general search. If a hit's provenance or date is unclear, verify it lives in one
of the two sources above before citing it.

## Output

```yaml
offering_matches:
  - pain_point_id: pp-01
    offering_name: "..."
    offering_category: "AI Offerings | DevOps Enablement | Data Enablement | Platform Engineering | Business Agility | ..."
    duration: "as stated in the source doc"
    price: "as stated in the source doc"
    summary: "as stated in the source doc, or tightly excerpted"
    source_doc: "SharePoint path or URL to the exact document"
    source_priority: "primary" | "secondary"
    fit_rationale: "1-2 sentences: why this offering addresses this specific pain point"
  - pain_point_id: pp-02
    match_status: "no_match"
    reason: "Searched both sources; no current offering addresses this pain point. Flagging as a gap rather than inventing a service."
```

## Process

1. For each pain point, formulate a search query using the plain-language
   restatement (not the raw quote) — e.g. "supply chain visibility across
   regional teams," not the verbatim transcript line.

2. Search the primary SharePoint folder first. If a clear match with
   Duration/Price/Summary is found, use it and stop for that pain point.

3. If no primary match, search the secondary Central Sales/SPARC site. Same
   standard — must be a real, current offering with identifiable
   duration/price/summary information (regional decks may have looser
   formatting; extract what's genuinely there, don't force a Duration/Price
   field that the doc doesn't actually state — note "not specified in source"
   rather than guessing).

4. If neither source yields a real match, mark `match_status: no_match` and
   state the gap plainly. This is a valid and expected output — do not treat
   an unmatched pain point as a task failure. It is more useful to sales than
   a fabricated pitch.

5. Return the full list, matched and unmatched, so `prospect-message-draft` and
   the episode brief can see the complete picture.

## Failure Modes

| Failure | Action |
|---------|--------|
| SharePoint search/read tools unreachable | Stop. Do not proceed using cached knowledge of "what Improving sells." Report: "SharePoint offerings sources unreachable — cannot ground pitch angles. Retry once connectivity is confirmed." This is a hard stop, not a degraded-output case. |
| A document lacks a clear Duration or Price field | Use what is present; state "not specified in source" for the missing field rather than inventing a number. |
| Multiple offerings plausibly match one pain point | List the strongest 1-2 matches, not every tangential hit. Note if it's a close call. |
| Offering doc is clearly outdated (references a sunset product/team) | Flag it and search for a more current equivalent before citing it. |

## SKILL COMPLETE

After the offering matches are returned to the caller, write the skill-run signal
file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/offering-match-latest.json
```

Content:
```json
{
  "skill": "offering-match",
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
from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if some
pain points went unmatched (this is expected and should still be `"success"`
unless SharePoint itself failed — reserve `"partial"` for cases like one source
being unreachable while the other succeeded), `"failure"` if both SharePoint
sources were unreachable. Use the actual start time for `started`. This write is
always the final action.
<!-- system:end -->
