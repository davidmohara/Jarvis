# Step 03: Events and Context

## MANDATORY EXECUTION RULES

1. You MUST gather events from both sides -- the controller's events AND known partner events.
2. You MUST frame each event with a specific collaboration opportunity, not just "attend together."
3. You MUST include the office/space offering if the controller's organization has offices in the partner's territory.
4. You MUST search for recent partner news and program updates.
5. Do NOT fabricate events or news. If web search yields nothing, say so and move on.
6. Do NOT proceed to step 04 until events, news, and context sections are populated (or confirmed empty).

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Partner details from step 01, account overlap from step 02, calendar, web, knowledge layer
**Output:** Events calendar, partner news, office offerings, and co-sell program context stored in working memory for step 04

---

## CONTEXT BOUNDARIES

- Events are a forcing function for collaboration. An upcoming event creates urgency and a natural reason to co-invest.
- The partner events table should have intentional blanks -- ask the partner to add their events.
- Office space is a differentiator. Most partners don't offer physical space for joint activities.
- News and program updates provide conversation starters and show preparation.

---

## YOUR TASK

### Sequence

1. **Gather the controller's upcoming events.**
   - Check calendar for events in the next 8 weeks that could involve the partner.
   - Check `identity/MISSION_CONTROL.md` or knowledge layer for planned events, workshops, or conferences.
   - Filter for events relevant to the partner's geography, vertical, or interest.
   - For each: event name, date, location, and a specific collaboration opportunity.

   Collaboration opportunities to look for:
   - Co-presenting or co-sponsoring
   - Inviting each other's clients
   - Joint workshops or lunch & learns
   - Booth sharing at conferences
   - Client dinners or networking events

2. **Identify known partner events.**
   - Search web for `{Partner} events {Year}` and `{Partner} conferences {Year}`.
   - Check email threads for event invitations or mentions.
   - Check the partner's website for upcoming events, webinars, or conferences.
   - For each: event name, date, location, and what value the controller's team could add.

3. **Identify industry events both may attend.**
   - Conferences, trade shows, community meetups where both organizations are likely present.
   - For each: note if joint planning would be valuable (shared booth, client dinner, panel, etc.).

4. **Search for recent partner news.**
   - Web search for `{Partner} news` -- look for:
     - Product launches or major updates
     - Leadership changes
     - Funding or acquisitions
     - Partnerships with other companies (competitive intelligence)
     - Strategic direction shifts
   - Keep it to the 3-5 most relevant items. Not a news dump.

5. **Gather co-sell program context.**
   - Check email and knowledge layer for information about the partner's co-sell or partner program.
   - Note any program updates, certification requirements, or enablement opportunities.
   - Note any MDF (market development funds) or joint marketing budgets available.
   - If the partner has a formal partner portal or program tier, note the controller's status.

6. **Build the office/space offering.**
   - Identify which controller organization offices are in the partner's territory.
   - For each relevant office: location, available space (presentation rooms, workshop space, co-working desks), and what it's available for.
   - Frame it as: "We're happy to host partner events, joint workshops, or client meetings at any of our locations."

7. **Check for training and enablement opportunities.**
   - Does the partner offer certifications the controller's team should pursue?
   - Are there upcoming partner enablement sessions or training programs?
   - Would a joint training session for both teams create value?

8. **Store results** in working memory:
   ```
   events_and_context:
     controller_events:
       - event: ...
         date: ...
         location: ...
         collaboration_opportunity: ...
     partner_events:
       - event: ... (or mostly blank for partner to fill)
         date: ...
         location: ...
         opportunity_for_controller: ...
     industry_events:
       - event: ...
         date: ...
         location: ...
         joint_plans: ...
     partner_news:
       - headline: ...
         relevance: ...
     co_sell_program:
       program_name: ...
       status: ...
       updates: [...]
       mdf_available: true/false/unknown
     office_offerings:
       - location: ...
         available_for: [workshops, lunch & learns, co-working, client events]
     enablement:
       certifications: [...]
       upcoming_training: [...]
   ```

---

## SUCCESS METRICS

- Controller events listed with specific collaboration opportunities
- Partner events table present (populated where possible, blanks where not)
- Industry events identified with joint planning opportunities
- 3-5 recent partner news items captured
- Office/space offering built for relevant locations
- Co-sell program context gathered (or noted as unknown)

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Web search yields no partner events | Leave the partner events table blank with the note: "Partner team: please share your upcoming events calendar." This is expected and fine. |
| No partner news found | Note: "No recent news found via web search." Skip the section rather than padding it. |
| No co-sell program information available | Note: "Co-sell program details unknown -- add to discussion topics." This becomes a meeting question. |
| Calendar unavailable | Ask the controller: "What events do you have coming up that {Partner} should know about?" Build from their response. |
| Too many events | Prioritize the next 8 weeks. Focus on events with the highest collaboration potential. |

---

## NEXT STEP

Read fully and follow: `step-04-build-document.md`
