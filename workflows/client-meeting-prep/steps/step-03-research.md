---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 03: External Research

## MANDATORY EXECUTION RULES

1. You MUST search for recent company news (last 90 days). Walking into a meeting without knowing the client's recent headlines is amateur.
2. You MUST check for executive changes at the client org. New leadership changes buying priorities overnight.
3. You MUST pull recent email and Teams threads with the specific attendees — not just the account. Know what has been discussed with the people in the room.
4. Do NOT fabricate research. If a search returns nothing, say "No recent news found." Do not invent context.
5. Do NOT spend excessive time on deep research for routine relationship meetings. Scale depth to meeting importance.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Meeting details from step 01, account context from step 02, web search tools, M365 MCP
**Output:** External research and attendee-specific communication history stored in working memory for step 04

---

## CONTEXT BOUNDARIES

- Research depth scales with meeting type:
  - `new-business` or `qbr` — full research (all sections)
  - `active-deal` — news + financials + attendee threads
  - `relationship` or `renewal` — news headlines + attendee threads
  - `escalation` — skip news, focus entirely on email/Teams history to understand the issue
- Financial data only applies to public companies. Skip for private companies.
- Tech stack data from ZoomInfo or similar is a bonus, not a requirement.
- All web research is context-gathering. Do not make recommendations in this step.

---

## YOUR TASK

### Sequence

1. **Search for recent company news (last 90 days):**
   - Company name + "news" via web search
   - Capture: headline, date, source, one-line summary
   - Prioritize: leadership changes, funding/M&A, product launches, layoffs, earnings, partnerships
   - Flag anything that directly relates to services the controller's organization provides
   - Limit to 5-7 most relevant items

2. **Check for key executive changes:**
   - Search "[company name] executive appointments" or similar
   - Check if any meeting attendees recently changed roles
   - New CTO/CIO/VP Eng = potential new budget priorities
   - New CEO/CFO = potential strategic shift
   - If found: note who changed, from what to what, when

3. **Pull financial highlights (public companies only):**
   - Recent earnings: revenue trend (up/down/flat), key commentary
   - Guidance: are they investing or cutting?
   - Stock performance: notable movement (> 10% in 90 days)
   - If private: skip and note "Private company — no public financials"

4. **Identify industry trends relevant to the conversation:**
   - What is this client's industry doing right now?
   - Any regulatory changes, technology shifts, or market dynamics?
   - How do these trends create opportunities for the controller's services?
   - Keep to 2-3 bullet points — enough for an informed comment, not a lecture

5. **Search for tech stack (if available):**
   - ZoomInfo, BuiltWith, or similar tools
   - What technologies does the client use?
   - Any known modernization initiatives?
   - Overlap with the controller's org capabilities?
   - If unavailable: note "Tech stack data not available — consider asking in the meeting"

6. **Pull attendee-specific email threads** via M365 MCP (`outlook_email_search`):
   - Search by each external attendee's email address (last 30 days)
   - For each relevant thread:
     - Date, subject, key points
     - Commitments made (by either side)
     - Open questions or unresolved items
     - Tone: positive, neutral, contentious
   - Flag any thread where the controller committed to something and hasn't delivered

7. **Pull attendee-specific Teams threads** via M365 MCP (`chat_message_search`):
   - Search by each external attendee's email address (last 30 days)
   - Capture recent discussion topics, decisions, or open threads
   - Note anything that suggests the attendee's current priorities or concerns

8. **Store results** in working memory:
   ```
   external_research:
     company_news:
       - headline: ...
         date: YYYY-MM-DD
         source: ...
         summary: ...
         relevance: direct | contextual
     executive_changes:
       - name: ...
         old_role: ...
         new_role: ...
         date: YYYY-MM-DD
         impact: ...
     financials:
       available: true/false
       revenue_trend: up | down | flat
       guidance: investing | cutting | neutral
       stock_movement: ...
       summary: ...
     industry_trends:
       - trend: ...
         implication: ...
     tech_stack:
       available: true/false
       technologies: [...]
       modernization_signals: [...]
   attendee_threads:
     - attendee: ...
       emails:
         - date: YYYY-MM-DD
           subject: ...
           key_points: ...
           commitments: [...]
           open_items: [...]
           tone: positive | neutral | contentious
       teams:
         - date: YYYY-MM-DD
           topic: ...
           summary: ...
   unfulfilled_commitments:
     - commitment: ...
       made_by: controller | team
       date: YYYY-MM-DD
       status: open
   ```

---

## SUCCESS METRICS

- Recent company news captured (or confirmed as none)
- Executive changes checked
- Financials summarized for public companies
- Industry trends identified (2-3 relevant points)
- Attendee-specific email and Teams threads reviewed
- Unfulfilled commitments flagged

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Web search returns nothing relevant | Note: "No recent news found for [company]." This happens with smaller companies. Proceed. |
| M365 search unavailable | Proceed without email/Teams data. Note: "Communication history unavailable — review your email manually before the meeting." |
| Company name is ambiguous (common name) | Add industry or location qualifiers to narrow the search. If still ambiguous, note the limitation. |
| Too much data (very active account) | Filter to most recent and most relevant. Cap email threads at 10, news at 7. The brief should inform, not overwhelm. |
| ZoomInfo or tech stack tool unavailable | Skip. Note: "Tech stack data not available." This is optional context, not critical. |

---

## NEXT STEP

Read fully and follow: `step-04-build-brief.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
