# Call Prep: GE HealthCare - Twice Weekly Internal Check-In (Internal Team Sync)

**2:00-2:30 PM CDT (30 min) | Microsoft Teams (link on the invite) | Ongoing engagement - repeat meeting; internal Improving-side sync. You joined the account 2026-09-11 as Tim Rayburn's replacement.**

**Calibration note:** This is an internal Improving team sync (classification: internal-review / existing engagement), not a client-facing call - every attendee is an Improving colleague. Do not pitch, do not treat this as a sales or demo room, and do not carry client-facing problems into the Wednesday GE HealthCare sync without first raising them here. This is the room where internal friction, access gaps, and capacity conflicts are supposed to surface. Nothing you say here needs to win work; it needs to keep the team unblocked and aligned ahead of the client cadence.

## Who They Are

| | |
|---|---|
| **Company** | GE HealthCare (contracting entity: GE Precision Healthcare, LLC) |
| **Division** | Imaging - Core Routing Validation workstream |
| **Industry** | Medical technology / medical imaging (MRI, CT, modalities) |
| **HQ** | Chicago, IL (this engagement's GEHC site: WSO, 3000 N Grandview) |
| **Founded** | Spun out of GE in January 2023 |
| **Size** | Large-cap public medtech (not researched in depth this run - repeat meeting) |
| **Known tech stack** | GEHC Clinical Data Hub (primary data source); AWS (SQS, Fargate); small language model (Qwen 3B, swappable to Bedrock/Ollama via an OpenAI-compatible interface); MCP destination adapters (Iconmetrics, Milview); SQLite/Dynamo registry; DICOM / DICOMweb; GEHC-approved Git; PRISMA browser; GlobalProtect VPN |
| **Email domain** | gehealthcare.com (external tenant) |
| **Improving side** | Improving Chicago is the contracting entity; SOW #22633 / PSBC02846 |

**Disambiguation note:** "GEHC" = GE HealthCare - specifically the Imaging division of GE Precision Healthcare, LLC, contracted through Improving Chicago. Not "GE" at large, not GE Aerospace, not GE Vernova. The PoC is scoped to one machine type within Imaging.

## Company Overview

**Depth: brief refresh (repeat meeting).** Nothing found in this run indicates a material change at GE HealthCare as a company since the engagement began. All relevant movement is inside the engagement itself.

- **Engagement arc:** ~12-week PoV, $27K fixed fee (list $54K, halved); invoiced Oct 2026 $9,000 / Nov 2026 $18,000; term ends 31 Dec 2026. Phase gates: D1 Discover (8/31) -> D2 Design (9/7) -> D3 Develop (9/14-10/5) -> D4 Deploy (~10/12; the kickoff deck also renders 11/9-11/23) -> PoV completes ~12/18.
- **What's new since the last internal check-in (10/14):** The GEHC AI Router PoC **mid-point demo ran Thursday 2026-10-08, 9:30 AM CDT** (invite: Justin Holder, Sujatha Ramkumar, Braunstein, Pezet, Vlad). **Its outcomes are still unlogged** - no transcript, no note in the vault or memory. This is the single biggest internal gap heading into Monday.
- **Architecture evolution (client-facing):** 09-17 weekly sync -> 09-18 architecture review (Vlad walked the SQS -> metadata-only consumer -> Qwen 3B SLM + MCP-backed registry design; Mike Braunstein pressed on endpoint compatibility / destination discovery) -> 09-24 internal "Review for demo" (Vlad's new AI-dispatcher + MCP-adapter proposal; David pushed to simplify - drop the separate dispatcher MCP, make the event self-contained, relabel Ollama as "inference") -> 10-08 mid-point demo.
- **CRM history:** An active Dynamics opportunity, "GE Healthcare - AI PoC", exists under the GE Healthcare account. Its stage, value, and owner were not read this run.
- **Competitive/market pressure:** None identified. The engagement is budget-constrained on GEHC's side, not competitive.

Sources: calendar (M365) + prior prep (`meetings/2026-09-16-gehc-ai-routing-prep.md`) + Plaud notes (09-14, 09-17, 09-18, 09-24) + morning briefings (10-07, 10-08).

## Who They Is

The invite's attendees are all Improving - this is the internal account team, not GEHC. Bios below are built from first-party sources only (Plaud notes, the internal hand-off doc, prior prep); no Clay or LinkedIn research was available this run.

**Lisa Barnes - Delivery Lead / PM, Improving (organizer).** Organizes this twice-weekly internal check-in and is David's primary internal channel on GEHC. She owns David's onboarding: reaching out to Justin Holder for repo/VPN access and submitting his network access request through GE's SAP FieldGlass process (only she can submit it).

**Vladimir "Vlad" Avila - AI Engineer, Improving (near-shore / Mexico delivery).** The single engineer building the PoC (~40 hrs/week). Vlad's own 09-14 status: the LLM routing engine and the MCP for dynamic destination routing are built, deployed on AWS with infrastructure-as-code; next up is mocking the production destination service and prompt-engineering refinement. Lisa Kimbrel's read: "super responsive," "detailed in his written updates," and he "has mastered the use of AI to communicate effectively" in writing - **but verbally it's not as good.** His unblocked-ness is the client PM's (Justin Holder's) stated top priority.

**Tim Rayburn - Improving.** Former Technical Lead / AI Architect on GEHC; **David replaced him** (Tim stepped aside 2026-09-08, pulled onto NRG training and McKesson). Still on every GEHC invite and on this one. No evidence a formal Tim -> David handoff ever happened.

**Lisa Kimbrel - Account Manager / Supplier PM, Improving.** The SOW's named Supplier PM and the commercial owner. She recruited David onto the account (1:1 on 2026-09-11), framing it as two jobs: technical oversight / code review of a near-shore engineer, and **US-based executive presence to demo Vlad's work to larger GE audiences** ("they'll probably get the directors and VPs... involved in the larger demos"). She flagged that Vlad needs "a little bit of babysitting" and "a few code reviews."

**"Read on them":** This is a small, budget-constrained, fixed-price engagement where the client's PM cares most about Vlad staying unblocked and momentum holding - so the room rewards "what's blocking us and what's the plan," not architectural debate. Your value to this team is (1) clearing Vlad's blockers and access, (2) owning the two bigger client demos, and (3) being the US-based, client-facing voice Vlad isn't.

## Common Connections

**Unavailable for this run.** No LinkedIn profile URLs were surfaced, and Clay (relationship intelligence) failed to connect this session - mutual connections could not be pulled. Treat as blank, not zero.

## Reason for the Call

**Meeting classification: internal-review / existing engagement (recurring cadence). Repeat meeting - first-touch depth not applicable.**

This is the standing internal Improving-side check-in on the GE HealthCare AI-Routing engagement, run twice weekly by Lisa Barnes. Per the invite body itself, Lisa set these up to "discuss plans, progress, internal issues, etc." - it is the team's alignment roundtable, not a client or sales meeting. The Monday 2026-10-19 instance sits the day before the client's Tuesday technical deeper dive (Oct 20, 11:00-12:00) and two days before the Wednesday weekly sync (Oct 21, 10:30-11:00) - so it is the last internal window to get aligned before facing GEHC.

Evidence cited:

| Source | Evidence |
|---|---|
| **Calendar invite (M365)** | "GEHC Twice Weekly Internal Check-In," organizer lisa.barnes@improving.com, Mon 2026-10-19 14:00-14:30 Central, Teams. Attendees: Lisa Barnes, Vladimir Avila, Tim Rayburn, Lisa Kimbrel, David O'Hara. Body: *"Need to adjust the time of our Monday meeting going forward. Please let me know of major conflicts... internal alignment meetings to discuss plans, progress, internal issues, etc."* |
| **Calendar (M365)** | Recurring GEHC client cadence: "GEHC Improving - AI Routing technical deeper dive (weekly)," Tue 2026-10-20 11:00-12:00 (organizer justin.holder@gehealthcare.com); "GEHC Improving - AI Routing weekly sync," Wed 2026-10-21 10:30-11:00 (a duplicate invite "(2)" also exists on the calendar). |
| **Prior prep sheet** | `meetings/2026-09-16-gehc-ai-routing-prep.md` - same internal check-in, characterized as the informal roundtable where the team gets on the same page before facing GEHC. |
| **Plaud note 09-14** | "GEHC AI Routing for DICOM Images - Project Status and Team Intro" - organizer Lisa Barnes (this same check-in); Vlad's status; David's intro; the SAP FieldGlass access workstream. |
| **Email (M365)** | Justin Holder, "welcome to the party" / "RE: welcome to the party," 2026-09-16/17: *"GEHC is a bureaucracy and quite a few steps end up being serial and with some delays for internal systems to synch up."* Plus "FW: globalprotect vpn instructions," "FW: prisma browser instructions," "FW: git access" (all 2026-09-21) - David's GEHC access was being provisioned. |
| **Memory** | `memory/personal/quarterly-objectives.md` (2026-10-09): *"GEHC AI Router POC mid-point demo ran Oct 8 on a ~12-week engagement; outcomes still uncaptured."* `reviews/weekly/2026-W41.md`: "GEHC AI Router POC mid-point was Oct 8 - outcomes still unlogged." |

**do_not_assume list:**

- **Do not treat this as a client meeting.** Every attendee is Improving. This is where internal issues go - not into the Wednesday GEHC sync.
- **Do not assume the mid-point demo went well (or badly).** It ran Oct 8; no outcome is recorded anywhere in the system. Ask, don't infer.
- **Do not assume the two open client questions were settled** (self-tuning / contextual-memory routing; DICOM destination fan-out count). Both were open as of 09-18; status unknown.
- **Do not assume access is fully granted.** VPN / Git / PRISMA emails went out 09-21, but whether David can actually get into the repo and code was not confirmed this run.
- **Do not assume the meeting time is fixed.** The invite body says the Monday time is being adjusted and asks for conflicts, and the event still shows as tentative.
- **Do not volunteer for more than ~5 hrs/week** without a conversation with Lisa Barnes and Lisa Kimbrel first - October carries a boot camp, Alberta Blue Cross, and travel.

## Suggested Talking Points / Questions

Pick a few - this is a 30-minute roundtable, not a status readout.

1. **The mid-point demo debrief.** *"Let's capture the Oct 8 mid-point demo while it's fresh - what did GEHC actually say about the back half, and what did they push on?"* (Nothing is logged; this is the top gap.)
2. **Vlad's blocker.** *"Vlad - what's the one thing blocking you this week that I can actually help clear?"* (Mirrors the client PM's stated priority; earns credibility.)
3. **Access status.** *"Lisa - where did the repo / VPN / PRISMA access land? I want to be reading Vlad's code, not just hearing about it."* (FieldGlass request was pending as of 09-14; access emails went out 09-21.)
4. **The two open client questions.** *"Were the self-tuning / contextual-memory question and the DICOM destination fan-out count ever settled after the 09-18 review? If not, who owns them before Tuesday's deep dive?"*
5. **The demo plan and the calendar.** *"The week-6 demo is mine and it lands in the same window as the boot camp and Houston travel - let's put a date on it now and decide who covers what."*
6. **The Tim -> David handoff.** *"Is there a formal handoff from Tim I still owe, or am I fully in?"* (Tim stepped aside 09-08; no evidence a handoff discussion ever happened.)
7. **Scope discipline.** *"Anything creeping in that isn't in the SOW? This is fixed-price and undersized - I'd rather flag it here than eat it."*

## Landmines / Notes

- **Internal friction belongs in this room, not the client room.** Do not carry a scheduling, access, or capacity problem into the Wednesday GEHC sync without raising it here first.
- **Do not overstate your knowledge of the codebase.** As of the last evidence you have no confirmed repo / PRISMA access. Saying "I haven't been in the repo yet" reads as competent here, not weak.
- **Do not confuse "5 hours a week" with "small."** Fixed-price, $27K ceiling, 50%-discounted, 12/18 completion, with risk-register entries for timeline overrun and thin GEHC engineering bandwidth. Overrun is Improving's loss.
- **Do not put Vlad on the spot for an unrehearsed verbal walkthrough.** Written updates are excellent; verbal is weaker. In front of the broader GEHC audience, that is the gap you were recruited to cover - rehearse it internally first.
- **Do not let the Wintrust reference reach the client.** The weekly topics deck (`GEHC_Improving AI Routing Weekly Meeting Topics 0909.pptx`) carries a header reading "GOVERNANCE Wintrust DevSecOps Status Report - Week ending 9" - template residue from another client. If it is still in circulation, flag it privately to Lisa Barnes.
- **Do not schedule anything with Anthony Pezet after noon CT.** He is based in France; the internal hand-off doc calls this out explicitly.
- **Regulatory sensitivity is live.** The design contemplates a human-in-the-loop queue and an FDA-aligned audit ledger. Do not discuss routing output as if it runs autonomously in production.

## Open Questions Going In

- **Did the Oct 8 mid-point demo land well, and what did GEHC ask for in the back half?** No outcome is recorded anywhere in the system.
- **Is David's GEHC access (repo / VPN / PRISMA) actually granted?** Access emails went out 2026-09-21; whether the repo is reachable and code review is possible was not confirmed this run.
- **Were the two open client questions settled?** (1) Does the routing system self-tune over time - contextual memory vs. telemetry; (2) how many destinations typically receive a single DICOM file (which settles queue topology). Open as of the 09-18 review; status unknown.
- **Is Tim Rayburn still on the account at all, or fully out?** He remains on every invite; no formal handoff is on record.
- **What is the week-6 demo's actual date and audience?** Lisa Kimbrel said "about six weeks in" (~mid-October), and the client PM wants a broader midpoint demo "around week five or six." No exact date on record; it collides with the boot camp and Houston travel.
- **Is the Monday time actually moving?** The invite body says the time is being adjusted and asks for conflicts; the event still shows as tentative.
- **Timezone nuance:** the invite's timeZone label reads "Central Standard Time," but 2026-10-19 is still daylight time (DST ends 2026-11-01), so the real local time is **CDT (UTC-5)**. Verified against the Mac's local clock (CDT) on 2026-10-16.
- **Which build of the timeline is live?** The kickoff deck renders D4 as both "Wks 7-8 - 10/12" and "11/9-11/23"; the week-6 demo commitment hangs off it.
- **CRM gap:** an active Dynamics opportunity ("GE Healthcare - AI PoC") is known to exist, but its stage, value, and owner were not read this run.
- **Account-context gap:** there is no GEHC entry in `projects/improving-accounts-overview.md` and no `accounts/GEHC/` folder - the account has no standing plan document.
