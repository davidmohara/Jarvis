
---

# ADDENDUM 2: Category 3 Deep-Dive, HRIS / Agent Integration (received 2026-10-14)

[P]=primary vendor PR/docs; [S]=reputable secondary quoting the vendor; [W]=weak.

## Workday (anchor)
- Agent System of Record (ASOR): announced Feb 11 2025, GA Feb 18 2026. "Onboard new AI agents, define roles, track impact, budget costs"; agents "measured like investments, governed like employees." https://investor.workday.com/2025-02-11-The-Next-Generation-of-Workforce-Management-is-Here-Workday-Unveils-New-Agent-System-of-Record [P]
- Agent Partner Network + Agent Gateway: announced Jun 3 2025; ASOR + Gateway support MCP and A2A; 65+ partners. https://investor.workday.com/2025-06-03-Workday-Announces-New-AI-Agent-Partner-Network-and-Agent-Gateway-to-Power-the-Next-Generation-of-Human-and-Digital-Workforces [P]
- Agent Passport (trust/verification, OWASP/NIST/MITRE, one-click revocation, Cisco launch partner): announced Jun 2 2026, early access H2 2026, GA projected end 2026. [S]
- Workday Rising Oct 12-13 2026: Trusted Agent Platform headless; build agents in Claude Code/Codex/Cursor/Google ADK/LangChain; "Agent-Ready Tools are Workday's MCP tools"; "No agent gets a side door." https://blog.workday.com/en-us/rising-product-announcements.html [P]
- Acquires ConductorOne (d/b/a C1.ai), agentic identity, announced Oct 12 2026, closing by Jan 31 2027. [P/S]
- EARNINGS: "AI driving more than 25% of our new ACV"; 5,500+ customers using at least one organic agent. SiliconANGLE, Aug 27 2026. https://siliconangle.com/2026/08/27/workday-posts-strong-earnings-revenue-amid-rapid-uptake-of-its-ai-agents/ [S]
- Workday<->Microsoft: Entra Agent ID integration (Sep 16 2025); Sana Self-Service Agent GA inside M365 Copilot (May 13 2026). [S]

## SAP
- MCP support for SAP HANA Cloud + MCP Gateway, Joule Studio supports A2A+MCP (Nov 5 2025) [P]; SAP+Anthropic Claude via MCP announced May 12 2026, no GA [P]; first SuccessFactors Joule Agent GA Nov 2025, four more H1 2026 [P]; AI Agent Hub GA Oct 8 2026: "govern every agent, LLM, and MCP server across SAP and non-SAP" [P].

## Oracle
- Fusion HCM 100+ agents incl. Job Discovery, Interview Management, Learning Tutor (SiliconANGLE, Sep 16 2025) [S]; Fusion Claw Sep 29 2026 via APIs/MCP/A2A, availability disputed [S]. Oracle's own MCP server is for the database, not HR.

## ServiceNow
- MCP Server GA at Knowledge 2026 (May 5 2026): platform opened to any AI agent; AI Control Tower; Autonomous Workforce incl. HR. [S]

## Microsoft
- Agent 365 GA May 1 2026: "control plane for observing, governing, and securing AI agents." https://www.microsoft.com/en-us/security/blog/2026/05/01/microsoft-agent-365-now-generally-available-expands-capabilities-and-integrations/ [P]

## Real MCP servers / connectors (HR vendors)
- BambooHR connector for Claude, first built on BambooHR MCP: reports, org, hiring, time-off; respects permissions; open beta Oct 8 2026. [P]
- G-P MCP Server: global employment data into Claude/ChatGPT/Gemini/Cursor and Workday/ADP/Paylocity/SAP; human-in-the-loop. Aug 26 2026. [P]
- isolved Connector for Claude GA + six autonomous HR agents; "much more like an employee." Jun 16 2026. [P]
- UKG People Assist in Gemini Enterprise Agent Gallery; GA expected Jul 2026. [P]
- Remote MCP (~Oct 2026) [S]; Rippling building MCP gateway [S]. No MCP server found for ADP, HiBob, Personio, Deel, Dayforce.

## Caveats for the deck
- "Agents are onboarded as employees with real employee records" is MOSTLY VENDOR FRAMING. What ships in 2025-2026 is an AGENT REGISTRY / GOVERNANCE LAYER inside or alongside the HR platform (Workday ASOR, ServiceNow AI Control Tower, Microsoft Agent 365, SAP AI Agent Hub). No mainstream HRIS gives agents real employee records, payroll, or headcount.
- TENSION ITEM: The Information (Mar 24 2026): "Slack, Workday and LinkedIn Are Resisting Customers' AI Agents." Platforms market openness while restricting third-party agents in practice.
- Accuracy flags: Workday does NOT sell a product named "Workday MCP Server" (it is Agent-Ready Tools + Agent Gateway); SAP has no SuccessFactors-branded MCP server (MCP is platform-level); "ADP MCP server" is unverified.

---

# ADDENDUM 3 (FINAL): Category 4 Deep-Dive, Controversies, Cases, Enforcement (received 2026-10-14)

## Verified court cases
- **Mobley v. Workday** (ONGOING), N.D. Cal., Case No. 3:23-cv-00770-RFL, Judge Rita Lin. Nationwide ADEA collective conditionally certified May 16 2025; Jun 22 2026 court let amended case proceed (CA law applies; ADA 'proxy indicators' claim survives). Theory: Workday liable as employer's 'agent.' Class-cert hearing Mar 2027. Reuters Jun 22 2026: https://www.reuters.com/legal/government/workday-must-face-california-lawsuit-over-ai-bias-job-screening-tools-2026-06-22/
- **Kistler v. Eightfold AI** (ONGOING), filed Jan 20 2026, Contra Costa Co. Superior Court. FCRA transparency claim (NOT bias): 1B+ workers scraped, 0-5 Match Scores, low-ranked candidates discarded before human review, no FCRA disclosures. Platform used by Microsoft, PayPal, Morgan Stanley, Starbucks, Chevron, Bayer. Brought by former EEOC chair Jenny Yang. Reuters Jan 21 2026: https://www.reuters.com/sustainability/boards-policy-regulation/ai-company-eightfold-sued-helping-companies-secretly-score-job-seekers-2026-01-21/ ; NYT same day.
- **Baker v. CVS Health** (SETTLED Jul 2024), D. Mass. 1:23-cv-11483: HireVue video interview 'employability score' vs Massachusetts lie-detector statute; tentative class settlement. HR Dive Jul 24 2024.
- **Meta AI layoffs suit** (ONGOING, filed Jul 13 2026, N.D. Cal.): 26 employees allege AI-selected layoff targets using inputs (AI-token consumption, 'AI-native' ratings) that workers on medical/parental leave or with disabilities cannot accumulate. CNBC Jul 14 2026: https://www.cnbc.com/2026/07/14/meta-lawsuit-layoffs-ai.html

## Regulatory / administrative
- **EEOC v. iTutorGroup** (SETTLED 2023), E.D.N.Y. 1:22-cv-02565, $365K: PRIMARY URL recovered: https://www.eeoc.gov/newsroom/itutorgroup-pay-365000-settle-eeoc-discriminatory-hiring-suit . CRITICAL NUANCE: intentional, human-coded age cutoffs (rule-based disparate treatment), NOT machine-learning bias. Framing as an 'AI discrimination case' is contested (Epstein Becker Green).
- ACLU complaints: vs Intuit + HireVue (Mar 2025, disability/race; HireVue disputes the facts, says Intuit did not use its AI assessment); vs Aon (May 2024, FTC/EEOC; no FTC action as of Oct 2026).
- HireVue facial analysis: discontinued Jan 2021 after EPIC FTC complaint; ORCAA audit mostly cleared it; facial data was only ~0.25% of predictive power. Do NOT frame as 'stopped because biased.'
- **NYC Local Law 144 effectively unenforced**: NY State Comptroller audit Dec 2 2025: 2 complaints in 2 years; DCWP found 1 non-compliance where Comptroller found 17+. https://www.osc.ny.gov/state-agencies/audits/2025/12/02/enforcement-local-law-144-automated-employment-decision-tools
- **Colorado**: SB26-189 (signed May 14 2026) repealed/replaced SB24-205; narrower (transparency/notice); effective Jan 1 2027; AG-only enforcement, 60-day cure, no private right of action. https://leg.colorado.gov/bills/sb26-189
- **Illinois HB 3773**: effective Jan 1 2026; civil-rights violation to use AI with discriminatory effect or zip-code proxy; employee notice required.
- **Connecticut CART Act** (PA 26-15): signed Jun 2 2026, effective Oct 1 2026; pre-decision notice for hiring/promotion/discipline; AI disclosure in WARN notices. Ropes & Gray Jun 2026.
- **EU AI Act**: employment stays high-risk (Annex III) but obligations DELAYED to Dec 2 2027 (Digital Omnibus). Ogletree Jun 2026.
- **Federal US**: EEOC/DOL AI-workplace guidance rescinded early 2025; FY2025-2029 NEP deprioritizes disparate impact; DOJ OLC (Jun 9 2026) found EEOC Title VII disparate-impact guidelines UNCONSTITUTIONAL (does not address ADEA). Jackson Lewis Jun 11 2026.
- **FTC**: NO hiring-specific action; only 'Operation AI Comply' (Sep 2024, consumer claims). https://www.ftc.gov/news-events/news/press-releases/2024/09/ftc-announces-crackdown-deceptive-ai-claims-schemes
- **Amazon 2018 correction**: tool was never used to evaluate actual candidates (internal project, scrapped). Reuters Oct 10 2018: https://www.reuters.com/article/us-amazon-com-jobs-automation-insight/amazon-scraps-secret-ai-recruiting-tool-that-showed-bias-against-women-idUSKCN1MK08G

## Do-NOT-cite additions
- D12: 'Amazon's AI discriminated against women' (never used on real candidates)
- D13: 'HireVue stopped facial analysis because it was biased' (low value + PR, ~0.25% predictive power)
- D14: 'FTC cracked down on AI hiring' (no hiring action exists)
- D15: 'Colorado AI Act' as current law (repealed/replaced, effective Jan 1 2027)
- D16: 'iTutorGroup was an AI/ML discrimination case' (rule-based human-coded cutoffs)
- D17: No named employer's AI has been ADJUDICATED to reject candidates based on race as of Oct 2026; race claims are alleged/unresolved.

## Bottom-line framing for the governance slide
(a) Real 'AI rejected me' cases are vendor-liability and process cases (Workday = agent liability; Eightfold = FCRA transparency), plus one clear intentional case (iTutorGroup, rule-based). (b) Enforcement moved to PRIVATE plaintiffs: federal guidance rescinded, DOJ vs disparate impact, NYC LL144 documented unenforced; action is in class actions and new state laws (IL, CT, narrowed CO). (c) Regulatory dates are SLIDING: Colorado repealed, EU delayed to Dec 2 2027. (d) Documented harms cluster in AGE (Workday, iTutorGroup), DISABILITY/LEAVE (Meta, Intuit/HireVue, Aon), RACE/GENDER (alleged: Workday, Aon).

---

# ADDENDUM 4 (PRIMARY REPORT, parallel stream): received 2026-10-14

Method: WebSearch unauthorized; all items fetched from source pages directly (WebFetch / reader proxy), Google News RSS for discovery. Vendor self-reported numbers labeled.

## Bucket 1, Adoption stats (verified primary)
- SHRM State of AI in HR 2026 (n=1,908 HR pros, Apr 8 2026): 39% of orgs use AI in HR; recruiting 27% (highest), HR tech 21%, L&D 17%; orgs 5,000+ employees: 60% adoption; 87% of adopters report improved efficiency. https://www.shrm.org/topics-tools/news/ai-hr-2026-from-hype-to-measured-human-centered-impact
- SHRM 2025 Talent Trends (n=2,040): 43% of HR professionals use AI in HR tasks, up from 26% in 2024. NOTE: different denominator (individuals vs orgs); do not place next to 39%.
- SHRM 2024 Talent Trends (n=2,366): among AI users, recruiting/interviewing/hiring 64% top use; JD generation 65%; targeted postings 42%; resume screening 34%; AI video pre-screening only 7%. 88% say AI saves time; 35% say reduces recruiting costs.
- LinkedIn Future of Recruiting 2025 (n=1,271, 23 countries): 37% of recruiting orgs integrating GenAI (up from 27%); ~20% of work week saved; 73% say AI will change how orgs hire.
- Gartner (Jul 2025, n=114 HR leaders): 88% say their org has NOT realized significant business value from AI tools. Companion (n=2,986 employees): 65% excited, 62% say AI saved time. https://www.gartner.com/en/newsroom/press-releases/2025-10-28-gartner-survey-shows-88-percent-of-hr-leaders-say-their-organizations-have-not-realized-significant-business-value-from-ai-tools
- WEF Future of Jobs 2025 (1,000+ employers): 77% plan to upskill; 41% plan workforce reductions from AI automation; 63% cite skills gaps as biggest barrier.
- SHRM "From Adoption to Empowerment" (n=1,812, Jul 8 2025): 45% of US workers use AI on the job (Millennials 56%, Boomers 25%); 77% of users get more done in less time.
- Taggd (vendor-sponsored, label it): 80% of enterprises adopted AI in recruitment, only 10% see measurable hiring gains. Aug 2026.

## Bucket 2, Deployed in production
- IBM AskHR (PRIMARY, IBM case study Feb 2026; corroborated SHRM May 2025): resolves 94% of common inquiries; 75% ticket reduction; HR operating budget cut 40% over 4 years. https://www.ibm.com/case-studies/ibm-client-zero
- Microsoft Employee Self-Service Agent (Inside Track Nov 13 2025): 200,000+ FTEs; targets: >=40% fewer tickets, -44% monthly HR tickets by mid-2026; visitor registration saves 50,000 hours/yr. Label as targets.
- Chipotle Ava Cado (Chipotle PR Oct 22 2024 + CNBC Jun 13 2025, CEO-confirmed): hiring time cut 75%; 3,500+ restaurants.
- McDonald's Olivia/McHire (NBC Jul 11 2025): 21 days to under 3.
- Fontainebleau Las Vegas Morris (HR Executive Sep 16 2025, CPO quoted): 6,500 hires in 4 months; 3-minute application; expected 80k applications, got 300k; 41% of chats after hours.
- 7-Eleven (Workday customer story, vendor-reported): 95% of hiring automated; 40,000+ hours/week returned to store leaders; time-to-hire 10+ days to under 3.
- JLL (Workday customer story, vendor-reported): 1.5M applications/yr; time-to-fill 52 to 30 days; quarterly hires +64%; recruiters 10 to 50 concurrent reqs.
- Standard Chartered + Gloat (Fortune Mar 6 2026): ~$49,000 saved per employee reskilled internally vs external hire; internal hiring 30% (2023) to 50%+ (mid-2025); $55M+ saved. (Gloat's own case study gives different scope; don't mix.)
- Schneider Electric Open Talent Market / Gloat (Modern Executive Solutions Oct 3 2025, CHRO Charise Le): 89% employee adoption; 13,400+ gig matches; 27,500 mentor matches; ~4,000 job matches. COHORT MEMBER COMPANY.
- TCS (Integrated Annual Report FY2026 + earnings): ~50% of internal resource allocations via AI talent marketplace (~584k employees); GenAI Learning Coach 80,000+ interactions.
- Salesforce Career Connect (newsroom Sep 4 2024, pilot ~1,200 employees): 28% applied via platform; 91% of roles filled were surfaced by it.
- CVS Health + ServiceNow (TechTarget May 2026 + ServiceNow earnings Apr 22 2026, vendor-reported): case resolution ~2 days to under 20 minutes.
- AdventHealth (Workday blog, vendor-reported): ~300 nurses hired via resurfaced past candidates; doubled requisition close rates in 90 days; -40% hiring-manager decision time.
- Unilever (Guardian Oct 2019 / dated 2016-2019 deployment): time-to-hire 4 months to 4 weeks; ~1M GBP/yr; completion 50% to 96%. LABEL AS DATED.
- Government/public sector: GAP. No well-quantified deployment found; NC SL 2026-40 modernization has no AI outcome numbers yet.

## Bucket 3, Emerging + governance
- Workday Autopilot Agents + Trusted Agent Platform (PR Newswire Oct 13 2026): TA Agent early access, GA planned early 2027; Agent-Ready Tools = MCP tools (GA); Agent Gateway A2A+MCP; Workday+Anthropic+Sana via MCP early access. Acquisitions: Sana (Nov 2025), Paradox (Oct 1 2025), C1.ai (Oct 2026).
- SAP SuccessFactors Joule agents available Oct 2026; SAP acquiring TechWolf (Oct 6 2026). SAP "20% productivity" is self-claim.
- Salesforce Agentforce HR Service (May 6 2025): shipped; 96% self-service resolution as customer zero.
- Oracle Fusion Agentic Applications (Aug 19 2026): announced, no GA. ADP Assist (Jan 28 2026): announced, no GA, no named customers.
- Workable MCP Server GA May 13 2026: 38 MCP tools. Eightfold Candidate Agent GA Jul 15 2026: 24/7, 24+ languages.
- Amazon Connect Talent: announced Apr 28 2026, GA Sep 17 2026; voice interviews, anonymized competency scores. Amazon context: 250,000 seasonal hires for 2025 peak. https://www.aboutamazon.com/news/aws/amazon-connect-ai-business-set
- HireVue AI Interviewer launched Jun 18 2026 (vendor claims 1,150+ customers; scale unverified). Facial analysis discontinued 2021.
- Apriora Alex: up to 1,000 AI interviews/day; 7 of 8 Xponential Fitness brands. Vendor-sourced.
- Greenhouse Apr 2026 (n=2,950, via CNBC Sep 2026): 63% interviewed by AI; ~4 in 10 withdrew over AI interview; 8% believe AI makes hiring fairer.

## Regulatory (corrected, high confidence)
- EEOC: AI guidance removed from eeoc.gov late Jan 2025 but NOT formally rescinded; NEP FY2025-29 (signed Jun 4 2026) will not pursue disparate impact, no AI mention; Title VII/ADA/ADEA + Uniform Guidelines (29 CFR 1607) remain in force; private suits continue. https://www.eeoc.gov/sites/default/files/2026-06/NEP_-_signed.pdf
- NYC LL144: enforcement began Jul 5 2023; penalties $500-1,500/day; NO fines ever issued; Comptroller audit Dec 2 2025: DCWP had no effective enforcement system (1 of 32 flagged vs 17+ potential).
- Illinois HB 3773 (PA 103-0804): effective Jan 1 2026; disparate-effect standard (no intent required); ZIP-as-proxy banned; notice required; no audit mandate; IDHR rulemaking postponed Jun 2 2026.
- EU AI Act: employment = Annex III high-risk; obligations delayed to Dec 2 2027 by AI Omnibus Reg. (EU) 2026/1744 (in force Jul 27 2026). Deployer duties when live: human oversight, 6-month logs, inform workers (Art. 26).
- Colorado: SB24-205 ENJOINED Apr 27 2026 (xAI v. Weiser, DOJ intervened), then repealed/replaced by SB26-189 (May 14 2026); narrower notice regime; rest effective Jan 1 2027.
- California: FEHA ADS regs effective Oct 1 2025; 4-year record retention.
- Texas TRAIGA (HB 149): effective Jan 1 2026 but EXCLUDES employment (consumer definition); intent-based only. LOCAL CONTRAST for a Dallas audience.
- Federal preemption: EO 14365 (Dec 11 2025) DOJ AI Litigation Task Force challenging state AI laws; litigation pending.

## Do-NOT-use additions
- "IBM 96% candidate-experience improvement / 35% time-to-hire / 25% cost-per-hire": misattributed, no primary source.
- "70-75% time-to-hire reduction" as industry-wide: vendor case studies only.
- ResumeBuilder "7 in 10 companies use AI in hiring": 2025 PROJECTION, vendor-sponsored.
- "43% of recruiters use AI (SHRM)": misquote; 43% is HR tasks overall; recruiting-specific is 64% of adopters.
- HireVue "72% of HR leaders use AI": content-farm only.
- "Maryland HB 1202 AI-employment law": does not exist (drug-trafficking bill).
- "NYC LL144 first fines 2024/2025": no fines ever.
- "Colorado effective Feb 1 / Jun 30 2026": superseded by repeal/replace.
- "EU high-risk obligations Aug 2 2026": delayed to Dec 2 2027.
- Unilever "90% time-to-hire reduction": real but dated 2016-2019; label it.

---

# ADDENDUM 5 (FINAL): sector gap-fill, received 2026-10-14

- **Walmart** (PRIMARY, press release Jun 24 2025): AI task prioritization + auto shift-planning + GenAI associate self-service + real-time translation (44 languages). Shift-planning for team leads 90 min to 30; 900,000+ weekly users, 3M+ queries/day; rollout to 1.5M US associates. https://corporate.walmart.com/news/2025/06/24/walmart-unveils-new-ai-powered-tools-to-empower-1-5-million-associates
- **U.S. Army** (secondary citing org's own award case study, unaudited): Army Marketing Cloud AI decisioning + lead scoring; conversion +112%; days-to-contract -60%; cost-per-contract -23%; annual recruiting mission met 4 months early. The Drum, Jun 5 2026. https://www.thedrum.com/awards-case-study/how-the-army-used-ai-decisioning-to-double-recruitment-conversion-rates
- **Providence** (vendor-reported, IBM newsroom Oct 7 2026): 'RITA' digital worker on watsonx Orchestrate over Oracle HCM; admin effort -90%; internal movers start 12 days sooner; transfer costs -60%; ~119,000 caregivers. https://newsroom.ibm.com/2026-10-07-providence-health-collaborates-with-ibm-using-ai-to-reduce-hiring-admin-time-without-replacing-a-single-system
- **Barts Health NHS Trust** (vendor-reported, DXC Dec 10 2025): RPA on People Services, 18,000+ hours automated year one, ~80,000 case records/yr; AI screening is next phase (label as RPA-then-AI).
- **FedEx** (PRIMARY, newsroom Dec 2 2025): enterprise AI literacy program, 500,000+ employees (scale only, no outcome metric). https://newsroom.fedex.com/newsroom/global-english/fedex-empowers-global-workforce-with-ai-education-and-literacy-program
- Rejected leads (do not re-chase): OPM USA Class (no numbers); Mercy Joy / Duke Ask CHRIS (no results); Hilton/Marriott (guest-facing, not HR); GXO / C.H. Robinson (operational, not HR). Hotel-chain HR has no verifiable public example.
