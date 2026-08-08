---
name: prospect-message-draft
owning_agent: harper
model: sonnet
trigger_keywords: [draft campaign message, prospect message, campaign outreach content]
trigger_agents: [harper]
description: >
  Eighth skill in the Podcast-to-Pipeline pipeline. Drafts personalized cold
  outreach content for one contact, referencing the specific episode, pain point,
  and matched offering. Reuses harper-email's content-quality pattern (VOICE.md,
  Draft/Notes/Alternative-closings presentation, cold-prospect tone-table entry)
  but produces content only — not a delivered draft. Output becomes the Email
  asset for campaign-send's Journey step, never an Outlook/Superhuman draft.
  Called by workflows/audience-target-outreach/workflow.md step 03, looped once
  per contact.
---

<!-- system:start -->
# Prospect Message Draft

## Purpose

Produce personalized cold-outreach message content for one contact, grounded in
the actual episode, the specific pain point that applies to them, and the
matched offering — content quality held to the same bar as `harper-email`, but
with a fundamentally different delivery destination.

**Explicit deviation from `harper-email` — read this before drafting anything:**
This skill reuses `workflows/email-drafting/`'s voice/tone/draft-presentation
*content* pattern (loading `identity/VOICE.md`, the fixed
Draft/Notes/Alternative-closings presentation format, and the tone-calibration
table in `workflows/email-drafting/steps/step-02-draft.md`, which now includes
a "Cold Prospect / Campaign Outreach" column added for this system). It does
**not** reuse that workflow's delivery step
(`mcp__claude_ai_Microsoft_365__outlook_create_draft`). The output of this
skill is message content that becomes the Email asset inside a Customer
Insights – Journeys journey step, created and sent by `campaign-send` — never
an Outlook draft, never a Superhuman draft, never something delivered from
David's personal inbox. This distinction exists because CRM-side reply
attribution only works if the send itself is CRM-native. Do not "simplify"
this by routing content through `harper-email`'s Outlook delivery in a future
edit — that would silently break attribution for the whole system.

## Input

- One contact (from `contact-targeting`'s output)
- The pain point + offering pairing relevant to that contact (from
  `pain-point-extraction` + `offering-match`)
- Episode metadata (title, episode number, guest, date)

## Process

1. **Load `identity/VOICE.md`** exactly as `workflows/email-drafting/steps/step-01-clarify-context.md`
   does, for baseline formatting conventions (em-dash rule, greeting/paragraph
   spacing, closing style).

2. **Load recipient context.** Same as `harper-email`'s pattern: check
   CRM/Clay for anything relevant to this specific contact (existing
   relationship, prior interaction) that should shape tone — a contact with an
   existing relationship gets a warmer opener than a fully cold one.

3. **Apply the "Cold Prospect / Campaign Outreach" tone-table entry** in
   `workflows/email-drafting/steps/step-02-draft.md` for structure, sentence
   length, vocabulary, and sign-off. Read that entry's additional rules before
   drafting.

4. **Draft the message**, anchored to:
   - The specific pain point (plain-language restatement, and — if it reads
     naturally, not forced — a short reference to the episode itself, e.g.
     "On a recent episode of The Improving Edge, we talked about...")
   - The matched offering, referenced only if `offering-match` found a real,
     tight fit for this pain point — never force in an offering that was
     flagged `no_match`
   - One clear, low-friction call to action

5. **Present using the same fixed structure `harper-email` uses**: Draft /
   Notes (tone, assumptions, call to action) / Alternative closings. This is
   content for controller review and approval — approving the content here is
   NOT the same as approving the send. Say so explicitly in the presentation:
   "Content approval only — sending still requires the explicit per-contact
   confirmation at campaign-send time."

6. **Return the approved content** (subject line + body) to the caller in a
   form `campaign-send` can use directly as the journey step's Email asset:

```yaml
message:
  contact_name: "..."
  subject: "..."
  body: "..."
  pain_point_id: "pp-0X"
  offering_referenced: "..." | null
  tone_used: "cold-prospect-campaign-outreach"
  content_approved: true/false
```

## Failure Modes

| Failure | Action |
|---------|--------|
| No tight offering match exists for this contact's pain point | Draft content that references the pain point/episode without forcing an offering pitch — a soft "we've been thinking about this too" outreach is valid; note in the presentation that no offering was cited. |
| Contact has an existing CRM/Clay relationship history | Reference it naturally (warmer opener) rather than drafting as if this were a fully cold contact. |
| Controller wants to reject the draft | Iterate per the same pattern as `workflows/email-drafting/steps/step-03-iterate.md` — do not proceed to campaign-send with unapproved content. |
| VOICE.md unavailable | Use the cached formatting rules already documented in `workflows/email-drafting/workflow.md`'s initialization section, and flag it. |

## SKILL COMPLETE

After the content is approved (or the iteration loop for this contact ends),
write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/prospect-message-draft-latest.json
```

Content:
```json
{
  "skill": "prospect-message-draft",
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

Set `trigger` to `"boot"` if called from a boot workflow, `"scheduled"` if
called from a scheduled task, `"manual"` otherwise. Set `status` to
`"partial"` if content was drafted without a matched offering, `"failure"` if
VOICE.md and recipient context were both unavailable and content could not be
meaningfully personalized. Use the actual start time for `started`. This
write is always the final action.
<!-- system:end -->
