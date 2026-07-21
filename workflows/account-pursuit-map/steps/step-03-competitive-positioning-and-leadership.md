---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 03: Competitive Positioning and Leadership / Decision-Maker Map

## MANDATORY EXECUTION RULES

1. You MUST map Improving's actual capabilities to the stated priority themes from step 02 — not a generic capabilities pitch. Each mapping should tie a named Improving strength to a specific stated priority.
2. You MUST name a specific win-wire proof story (a past Improving engagement that is a direct analog to the target's situation) to prepare for technical/leadership conversations.
3. You MUST include an honest competitive note: who else is likely already in the account (large SIs, incumbents), and where Improving realistically wins vs. loses. Do not oversell — name the specific dimensions (senior talent density, delivery speed, lower-ego partnership) versus what Improving concedes (scale, brand recognition).
4. You MUST build a complete org chart covering the full C-suite (CEO and every C-level executive, not just technology-relevant ones) plus one level down (SVPs/VPs reporting to the C-suite), sourced from the company's leadership/investor-relations pages, LinkedIn, and news. This is broader than "who's relevant to the pitch" — it's the full leadership structure.
5. For every name in the org chart, you MUST cross-reference CRM for existing engagement history (past meetings, prior deals, an existing contact record, prior email/Teams threads). If a contact has CRM history, flag it inline as an existing CRM contact with a pointer to the engagement history rather than treating them as cold outreach.
6. You MUST select 3-5 of the most strategically relevant contacts (per step 02's stated priorities) for full narrative profiles: background, "what this role likely means" labeled explicitly as inference (not fact), a specific pitch angle written as an actual quote David could say, and an explicit "what to avoid" for that person. Known-CRM contacts among these 3-5 get relationship-history treatment (what the history shows) instead of cold background/pitch-angle treatment where CRM history exists.
7. Every other name in the org chart (i.e., not selected for full narrative treatment) MUST still be listed in a compact table — name, title, CRM status only. Do not skip anyone in the C-suite + one-level-down scope; compact listing is the minimum bar, not an excuse to omit people.
8. You MUST NOT assert a person's responsibilities, priorities, or receptiveness as fact when it is actually a reasoned guess from title/scope. Label inference as inference every time.
9. Do NOT proceed to step 04 until the org chart is complete for C-suite + one level down, the CRM cross-reference has been run for every name in it, and the 3-5 selected contacts have full profiles built.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Strategic priorities from step 02, entity anchor from step 01
**Output:** Capability-to-priority mapping, win-wire story, competitive note, a complete C-suite + one-level-down org chart with CRM cross-reference, and full narrative profiles for the 3-5 most strategically relevant contacts — stored in accumulated-context for step 05

---

## CONTEXT BOUNDARIES

- This step covers the *organizational* map (titles, roles, reporting lines, individual profiles) — the *personal/relationship* network (YPO, alumni, mutual connections) is a separate track handled in step 04. Do not blend the two here.
- Org chart scope is the full C-suite (CEO plus every C-level executive, not just technology-relevant ones) plus one level down (SVPs/VPs reporting to the C-suite). This is a completeness requirement for the chart itself — it is separate from and broader than the 3-5 contacts who get full narrative profiles.
- Full narrative profiles (background, role inference, pitch angle, what to avoid) are reserved for the 3-5 contacts most strategically relevant to step 02's stated priorities — practically, this is usually the person with budget/decision authority over the pursued capability area plus a few working-level practitioners who'd be actual technical/delivery contacts. Everyone else in the C-suite + one-level-down scope gets a compact table row (name, title, CRM status) and nothing more — do not pad every name with a full narrative to avoid this judgment call, and do not use the compact table as an excuse to drop people from the chart.
- CRM cross-reference changes the research depth calculus, not the org-chart scope: a contact with existing CRM history (past meetings, prior deals, an existing contact record, prior threads) gets relationship-history treatment instead of cold background/pitch-angle treatment, whether or not they land in the 3-5 full-profile set.
- "What this role likely means" is inference from title, scope, and public activity (posts, talks, certifications) — always labeled as such, never asserted as confirmed fact unless a primary source states it directly (e.g., an official press release naming someone's mandate).
- The competitive note should be realistic, not defeatist or falsely confident. Large enterprise accounts almost always have incumbent Big-4/SI relationships on major programs — say so plainly.

---

## YOUR TASK

### 1. Map Improving's capabilities to stated priorities

- For each priority theme from step 02, identify the specific Improving capability area that addresses it (e.g., Data/AI engineering, Application Modernization, Cloud/Azure, Instructional Design/enablement).
- Note any structural advantage relevant to the specific target (e.g., existing Azure-native stack alignment if the target is Azure-based; an existing contract vehicle if active-but-underleveraged).
- Record:
  ```yaml
  capability_mapping:
    - priority_theme: "{Theme name from step 02}"
      improving_capability: "{Specific capability area}"
      why_it_fits: "{1-2 sentences}"
  structural_advantages:
    - "{e.g., 'Azure-native stack alignment' or 'Existing MSA eliminates procurement friction'}"
  ```

### 2. Name the win-wire proof story

- Identify one past Improving engagement that is a direct analog to the target's situation (similar problem shape, similar industry, similar scale).
- Record:
  ```yaml
  win_wire_story:
    client: "{Past client, if clearable to name — otherwise describe genericized}"
    engagement: "{What was built/delivered}"
    parallel_to_target: "{Why this is a direct analog to the target's situation}"
    prep_note: "Prepare a clean one-page version before any technical meeting."
  ```

### 3. Write the honest competitive note

- Identify likely incumbents: large SIs (Accenture, Deloitte, etc.), any known incumbent vendor relationships (from web search, job postings mentioning existing tools/partners, or CRM if documented).
- State plainly where Improving wins (senior talent density, delivery speed, lower-ego partnership, embedded delivery) and where it doesn't (scale, brand, headcount, global footprint).
- Record:
  ```yaml
  competitive_note:
    likely_incumbents: ["{Name and what they likely own}", ...]
    where_improving_wins: ["{Specific dimension}", ...]
    where_improving_loses: ["{Specific dimension}", ...]
    positioning_summary: "{1-2 sentences on how to frame this honestly to the target}"
  ```

### 4. Build the full C-suite + one-level-down org chart

- Source from the company's leadership/investor-relations pages, LinkedIn, and news: the CEO, every C-level executive (not just technology-relevant roles — include CFO, COO, CHRO, CMO, General Counsel, etc. alongside CTO/CIO/CDO), and one level down (SVPs/VPs reporting to the C-suite).
- Record every name found, regardless of whether they'll get a full profile:
  ```yaml
  org_chart:
    - name: "{Full name}"
      title: "{Title}"
      reports_to: "{If findable}"
      crm_status: "existing-crm-contact" | "no-crm-history" | "not-checked"
      source: "{Leadership page URL / LinkedIn URL / news URL}"
  ```
- Cap this list's presentation compactly in the final output — it should read as a scannable org chart, not a research dossier. If the company's leadership page is unusually large (e.g., 20+ SVPs), keep all of them in the data but flag in the note that the list is long.

### 5. Cross-reference CRM for every name in the org chart

- For every name recorded in Task 4, check CRM for existing engagement history: past meetings, prior deals/opportunities, an existing contact record, or prior email/Teams threads.
- Update each org chart entry's `crm_status` to `existing-crm-contact` (with a pointer to the engagement history) or `no-crm-history`. Never leave an entry at `not-checked` once this task completes.
- If CRM is not accessible in this session, set `crm_status: "not-checked"` for all entries and state plainly that the CRM cross-reference could not be run — do not guess at engagement history.
- This changes downstream research depth: a contact flagged `existing-crm-contact` gets relationship-history treatment (Task 6) rather than being treated as a cold lead.

### 6. Select and build full narrative profiles for the 3-5 most strategically relevant contacts

- From the org chart, select the 3-5 contacts most strategically relevant given step 02's stated priorities — typically whoever has budget/decision authority over the pursued capability area, plus a few working-level practitioners who'd be the actual technical/delivery contacts.
- For each selected contact, research via LinkedIn, company leadership pages, and news, then populate:
  ```yaml
  leadership_profiles:
    - name: "{Full name}"
      title: "{Title}"
      reports_to: "{If findable}"
      crm_status: "existing-crm-contact" | "no-crm-history"
      background: "{Career history, prior companies, notable credentials/certifications, public activity — OR if existing-crm-contact, summarize the CRM engagement history instead: what was discussed, when, by whom, outcome}"
      role_inference: "{'What this role likely means' — explicitly labeled: 'Inference from title/scope: ...'}"
      pitch_angle: "\"{An actual quote David could say to this person — calibrated to their background/likely pain point, or to the prior engagement history if existing-crm-contact}\""
      what_to_avoid: "{Specific guidance — e.g., 'Don't lead with a capabilities list' or 'Don't mention the lost deal as a credential' or, for existing CRM contacts, 'Don't pitch as new business — acknowledge the prior relationship'}"
      source: "{LinkedIn URL / leadership page URL / news URL / CRM record reference}"
  ```
- If a person's exact scope is ambiguous (e.g., could sit in one of two orgs), note the ambiguity and what to confirm before the first meeting rather than guessing.
- Every org chart name not selected for a full profile stays in the compact table from Task 4 — do not duplicate a stripped-down profile for them elsewhere.

---

## SUCCESS METRICS

- Every stated priority theme mapped to a specific Improving capability
- One win-wire story named with a clear parallel to the target's situation
- Competitive note is honest — names specific dimensions won and conceded, not generic confidence
- Org chart is complete for C-suite (full, not just tech-relevant) + one level down, sourced and cited
- CRM cross-reference run for every name in the org chart, with a definite status (existing-crm-contact / no-crm-history / not-checked) — never left blank
- 3-5 contacts selected for full narrative profiles, each including background-or-CRM-history, inference-labeled role interpretation, a quotable pitch angle, and an explicit what-to-avoid
- Remaining org chart names listed compactly (name/title/CRM-status only) — not padded, not dropped
- No role responsibility or receptiveness asserted as fact without primary-source backing

## FAILURE MODES

| Failure | Action |
|---------|--------|
| No clear analog win-wire story exists | Say so plainly rather than stretching a weak parallel. Note: "No strong direct analog identified — closest comparable is {X}, but the fit is partial." |
| Incumbent vendor relationships unknown | State "Likely incumbents unknown — no public signal found" rather than guessing at named competitors. |
| Leadership page doesn't list one level down completely | Supplement with LinkedIn org search and news; state plainly if the one-level-down list is likely incomplete rather than presenting it as exhaustive. |
| CRM not accessible this session | Set `crm_status: "not-checked"` for all org chart entries and state plainly that the cross-reference could not be run. Do not guess at engagement history. |
| Leadership profile has minimal public footprint | Report what's found; state plainly the limitation (e.g., "Limited public information — 2 sources checked, no LinkedIn profile located"). Do not pad with generic filler. |
| Role scope ambiguous between two possible orgs | Flag as an open item to confirm before outreach rather than asserting one interpretation as fact. |
| Pitch angle risks sounding like a generic sales pitch | Rewrite to be peer-to-peer and specific to the person's background/public activity, not a capabilities-list recitation. |
| Org chart is unusually large (20+ names one level down) | Keep all names in the data; note in the compact table that the list is long rather than silently truncating it. |

---

## NEXT STEP

Read fully and follow: `step-04-icp-account-9box.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
