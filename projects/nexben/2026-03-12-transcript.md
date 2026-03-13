# 03-12 Consultation: Nexben ICHRA Pre-Sales Analysis Tool

**Date**: 2026-03-12
**Time**: 2:07 PM CT
**Duration**: 29 min 18 sec
**Source**: Plaud AI Recording
**Participants**: O'Hara, Speaker 2, Kristin Johnson

---

## Summary

## Overview
The customer represents a benefits technology platform called NextBen that enables brokers to help employers transition from traditional fully insured/self-funded health plans to a defined contribution model (ICHRA). They urgently need a high-performance, broker-facing pre-sales analysis application that ingests large employer census files, estimates cost impacts versus current group plans using individual market rates, recommends optimal classing/slicing strategies, and generates proposals—integrated with their existing platform/pipeline. Current tools crash at 70–700 employees, lack end-to-end functionality, and don’t integrate with NextBen’s systems. The primary pain point is time-sensitive: manual Excel analyses for “ten census files” take hours each, delaying sales. The desired outcome is a scalable, fast, integrated tool that brokers can self-serve within NextBen’s platform, handling up to “three hundred thousand lives,” delivering results within seconds, and supporting configuration levers (employer/employee cost share, dependents, metals, affordability checks). The consultant proposed a one-week fixed discovery ($15,000) with credit applied if proceeding.
## Background
- The discussion involves NextBen’s executive (Speaker 2; also referenced as Lauren at the end) and consultant O’Hara. They are based in the Frisco/Plano, TX area.
- NextBen’s platform supports brokers and employers transitioning to ICHRA by setting defined contributions and enabling employee plan shopping based on zip code, with funds movement facilitated by NextBen.
- Current growth has been organic with comparable subscriber counts to larger competitors, but target brokers now focus on larger employers needing rigorous cost-savings analysis.
- Competitor tools exist but have critical limits: one freezes over “70” employees; another will not work over “700” employees; they cover only parts of the workflow and are not available to NextBen (true competitor).
- NextBen outsources all IT to a single third party; proprietary core platform; has SSO with a marketplace partner; API status uncertain; prior plans for a CTO stalled due to a candidate’s unexpected passing.
- The consultant outlined a two-phase approach: a one-week discovery to define inputs/outputs and scope (fixed cost “15 k”), then build. If proceeding, the $15,000 is credited to the next phase. Deliverables from discovery are reusable with other vendors.
## Pain Points
[Performance and Scalability Limits of Existing Tools Prevent Large-Group Analyses and Slow Sales Cycles]
The current available tools either freeze over “70” employees or do not work over “700” employees, and they only complete part of the needed analysis. This prevents NextBen and brokers from modeling large employer groups and slows the sales process, forcing manual Excel analyses.
- Impact: **Delays in producing cost-savings estimates** for prospects, inability to engage large self-funded employers, lost competitive edge, and reduced broker self-service. Sales momentum is hampered.
- Current Situation: Using third-party tools with strict limits and manual Excel for analyses; “ten census files” are on the desk being manually run; hours per analysis.
- Quantitative Metrics: Tool crashes over “70” and “700” employees; desired tool should handle up to “three hundred thousand lives” and return results **within seconds**.
- Examples: One partner tool “spins and crashes” if > “70” employees; another “will not work” if > “700” employees.
- Context: Competing in a space where brokers need fast, data-rich pre-sales insights across “one hundred and ten” or more plan options; large employers require robust modeling to see savings.
- Stakeholders: **Brokers**, **NextBen growth/sales team**, **Large employer prospects**, and **Executive team (CEO Mark Smith)**.
[Workflow Fragmentation and Lack of Integration with NextBen’s Platform/Pipeline]
Existing small tools do not feed any data back into NextBen’s systems, preventing visibility and accountability for quotes and pipeline tracking.
- Impact: **No visibility into quotes**, inability to hold brokers/account teams accountable, lost insights for forecasting and follow-up, manual re-entry.
- Current Situation: Third-party tool for up to “fifty” people returns minimum contribution and pricing but **does not feed** into NextBen’s system; no data export offered.
- Quantitative Metrics: Small tool limit “fifty” people; zero data integration paths offered by current vendor.
- Examples: Vendor claimed “there’s not a way” to get data; even raw data files are unavailable.
- Context: NextBen has SSO with a marketplace partner; API existence for core platform is unknown but “could be built”; outsourced IT handles coding.
- Stakeholders: **Sales operations**, **Brokers**, **Product/Platform team**, **Executive leadership**.
[Inability to Provide Comprehensive, Broker-Friendly Pre-Sales Functionality]
Competitor tools demonstrate desired features (state coverage mapping, affordability flags, plan filters), but NextBen lacks a unified application that guides brokers through setting budgets (flat/dynamic), matching to comparable metals (bronze/silver/gold), and generating proposals.
- Impact: **Brokers need more help articulating cost savings** to employers; without a robust tool, adoption among larger clients stalls, diminishing value proposition.
- Current Situation: Relying on screenshots from a competitor to illustrate desired capabilities; no in-platform broker tool exists today; manual processes are used.
- Quantitative Metrics: Examples include needing to model “six hundred dollars a month” budgets, compare against “ninety six percentile” benchmarks, and evaluate “one hundred and fourteen medical plans.”
- Examples: Desire to flag affordability issues at “9.96% of annual income” based on the lowest-cost silver plan; show savings like “2 million dollars” for employer and “five hundred thousand” for employees.
- Context: Metals mapping from current plan deductibles (e.g., “$2,000 deductible” as a high bronze); desire for low/mid/high averages per metal for comparison.
- Stakeholders: **Brokers**, **Employers**, **NextBen product and sales**.
[Lack of Automated Classing/Slicing Strategy Recommendations for Large Employers]
For large self-funded employers, optimal carve-outs (by state, facility, or classification) could maximize savings, but NextBen lacks automated recommendations and scenario levers.
- Impact: **Missed savings opportunities** and less persuasive proposals; more manual analysis burden on the team; slower decision cycles.
- Current Situation: Conceptual desire for classing as a configurable “dial” in the tool; currently not implemented; manual Excel cannot quickly iterate.
- Quantitative Metrics: No specific counts beyond group sizes; expectations to show strategies and savings deltas (e.g., scenarios that still allow higher dependent coverage while maintaining savings).
- Examples: Slice by “state of Texas” or by a “manufacturing plant” with higher claims; adjust dependent coverage while staying within targeted savings.
- Context: Larger employers will consider partial migrations to ICHRA; classing guidance is pivotal to win them over.
- Stakeholders: **Large employer decision-makers**, **Brokers**, **NextBen’s growth team**.
[Resource and Ownership Constraints in Technology Execution]
NextBen’s platform is proprietary, with all IT outsourced to a single company; internal knowledge is thin, and planned CTO hiring fell through.
- Impact: **Slow implementation timelines**, backlog prioritization issues, dependency on a third party, and potential misalignment on priorities; urgent projects slip.
- Current Situation: One or two internal users with surface-level access; third party codes and maintains; list of platform improvements exists but moves slowly.
- Quantitative Metrics: Not explicitly quantified; urgency indicated by “need this project to be done like yesterday.”
- Examples: SSO exists with marketplace partner; API uncertain and may need to be built.
- Context: Desire to avoid an oversized internal IT team; considering hiring a CTO/COO replacement and a small, efficient team.
- Stakeholders: **Executive team (CEO Mark Smith, Speaker 2/ELT)**, **Third-party IT vendor**, **Consultant**.
## Expectations
[Deliver a High-Performance, Scalable Pre-Sales Analysis Tool Integrated with NextBen’s Platform]
Build a broker-facing application that ingests large census files, computes individual market costs against current plans, supports configurable budgeting and contribution strategies, recommends classing, flags affordability, and generates proposals—integrated with NextBen’s platform/pipeline.
- Specific Goals: **Handle up to “three hundred thousand lives”**; process **within seconds**; support **flat and dynamic budgeting** (age/age bands/classes); map current plan deductibles to metals (bronze/silver/gold with low/mid/high averages); display state coverage; provide filters across “one hundred and fourteen” or more plans; compute employer/employee savings (e.g., “2 million dollars” and “five hundred thousand” examples); flag affordability at **“9.96% of annual income.”**
- Timeframe: **Urgent (“yesterday”)**; immediate need to reduce hours-long Excel work; initial discovery proposed as **one week**.
- Resources Required: Access to **carrier rates** (they “will have it”), **census files**, current plan designs and costs, **platform integration details (SSO/API)**, and cooperation from the outsourced IT vendor.
- Success Metrics: **Speed** (seconds per run), **scale** (up to 300,000 lives), **broker self-service adoption** (usage within broker portal), **proposal conversion rates**, **accuracy** of savings estimates, and **data flow into pipeline** for visibility.
- Stakeholders: **Brokers**, **NextBen sales/growth team**, **Product/Platform**, **Executive leadership**, **Third-party IT vendor**, **Consultant team**.
[Complete Structured Discovery and Provide Reusable Documentation]
Engage in a fixed-cost discovery to define inputs/outputs, user roles, workflows, data sources, and integration paths; deliver artifacts reusable with other vendors if needed.
- Specific Goals: **Produce a roadmap, scope, backlog, and requirements** memorialized in documents; align on team size and sprint plan.
- Timeframe: **One week** discovery; follow-on build timeline defined after.
- Resources Required: Access to internal SMEs (sales, broker support, product), existing “list of outputs,” any BRDs/screenshots, and IT vendor contacts.
- Success Metrics: Acceptance of discovery deliverables by ELT; clarity sufficient for competitive vendor bids; utilization of $15,000 credit if proceeding.
- Stakeholders: **Speaker 2/ELT**, **CEO Mark Smith**, **Consultant**, **Third-party IT vendor**.
[Enable End-to-End Data Integration and Pipeline Visibility]
Ensure the tool feeds proposals/quotes into NextBen’s platform or CRM/pipeline for tracking and accountability.
- Specific Goals: **Seamless data flow** via API or batch; attach quotes to accounts; support SSO for brokers; reduce manual re-entry.
- Timeframe: Parallel to or immediately after MVP tool delivery.
- Resources Required: API design/availability, data schemas, collaboration with outsourced IT, security review for SSO.
- Success Metrics: **100% of quotes** generated are visible in pipeline; reduced manual effort; consistent reporting.
- Stakeholders: **Sales operations**, **Brokers**, **IT vendor**, **Consultant**.
## Other Information Summary
- The platform currently has SSO with a shopping marketplace partner; API may need to be built or exposed.
- Desired UI patterns include interactive benchmarking (e.g., “ninety six percentile” sliders), state maps, and dynamic levers for employer/employee/dependent contributions.
- Affordability compliance: employees cannot spend more than “9.96%” of annual income based on the lowest-cost silver plan; the tool should flag unaffordable cases.
- Metals mapping: use current plan deductible (e.g., “$2,000”) to map to high bronze/low silver; need low/mid/high aggregate averages by metal.
- Future hiring: evaluating CTO/COO replacement; desire to keep the IT team lean and efficient; open to consultant assistance in hiring after successful delivery.
- Competitor examples are from confidential screenshots taken during demos; not publicly accessible; NextBen seeks a more “intellectual” and proprietary spin.
- The consultant offered $15,000 fixed discovery with credit applied if proceeding to build; deliverables are client-owned and vendor-agnostic.
## To-Do List
- [ ] Consultant to email a detailed discovery kickoff checklist (required inputs: sample census templates; current plan designs/costs; desired outputs; rate data sources; integration/SSO details; pipeline/CRM endpoints). Deadline: ASAP. Stakeholders: O’Hara, Speaker 2, outsourced IT.
- [ ] Customer to share existing “list of outputs,” any BRDs, and competitor screenshots (as reference only). Deadline: ASAP. Stakeholders: Speaker 2.
- [ ] Schedule one-week discovery sessions with SMEs (sales; broker enablement; product/ops; IT vendor). Deadline: Within 1 week of agreement. Stakeholders: O’Hara, Speaker 2, IT vendor.
- [ ] Confirm data access for carrier rates (current or planned), affordability rules, and metals mapping methodology. Deadline: During discovery. Stakeholders: Product/Analytics, Speaker 2.
- [ ] Define integration approach (API vs. batch) with the proprietary platform and CRM/pipeline; validate SSO scope. Deadline: During discovery. Stakeholders: IT vendor, Consultant.
- [ ] Align on non-functional requirements (performance: seconds; scalability: up to 300,000 lives; security/compliance). Deadline: During discovery. Stakeholders: Consultant, Speaker 2.
- [ ] Executive alignment: Present discovery plan and $15,000 fixed cost with credit structure to CEO Mark Smith for approval. Deadline: Before discovery start. Stakeholders: Speaker 2, CEO.
- [ ] Provide initial timeline and team composition recommendation post-discovery with phased delivery/MVP. Deadline: End of discovery week. Stakeholders: Consultant.
> AI Suggestions
> The AI has identified the client's biggest pain point as performance and scalability limits preventing fast, large-group pre-sales analyses (forcing manual Excel and delaying sales). Possible solutions:
> 1. Build a cloud-native, event-driven analysis service using scalable data processing (e.g., columnar storage + vectorized computation) to handle up to 300,000 lives with sub-second to few-seconds results; preload and cache carrier rate tables by geography/metal to minimize compute time.
> 2. Deliver an MVP broker portal module with prioritized features (census upload, metals mapping, savings calculator, affordability flags) and defer advanced visualizations to Phase 2; this gets brokers off Excel quickly while proving performance at scale.
> 3. Implement a robust data integration layer (API-first with a fallback scheduled batch) to push proposal data into the proprietary platform and CRM/pipeline; include SSO and standardized schemas to ensure accountability and reporting from day one.
> 4. Add an optimization engine for classing/slicing strategies (e.g., heuristic or linear programming) that tests carve-outs by geography or cohort and surfaces top savings scenarios with configurable employer/dependent contributions.
> 5. Establish a joint performance SLA and test harness (synthetic mega-census up to 300,000 lives) with automated load testing in CI/CD to guarantee “seconds” response time and prevent regressions as carrier rate datasets grow.

---

## Action Items
- @O'Hara - Send an email outlining the necessary information needed to create an estimate for the project. - No Due Date Mentioned.
## Key Decisions
- The initial one-week discovery and planning phase will have a fixed cost of $15,000. - Rationale: To cover the work of interviewing stakeholders, processing requirements, and developing a detailed project plan and backlog.
- O'Hara will apply the $15,000 from the discovery phase as a credit toward the cost of the full development project if Speaker 2's company moves forward with them. - Speaker 2 agreed this was a fair arrangement.
## Detailed Minutes
[01:02-02:04] **Speaker 2 outlines an urgent need for a custom-built pre-sales tool to accelerate their sales cycle.**
- The primary business objective is to acquire a specific tool quickly to support their growth strategy.
- Speaker 2's company, NextBen, intends to evaluate several development partners for this build.
- While a custom build is the focus, they remain open to an existing off-the-shelf solution if one that meets their needs is discovered.
- Speaker 2 draws a contrast with a past experience on "Project Two Hundred and Two" at a company called Carrington, noting that while the workshop-driven process was valuable then, their current timeline does not permit a similar approach.
[02:04-02:49] **O'Hara confirms his firm's relevant experience in the financial services and healthcare sectors.**
- O'Hara states that his firm's two largest industry verticals are financial services and healthcare, which directly align with NextBen's and Carrington's business domains.
- He notes a prior business relationship with Magellan, where Speaker 2 previously worked, highlighting the interconnected nature of the industry in the Frisco area.
- O'Hara has lived in Frisco for 16 years, which has resulted in him knowing many people in the local industry.
[02:50-04:33] **Speaker 2 provides an overview of NextBen's business model, which offers an alternative funding strategy for employer benefits.**
- NextBen provides a platform for benefits brokers to help employers shift from traditional funding models (self-funded or fully insured) to a defined contribution plan.
- This model addresses the issue of escalating healthcare costs and double-digit budget increases faced by employers.
- The process involves:
    - Brokers adding employers to the NextBen platform.
    - Employers setting up a defined contribution plan (e.g., a $600/month budget per employee).
    - Employees receive an email to log into the platform, where they can shop for benefits from a wide selection of plans (e.g., 60+ options) based on their individual zip code.
[04:33-06:28] **The core business problem is identified: brokers need a tool to demonstrate cost savings to larger, more strategic employers.**
- Speaker 2 was hired to drive "10x" growth, moving beyond the company's initial success with small groups acquired through organic referrals.
- The platform's early adopters were small employers who did not require complex strategic analysis to see the value in offering any benefits.
- The current target market consists of brokers working with larger employers who have never used this type of defined contribution program before.
- These brokers require a tool to clearly articulate the cost savings opportunity to convince employers to switch models.
[06:29-09:02] **Speaker 2 details the functional requirements for a new pre-sales analysis application.**
- The tool's purpose is to act as a pre-sales aid, analyzing an employer's current benefits plan and demonstrating the financial impact of moving to NextBen's model.
- Key functionality includes:
    - Ingesting a census file with employee data and information on the employer's current plan, costs, and coverage.
    - Accessing rate data from all insurance carriers to model costs on the individual market.
    - Processing large census files (e.g., up to 300,000 lives) and generating results in seconds within the same screen.
    - The output should identify a plan on the individual market that best matches the employer's current offering and show the total cost comparison.
    - The tool must include adjustable "levers" for brokers to fine-tune the strategy (e.g., adjust cost-sharing).
    - The final output should be a proposal that quantifies savings for both the employer and employees (e.g., "you are going to save two million dollars").
- Speaker 2 believes their competitor's tool was built by engineers, not benefits experts, suggesting an opportunity to create a more proprietary and effective solution.
[09:07-09:38] **Existing competitor tools have significant performance and functional limitations.**
- Speaker 2 highlights the shortcomings of two competitor tools they have evaluated:
    - One tool, which they have access to as a partner, freezes and crashes when a census file with more than 70 employees is uploaded.
    - Another tool fails if the employee count exceeds 700.
    - A further limitation is that these tools only perform a partial analysis, not the "whole exercise" that NextBen requires.
[09:59-14:44] **A competitor's tool was presented as a functional model, despite its inaccessibility and performance limitations for larger-scale use.**
- Speaker 2 demonstrated screenshots of a competitor's tool to illustrate the desired user experience and functionality, clarifying that the information is confidential and was obtained from a partner who attended a demo.
- The goal is to embed this new tool directly into the NextBen platform for brokers to use on-demand, rather than having NextBen staff run the analysis for them.
- The goal is not to replicate the tool exactly but to create something with a similar "vibe" that is more "intellectual" or advanced.
- O'Hara noted that the competitor's tool appears to have performance issues with large data volumes, which is a key reason not to use it.
- Speaker 2 added that as a direct competitor, they would be unable to use the tool even if they wanted to, as the competitor would not provide access.
- **User Flow & Analysis Features from Demo:**
    - A broker uploads a census file or performs manual entry.
    - The system displays budgeting options (flat budget vs. dynamic budgeting by class).
    - The tool immediately shows a high-level cost comparison and total savings, with a map highlighting states with employees.
    - Plans are bucketed by metal tiers (Bronze, Silver, Gold), and the analysis computes aggregate averages for each.
    - Interactive "levers" allow brokers to benchmark against cost percentiles and adjust employer/dependent contributions.
[14:45-16:37] **The desired new tool should incorporate affordability rules and suggest optimal employee "slicing strategies" for large employers.**
- The competitor's tool was used to demonstrate desired functionality, such as flagging employees whose benefit costs exceed the affordability threshold (9.96% of annual income, based on the lowest-cost silver plan). This helps identify where contribution adjustments are needed.
- Speaker 2 identified a gap in the competitor's tool: it works well for small to mid-sized employers but lacks features for large, self-funded employers.
- A key requirement for the new tool is to analyze a census file and recommend a "slicing strategy" for large employers using Icra (Individual Coverage HRA).
    - This involves carving out specific employee groups (e.g., by state, by manufacturing plant) to move to the new plan, rather than moving the entire company at once.
- The tool should identify the classing strategy that provides optimal savings, even if the employer chooses to contribute more than the affordability rules mandate.
[16:37-18:17] **The new tool must integrate with the company's core system to automate the setup of chosen benefit strategies.**
- O'Hara suggested that the "classing strategy" should be an adjustable variable or "dial" within the tool's interface, allowing users to see how different strategies affect outcomes.
- Speaker 2 described the ideal workflow:
    1. The tool presents a cost-savings analysis and suggests a strategy.
    2. The broker uses the output to create a proposal for the client.
    3. Once the client approves a strategy (e.g., "Strategy A"), that selection should feed directly into the company's core system.
    4. This integration would pre-populate contribution amounts when the employer logs in, eliminating manual data entry.
- O'Hara affirmed this is achievable, suggesting that the tool could output a batch file or make a direct API call to the core system to transfer the data.
[18:18-19:35] **The current third-party tool is a silo with no data integration, creating a major business visibility and accountability problem.**
- Speaker 2 described their current process, which uses a limited third-party tool that only accepts up to 50 people and provides minimal output (minimum contribution and total price).
- A critical flaw of the current tool is its complete lack of integration; it does not feed data back into their system.
- This creates significant business challenges:
    - The company has no visibility into what is being quoted to potential clients.
    - They cannot track which accounts are in the pipeline or hold brokers accountable.
- The third-party provider claimed there was no way to export the data, a statement Speaker 2 finds unbelievable.
- The new tool must be connected to their pipeline, whether through the core platform or another pipeline tool, to solve this data silo issue.
- O'Hara inquired about the name of the core platform to assess integration possibilities.
[19:36-21:59] **The company's IT is fully outsourced and has a long backlog, creating an urgent need for this "side project" to be completed by an external team.**
- The company's core platform is a proprietary system that they own.
- However, all IT functions, including coding and updates, are outsourced to a single third-party company.
- Internal expertise is minimal, with only a few employees capable of surface-level platform work.
    - This situation arose after a prospective CTO unexpectedly passed away before being hired.
- The third-party IT provider has a long list of needed platform enhancements, making it difficult to get new projects prioritized. Speaker 2 noted, "I need this project to be done like yesterday."
- Speaker 2 mentioned they are currently looking to hire a replacement CTO/COO and want to build an efficient IT team, avoiding the bloat of their previous 40-person team which had too many managers.
- Another desired feature from the competitor's tool is the ability to display and filter all available medical plans (e.g., "114 medical plans available") to answer client questions about plan and carrier availability.
[21:43-24:02] **Successful and rapid completion of this tool could lead to more work, including assistance with hiring technical staff.**
- O'Hara explained that their firm often helps clients who have urgent projects stuck at the bottom of an internal backlog, and a key part of their service is to help hire and onboard the right permanent staff to ensure long-term success.
- Speaker 2 confirmed their current manual process involves running analyses in Excel on numerous census files, which is extremely time-consuming ("takes hours for some").
- Speaker 2 stated that if this project is completed quickly and successfully, it could lead to more work and potentially an engagement to help with hiring resources.
- To secure further work, the project outcome must impress the CEO, Mark Smith.
- `Action Item: @O'Hara - Send an email outlining the necessary information needed to create an estimate for the project. - [No Due Date Mentioned].`
[24:03-27:00] **The proposed engagement model involves a two-phase approach, starting with a one-week discovery phase to define scope and provide an accurate estimate.**
- O'Hara outlined their standard process for projects like this:
    - **Phase 1: Initial Discovery & Scoping:** A one-week engagement to conduct a deep dive into requirements.
        - This involves reviewing materials like the screenshots and any business requirements documents.
        - The team will conduct interviews with key users of the system to understand their precise needs.
        - The goal of this phase is to gain clarity on inputs, outputs, and functionality to create a reliable project estimate.
    - **Phase 2: Development:** Building the actual tool based on the findings from Phase 1.
- O'Hara emphasized that any estimate provided without this initial discovery would be a guess, and that his team prefers to work with small, tight-knit teams using agile development methods to deliver usable components for rapid feedback.
- Speaker 2 confirmed they have a compiled list of desired outputs which should help the process.
[27:02-29:13] **The initial one-week discovery phase is a fixed-cost engagement at $15k, with the fee credited back if the full project proceeds.**
- Speaker 2 asked about the cost of the one-week discovery phase.
- `Key Decision: The initial one-week discovery and planning phase will have a fixed cost of $15,000. - Rationale: To cover the work of interviewing stakeholders, processing requirements, and developing a detailed project plan and backlog.`
- O'Hara clarified the "week" is not 40 continuous hours, but a series of interviews and internal processing time.
- If the client chooses not to proceed with development after the discovery phase, they will receive all the documentation created (project plan, requirements, backlog). O'Hara stated they could take this package to other firms for quotes.
- Speaker 2 asked if the $15k fee was negotiable.
- `Key Decision: O'Hara will apply the $15,000 from the discovery phase as a credit toward the cost of the full development project if Speaker 2's company moves forward with them. - Speaker 2 agreed this was a fair arrangement.`

---

## Transcript

**O'Hara** [00:00]:
So I live in Frisco. Um, so we're yeah, we're right over at Stonebrook and Teal. Um, okay. And so yeah, but then our office here is is yeah Plano in the tollway.

**Speaker 2** [00:12]:
Okay. Yeah I am my first house was at Teal and Maine many years ago in Frisco. And uh now we're in like Legacy Lebanon areaum. Okay, so closer to the star, like probably seven minutes away from the star. So yeah,

**O'Hara** [00:31]:
Very good. Yeah, so over uh maybe Stonebriar area.

**Speaker 2** [00:36]:
We used to live in Stonebriar, now we live in uh the Hills of Kingswood.

**O'Hara** [00:40]:
Oh yeah okay my best friend lives there. He's like when you go in on the circle, he's like the if you go straight, he's like three houses in on the left. So.

**Speaker 2** [00:52]:
Those are all really pretty houses on the main street there. Yeah,

**O'Hara** [00:55]:
It's they've been there for a while, but it's just blown up. It's gotten so big over there. It's crazy.

**Speaker 2** [01:02]:
It really hasum, but yeah so if we need to get together we can, But I also wanted to kind of tell you here is what I really want, and I know everybody says this to you, I am sure, which is I need a job fast, okay, because. You know, I've done a big tech build with like Project Two Hundred and Two. I did that like probably seven or eight years ago when I worked at a company called Carrington. And they they were fantastic. Project Two Hundred and Two was was great, But they, you know, we had to go through a workshop and where I love the workshop, we just don't have time for all that. Okay, We're looking for a very specific tool, and we need to build it um and we're going to shop a few different places. We may even look at something that so far, we haven't found something that exists that would work for us. But if something turns up, we could still consider that. Butum I'll tell you about our company first. So what do you know about Carrington by the way? Cause I knowum they've seen really well.

**O'Hara** [02:04]:
Yeah, so improving kind of our two big, Two largest of our verticals, so we're across I don't know something like sixteen or eighteen different industries. But our number one is financial services and number two is healthcare. And so it's like down the fairway in terms of what you all do, what they do kind of the space that you are talking in. And and so um because I think you were at Magellan previously? And so yeah I was Magellan's been a customer for a number of years. So it's just uh. You know, it's a small world. So and plus they're in Frisco. So having been in Frisco for you know for the last 16 years, I've run into a number of folks.

**Speaker 2** [02:50]:
Okay cool. Wellum so what next Ben does and I'm sure you did a little bit of research before you got on. But basically, there's this whole alternative funding strategy for employers to be able to offer benefits to their employees. Today, most employers are either self funded, so they take the risk on the claims. Like they're actually you know no matter what happens, You know, your employer's got a claim funding account and the dollars come out of it. Or they're fully insured. And the larger the employer, the less likely they are to be fully insured; they're all self funded. But with all of healthcare costs escalating being out of control, It's you know that these employers are facing, you know, double digit budget increases and. It's there's no end in sight. So, Next, ben is a platform for a broker. Who would you know help employers sell benefits to be able to add an employer to our system, our platform. The employer gets access to this platform ; they go in and they add their employees so they can set up a defined contribution plan basically. So, they would move from those old models to. Instead of picking the benefits that I think are going to be good for you and giving you like three options from the same carrier, they give you a budget. And your budget may be let's say six hundred dollars a month. And, our platform facilitates all that all the way to the individual, getting an email, saying your open enrollment period has began. Log in to our platform, start shopping. They log in, they hit a button. And they start shopping for benefits, And they now have maybe sixty plans to choose from because it's based on their individual zip code, and they are basically going into like an individual market. Um, we facilitate the moving of the funds, the monies. So when the employee shops, it looks like I've got a six hundred dollars budget from my employer, and I see what I am responsible for. Um. So all that's fine. I came in late last year to really, you know, build the growth team. Turn this into, you know, a ten x success. We have pretty comparable enrollment in terms of total subscribers compared to the big competitors. And all that's been sort of organic word - of- mouth referrals. But most of the business that has jumped into this from an employer standpoint are really small groups. So brokers that were helping those employers get set up, those conversations were just kind of like, what's your baseline? What do you want to contribute? And they didn't really have to, I hate to say it like this, But I imagine they didn't really have to be too strategic with it because the groups were small enough to where maybe they didn't offer benefits before. So they're just going to give them something and that's new. Yeah. Fast forward to now, The brokers that I am working with and the brokers that are have the most level of interest um are brokers that have never sold this type of program before, and they need help articulating to the employer that there is a cost savings opportunity in moving to this. Okay. And it is a cost savings opportunity. So what we're looking for is. An application, actually. Let me show you a competitor's. I'll show you a competitor system, and it maybe will make a lot more okay sense for you.

**O'Hara** [06:29]:
So it's it's not quite a quoting tool because it's ahead of that. It's almost like a pre- sales tool to help them understand,

**Speaker 2** [06:39]:
Right? And there are imagine there is one hundred and ten different plans out there, okay? And, When an employer gives us a census file and information that says, this the current plan that we offer. This how much it costs us. This how much it can cost the employees. And this what the plan covers. We we then want to take that, Upload it into this tool that would grab the rates from all the carriers because would have access to the data. Just imagine we've got all the rates. We don't but we will have it um. Then, it would be able to spit out what the cost would be for these individuals. It's a roundabout estimate for if they were buying plans on the in the individual market. So, I'm going to show you this, and it's going to make a lot more sense probably. But, we want to be able to create a tool that can be in that can take in a census file without size limits, I mean, Within we can have a reasonable size limit, But it needs to be able to take, you know, a group of even three hundred thousand lives, ideally. And spit out within a matter of seconds, a um really not a PDF but within the same screen, A hey, here is the plan that matches best to what you currently offer. And here is the total cost of that. Yep. And and you, you want to have, we want to have levers, they can adjust. To fine tune that strategy, so at the end of it we can hit okay, done. Create a proposal or whatever we need to do, and the broker can take that to the employer and say hey, Just by moving to this right here, you are going to save two million dollars. Your employees are going to save five hundred thousand. And it's you know so I will show you what the competitor has. I think there is some different spins. We can put on this. Definitely make it more proprietary unique. I think these are just engineers that built it, um, not benefits people.

**O'Hara** [08:45]:
Yeah, that that happens a lot of times. Yeah or accountants do it and then it looks like Excel.

**Speaker 2** [08:52]:
Right okay. Where's that? Sorry? I'm gonna pull this up. I thought I had it since my computer crashed earlier. Um they're gone. By the way, so the couple of tools we have seen out there, and one we have access to because they're a partner of ours. One only will if you if you upload more than 70 employees, it just spins and crashes it freezes up. Um The other one, it will not work if you have more than 700 employees. Okay some serious limitations And. They only do part of the exercise. They don't do the whole exercise Yeah So um hold on I'm. So sorry, I thought I had this I'm gonna have to. Pull it up from my email.

**Kristin Johnson** [09:46]:
Okay, boom, got it. Again,

**Speaker 2** [09:59]:
This isum just what they've come up with. You know I want to be, Do a better job, but I do think it's pretty slick from a tech standpoint. So I am in this would be a screen if I was a broker in the platform. To start, we would want like an HTML that we could keep on an intranet somewhere, But we would like to actually add this to our platform so that when brokers log in, they can use the tool, and we don't have to run it for them. So imagine we're in that world right now. The broker can upload a census. There's a template they have to follow, which is fine. Or they can do manual entry, Then they confirm these are the employees that they want to include in this analysis. They can with an ICHRA program, which is what we offer, you can either set up. Flat budget where everybody gets the same amount, or you can do dynamic budgeting, which is what most people do. Calculating a budget for each employee based on age and.

**O'Hara** [11:06]:
Yeah, that's real person by person.

**Speaker 2** [11:08]:
Mhm. Or by like age band.

**O'Hara** [11:11]:
Okay. Um,

**Speaker 2** [11:12]:
So there's different ways. You can class people with an acre program Yep So. But you kind of get the gist So, if I pick that option I'm sure, there's another step somewhere that says, well, okay, how do you want to break this down? But at a high level, do you see how immediately here. Based on the people I uploaded, I'm sure there was an input for the broker somewhere to type in, what are they currently paying overall. Yep. And then this top number is saying, hey, if you move to Enkra and people enroll in this plan right here, which is closest to what you offer today, it's 6. 3 million versus seven. So that's a immediate savings of 1.

**O'Hara** [11:53]:
1 Well little less than.

**Speaker 2** [11:56]:
Yeah, and here they even break it down to like by the employer contribution. I think in this it's saying it went slightly up, and for this one the employees say so. Then we could adjust things, But in Igra, basically the plans that are available on the market, like I said, there is many carriers, many rates, but they bucket them in by metal. So um there is silver bronze and gold plans. Gotcha. And basically. Right now, What we do is we look at the deductible for the plans, the employer currently offers. And if they're like, you know, a $2,000 deductible will say, well that's kind of like a high bronze. So, we almost need like a low, mid and high aggregate average from each of these metals. And again if you got the data it can be computed pretty easily. Then on this page I think this is really slick. Boom, it highlights all the states where they have employees. On the left, you can benchmark and start to say, okay, What is the ninety six percentile of silver like the highest cost in that area? You can reduce and toggle the cost share of the employer. Change, how much you want to pay towards the dependence, which is another thing we ask. So I could give you like. Essentially, We give you all the pieces of information that are pretty important to informing the quote. Right. That that way, when you build in the logic, it's just computing it. Right. So this PDF,

**O'Hara** [13:39]:
This is from them is that is it public? Is this is this confidential information? These screenshots?

**Speaker 2** [13:46]:
Yeah, I probably shouldn't even show it to you but yeah, this isum This is a competitor's tool and one of our partners, Got access, basically sat in a demo and took screenshots. Gotcha. Okay. So yeah, there wouldn't be a place for you to go and grab it, but you know we I do think it looks really slick, but we want to do something that a little more um intellectual, But similar vibe, I guess is what I'm saying. Well,

**O'Hara** [14:17]:
You still need the same functionality and you might even need a little bit more. But it sounds like the biggest reason for not using it is performance. Like it just it can't hang for for the volumes you're talking about.

**Speaker 2** [14:29]:
Well, And well, this one, actually, this is a true competitor of us. So we wouldn't even be able to use it if we wanted to, because they wouldn't give it to us. Gotcha. This is what they provided their brokers. And so I show it to you because I'm trying to explain like.

**O'Hara** [14:45]:
The functions you want.

**Speaker 2** [14:47]:
Yeah. And so then here you've got like nine employees that have unaffordable coverage. So, there's some affordability rules that you have to follow, just like you do with your group where the employee can't spend more than 9. 96% of their annual income on benefits and you base that off of the lowest cost silver plan. So, If you had set your contribution amount at a level that's too low for some employees because their income is really low, it would flag them, which is helpful. So, you can see, okay, where do we have our problems? And how do I need to adjust these things on the left so that we're taking care of these. Um what this doesn't do is and maybe I'm giving you too much information, but this works really well in that small to mid market space in terms of employer size. When you get to larger and larger employers, We believe Icra is going to be a big play for those large self- funded employers to carve out certain pockets of people. So instead of saying, okay, we're all moving to this, They're going to move maybe everybody just in the state of Texas, or maybe they're going to move everybody that works for this one manufacturing plant because it tends to be the highest cost claims plant because. The people that work there are sickly. I am making this up, but so what? I think would be cool is if when we input, and you know that census file, it tells us what that slicing strategy maybe should be. Yeah, and so hey, here is your overall cost. It should say hey, We've identified the following classing strategy is right. And this is the optimal savings for you, even if you wanted to fund. Set your contribution at maybe a higher amount than the affordability rule. Well,

**O'Hara** [16:37]:
It's almost like that the slicing, the classing strategy becomes another dial here. Like when you're looking at all right, what is it we can adjust? Well, if we class them this way and maybe shift dependent coverage. Um, you know, then that moves us in this direction. Or if we use this strategy, Maybe then we can cover more of the dependent or and still end up in the same ballpark or whatever the case may be.

**Speaker 2** [17:03]:
Right exactly. Um and then you know ultimately be able to just make those changes. So, this is kind of a suggestion, and you know, your core cost savings analysis, but then you'll get it right to where once you've. Confirm this is the strategy I want. Maybe they print out the proposal, they come back and say yes, they went with strategy A. Then perfect world that strategy would feed into our system so that when the employer logs in it already pre- populates those dollar amounts. And you wouldn't have to do that. I think we would just work with you to build the tool and then.

**O'Hara** [17:45]:
Yeah, I think it becomes a natural outgrowth of whether it's it dumps out a file that then y'all and I don't know what your core system is. Um, but whatever it is, I'm confident in it can consume some sort of a batch file if it doesn't have an API. It has an API; it's an easy call. It's just uh here you go. This who this is, and this what this and and you know, just make life easier, because you've already you've already ingested all that data. Right, and walked them through the process of picking.

**Speaker 2** [18:18]:
Right, And we we do need this because here is the other thing that's funny because we have access to like a little bitty tool that basically will just it'll take up to fifty people when we upload it. It'll tell us what the minimum contribution strategy should be, and it'll tell us what the total price is based on the lowest cost sober. Um, but anyway, that tool we're using right now and our brokers are using. Does not feed to our system whatsoever. So we have no idea what's being quoted. We have no idea like who the which accounts, we can't hold them accountable. It's a third party tool. And when I asked them, if we can get the data, they're like, oh yeah, there's not a way. I'm like there's no way there's not a way. Yeah. So I mean send me a raw data file, I don't care. Right But so anyway, I needed to plug into our pipeline somehow and um. You know, whether that's through the platform or it's through just connecting it to our, you know, pipeline tool. That's fine. But yeah, you're right. Like this needs to ultimately be connected. I know we have an SSO for our shopping marketplace partner. I don't know about an API if that exists. Um,

**O'Hara** [19:28]:
But it.

**Speaker 2** [19:29]:
Could be built I'm sure.

**O'Hara** [19:30]:
Yeah What's, the name of the platform that you all use for your core business?

**Speaker 2** [19:36]:
It Is it's proprietary. So, I don't know the system, but I could find out. I can ping the plot ops guys and to be transparent with you, we outsource all of our IT right now. All of it to one company and they don't own the system. We own it, But they know how to use it and they code in it. And all of that. Um, We had, I think, plans to hire a CTO. And then that I didn't this was pre my time, but that individual unexpectedly passed away. And so yeah. And. So we have like one or two people that can work within the platform, but just very surface level. They don't do any updates changes for us. That's all done by this third party. But this third party already has a list like this of things that we need to make our platform to work more efficiently with. And, you know, everything is just time and time and time. And I need this project to be done like yesterday because so before I go there, I guess one last thing, the other thing that thought was really cool is they show based on that census. What are those plans that are available because that's the next big question. Well, what are those? Plans, carriers, et cetera. So you can see one hundred and fourteen medical plans available. Um,

**O'Hara** [20:57]:
And this just goes through them like a list.

**Speaker 2** [21:01]:
Yeah, goes through them like a list, and you can filter right here. See that? Um.

**O'Hara** [21:06]:
Yeah because one hundred and fourteen I don't want to scroll through.

**Speaker 2** [21:10]:
Yeah I know, but when they filter that helps, but anywayum so I just say all that, because this is going to be like a side project. Andum. You know, Randy had told me I call him Randy because he's my buddy from growing up. But that he loved working with you guys, and that there was even a couple people, they ended up hiring. So down the road, I mean, we're going to be we're right now. We're looking for a replacement CTO COO. And then. Well, you know that person will probably get a couple people, but we don't want to get to like a forty person deep IT team. That was really expensive and ended up being a bunch of managers and only like two coders. Yeah. Um, so you know we want to be efficient, but I just want to give you that backstory so you know.

**O'Hara** [22:00]:
Okay. No it is it is something that that we do help our uh, our customers You know, we oftentimes folks come to us when either stuff's on fire or. It gets just like you were saying, you get kicked to the bottom of the backlog, right? And you're like, I actually need to prioritize this. And so we'll come alongside, add that capacity, get things done. But then we want to leave you better than when we were, you know, than when we showed up. And so let us help you find and hire the right people. Uh get those folks going so that you can continue your business uh and moving on. So that uh I appreciate yeah him giving us a good reference week. Have enjoyed working with because they were when we first started it was it was still market. And then it was IHS market and then S and P Global. So I don't know how long Randy's been there or been thereum, but it's been through a lot of changes in the last you know number of years. So yeah,

**Speaker 2** [22:57]:
Market is where he started. He was with Market originally. So yeah, yeah, he just said it was a good experience. And so I thoughtum. You know, I called him because I knew he was the project manager and I thought maybe he knew some coders or something. But you know, My i've got like ten census files right now on my desk, and we're manually running analyses in Excel. But you know, it takes hours for some of these. And so if if this project goes well, you can get it done fast. It's great work. Like I definitely think there could be opportunities to do more work together. You know, we could consider the whole hiring resources, but I think we'll have to kind of wow. I am on the executive team, so there's four EL team members, but we have to wow really Mark Smith, my boss, the CEO. Um to keep that train moving right. Butum right now, the most critical thing is trying to get some estimates. And so what would you need? Do, you want to send me an email with the things you need for me to start thinking about that or?

**O'Hara** [24:03]:
Yeah I mean, So typically the way that we work, especially with something like this where you have uh, you know, you've got a sense of hey, here's kind of what we've what we're looking for. Uh We typically start off and we do it in in two major phases. So the first phase is that initial kickoff. Let's, let's get to working. And then like walking through in a deeper dive, like the screenshots that you showed me saying, all right, here's kind of what we're. Here's what we're looking to do. Here's the functionality, our inputs, our outputs, right? What all it is that we need so that we can say, All right. Here's what we are looking at. Like the team getting together right now, even if we had all of those screenshots, it's going to be whatever the nice word is for a guess of okay. Is this going to take you? You know, is this a six week thing? Is this six months? Is this a year and a half like. We don't actually know, and anybody that tells you, oh, here is what it's going to be, Is probably selling you something and doesn't really know that unless they've built it before. Like if that thatch company said this is how long it took, I would trust that. But outside of that, Like somebody from the outside is not going to be able to give you super accurate. Now I can tell you from that initial and usually that initial is like a week. Right, So in the course of a week, we would sit down with you and probably a couple of your folks that actually use the system because they're the ones that are going to be able to tell you, here's what I need or here's what I don't. You don't want it built by the accounts, right? You want it built by somebody that understands. And. So those are the people we want to talk to for that initial chunk of work. Then, we can give you a reasonable estimate to say this is what we're going to go build. And this is how long it's going to take.

**Speaker 2** [26:00]:
Okay, yeah, And we've got a list we've compiled of like the outputs we want to get. So that probably will help too, because those visuals are just to kind of help me articulate it to somebody. I didn't know, like I wasn't sure if you knew too much about the business, but if you've already got that,

**O'Hara** [26:15]:
Then that's something we can jump on. Um. So if you have like that or a business requirements document or some of those types of things. Absolutely, that helps us kind of scope that initial piece of work to say, do we actually know what it is we're being asked to do? And once we're confident in that clarity, then we can say, all right, here's what we're going after. Because then I also need to know like how many people do I put on this? Because if you put too many people, you are chasing around. There's too many cooks in the kitchen. That's not good for anybody. And so we like to stay very very tight. And very much are into agile development, right? So like how can we get you something that you can see and use as rapidly as possible for maximum feedback.

**Speaker 2** [27:02]:
Cool. Okay. And, then the in terms of like if we do the longer exercise where it's a week of just digging in. And even if we have our requirements, I'm sure there's some of that. Is that pre work? Does that have a cost or do you Yeah,

**O'Hara** [27:16]:
It's but it's a fixed cost. So, it's a fixed cost, and then we will we'll go from there. And, it's not a full. It's not a full week of like we're not together for a full forty hours, right? So, It's like interviews with this, you know, with this role, interviews with this role, interviews with this role. And then from that, we're extracting back to say All, right, give us a couple days to go process this." U m and uh and then we're gonna. And then we're gonna pull together. Here's the scope, but that fixed. It's it's 15 k for that initial that initial week uh to put all that together. And so we can build you out a here's your roadmap, your plan in the backlog of what we're going to go build.

**Speaker 2** [28:02]:
And theum. Do we in if we don't move forward, do we get something for that at all? Like do you have then all the requirements memorialized?

**O'Hara** [28:13]:
Yeah, it's all those documents. So you can take the end of that. You can take that and that you can shop to I'll give you references to a number of other folks that do what we do here in Dallasum that I would trustum and say, You know what? If you feel like you want to go with a different firm, I'm totally in support of that. And here you go. And you can take that to them as a, Here's your project plan to go and build.

**Speaker 2** [28:37]:
Okay. Okay. All right, well, um, I am late for another call to jump on, butum. No, it's okay. No, I appreciate you walking through it with me and then let me circulate that. Um. There's no room for negotiation on that 15000 at all?

**O'Hara** [28:56]:
So how about this? I will give you the 15 k in credit on the second one, if you move forward with us. Okay. That works.

**Speaker 2** [29:06]:
That's that's that's fair, yeah. Okay. Okay. Cool. All right,

**O'Hara** [29:10]:
Thanks David Thank you Lauren Bye.

