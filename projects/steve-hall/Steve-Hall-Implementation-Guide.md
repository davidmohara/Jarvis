# Steve Hall — IES Implementation Guide

Companion document to the **AI Implementation Project Plan** (client-facing, Feb 2026) and the **Internal Kickoff Guide** (team playbook, Feb 2026). This guide catalogs all abilities Steve Hall has requested, maps them against both documents and the current IES platform, identifies gaps, and inventories every data source needed.

## Client Profile

| Field | Detail |
|-------|--------|
| **Client** | Steve Hall · stevehall11565@gmail.com · cell 703-626-9775 |
| **Account Owner** | Derek Nwamadi · derek.nwamadi@improving.com · M. 214.385.1603 |
| **Principal Technologist** | Bud Marrical |
| **Executive Sponsor** | David O'Hara (value-add, no bill) |
| **Engagement Type** | T&M · Phase 1 SOW with NTE cap |
| **CRM** | Dynamics — AI Implementation Plan · Est. Close 03/06/2026 |
| **Primary Ecosystem** | Gmail (all accounts) + iCloud Calendar (primary) + Google Calendar (invite mirror) + Google Drive + iCloud Contacts |
| **Runtime** | Claude Cowork (local) + Google Workspace MCP Connectors |
| **Businesses** | Denver Bentley, Honda of Paris, auto finance company, family foundation, Generosity Ventures |
| **EA** | Shelley — business & foundation; Friday weekly recaps |
| **PA** | Emberleigh (E-M-B-E-R-L-E-I-G-H) — home & personal; weekly email lists with tasks, blockers, updates |
| **Relationship** | YPO GOLD member, wine club at 55 Seventy (Preston Center), deeply relational, signs "with care" |
| **Phase 1 Timeline** | 3-4 weeks |
| **Kickoff Date** | 2026-03-10 (whiteboard + Plaud transcript captured) |

---

## Kickoff Meeting — March 10, 2026

**Source**: Whiteboard photos (Bud) + Plaud transcript (78m 36s)
**Participants**: O'Hara, Steve Hall, Bud Marrical, Derek Nwamadi (partial — account owner)

### Steve's Current Dataverse (Whiteboard — Black Text)

**AI Tools in Use:**
- Gemini (image generation, drafting, tone checks)
- ChatGPT (drafting, tone checks)
- Claude (Sonnet 4.6 Pro — heavy use for stewardship content)
- Whisper (voice capture — planned)
- Goal state: → Jarvis with 6 Agents

**Init Plan:**
- 10-min quick start
- 30-min deep dive with strategic materials

**Google / MBP Ecosystem:**
- Email → Gmail (all accounts)
- Calendar → iCloud (primary) / Google Calendar (invite mirror only)
- Data → Google Drive (will host the IES subsystem)
- Todo → Physical handwritten journal + calendar time blocks (no digital app)
- Contacts → iCloud (no Google Contacts)
- CRM → None personal; business CRMs exist per company (reports only via email)
- Video → Zoom (~50%) + Teams (~50%), both with Plaud
- Journal → Penzu (~277 pages, 10-12 entries/page; themes: Proverbs, "witnessing vs. judging," daily reflection)
- Branding → None currently
- Dropbox → FX / Datarooms (deal docs, financials)
- Content Capture → needed

**Home/Personal:**
- Gmail [Todos, Follow Ups]
- PA: Emberleigh — weekly email lists (tasks, blockers, updates) → route to home folder
- EA: Shelley — business & foundation work; Friday weekly recaps → route to business/foundation folder

**Active Investments/Board:**
- CRM Reports → Analysis only (Steve does NOT store underlying data; operates at speedometer/check-engine-light level)
  - Monthly Reviews (auto finance: tomorrow Mar 11; Bentley: Friday Mar 14)
- Sales Reports
- P&L
- Inventory Analysis (aging lists from Bentley)
- Marketing (Later)
- Adversarial Positioning / Challenge Agent

**Foundation (3 activities):**
- Evaluate leaders' capacity to scale
- Fund Stagen ILP + pilot investments ($25K-$100K)
- Produce stewardship content for partners (Mission, Vision, Analysis of Investment, Content Curation)
- Partner orgs: Conscious Capitalism (transitioning off as exec chair), Just Capital, CECP

**Convening Events:**
- Logistics → Format, Attendees, Agenda
- Comms (invites, RSVPs)
- Topic Gen from Content (journals, events)
  - Logs
- Types: Wisdom dinners, Jeffersonian dinners, one-day offsites, two-day retreats, annual CEO Conclave

**Whiteboard To-Do Items (Red):**
- Todo system needs solving — physical journal + time blocks won't integrate; Steve acknowledged "my to-do list is not going to be user-friendly for this"
- iCloud Contacts needs attention — primary contact store but no CRM linkage

### Key Decisions Made

1. **Calendar sources**: iCloud and Gmail (NOT Generosity Ventures email)
2. **Subsystem host**: Google Drive (cloud sync, multi-device)
3. **No data storage**: Steve does not store reports/underlying data; analysis only — "The alcoholic doesn't need to go to the bar"
4. **No DMS integration**: Data received via email; Steve explicitly avoids tactical systems
5. **Single unified system**: All investment contacts, foundation data, convening events in one personal system — no segregation
6. **Central to-do with delegation**: System's to-do list is source of truth; delegations flow out to Shelley/Emberleigh
7. **Sender-based email routing**: Emberleigh → home; Shelley → business/foundation; with decision surfacing
8. **Privacy opt-out**: Claude Pro set up and privacy configured during meeting
9. **Claude Desktop**: Installed during meeting

### New Use Cases Identified (Not in Prior Plan)

| Ability | Description | Source |
|---------|-------------|--------|
| **Adversarial "Challenge Agent"** | Steelmanning Steve's investment theses and strategic hypotheses; attack/critique mode | Transcript |
| **Communication Coaching Agent** | Review scripts, meeting communication style; Steve wants to be "more curious, less prescriptive" | Transcript |
| **Whisper Voice Capture + Routing** | Post-event/post-call notes routed by context (Honda, Bentley, auto finance, convening) | Whiteboard + Transcript |
| **Convening Event Engine** | Topic generation from content/journals, logistics, invites, run-of-show, agendas | Whiteboard + Transcript |
| **Stewardship Website Rebrand** | Consolidate content from Gemini/ChatGPT/Claude into stewardship-focused site | Transcript |
| **Assistant Email Parsing** | Extract tasks/blockers/updates from Shelley and Emberleigh emails; sender-based routing | Transcript |
| **Cross-Model Content Export** | Pull stewardship content from Gemini/ChatGPT/Claude history for consolidation | Transcript |

### Action Items

**O'Hara / Bud:**
- Set up Plaud desktop for Zoom/Teams capture → route transcripts to common repository
- Configure brand standards for Steve's generated presentations/PDFs
- Catalog and consolidate stewardship content from Gemini, ChatGPT, Claude for website rebrand
- Configure content ingestion from journals/events → generate topic lists and draft communications for convenings
- Research Whisper integration (output location, ingestion pipeline, routing rules)
- Implement email parsing to extract tasks/blockers/updates from assistant emails
- Create sender-based routing (Emberleigh → home; Shelley → business/foundation) with decision surfacing
- Define and configure adversarial "strategy/challenge agent"

**Steve:**
- Determine approach for recording important phone calls (AirPods won't capture; hold phone for vibration mic)
- Provide brand standards, starter templates, logos
- Provide access/exports from Gemini, ChatGPT, Claude with stewardship content
- ~~Log into Claude Pro and opt out of training~~ ✓ Done during meeting
- ~~Install Claude desktop app~~ ✓ Done during meeting

### Key Quotes

> "If I tied into those systems, I would get sucked in." / "The alcoholic doesn't need to go to the bar." — on avoiding tactical depth

> "I need to see the speedometer to make sure I'm not going too fast too slow. There's a check engine light comes on... just something very high level that just says you may want to inquire about this." — on desired insights

> "I might be being too prescriptive. I want to be more curious." — on communication style with operators

> "It's helpful to lay it all out now because now I've got okay, understand where -- I don't know how I am going to get there, but I know where I am going." — on the journey

> "My to-do list is not going to be user-friendly for this. Like, I need to find a better to-do list version." — on his physical todo system (O'Hara redirected: let Jarvis handle it abstractly)

---

## Discovery Meeting Worksheet

Use this section to walk through Steve's requests and data sources during the discovery kickoff. Validate priorities, confirm access, and identify unknowns.

### Steve's Asks — Complete List

| # | Ability | Phase | Status |
|---|---------|-------|--------|
| 1 | Email Response Generation — AI drafts replies in Steve's voice, trained on sent mail corpus | Phase 1 | In Plan |
| 2 | To-Do Follow-Up — Track pending items across email/calendar, send reminders, flag overdue | Phase 1 | In Plan |
| 3 | Voice-to-Draft — Dictate thoughts via voice memo, AI produces polished first drafts | Phase 1 | In Plan |
| 4 | Calendar & Morning Briefing — Manage scheduling, deliver morning briefing by 6:00 AM | Phase 1 | In Plan |
| 5 | Email & Time Intelligence — Analyze communication patterns, response times, topic distribution | Phase 1 | In Plan |
| 6 | Foundation Content Drafting — White papers, leadership covenants, Stewardship Mandates in Steve's voice | Phase 1 | In Plan |
| 7 | Shadow Board Agent — AI acts as skeptical activist investor challenging Steve's growth plans | Phase 2 | In Plan |
| 8 | Financial Reconciliation — Compare acquisition target financials, spot inconsistencies | Phase 2 | In Plan |
| 9 | Market & Competitive Intel — Real-time automotive market shifts, interest rates, competitor moves | Phase 2 | In Plan |
| 10 | Sentiment & Regulatory Agent — Analyze earnings call transcripts for linguistic shifts quarter-over-quarter | Phase 2 | In Plan |
| 11 | Moat Builder (F&I Simulation) — Simulate AI buyer vs. dealership F&I to find breakdowns | Phase 2 | In Plan |
| 12 | Synthetic Negotiation — Multi-agent acquisition pitch practice (AI as buyer + AI as Steve) | Phase 2 | In Plan |
| 13 | Operator Coaching — AI coaching briefs for portfolio company operators, track commitments | Phase 2 | In Plan |
| 14 | Wisdom Dinner Automation — End-to-end event logistics: invites, RSVPs, dietary, seating, follow-ups | Phase 2 | In Plan |
| 15 | Renovation Management — Coordinate contractors, track deliverables, flag delays | Phase 2 | In Plan |
| 16 | Unified Data / "Second Brain" — Bridge Penzu, Dropbox, local docs, AI histories into one database | Phase 1 | **Not in Plan** |
| 17 | Voice-to-Brain Filing — Record a thought, auto-file into project-specific folders | Phase 1 | **Not in Plan** |
| 18 | Content Ghostwriter Agent — Trained on Steve's "Next Generation Capitalism" voice for LinkedIn, YPO | Phase 1-2 | **Not in Plan** |
| 19 | Podcast & Video Content — Regular stewardship/capitalism-focused audio and video production | Phase 2 | **Not in Plan** |
| 20 | Investment Performance Monitor — Weekly analysis of Honda of Paris, Bentley Denver, Bepensa Capital | Phase 2 | **Not in Plan** |
| 21 | Communication Tone Auditor — Audit sent emails for supportive vs. judgmental tone with operators | Phase 2 | **Not in Plan** |
| 22 | Time Allocation Monitor — Track time across Steve's three life goals, flag imbalance | Phase 2 | **Not in Plan** |
| 23 | Board Advisor & CEO Coach Tracker — Track pro-bono advisory time, tone, and impact | Phase 2 | **Not in Plan** |
| 24 | Closed-Loop Assistant To-Do — Track tasks assigned to Steve's two assistants, auto-update on completion | Phase 1 | **Not in Plan** |
| 25 | Travel Persona — Store aviation and hotel preferences, simplify complex trip planning | Phase 1-2 | **Not in Plan** |
| 26 | Deep Research Agent — Pre-meeting intelligence briefings on individuals and companies | Phase 2 | **Not in Plan** |
| 27 | Scout & Convenor Agent — Surface discussion topics from journals for dinners, retreats, CEO Conclave | Phase 2 | **Not in Plan** |

### Data Sources — Complete List

| Data Source | Proposed / Existing | Feeds Abilities | Feasibility |
|-------------|:-------------------:|-----------------|:-----------:|
| Gmail (stevehall11565@gmail.com + business accounts) | Existing | #1, #2, #4, #5, #21, #24 | Green |
| Google Calendar | Existing | #4, #5, #22 | Green |
| Google Drive / Docs | Existing | #3, #6, #16, #18 | Green |
| Google Contacts | Existing | #1, #4, #14 | Green |
| Sent Email Corpus (3-6 months) | Existing | #1, #18, #21 | Green |
| Penzu Journals | Existing | #16, #17, #27 | Yellow |
| Dropbox Files | Existing | #16 | Green |
| MacBook Local Documents | Existing | #16 | Green |
| Apple Calendar | Existing | #16, #22 | Yellow |
| Gemini Conversation History | Existing | #16 | Yellow |
| ChatGPT Conversation History | Existing | #16 | Yellow |
| Claude Conversation History | Existing | #16 | Yellow |
| Voice Recordings / Memos | Existing | #3, #17, #19 | Yellow |
| Existing Publications & White Papers | Existing | #6, #18 | Green |
| Foundation Mission Docs | Existing | #6, #18 | Green |
| Current Task Lists | Existing | #2, #24 | Yellow |
| Assistant Communication Channels | Existing | #24 | Green |
| Travel Preferences File | Proposed | #25 | Green |
| Event Invitee Lists | Existing | #14, #27 | Green |
| Event History & Dietary Preferences | Proposed | #14 | Green |
| Venue Information | Proposed | #14, #27 | Green |
| Dealership DMS — Denver Bentley | Existing | #7, #8, #11, #20 | Red |
| Dealership DMS — Honda of Paris | Existing | #7, #8, #11, #20 | Red |
| Auto Finance Company Platform | Existing | #9, #20 | Yellow |
| Bepensa Capital Reports | Existing | #7, #20 | Yellow |
| Board Decks & Financial Statements | Existing | #7, #8 | Yellow |
| Acquisition Target Financials | Proposed | #8 | Yellow |
| Weekly Portfolio Performance Reports | Existing | #7, #20 | Yellow |
| F&I Product Data, Pricing, Deal History | Existing | #11 | Red |
| KPI Data (Portfolio Companies) | Existing | #13, #20 | Yellow |
| SEC EDGAR (Earnings Call Transcripts) | Proposed | #10 | Green |
| Automotive Market Data (NADA, KBB, Cox) | Proposed | #9, #20 | Yellow |
| Financial News (Bloomberg, Reuters) | Proposed | #9, #10 | Yellow |
| Interest Rate & Economic Data | Proposed | #9, #20 | Green |
| Competitor Data (Sonic, Lithia) | Proposed | #9, #10 | Yellow |
| Industry Benchmarks (NADA Guides) | Proposed | #7, #20 | Yellow |
| LinkedIn (Contact Intelligence) | Proposed | #26 | Yellow |
| Talk / Speech Transcripts | Existing | #18, #19 | Yellow |
| Organization Materials (Conscious Capitalism, CECP, Onyx, JUST Capital, YPO) | Existing | #18 | Yellow |
| Foundation Donor Management / CRM | Existing | #6 | Yellow |
| Content Publishing Platform | Proposed | #6, #18, #19 | Yellow |
| Contractor Contacts & Timeline | Existing | #15 | Yellow |
| Operator Email Threads & Meeting Notes | Existing | #13, #20, #23 | Green |
| Project Folder Taxonomy | Proposed | #17 | Green |
| Voice Capture App (Whisper / AudioPen) | Proposed | #3, #17 | Yellow |
| Steve's Brand Voice Corpus | Proposed | #1, #18, #21 | Green |

---

## Part 1: Complete Catalog of Steve Hall's Desired Abilities

### Source Emails

| Date | Subject | Key Content |
|------|---------|-------------|
| **Feb 8** | Re: Keeli in town | Steve asks David for AI consultant recommendation; "top 3 priority for 2026 is to learn how to better use AI (especially agents) to help me manage the operations of businesses I am investing in" |
| **Feb 11** | call on AI | Steve's initial wish list — 12 specific use cases |
| **Feb 17** | Re: call on AI | Steve responds to David's IES proposal — confirms excitement, mentions "unified command center," wants emails/journals/Google Docs/hard drive/dealership data in one cohesive database |
| **Feb 18** | Re: Improving MSA for review | Steve reviews MSA, requests phased approach starting with Phase 1 baseline IES (emails, documents, journals), asks for NTE cap and hourly rate clarity |
| **Mar 2** | more thoughts on the AI consultant agreement | Steve's expanded "second brain" vision — 12 additional abilities not in prior emails |

---

### 1.1 Abilities IN the Current Implementation Plan

#### Phase 1 — IES Foundation & Core Use Cases (SOW Scope, 3-4 Weeks)

| # | Ability | Description | Data Required | Source |
|---|---------|-------------|---------------|--------|
| 1 | **Email Response Generation** | AI drafts email responses in Steve's voice and tone. Learns from sent mail corpus over time. | Gmail accounts, sent mail corpus (3-6 months) for voice training | Feb 11 |
| 2 | **To-Do Follow-Up** | Track pending items across email and calendar, send reminders, flag overdue tasks. Replace manual list management. | Current task lists, email commitments, calendar actions | Feb 11 |
| 3 | **Voice-to-Draft** | Dictate strategy thoughts via voice memo; AI produces polished first draft of white papers, memos, and Stewardship Mandates. | Voice recording input, document templates, existing publications | Feb 11 |
| 4 | **Calendar & Morning Briefing** | Manage scheduling conflicts, meeting prep. Morning briefing with day's priorities delivered by 6:00 AM. | Google Calendar, contacts, meeting context | Plan |
| 5 | **Email & Time Intelligence** | Analyze communication patterns: who Steve engages with most, response times, topic distribution. Time allocation vs. stated priorities. | 6-12 months Gmail history, calendar data, stated priority list | Feb 11 |
| 6 | **Foundation Content Drafting** | Draft white papers, leadership covenants, and Stewardship Mandates in Steve's voice using existing publications as training data. | Existing publications, brand voice samples, foundation mission docs | Feb 11 |

#### Phase 2 — Advanced Agents & Domain Integrations (Future SOW, TBD)

**Financial Intelligence**

| # | Ability | Description | Data Required | Source |
|---|---------|-------------|---------------|--------|
| 7 | **Shadow Board Agent** | Feed AI board decks, financial statements, strategic briefs from automotive holdings. AI acts as skeptical activist investor: "Identify the three weakest assumptions in this growth plan." | Board decks, financials, strategic plans, DMS data | Feb 11 |
| 8 | **Financial Reconciliation** | Compare disparate financial reports from acquisition targets. Spot inconsistencies in "underperforming but mature" businesses that standard accounting misses. | Target financials, benchmarks, industry comps | Feb 11 |

**Market & Competitive Intelligence**

| # | Ability | Description | Data Required | Source |
|---|---------|-------------|---------------|--------|
| 9 | **Market & Competitive Intel** | Track real-time shifts in automotive market, interest rate changes affecting auto finance, competitor moves by Sonic and Lithia. | Market feeds, SEC filings, news APIs | Feb 11 |
| 10 | **Sentiment & Regulatory Agent** | Scrape and synthesize quarterly earnings calls for "linguistic shifts" — how CEOs talk about inventory levels or AI integration vs. previous quarters. | SEC EDGAR transcripts, NLP models, historical data | Feb 11 |

**Strategic Simulation**

| # | Ability | Description | Data Required | Source |
|---|---------|-------------|---------------|--------|
| 11 | **Moat Builder (F&I Simulation)** | Simulate aggressive AI buyer negotiating against dealership F&I processes. Identify breakdowns before real AI buyers arrive. | F&I products, negotiation scripts, pricing, deal history | Feb 11 |
| 12 | **Synthetic Negotiation** | Multi-agent simulation: one AI as buyer, another as Steve, to practice acquisition pitches — buying and selling companies. | Deal terms, valuations, comps, Steve's negotiation style | Feb 11 |

**Operational Automation**

| # | Ability | Description | Data Required | Source |
|---|---------|-------------|---------------|--------|
| 13 | **Operator Coaching** | AI prepares coaching briefs for portfolio company operators. Tracks commitments, surfaces patterns, suggests talking points. | Operator email threads, meeting notes, KPI data | Feb 11 |
| 14 | **Wisdom Dinner Automation** | End-to-end event logistics: invitations, RSVPs, dietary preferences, seating, follow-ups. | Google Contacts, venue info, event history | Feb 11 |
| 15 | **Renovation Management** | Coordinate multi-contractor communication, track deliverables, flag delays, consolidate updates. | Contractor contacts, project timeline, comms | Feb 11 |

**Custom Integrations Required (from Implementation Plan)**
- Dealer Management System (DMS): MCP server or data import for operational data
- Financial document pipeline: PDF/Excel parsing, OCR, table extraction
- SEC EDGAR API: earnings call transcripts and financial filings
- Market data feeds: automotive industry data (Cox Automotive, NADA, KBB)
- Financial news aggregation: Bloomberg, Reuters, or alternatives
- Contact enrichment: LinkedIn and company data integration
- Event management: Resy, Evite, or custom workflow for Wisdom Dinners

---

### 1.2 Abilities NOT IN the Current Plan

Steve's Mar 2, 2026 email to Derek ("more thoughts on the AI consultant agreement") introduced significant new abilities. His Feb 17 email also hinted at the "unified command center" concept. None of these are reflected in either the Implementation Plan or the Internal Kickoff Guide.

**Unified Data & Knowledge Layer**

| # | Ability | Description | Data Required | Suggested Phase |
|---|---------|-------------|---------------|-----------------|
| 16 | **Unified Data Environment / "Second Brain"** | Bridge Penzu journals, Dropbox files, MacBook local docs, and full history across Gemini, ChatGPT, and Claude into one accessible database. Real-time sync with emails and Apple Calendar so AI understands full professional and personal context. Steve called this his **"primary goal."** | Penzu journals, Dropbox files, local MacBook docs, Gemini history, ChatGPT history, Claude history, Gmail, Apple Calendar | **Phase 1** |
| 17 | **Voice-to-Brain Filing** | Record a 2-minute thought (via Whisper or AudioPen), auto-file into project-specific folders — e.g., "Stewardship" or "Investment" folder. | Voice input, project folder taxonomy | **Phase 1** |

**Content & Voice**

| # | Ability | Description | Data Required | Suggested Phase |
|---|---------|-------------|---------------|-----------------|
| 18 | **Content Ghostwriter Agent** | Trained on Steve's specific "Next Generation Capitalism" voice. Turn rough talk transcripts into polished LinkedIn posts or YPO briefings. Synthesize historical thoughts for Conscious Capitalism, CECP, Onyx, JUST Capital, YPO, and others. | Existing publications, talk transcripts, brand voice corpus, org materials | **Phase 1-2** |
| 19 | **Podcast & Video Content** | Regularly produce podcasts and video content focused on stewardship and next-generation capitalism. | Audio/video pipeline, content calendar | **Phase 2** |

**Portfolio & Advisory Oversight**

| # | Ability | Description | Data Required | Suggested Phase |
|---|---------|-------------|---------------|-----------------|
| 20 | **Investment Performance Monitor** | Analyze weekly updates and performance reports from Honda of Paris, Bentley Denver, and Bepensa Capital. Flag trends. Suggest high-leverage questions for Steve as strategic advisor. Avoid prescriptive — supportive and curious. | Weekly portfolio reports, DMS data, email updates | **Phase 2** |
| 21 | **Communication Tone Auditor** | Audit sent emails and calendar to check if Steve's tone is supportive and curious vs. judgmental or overly controlling — especially with portfolio company operators. | Gmail sent corpus (NLP analysis) | **Phase 2** |
| 22 | **Time Allocation Monitor (Multi-Goal)** | Monitor time across Steve's three life goals: (1) active investor in automotive, (2) pro-bono board advisor & CEO coach, (3) scout & convenor. Ensure not over-investing in one at expense of others. | Gmail + Calendar (analytics across three goal categories) | **Phase 2** |
| 23 | **Board Advisor & CEO Coach Tracker** | Track pro-bono advisory work — time spent, interaction tone, impact. Similar to automotive goal but for nonprofit board roles. | Calendar + Email | **Phase 2** |

**Administrative & Lifestyle**

| # | Ability | Description | Data Required | Suggested Phase |
|---|---------|-------------|---------------|-----------------|
| 24 | **Closed-Loop Assistant To-Do System** | Track tasks assigned to Steve's two assistants. AI auto-updates Steve when answers are provided. Eliminates manual follow-up on open items. | Assistant email/messaging channels | **Phase 1** |
| 25 | **Travel Persona** | Store all preferences for private aviation and luxury hotels. Make planning complex trips seamless. | Curated preference file | **Phase 1-2** |
| 26 | **Deep Research Agent** | Research individuals and companies before meetings. Pre-meeting intelligence briefings. | LinkedIn, web search, company databases | **Phase 2** |
| 27 | **Scout & Convenor Agent** | Suggest deep, relevant discussion topics from Steve's journals for Jeffersonian dinners, retreats, and the annual CEO Conclave. Scout unique venues for high-trust gatherings. | Journals, venue data, web search | **Phase 2** |

### Ability Count Summary

| Status | Count | Details |
|--------|-------|---------|
| In Implementation Plan — Phase 1 | 6 | #1-#6 |
| In Implementation Plan — Phase 2 | 9 | #7-#15 |
| **Not in Plan** (from Mar 2 email) | **12** | #16-#27 |
| **Total desired abilities** | **27** | 44% of requests came after plan was written |

---

## Part 2: Complete Data Source Inventory

### 2.1 Phase 1 Data Sources (Google Workspace + Personal)

| Data Source | Type | Feeds Abilities | Integration Path | Feasibility |
|-------------|------|-----------------|------------------|-------------|
| **Gmail** (stevehall11565@gmail.com + business accounts) | Email | #1, #2, #4, #5, #21, #24 | Google Workspace MCP connector | Green |
| **Google Calendar** | Calendar | #4, #5, #22 | Google Workspace MCP connector | Green |
| **Google Drive / Docs** | Documents | #3, #6, #16, #18 | Google Workspace MCP connector | Green |
| **Google Contacts** | Contacts | #1, #4, #14 | Google People API / MCP | Green |
| **Sent Email Corpus** (3-6 months) | Training | #1, #18, #21 | Gmail API (read-only) | Green |
| **Penzu Journals** | Journals | #16, #17, #27 | Penzu export or API — **needs discovery** | Yellow |
| **Dropbox Files** | Documents | #16 | Dropbox MCP connector | Green |
| **MacBook Local Documents** | Documents | #16 | Local filesystem access | Green |
| **Apple Calendar** | Calendar | #16, #22 | CalDAV / local sync | Yellow |
| **Gemini Conversation History** | AI History | #16 | Google Takeout export | Yellow (one-time) |
| **ChatGPT Conversation History** | AI History | #16 | OpenAI data export | Yellow (one-time) |
| **Claude Conversation History** | AI History | #16 | Anthropic data export | Yellow (one-time) |
| **Voice Recordings / Memos** | Audio | #3, #17, #19 | Whisper API / AudioPen | Yellow |
| **Existing Publications & White Papers** | Content | #6, #18 | Google Drive / local files | Green |
| **Foundation Mission Docs** | Content | #6, #18 | Google Drive | Green |
| **Current Task Lists** | Tasks | #2, #24 | Manual import / app API — **needs discovery** | Yellow |
| **Assistant Communication Channels** | Messaging | #24 | Gmail (shared threads) | Green |
| **Travel Preferences** | Personal | #25 | Curated preference file (to be created) | Green |

### 2.2 Phase 2 Data Sources (Business, Market, Domain)

| Data Source | Type | Feeds Abilities | Integration Path | Feasibility |
|-------------|------|-----------------|------------------|-------------|
| **Dealership DMS** (Denver Bentley) | Operational | #7, #8, #11, #20 | DMS API (R&R, CDK, Tekion — TBD) | **Red** — "dragons" per Bud |
| **Dealership DMS** (Honda of Paris) | Operational | #7, #8, #11, #20 | DMS API (TBD) | **Red** — "dragons" per Bud |
| **Auto Finance Company Platform** | Financial | #9, #20 | Custom / SaaS API (TBD) | Yellow |
| **Bepensa Capital Reports** | Financial | #7, #20 | Email attachments / portal | Yellow |
| **Board Decks & Financial Statements** | Financial | #7, #8 | PDF/Excel ingestion pipeline | Yellow |
| **Acquisition Target Financials** | Financial | #8 | Document ingestion (PDF, Excel) | Yellow |
| **Weekly Portfolio Performance Reports** | Financial | #7, #20 | Email parsing / shared drive | Yellow |
| **F&I Product Data, Pricing, Deal History** | Operational | #11 | DMS integration | **Red** |
| **KPI Data** (Portfolio Companies) | Performance | #13, #20 | Reports / spreadsheets | Yellow |
| **SEC EDGAR** (Earnings Call Transcripts) | Regulatory | #10 | SEC EDGAR API (free, no auth) | Green |
| **Automotive Market Data** (NADA, KBB, Cox) | Market | #9, #20 | Data feed subscriptions | Yellow |
| **Financial News** (Bloomberg, Reuters) | Market | #9, #10 | News aggregation API | Yellow |
| **Interest Rate & Economic Data** | Market | #9, #20 | Federal Reserve API / financial APIs | Green |
| **Competitor Data** (Sonic, Lithia) | Competitive | #9, #10 | Web scraping / SEC filings | Yellow |
| **Industry Benchmarks** (NADA guides) | Market | #7, #20 | Data feed / manual import | Yellow |
| **LinkedIn** (Contact Intelligence) | Social | #26 | LinkedIn API / web enrichment | Yellow |
| **Talk / Speech Transcripts** | Content | #18, #19 | Audio transcription pipeline | Yellow |
| **Organization Materials** (Conscious Capitalism, CECP, Onyx, JUST Capital, YPO) | Content | #18 | Email / shared drives — manual import | Yellow |
| **Foundation Donor Management** | CRM | #6 | Foundation CRM (TBD) | Yellow |
| **Content Publishing Platform** | CMS | #6, #18, #19 | Platform API (TBD) | Yellow |
| **Event Invitee Lists** | Contacts | #14, #27 | Google Contacts / spreadsheet | Green |
| **Venue Information** | Events | #14, #27 | Web search / curated database | Green |
| **Event History & Dietary Preferences** | Events | #14 | Spreadsheet (to be created) | Green |
| **Contractor Contacts & Timeline** | Project | #15 | Email / project management app | Yellow |
| **Operator Email Threads & Meeting Notes** | Communication | #13, #20, #23 | Gmail parsing | Green |

### Data Source Summary

| Feasibility | Count | Notes |
|-------------|-------|-------|
| Green (ready / public API) | 16 | Google Workspace, SEC EDGAR, local files, curated files |
| Yellow (API exists, needs work) | 22 | Penzu, Dropbox, market feeds, financial docs, content platforms |
| Red (no API / manual only) | 3 | DMS integrations — "there will be dragons" |
| **Total unique data sources** | **41** | |

---

## Part 3: Current IES Abilities & Data Sources

The standard IES platform capabilities (David O'Hara / Improving deployment) that form the baseline.

### 3.1 IES Agent Abilities

#### Chief — Daily Operations & Execution
| Ability | Data Sources |
|---------|--------------|
| Morning Briefing | M365 Calendar, Task mgmt, Delegation tracker, Knowledge layer |
| Daily Review | Task mgmt, Calendar, Knowledge layer |
| Inbox Processing | M365 Outlook, Task mgmt |
| Calendar Prep | M365 Calendar, Contacts, Dynamics CRM, Knowledge layer, Clay |
| Weekly Planning | Task mgmt, Goal hierarchy, Calendar |

#### Shep — People & Delegation
| Ability | Data Sources |
|---------|--------------|
| Delegation Tracker | Task mgmt (built-in), OmniFocus |
| 1:1 Prep | Delegation tracker, Knowledge layer, Calendar, Clay |
| Follow-Up Nudges | Delegation tracker, OmniFocus |
| Team Health Pulse | Knowledge layer, Delegation tracker, Clay |
| Performance Review Prep | Knowledge layer, Delegation tracker |

#### Quinn — Strategy & Planning
| Ability | Data Sources |
|---------|--------------|
| Quarterly Rock Review | Goal hierarchy, Task mgmt |
| Goal Alignment Check | Calendar, Task mgmt, Goal hierarchy |
| Initiative Tracker | Task mgmt, Knowledge layer |
| Weekly Review Prep | OmniFocus, Delegation tracker, Goal hierarchy, Calendar |
| Strategy Builder | Knowledge layer, Goal hierarchy |

#### Chase — Revenue & Pipeline
| Ability | Data Sources |
|---------|--------------|
| Pipeline Review | Dynamics 365 CRM |
| Client Meeting Prep | Dynamics CRM, Clay, Calendar, M365 Email, Knowledge layer |
| Account Strategy | Dynamics CRM, Email, Knowledge layer, Clay |
| Win/Loss Analysis | Dynamics CRM, Knowledge layer |

#### Harper — Communication & Content
| Ability | Data Sources |
|---------|--------------|
| Presentation Builder | Knowledge layer, Local templates |
| Email Drafter | M365 Email, Clay, Knowledge layer |
| Talking Points | Knowledge layer, Calendar context |
| Content Calendar | Knowledge layer, Calendar |
| Podcast Prep | Knowledge layer, Web search |

#### Knox — Knowledge Management
| Ability | Data Sources |
|---------|--------------|
| Vault Search | Obsidian vault (MCP) |
| Vault Health Audit | Obsidian vault (MCP) |
| Photo Tagging | Apple Photos (local) |
| Plaud Transcript Extraction | Chrome (Plaud web), Obsidian |
| reMarkable Sync | reMarkable Cloud API, Obsidian |

#### Rigby — System Operations
| Ability | Data Sources |
|---------|--------------|
| Evolution Packaging & Deployment | Local filesystem, Git, IES web app |
| Package Installation | IES web app, Local config |
| Capability Status | Git, Local filesystem |
| Release Watch | Web (release notes) |

### 3.2 Current IES Data Sources

| Data Source | Category | Integration Method | Used By |
|-------------|----------|-------------------|---------|
| Microsoft 365 — Outlook Email | Communication | MCP (M365 connector) | Chief, Chase, Harper |
| Microsoft 365 — Calendar | Scheduling | MCP (M365 connector) | Chief, Quinn, Chase |
| Microsoft 365 — OneDrive/SharePoint | Documents | MCP (M365 connector) | Chief, Harper |
| Microsoft 365 — Teams Chat | Communication | MCP (M365 connector) | Chief |
| Dynamics 365 CRM | Pipeline/Accounts | Browser automation (V1) / Dataverse API (V2) | Chase |
| Obsidian Vault | Knowledge Base | MCP (obsidian-mcp-tools) | Knox, all agents |
| OmniFocus | Task Management | osascript (AppleScript) | Chief, Shep, Quinn |
| Clay | Relationship CRM | MCP (Clay connector) | Chief, Chase, Shep, Harper |
| Plaud Web | Meeting Transcripts | Browser automation (Chrome) | Knox, Chief |
| reMarkable Cloud | Handwritten Notes | reMarkable API | Knox |
| Apple Photos | Photo Library | Local filesystem / AppleScript | Knox |
| Local Filesystem | System State | Direct file access | All agents, Rigby |
| Git | Version Control | CLI | Rigby |
| IES Web App | Evolution Management | API | Rigby |
| Web Search | Research | MCP (web search) | Chase, Harper, all agents |
| Playwright (Browser) | Automation | MCP (Playwright) | Rigby, Knox |
| Mermaid Chart | Visualization | MCP (Mermaid connector) | Harper |
| Excel/Financial Files | Financial | Local file import | Quinn |

---

## Part 4: Gap Analysis

### 4.1 Plan Coverage

| | In Plan | Not in Plan | % Covered |
|---|---------|-------------|-----------|
| Steve's Phase 1 requests | 6 | 4 | 60% |
| Steve's Phase 2 requests | 9 | 8 | 53% |
| **Total** | **15** | **12** | **56%** |

**Missing from Phase 1**: Unified "Second Brain" (#16), Voice-to-Brain Filing (#17), Closed-Loop Assistant To-Do (#24), Travel Persona (#25)

**Missing from Phase 2**: Content Ghostwriter (#18), Podcast/Video (#19), Investment Monitor (#20), Tone Auditor (#21), Time Allocation Monitor (#22), Board Advisor Tracker (#23), Deep Research (#26), Scout & Convenor (#27)

### 4.2 Platform Adaptation: M365 → Google Workspace

| Current IES | Steve's IES | Impact |
|-------------|-------------|--------|
| M365 Outlook | Gmail / Google Workspace MCP | Connector swap — available |
| M365 Calendar | Google Calendar | Connector swap — available |
| OneDrive/SharePoint | Google Drive | Connector swap — available |
| Dynamics 365 CRM | None (no CRM for Steve) | Remove Chase pipeline features; repurpose for portfolio oversight |
| OmniFocus | Built-in to-do + assistant delegation system | New task architecture needed |
| Obsidian Vault | TBD — Steve doesn't use Obsidian | Knowledge layer needs alternative (Google Docs? Penzu? New vault?) |
| Clay | TBD — evaluate if Steve needs relationship tracking | Discovery item |
| Plaud | TBD — Steve may not use Plaud | Discovery item |

### 4.3 IES Abilities That Map to Steve's Requests (Adapt, Don't Build)

| Steve's Request | IES Equivalent | Adaptation |
|-----------------|---------------|------------|
| Email Response Generation (#1) | Harper — Email Drafter | Gmail swap; voice training on Steve's corpus |
| To-Do Follow-Up (#2) | Shep — Delegation Tracker + Nudges | Replace OmniFocus with assistant workflow |
| Calendar & Morning Briefing (#4) | Chief — Morning Briefing + Calendar Prep | Google Calendar swap |
| Email & Time Intelligence (#5) | Chief — partially tracks patterns | Build dedicated analytics pipeline |
| Foundation Content (#6) | Harper — Content Calendar + Presentations | Extend for white papers; train on Steve's voice |
| Operator Coaching (#13) | Shep — 1:1 Prep, Team Health Pulse | Adapt for external portfolio operators |
| Deep Research (#26) | Chase — Client Meeting Prep | Generalize beyond Improving clients |

### 4.4 Entirely New Build Required

| Ability | Complexity | Phase |
|---------|-----------|-------|
| Unified "Second Brain" (#16) | **High** | 1 |
| Voice-to-Brain Filing (#17) | Medium | 1 |
| Content Ghostwriter (#18) | Medium | 1-2 |
| Closed-Loop Assistant To-Do (#24) | Medium | 1 |
| Travel Persona (#25) | Low | 1-2 |
| Investment Performance Monitor (#20) | Medium | 2 |
| Communication Tone Auditor (#21) | Medium | 2 |
| Time Allocation Monitor (#22) | Medium | 2 |
| Board Advisor & CEO Coach Tracker (#23) | Low | 2 |
| Scout & Convenor (#27) | Medium | 2 |
| Podcast & Video (#19) | Medium | 2 |
| Shadow Board Agent (#7) | **High** | 2 |
| Financial Reconciliation (#8) | **High** | 2 |
| Sentiment & Regulatory (#10) | **High** | 2 |
| Moat Builder / F&I Sim (#11) | **Very High** | 2 |
| Synthetic Negotiation (#12) | **Very High** | 2 |

---

## Part 5: Recommended Updates

### 5.1 Update the Implementation Plan

**Add to Phase 1 scope (or create Phase 1B):**

| Ability | Rationale | Impact on Timeline |
|---------|-----------|-------------------|
| Unified "Second Brain" (#16) | Steve called this his **"primary goal"** in the Mar 2 email. Foundation for everything else. | +1-2 weeks (high complexity: Penzu, Dropbox, AI history imports) |
| Voice-to-Brain Filing (#17) | Extension of Voice-to-Draft (#3) already in scope. Same pipeline, different output routing. | Minimal — additive to existing voice pipeline |
| Closed-Loop Assistant To-Do (#24) | Steve specifically wants to "stop manually following up." Core daily value. | +0.5 weeks |
| Travel Persona (#25) | Low effort, high visibility. Preference file + simple agent logic. | Minimal |

**Add to Phase 2 scope:**

All 8 remaining abilities (#18, #19, #20, #21, #22, #23, #26, #27) — details in Section 1.2.

### 5.2 Update the Internal Kickoff Guide

**Add to Kickoff Meeting Agenda (Section 2 — Current Tools & Systems Walkthrough):**
- Penzu journals — format, export options, volume, how frequently Steve journals
- Dropbox — what's stored there vs. Google Drive? Overlap?
- Apple Calendar — is this a secondary calendar or primary? Relationship to Google Calendar?
- AI conversation history — does Steve want Gemini/ChatGPT/Claude history imported? How much?
- Assistant workflow — who are the two assistants? How do they communicate with Steve today? (Email? Text? Shared app?)
- Three life goals framework — confirm the three goal categories for time allocation monitoring
- Voice memo habits — does Steve use them today? What device and app? (Kickoff Guide asks this but doesn't mention Whisper/AudioPen)

**Add to Discovery Checklist (Step 2):**
- [ ] Penzu API access or export format confirmed
- [ ] Dropbox folder structure mapped
- [ ] Apple Calendar sync method identified
- [ ] AI conversation history export feasibility assessed
- [ ] Assistant names, roles, and communication channels documented
- [ ] Three life goals framework documented with allocation targets
- [ ] Voice capture device and preferred app confirmed

**Add to Risk Matrix (Step 5):**

| Risk | Impact | Mitigation | Escalate To |
|------|--------|------------|-------------|
| "Second Brain" unification overwhelms Phase 1 | Timeline slip, NTE risk | Split into Phase 1A (current 6) and 1B (new 4) | Derek (scope) |
| Penzu has no API | Blocks journal integration | Manual export + import pipeline | Tech Lead |
| Steve's three life goals aren't clearly defined | Time Allocation Monitor has no baseline | Discovery session dedicated to goal framework | David → Steve |
| AI history imports are messy/unstructured | Low value relative to effort | Defer to Phase 2; focus on forward-looking capture | Tech Lead |

---

*Last updated: 2026-03-10*
*Sources: Steve Hall emails (Feb 8, 11, 17, 18, Mar 2, 2026), AI Implementation Plan (Feb 2026), Internal Kickoff Guide (Feb 2026), Steve Hall Discovery Script, IES system documentation (Improving Executive System.md), Kickoff whiteboard photos (Bud, Mar 10), Plaud transcript — "Executive Assistant AI System Integration" (Mar 10, 78m 36s)*
