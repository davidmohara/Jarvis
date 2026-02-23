<!-- system:start -->
# Step 02: Account Context

## MANDATORY EXECUTION RULES

1. You MUST pull the full account record from CRM. Partial account context leads to uninformed conversations.
2. You MUST identify all open opportunities on this account, not just the one linked to this meeting.
3. You MUST pull recent touchpoints — emails, meetings, and notes from the last 30 days.
4. You MUST map relationships: who from the controller's team knows who at the client.
5. Do NOT create or update CRM records in this step. This is read-only reconnaissance.
6. Do NOT skip the competitive landscape check. Walking into a meeting unaware of a competitor is how you lose deals.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Attendee data from step 01, CRM account record, M365 email/calendar history
**Output:** Account deep-dive stored in working memory for step 04

---

## CONTEXT BOUNDARIES

- Account context is scoped to information relevant for the upcoming meeting.
- "Recent touchpoints" = last 30 days unless the account has been dormant, in which case extend to last 90 days and note the gap.
- Relationship mapping uses CRM owner fields and meeting/email participation as evidence.
- Competitive intelligence comes from CRM notes, opportunity fields, and knowledge layer — not from guessing.

---

## YOUR TASK

### Sequence

1. **Pull account record from CRM** (CRM):
   - Account name and industry
   - Account owner (who on the team owns this relationship)
   - Account tier or classification (if defined)
   - Account creation date (how long has this been a client/prospect)
   - Total lifetime revenue (closed-won opportunities)
   - Active engagements (current SOWs, active projects, team members deployed)

2. **Pull all open opportunities on this account:**
   - For each:
     - Opportunity name
     - Stage
     - Amount (total and weighted)
     - Owner
     - Expected close date
     - Next step
     - Last activity date
     - Days in current stage
   - Identify which opportunity (if any) is the focus of this meeting

3. **Pull recent touchpoints (last 30 days):**

   a. **Email threads** via M365 MCP (`outlook_email_search`):
      - Search by attendee email addresses and account domain
      - Capture: date, subject, key points (from/to, first few lines or summary)
      - Flag any unanswered emails from the client

   b. **Meeting history** via M365 MCP (`outlook_calendar_search`):
      - Past meetings with this account in the last 30 days
      - For each: date, subject, attendees, any notes

   c. **Teams threads** via M365 MCP (`chat_message_search`):
      - Search for messages involving attendee email addresses
      - Capture recent discussion topics, decisions, or open threads

   d. **Knowledge layer:**
      - Search for meeting notes, prep docs, or account files for this client
      - Pull the most recent relevant notes
      - Extract action items, commitments, and open questions

4. **Map relationships:**
   - Build a relationship matrix: Internal team member <-> Client contact
   - For each connection: how strong (frequent interaction vs. one-time), last interaction date
   - Identify gaps: client contacts with no internal relationship
   - Identify the economic buyer and whether anyone on the team has access

5. **Check competitive landscape:**
   - Search CRM notes and opportunity fields for competitor mentions
   - Search knowledge layer for any competitive intel documented
   - If known: competitor name, what they offer, their position at this account
   - If unknown: note "No competitive intel available — consider asking in the meeting"

6. **Store results** in working memory:
   ```
   account_context:
     account:
       name: ...
       industry: ...
       owner: ...
       tier: ...
       tenure: N years
       lifetime_revenue: $X
       active_engagements: [{name, team_size, status}, ...]
     opportunities:
       - name: ...
         stage: ...
         amount: $X
         weighted: $X
         owner: ...
         close_date: YYYY-MM-DD
         next_step: ...
         last_activity: YYYY-MM-DD
         meeting_focus: true/false
     recent_touchpoints:
       emails:
         - date: YYYY-MM-DD
           subject: ...
           summary: ...
           unanswered: true/false
       meetings:
         - date: YYYY-MM-DD
           subject: ...
           attendees: [...]
           key_notes: ...
       teams_threads:
         - date: YYYY-MM-DD
           topic: ...
           summary: ...
       knowledge_layer:
         - file: ...
           date: YYYY-MM-DD
           key_points: [...]
           open_items: [...]
     relationships:
       mapped:
         - internal_person: ...
           client_contact: ...
           strength: strong | moderate | new
           last_interaction: YYYY-MM-DD
       gaps:
         - client_contact: ...
           role: ...
           no_internal_connection: true
     competitive:
       known_competitors: [{name, offering, position}, ...]
       intel_available: true/false
   ```

---

## SUCCESS METRICS

- Full account record pulled with revenue history and active engagements
- All open opportunities identified with current status
- Recent touchpoints captured from email, calendar, Teams, and knowledge layer
- Relationship map built showing connections and gaps
- Competitive landscape assessed (even if the answer is "unknown")

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Account not found in CRM | This is a new prospect or a data gap. Note: "No CRM account record. Treating as new prospect." Proceed with whatever data is available from email/calendar. |
| No opportunities on the account | Note: "No open opportunities. This is a relationship or new-business meeting." Adjust the brief accordingly. |
| No recent touchpoints found | Extend search to 90 days. If still nothing: "No documented touchpoints in 90 days. The controller is going in cold — prepare accordingly." |
| M365 search returns too many results | Filter by most recent and most relevant (direct attendee interaction > group threads). Cap at 10 most relevant items. |
| Relationship mapping incomplete | Work with what CRM shows. Note gaps explicitly. Relationship mapping improves over time as CRM data improves. |

---

## NEXT STEP

Read fully and follow: `step-03-research.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
