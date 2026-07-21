---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 05: Referral & Partner Network — Two Separate Tracks

## MANDATORY EXECUTION RULES

1. You MUST keep this research track structurally separate from the leadership/org map built in step 03. This step covers warm relationship paths (YPO, personal ties, existing engagement sponsors, alumni, mutual connections) and Improving's partner network — not organizational roles. Do not merge either subsection with step 03's org map in output.
2. You MUST also keep the two subsections within this step — Referral Network and Partner Network — clearly labeled and separate from each other in output, since the research methods differ (personal-network/LinkedIn lookup vs. partner tech-stack inference and CRM partner records). Do not blend them into one list.
3. You MUST explicitly mark each contact/path in both subsections as **confirmed** or **needs-verification**. Never assert a relationship or tech-stack usage exists without a citable basis (David's direct knowledge, an existing CRM contact record, a documented prior interaction, a verified LinkedIn connection, or a cited public source for tech-stack signals).
4. You MUST reuse the LinkedIn mutual-connections lookup mechanics already built in `workflows/client-meeting-prep/steps/step-03-research-company-and-attendee.md` (Task 6) for any leadership-profile contact from step 03 where a warm path might exist — same tool sequence (`mcp__claude-in-chrome__navigate`, `get_page_text`, `tabs_context_mcp`, loaded via ToolSearch if deferred), same capture discipline (names and companies only, no bios or relationship speculation).
5. You MUST cap displayed mutual-connections output compactly: top 5-8 most senior/relevant, with a total-count note when capped. Do not dump a full list. The same capping discipline applies to the partner list (Improving's fixed 8-partner list, never expanded) and to any partner-side contact list.
6. Do NOT invent a referral path or a tech-stack usage claim. If no warm path exists to a given contact, or no public signal supports a partner's tech-stack usage, say so — "no warm path identified" and "no public signal found" are valid, useful findings.
7. Do NOT proceed to step 06 until every leadership-profile contact from step 03 has been checked for a warm path (even if the answer is "none found"), and every one of Improving's 8 partners has been checked against the target's public tech-stack signals (even if the answer is "no signal found").

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Leadership profiles from step 03, David's known personal/professional network (YPO, alumni, prior colleagues), Clay (if connected), Improving's fixed partner list, public tech-stack signals for the target, Improving's CRM partner records
**Output:** A referral network map and a partner network map, each separate from step 03's leadership map and from each other, with every contact/path/tech-stack claim tagged confirmed or needs-verification — stored in accumulated-context for step 06

---

## CONTEXT BOUNDARIES

- "Referral network" means: YPO relationships, personal ties, existing engagement sponsors (if active-but-underleveraged per step 01), alumni networks, mutual connections found via LinkedIn, and any named individual who has offered or could offer an introduction (e.g., "Cole at [Company] can refer into contacts at the target").
- This is not the org chart. A referral-network contact might not work at the target company at all (e.g., a YPO peer, a mutual connection who could make an intro).
- "Partner network" means: Improving's own current partner relationships — **AWS, Microsoft, GCP, Confluent, Databricks, SpaceX/xAI, Snowflake, SAP**. This is Improving's authoritative, fixed partner list — not an illustrative example, and not to be expanded with other vendors or narrowed to a subset. For the target account, research (a) which of these 8 partners the account likely already uses, based on public tech-stack signals, and (b) contacts at that partner company who could help (account team, co-sell/alliance contacts).
- Partner research method differs from referral research: it starts from public tech-stack signals about the target (job postings mentioning the platform, press releases, case studies, cloud-provider customer references, conference sponsorships) rather than David's personal network or LinkedIn.
- Depth of the referral-network track does not depend on step 01's engagement-shape determination the way step 05's phased path does — run the full referral-network research regardless of active-but-underleveraged or cold/lost-re-entry, since warm paths matter in both cases (though for cold/lost re-entry, an existing sponsor from the lost deal is a distinct and important warm path to check). The partner-network track runs the same way regardless of engagement shape as well.

---

## YOUR TASK

### 1. Check for existing engagement sponsors (if applicable)

- If step 01 determined active-but-underleveraged, identify the current engagement's sponsor(s) and whether they can make warm introductions into the capability areas being pursued.
- If step 01 determined cold/lost-re-entry with a documented lost deal, identify the original deal's buyer/sponsor as a specific warm (if awkward) re-entry path — this is often the most direct path back in, even after a loss.
- Record:
  ```yaml
  existing_sponsor_path:
    applicable: true/false
    sponsor: "{Name/role, if applicable}"
    status: "confirmed" | "needs-verification"
    note: "{What this path could open, or why it's not applicable}"
  ```

### 2. Map YPO, alumni, and personal ties

- Check for any known YPO relationship, personal tie, or alumni connection David has to individuals at or connected to the target company. Use David's known network (do not fabricate a tie that doesn't exist).
- For each identified tie, record who it connects to, how direct the path is (direct tie vs. one hop via a named intermediary), and confirmation status.
- Record:
  ```yaml
  personal_network_ties:
    - contact: "{Name at or connected to the target}"
      tie_type: "YPO" | "personal" | "alumni" | "prior-colleague" | "other"
      path: "{Direct David tie, or via named intermediary — e.g., 'Direct YPO relationship' or 'Via Cole at [Company]'}"
      status: "confirmed" | "needs-verification"
      note: "{Any relevant context}"
  ```

### 3. Check Clay (if connected) for enrichment

- If a Clay/Mesh connector is active, use it to enrich known contacts with warmth signals or additional relationship data. Treat Clay output as supplemental — never authoritative on its own. If Clay is not connected, note it and skip.

### 4. Run LinkedIn mutual-connections lookup for each step-03 leadership profile

- For each leadership profile built in step 03, check whether a LinkedIn URL was found. If so, load the Claude in Chrome tools (`ToolSearch` for `mcp__claude-in-chrome__navigate,get_page_text,tabs_context_mcp` if not already loaded) and navigate to the profile while logged in as David.
- Read the mutual-connections module. Capture names and companies only — no bios, no speculation.
- Cap at top 5-8 most senior/relevant if the list exceeds 8, noting the total count.
- Record per profile:
  ```yaml
  mutual_connections:
    - profile: "{Leadership contact name from step 03}"
      status: "found" | "zero" | "unavailable"
      total_count: {N or null}
      displayed:
        - name: "{Name}"
          company: "{Company}"
      note: "{e.g., 'Showing top 6 of 14 mutual connections.' or 'LinkedIn profile not accessible.' or 'No mutual connections shown.'}"
  ```
- Never leave this blank for a profile that has a LinkedIn URL — always populate a definite status.

### 5. Synthesize the referral network summary

- Roll up Tasks 1-4 into a single view, explicitly separate from step 03's leadership map and from the partner network below:
  ```yaml
  referral_network:
    existing_sponsor_path: {from step 1}
    personal_ties: [{from step 2}]
    mutual_connections_by_contact: [{from step 4}]
    strongest_path: "{Which single path is the warmest overall, and why — e.g., 'Direct YPO tie to [Name] is the warmest, most senior path in the account.'}"
  ```

### 6. Research the Partner Network

- Improving's current partner list (fixed, authoritative — use exactly these 8, do not add or drop any): **AWS, Microsoft, GCP, Confluent, Databricks, SpaceX/xAI, Snowflake, SAP.**
- For each of the 8 partners, research whether the target account likely already uses that platform, based on public tech-stack signals: job postings mentioning the platform, press releases, case studies, cloud-provider customer references, conference sponsorships, or other citable public evidence. Cite the source for every claim, same discipline as the rest of this workflow.
- Where a partner is likely in use, identify contacts at that partner company who could help — account team members, co-sell/alliance contacts — via CRM partner records, David's own knowledge, or public sources (e.g., LinkedIn search for "[Partner] account team" + target account industry/region). Tag each contact confirmed or needs-verification.
- Record:
  ```yaml
  partner_network:
    - partner: "AWS" | "Microsoft" | "GCP" | "Confluent" | "Databricks" | "SpaceX/xAI" | "Snowflake" | "SAP"
      likely_in_use: "confirmed" | "likely" | "no-signal-found"
      evidence: "{Specific citable signal — job posting title/URL, press release, case study, conference sponsorship — or 'No public signal found' if none}"
      partner_contact:
        name: "{Name, if identified}"
        role: "{e.g., 'AWS account team', 'Databricks alliance manager'}"
        status: "confirmed" | "needs-verification" | "not-identified"
        how_they_could_help: "{e.g., 'Potential co-sell intro if AWS is the account's primary cloud' — or 'Not identified — would need to go through Improving's partner relationship owner'}"
      source: "{URL or CRM reference}"
  ```
- Cap this list at exactly the 8 partners — do not pad with additional vendors even if other tech-stack signals surface (e.g., Oracle, GCP-adjacent tools). Note those separately as "observed but not an Improving partner" only if directly relevant to positioning, not as part of this list.
- If CRM partner records aren't accessible this session, note it and rely on public sources plus David's direct knowledge, same fallback discipline as Task 3's Clay handling.

### 7. Synthesize the partner network summary

- Roll up Task 6 into its own view, kept separate from `referral_network`:
  ```yaml
  partner_network_summary:
    partners_checked: 8
    likely_in_use: ["{Partner name}", ...]
    no_signal: ["{Partner name}", ...]
    strongest_partner_path: "{Which partner relationship offers the clearest co-sell/intro opportunity, and why — or 'None identified' if no partner contact could be confirmed or found.}"
  ```

---

## SUCCESS METRICS

- Referral network kept structurally separate from step 03's leadership/org map and from the partner network
- Partner network kept in its own clearly labeled subsection, separate from the referral network, reflecting the different research method (tech-stack inference + CRM partner records vs. personal-network/LinkedIn lookup)
- Every contact/path/tech-stack claim explicitly tagged confirmed, needs-verification, or (for tech-stack signals) no-signal-found
- Existing sponsor path (or lost-deal buyer, if applicable) explicitly checked
- LinkedIn mutual-connections lookup run for every step-03 leadership profile with a findable URL, each with a definite status (found/zero/unavailable)
- Mutual-connections output capped compactly (top 5-8) with a total-count note when capped
- All 8 of Improving's partners (AWS, Microsoft, GCP, Confluent, Databricks, SpaceX/xAI, Snowflake, SAP) checked against the target's public tech-stack signals, each with a definite likely_in_use status and cited evidence
- Partner list capped at exactly 8 — no added vendors, no omissions
- A single "strongest path" identified for the referral network, and a single "strongest partner path" identified for the partner network, both carried to step 05

## FAILURE MODES

| Failure | Action |
|---------|--------|
| No YPO/personal/alumni ties found | State plainly: "No personal network ties identified to this account." Do not fabricate one to fill the section. |
| LinkedIn profile unreachable, no URL found, or Chrome tools unavailable | Set that profile's `mutual_connections.status: "unavailable"` with a plain note. Do not omit the entry. |
| Clay not connected | Note: "Clay not connected — referral network built from direct knowledge and LinkedIn only." Proceed. |
| Existing sponsor identified but unwilling/unable to make intros (per prior knowledge) | Note this explicitly rather than presenting the sponsor as a guaranteed warm path. |
| Too many mutual connections to list | Cap at top 5-8 most senior/relevant, note the total count, per Mandatory Execution Rule 5. |
| No public tech-stack signal found for a given partner | Set `likely_in_use: "no-signal-found"` and state so plainly. Do not guess based on industry norms alone. |
| CRM partner records not accessible this session | Note it explicitly; build the partner section from public sources and David's direct knowledge only. |
| No partner contact identifiable even where tech-stack usage is confirmed | Set `partner_contact.status: "not-identified"` and note that David would need to go through Improving's partner relationship owner — do not fabricate a name. |

---

## NEXT STEP

Read fully and follow: `step-06-synthesize-and-deliver.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
