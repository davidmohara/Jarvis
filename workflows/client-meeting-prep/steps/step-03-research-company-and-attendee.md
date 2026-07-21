---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 03: Research the Company and Attendee — Disambiguate First

## MANDATORY EXECUTION RULES

1. You MUST confirm company identity before writing any company content. If the company name or acronym is ambiguous, verify it via domain match (email domain from step 02's evidence) or other unambiguous evidence (LinkedIn company link in the thread, explicit URL, etc.) before proceeding.
2. If ambiguity existed and was resolved, you MUST include a disambiguation note in the accumulated context so it carries into the final prep sheet.
3. You MUST calibrate the depth and framing of this research to the meeting_classification set in step 02 — do not build a generic discovery-call research packet for a peer/relationship call, and do not undersell research for a real sales-sourced opportunity.
4. You MUST NOT let web research override or contradict the reason_for_call or meeting_classification established in step 02 from email evidence. Web research fills in identity and background — it does not re-litigate why the meeting exists.
5. Do NOT proceed to step 04 until company identity is confirmed (or the ambiguity is explicitly flagged as unresolved) and attendee bio research is complete.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Attendee/company from step 01, reason_for_call + meeting_classification + evidence from step 02
**Output:** Confirmed company profile, attendee bio, "read on them" interpretation — stored in accumulated-context

---

## CONTEXT BOUNDARIES

- This step is identity and background research only. The "why are we meeting" question was already answered in step 02 from email evidence — do not re-derive it here from web sources.
- If the company name is a common acronym or shared by multiple unrelated companies (e.g., "OFS" matching both a furniture manufacturer and an unrelated company), this is exactly the failure mode that produced `err-20260720T144623-LSBA9A`. Treat any acronym or short/generic company name as ambiguous by default until confirmed.
- Calibration matters: a peer/relationship call gets a lighter research touch focused on shared context and credibility; a sales-sourced lead gets fuller company/buyer-persona research; an internal review pulls from CRM/account history first.

---

## YOUR TASK

### 1. Disambiguate the company

- Pull the email domain from step 02's evidence (e.g., `@ofs.com`). This is your primary disambiguation signal.
- Cross-reference the domain against the company you're about to research. If a web search for the company name surfaces multiple distinct organizations (different industries, different HQs, same name/acronym), do not pick the most prominent one by default — match the domain, and secondarily match any other detail from the email thread (signature block, referenced products/services, mentioned colleagues).
- If you cannot confirm the match with reasonable confidence, do not silently guess. Record it as an unresolved disambiguation flag to surface in the final prep sheet's Open Questions section.
- Once confirmed (or flagged unresolved), record:
  ```yaml
  company_disambiguation:
    ambiguous: true/false
    resolution_method: "email domain match" | "signature block reference" | "unresolved"
    note: "{One line if ambiguity existed, e.g., 'OFS confirmed as the contract-furniture manufacturer (Huntingburg, IN) via ofs.com email domain — not to be confused with [other OFS].'}"
  ```

### 2. Build the company profile

Research and populate:

```yaml
company_profile:
  company: "{Confirmed name}"
  industry: "{Industry}"
  hq: "{City, State/Country}"
  founded: "{Year, if findable}"
  size: "{Employee count / revenue band, if findable}"
  known_tech_stack: "{If findable/relevant}"
  email_domain: "{domain from step 02 evidence}"
```

Depth of research here should match the classification from step 02 — a sales-sourced lead warrants checking Improving's buyer persona repository (see Chase's Shared Conventions) for fit; a peer/relationship call does not need buyer-persona mapping at all.

### 3. Build the Company Overview (deeper narrative)

This is distinct from the company_profile table above. That table is "at a glance" facts (HQ, size, industry). The Company Overview is the narrative layer: what's actually going on at this company right now that's relevant to the meeting — recent news, strategic initiatives, competitive/market pressures. It renders in the prep sheet right after "Who They Are" and before the attendee bio, because it's still establishing "who they are" — just at depth, not the reason for the call.

**Research source priority — work in this order, do not skip ahead:**
1. **Company's own website** — primary source. Homepage, About, product/service pages, leadership page, newsroom/press releases, investor page if public.
2. **Web search** — recent news, press coverage, funding events, leadership changes, analyst coverage, strategic announcements from the last 6-12 months.
3. **CRM** — prior Improving engagement history with this company: past proposals, account notes, prior opportunities. (Skip if no CRM connector active or no history exists.)
4. **Clay (Mesh)** — supplemental only, after the above are exhausted. Use it to fill gaps or add color from David's personal relationship data. Never present Clay data as an authoritative company overview source, and never let it substitute for the website/web-search/CRM sequence above.

**Depth by contact_depth (from step 02):**
- **first-touch**: Full overview. Work through all four sources in priority order. Cover recent news, strategic initiatives, and competitive/market pressures relevant to this meeting — this is the primary anchor for a cold or first-time contact, so it should read as a real narrative, not a bullet dump.
- **repeat-meeting**: Brief refresh only. Skip re-researching stable background already covered in a prior prep sheet (if step 01 found one, pull it forward and only look for what's changed). Focus on: what's new since the last touchpoint — org changes, new initiatives, competitive shifts. If nothing material has changed, say so plainly rather than padding.

Populate:
```yaml
company_overview:
  depth: "full | brief-refresh"
  narrative: "{2-4 sentences for full depth; 1-2 sentences for brief refresh — the actual story, not a list of facts already in company_profile}"
  recent_news:
    - "{Item + source + rough date, if findable}"
  strategic_initiatives:
    - "{Named initiative or direction, if findable}"
  competitive_or_market_pressures:
    - "{Relevant pressure, if findable — e.g., a named competitor move, a market shift, a regulatory change}"
  sources_used: "{e.g., 'Company website + 2 web search results' or 'Company website only — no notable web coverage found' or 'CRM account notes + brief web refresh'}"
  crm_history: "{Prior Improving engagement with this company, if any, else 'No prior CRM history found' or 'CRM not checked — no connector active'}"
```
If nothing findable beyond company_profile's basic facts, state that plainly in `narrative` (e.g., "Limited public narrative beyond basic company facts — no notable recent news or announcements found.") rather than inventing texture.

### 4. Build the attendee bio

Research (web, LinkedIn, prior knowledge layer entries) and populate:

```yaml
attendee_bio:
  name: "{Full name}"
  title: "{Title — prefer what was stated in the email thread from step 02 if it conflicts with web sources}"
  education: "{If findable}"
  location: "{If findable}"
  affiliations: "{Professional groups, boards, associations — especially relevant if step 02 classified this as a peer/referral intro through such a group}"
  public_facing_work: "{Publications, talks, podcasts, notable public work}"
  linkedin: "{URL if found}"
  read_on_them: "{One line interpreting what this person's role and background mean for how to calibrate the conversation — e.g., 'Strategy-focused exec, not a buyer — calibrate as peer exchange, not a pitch.'}"
```

### 5. Cross-check against CRM/knowledge layer (if applicable)

- If meeting_classification from step 02 is "internal-review" or the company already has CRM history, pull prior opportunity/account records and prior meeting notes. This takes priority over fresh web research for this company.
- If a prior prep sheet exists for this person (flagged in step 01), pull forward any durable facts (title, bio) rather than re-researching from scratch — but re-verify anything time-sensitive (current title, current company).

### 6. Pull LinkedIn mutual/common connections

- If the attendee's LinkedIn URL was found in step 3, use the Claude in Chrome browser tools (load via `ToolSearch` if needed: `mcp__claude-in-chrome__navigate`, `mcp__claude-in-chrome__get_page_text`, `mcp__claude-in-chrome__tabs_context_mcp`) to navigate to the attendee's LinkedIn profile while logged in as David.
- Read the "mutual connections" module on the profile (typically shown near the top of the profile or under a "X mutual connections" link).
- Capture only **names and companies** of mutual connections — no bios, no relationship history, no speculation about how or why they're connected. This is a name/company list, nothing more.
- If there are more than 8 mutual connections, capture the total count and select the top 5–8 most senior/relevant ones for display (favor titles like founder, C-suite, VP, director over individual contributors when the info is visible in the connections list).
- Record:
  ```yaml
  common_connections:
    status: "found" | "zero" | "unavailable"
    total_count: {N or null}
    displayed:
      - name: "{Full name}"
        company: "{Company}"
      - name: "{Full name}"
        company: "{Company}"
    note: "{One line if capped, e.g., 'Showing top 6 of 14 mutual connections.' Or if unavailable: 'LinkedIn profile not accessible — could not load mutual connections module.' Or if zero: 'No mutual connections shown on LinkedIn.'}"
  ```
- If the attendee's LinkedIn URL was not found, or navigation/read fails for any reason, or the profile shows zero mutual connections, still populate `common_connections` with the appropriate `status` and a plain-language `note` — do not skip this field. It must always carry a state into step 04 so the prep sheet section is never silently omitted.

---

## SUCCESS METRICS

- Company identity confirmed via domain match or other hard evidence, OR explicitly flagged as unresolved
- Company profile populated with available fields; missing fields left blank rather than guessed
- `company_overview` populated per source priority (website → web search → CRM → Clay supplemental-only), depth matched to `contact_depth` (full for first-touch, brief refresh for repeat-meeting) — never left blank
- Attendee bio populated, with any title conflict between email evidence and web sources resolved in favor of the email thread
- "Read on them" line calibrated to the meeting_classification, not generic
- No company-identity guess made silently
- `common_connections` populated with a definite status (found/zero/unavailable) — never left blank

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Company name/acronym matches multiple unrelated organizations and domain evidence is inconclusive | Do not pick one. Flag explicitly: "Company identity unresolved — {name} matches multiple organizations; email domain {X} suggests {candidate} but confidence is not high enough to assert." Carry to Open Questions in step 04. |
| No notable company news/initiatives findable beyond basic facts | State plainly in `company_overview.narrative` rather than padding with generic industry filler. Do not present speculation as a strategic initiative. |
| Clay surfaces company context that contradicts or isn't corroborated by the website/web search/CRM | Do not include it as fact. Either omit or note it explicitly as an unverified, supplemental signal from Clay — never presented at the same confidence level as the primary sources. |
| Attendee has minimal public footprint | Report what's found. State plainly: "Limited public information found — {N} sources checked." Do not pad with generic filler. |
| Web-sourced title contradicts the email thread's stated title | Use the email-sourced title. Note the discrepancy internally in case it's worth a quick clarifying question, but do not present both as equally valid in the final sheet. |
| CRM unavailable for an internal-review classification | Proceed with web + knowledge layer only, note the CRM gap. |
| LinkedIn profile unreachable, no LinkedIn URL found, or Chrome tools unavailable | Set `common_connections.status: "unavailable"` with a plain note (e.g., "LinkedIn profile not accessible — no URL found in research" or "Browser tools unavailable for this run"). Do not omit the section or leave it blank. |
| LinkedIn profile loads but shows zero mutual connections | Set `common_connections.status: "zero"`, `total_count: 0`, empty `displayed` list, note: "No mutual connections shown on LinkedIn." |

---

## NEXT STEP

Read fully and follow: `step-04-build-prep-sheet.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
