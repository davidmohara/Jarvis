---
name: episode-campaign-brief
description: Turn a podcast episode into a markdown Episode Campaign Brief - pain points, audience profile, and grounded pitch angles citing real offering documents
agent: harper
model: sonnet
fairness:
  applicable: false
  reason: "internal sales/marketing research and drafting, not a decision about individuals' access to opportunity or resources"
---

<!-- system:start -->
# Episode Campaign Brief Workflow

**Goal:** Produce one markdown "Episode Campaign Brief" document — pain points
extracted from the episode, the target audience profile they imply, and
grounded pitch angles that cite real, current Improving offering documents
(never fabricated services). This is the first half of the Podcast-to-Pipeline
system; its output feeds the second workflow, `audience-target-outreach`.

**Agent:** Harper — Storyteller, Communication, Content & Thought Leadership

**Architecture:** Sequential 4-step workflow composing four discrete skills,
each doing one thing against one source:

1. `episode-transcript-intake` — retrieve and normalize the transcript
2. `pain-point-extraction` — extract quote-grounded pain points
3. `audience-profile-builder` — derive the ICP from those pain points
4. `offering-match` — ground pitch angles against live SharePoint offering docs
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Podcast URL / Obsidian | Episode transcript + metadata | Chrome (public) or Obsidian MCP (internal) — via `episode-transcript-intake` |
| SharePoint — Sales Offerings folder | Primary offering grounding (Duration/Price/Summary) | `mcp__claude_ai_Microsoft_365__sharepoint_*` — via `offering-match` |
| SharePoint — Central Sales/SPARC site | Secondary offering grounding | Same, via `offering-match` |
| **SharePoint — Marketing/Personas** ([`Buyer Personas` / `Anti-Buyer Personas`](https://improving.sharepoint.com/sites/OfficeoftheChiefConsultingOfficer/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2FOfficeoftheChiefConsultingOfficer%2FShared%20Documents%2FGeneral%2FMarketing%2FPersonas&viewid=0aa516ce%2D0323%2D42ae%2D90d2%2D448e258ea263)) | For each matched offering: the buyer persona (Service line match) and anti-buyer persona, with their "How Improving Wins"/"How Improving Disarms" responses | Same, via `offering-match` |

### Output

- `Episode Campaign Brief` markdown document containing:
  1. Episode metadata
  2. Pain points (with supporting quotes)
  3. Audience profile (ICP)
  4. Offering matches (with source doc citations) or explicit gaps where no
     real offering exists
- Handed off to `audience-target-outreach` as the `audience_profile` input,
  or run standalone if David only wants the brief.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## STATE CHECK

Read and follow `reference/state-check-protocol.md` before any execution. Workflow: `episode-campaign-brief`; agent: `harper`.

## EXECUTION

Read fully and follow: `steps/step-01-transcript-intake.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
