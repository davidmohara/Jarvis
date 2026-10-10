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
from SharePoint at the time this skill runs.

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
3. **Persona sources** (used only for the buyer/anti-buyer persona step, Process
   step 5) — `https://improving.sharepoint.com/sites/OfficeoftheChiefConsultingOfficer/Shared Documents/General/Marketing/Personas/`,
   specifically the `Buyer Personas/` and `Anti-Buyer Personas/` subfolders. Buyer
   persona docs carry a "Persona at a Glance" table with a Service line field and
   a "How Improving Wins" section. Anti-buyer persona docs carry a "Buyer personas
   they counter" cross-reference field and a "How Improving Disarms" section.

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
    buyer_persona:
      name: "..."
      role: "..."
      service_line: "..."
      response: "How Improving Wins summary — positioning/differentiation"
      source_doc: "SharePoint path"
    anti_buyer_persona:
      name: "..."
      role: "..."
      cross_referenced: true/false
      response: "How Improving Disarms summary — counter-move/conversion play"
      source_doc: "SharePoint path"
  - pain_point_id: pp-02
    match_status: "no_match"
    reason: "Searched both sources; no current offering addresses this pain point. Flagging as a gap rather than inventing a service."
```

`buyer_persona` and `anti_buyer_persona` are only present when `match_status` is not `no_match` — there's no offering to attach a persona to for an unmatched pain point. If persona matching itself comes up empty for a matched offering, see Step 6 of the Process below (`persona_match_status: no_match`) rather than omitting the field silently.

## Process

1. For each pain point, formulate a search query using the plain-language
   restatement (not the raw quote) — e.g. "supply chain visibility across
   regional teams," not the verbatim transcript line.

2. Search the primary SharePoint folder first. If a clear match with
   Duration/Price/Summary is found, use it and stop for that pain point.

3. If no primary match, search the secondary Central Sales/SPARC site. Regional
   decks may have looser formatting; extract what is genuinely there and note
   "not specified in source" for a field the doc does not state, rather than
   guessing.

4. If neither source yields a match, mark `match_status: no_match` and state
   the gap plainly. An unmatched pain point is a valid and expected output, not
   a task failure.

5. For each pain point that DID get a real offering match (skip this step
   entirely for `no_match` pain points — there's no offering to attach a
   persona to), identify the buyer persona and anti-buyer persona fit:

   a. Query `Personas/Buyer Personas/` under
      `https://improving.sharepoint.com/sites/OfficeoftheChiefConsultingOfficer/Shared Documents/General/Marketing/Personas/`
      via `sharepoint_search`/`read_resource`. Each doc has a "Persona at a
      Glance" table with a **Service line** field. Select the persona whose
      Service line most closely matches the matched offering's category. If no
      persona's Service line is a reasonable match, set
      `persona_match_status: no_match` on that offering match and say so
      plainly — do not force-fit an unrelated persona onto an offering just to
      fill the field.

   b. Query `Personas/Anti-Buyer Personas/` in the same folder. Each doc has
      a "Buyer personas they counter" cross-reference field. Prefer the
      anti-buyer persona whose cross-reference field explicitly names the
      buyer persona selected in (a). If none explicitly cross-references it,
      select the most contextually relevant generic blocker archetype and
      set `cross_referenced: false` — anti-buyer personas are largely
      offering-agnostic archetypes, so a generic pick here is expected and
      fine. Never set `cross_referenced: true` unless the source document's
      "Buyer personas they counter" field actually names the persona from
      (a) by name.

   c. For both selected personas, extract the actual response content, not
      just the persona name: the buyer persona's "How Improving Wins"
      section (positioning/differentiation, including the T.I.N.B.
      competitive rebuttal and Maslow-need framing where present); the
      anti-buyer persona's "How Improving Disarms" section (disarming
      factors, counter-move, conversion play). Summarize tightly rather than
      pasting the full section — this is what feeds the brief's Buyer /
      Anti-Buyer subsection.

6. Return the full list, matched and unmatched, with persona data attached
   to each matched offering, so `prospect-message-draft` and the episode
   brief can see the complete picture.

## Failure Modes

| Failure | Action |
|---------|--------|
| SharePoint search/read tools unreachable | Stop. Report: "SharePoint offerings sources unreachable — cannot ground pitch angles. Retry once connectivity is confirmed." This is a hard stop, not a degraded-output case. |
| A document lacks a clear Duration or Price field | Use what is present; state "not specified in source" for the missing field rather than inventing a number. |
| Multiple offerings plausibly match one pain point | List the strongest 1-2 matches, not every tangential hit. Note if it's a close call. |
| Offering doc is clearly outdated (references a sunset product/team) | Flag it and search for a more current equivalent before citing it. |
| No buyer persona's Service line reasonably matches the offering's category | Set `persona_match_status: no_match` on that offering entry and state the gap plainly. Do not force-fit an unrelated persona. The offering match itself still stands — this only affects the persona subsection. |
| No anti-buyer persona's "Buyer personas they counter" field names the selected buyer persona | Select the most contextually relevant generic blocker archetype, set `cross_referenced: false`, and say so. This is expected and not a failure — do not claim a false cross-reference to make the field look more precise than it is. |
| Personas SharePoint folders unreachable | Persona matching for this run is degraded, not the whole skill. Return offering matches without `buyer_persona`/`anti_buyer_persona` fields, flag "Persona folders unreachable — offering matches returned without persona fits," and mark the skill-run signal `status: partial`. |

<!-- system:end -->

