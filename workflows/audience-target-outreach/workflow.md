---
name: audience-target-outreach
description: Find target accounts and contacts for an audience profile, draft personalized outreach content, and run the send as a trackable Customer Insights – Journeys campaign so replies tie back to the episode
agent: harper
model: sonnet
fairness:
  applicable: false
  reason: "internal sales/marketing research and drafting, not a decision about individuals' access to opportunity or resources"
---

<!-- system:start -->
# Audience Target Outreach Workflow

**Goal:** Take an audience profile (from `episode-campaign-brief`, or supplied
directly) and run it through to a live, trackable outbound campaign — real
target accounts, real qualified contacts, personalized content, and a CRM-native
send via Customer Insights – Journeys, so that replies tie back to the episode
that generated them rather than to David's personal inbox.

**Agent:** Harper — Storyteller, Communication, Content & Thought Leadership

**Architecture:** Sequential 5-step workflow. Steps 1-2 run once for the whole
audience. Step 3 loops once per contact (each presented for content approval).
Step 4 runs once for the whole episode (CRM structure setup). Step 5 loops once
per contact (each gated by an explicit live send confirmation — never a batch
auto-send). This ordering matters: `campaign-setup` (CRM structure) must exist
before `campaign-send` can attach an Email asset to a Journey step, so setup
runs as step 4, between drafting and sending.

1. `account-targeting` — CRM-first, public/LinkedIn research → target accounts
2. `contact-targeting` — drill to individual contacts matching the buyer role
3. `prospect-message-draft` — looped per contact, content approval only
4. `campaign-setup` — create/reuse the episode's Segment + Journey, add contacts
5. `campaign-send` — looped per contact, explicit live send confirmation required
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Why This Exists

A grounded episode brief is only valuable if it turns into real outreach to
real people — and that outreach has to be attributable, not a pile of personal
emails David can't tie back to a campaign later. This workflow exists to
guarantee: real accounts and contacts (never invented), content held to the
same quality bar as `harper-email`, and a send path that is CRM-native by
design so response tracking actually works.

**Send path — read before touching this workflow:** Outbound send goes through
a Dynamics **Customer Insights – Journeys** Segment/Journey, never through
Outlook or Superhuman. This is deliberate, not a placeholder to be
"reconciled" later — see `skills/campaign-setup/SKILL.md` and
`skills/campaign-send/SKILL.md` for the full rationale. David's personal
email drafting via `harper-email` is untouched and still used for everything
else.

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Dynamics CRM | Existing accounts/contacts, relationship history, Segment/Journey structures | Chrome/Playwright browser automation — no API/MCP connector exists |
| Clay | Personal relationship context on contacts | `mcp__clay__*` / `mcp__claude_ai_Clay_custom__*` |
| LinkedIn | Contact discovery, title tie-breaker/authority (see `memory/feedback_linkedin_over_crm_titles.md`) | Playwright browser automation |
| `identity/VOICE.md` | Baseline voice/formatting conventions for message content | Read directly, via `prospect-message-draft` |

### Compliance Note

`account-targeting` runs a mandatory pre-check before any research: confirm
the data being touched is Improving's own commercial CRM data, not a
client's confidential material. This workflow halts rather than guesses if
that's ambiguous.

### Output

- A target account/contact list document (from steps 1-2)
- A live Customer Insights – Journeys Segment/Journey with members and any
  sent emails (from steps 4-5), all traceable back to the originating episode
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## ROLLBACK PROTOCOL

This workflow writes to live CRM records starting at step 4
(`campaign-setup`) and fires irreversible sends at step 5 (`campaign-send`).
There is no automated rollback for a send that has already gone out — email
delivery cannot be undone. If a run needs to be aborted mid-flight:

- **Before step 4:** No CRM writes have occurred. Simply set `state.yaml`
  `status: aborted`. Nothing to undo.
- **After step 4, before any sends in step 5:** The Segment/Journey exist in
  Draft/unsent state. It is safe to leave them as-is (they'll be reused on
  resume) or to manually delete them in Dynamics if the campaign is being
  scrapped entirely — this is a controller decision, not automated.
- **Mid-way through step 5's per-contact loop:** Contacts already confirmed
  and sent to CANNOT be un-sent. Set `state.yaml` `status: aborted` with
  `current-step: step-05` — on resume, the per-contact confirmation loop
  re-presents only the contacts not yet marked sent (tracked in
  `accumulated-context.contacts_sent`), so a resume never re-sends to
  someone already reached.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.

2. If `status: in-progress`:
   - You are resuming a previous run. Do NOT start over.
   - Read `current-step` to find where to continue.
   - Load `accumulated-context` — data already gathered. Do not re-pull it.
   - If resuming into step 05, load `accumulated-context.contacts_sent` and
     skip confirmation for any contact already marked sent — never re-send.
   - Check that step's frontmatter: if `status: in-progress`, re-execute it; if
     `status: not-started`, begin it fresh.
   - Notify the controller: "[Harper]: Resuming audience-target-outreach from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01`.
   - If the input audience profile comes from a prior `episode-campaign-brief` run,
     load it into `accumulated-context.audience_profile` and
     `accumulated-context.episode_metadata` now.
   - Begin at step-01.

4. If `status: aborted`:
   - Surface to controller: "[Harper]: audience-target-outreach was previously aborted at
     [current-step]. Resume or start fresh?" If aborted mid-send (step-05),
     explicitly state how many contacts were already sent to and how many remain.
   - Wait for instruction.

## EXECUTION

Read fully and follow: `steps/step-01-account-targeting.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
