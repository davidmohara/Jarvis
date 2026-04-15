---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 01: Clarify Context

## MANDATORY EXECUTION RULES

1. You MUST load the controller's voice profile from `identity/VOICE.md` before doing anything else.
2. You MUST determine the recipient, purpose, and tone before drafting. Ask only for what was NOT provided.
3. You MUST check for an existing email thread if this is a reply. Pull the thread for context.
4. You MUST search CRM for recipient context -- relationship, account, role.
5. Do NOT draft anything in this step. This step is context gathering only.
6. Do NOT ask questions the controller already answered. Parse their initial request carefully.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** Controller's request, identity layer, CRM, calendar, M365 email
**Output:** Complete context profile stored in working memory for step 02

---

## CONTEXT BOUNDARIES

- Ask the minimum number of questions needed. If the controller said "draft a follow-up to Sarah at AT&T about the workshop" -- you already have recipient, purpose, and enough to infer tone. Don't ask 5 clarifying questions.
- If the controller gives you a task prefix ("Task:"), this is NOT an email -- it's a task management inbox capture. Stop and redirect.
- The controller's time is the bottleneck. One smart clarifying question is better than five comprehensive ones.

---

## YOUR TASK

### Sequence

1. **Load the controller's voice profile.**
   - Read `identity/VOICE.md` -- specifically the Email Drafting Conventions section.
   - Store the formatting rules in working memory. These are non-negotiable for every draft.

2. **Parse the controller's request.** Extract everything already provided:

   | Element | Example | Status |
   |---------|---------|--------|
   | Recipient | "Sarah at AT&T" | Provided / Not provided |
   | Relationship | Client, partner, internal, personal | Inferred / Not provided |
   | Purpose | Follow-up, introduction, proposal, thank you, announcement, request | Provided / Inferred / Not provided |
   | Tone | Formal, warm, direct, casual | Provided / Inferred from relationship |
   | Key points | Specific things to include | Provided / Not provided |
   | Sensitivities | Things to avoid | Provided / Not provided |
   | Thread context | Is this a reply? | Provided / Need to check |

3. **Fill in gaps with data pulls.** Before asking the controller anything, try to fill gaps from available sources:

   - **Recipient unknown?** Ask. You need a name at minimum.
   - **Relationship unclear?** Search CRM for the recipient. Check CRM for account, contact record, and relationship history.
   - **Recent thread exists?** Search M365 email for recent threads with the recipient. If this is a reply, pull the thread for context and tone matching.
   - **Meeting context?** Check calendar for upcoming or recent meetings with the recipient. A meeting tomorrow changes the email's urgency and framing.
   - **Knowledge layer?** Search the knowledge base for notes about the recipient or their company.

4. **Ask only what you still need.** Formulate one concise question (or a short set) covering only the gaps:

   Good: "Got it -- follow-up to Sarah Chen at AT&T about the AI workshop. What specific next step do you want to propose?"

   Bad: "Who is the recipient? What is the purpose? What tone? What key points? Any sensitivities?"

   If you have everything you need, say so and move to step 02 without asking anything.

5. **Determine the tone calibration.** Based on all context:

   | Audience | Default Tone |
   |----------|-------------|
   | C-level executive (external) | Respectful, concise, high-signal. No fluff. |
   | Client contact (working level) | Professional-warm. Direct but friendly. |
   | Partner contact | Collaborative, specific. Reference shared goals. |
   | Internal peer | Direct, efficient. Match their energy. |
   | Internal leader (upward) | Crisp, prepared. Lead with the headline. |
   | Networking / new relationship | Warm, brief. Value their time. Clear ask. |
   | Personal / social | Casual, genuine. Let personality show. |

6. **Store results** in working memory:
   ```
   email_context:
     recipient:
       name: ...
       email: ... (if known)
       company: ...
       role: ...
       relationship: client | partner | internal | personal
     purpose: follow-up | introduction | proposal | thank-you | announcement | request | other
     tone: formal | professional-warm | direct | casual | ...
     key_points: [...]
     sensitivities: [...]
     thread:
       is_reply: true/false
       thread_subject: ... (if reply)
       last_message_summary: ... (if reply)
       last_message_date: ... (if reply)
     related_meetings: [...]
     crm_context: ...
     voice_conventions: {loaded from VOICE.md}
   ```

---

## SUCCESS METRICS

- Voice profile loaded from identity layer
- Recipient identified with relationship context
- Purpose and tone determined
- Existing thread pulled if this is a reply
- All needed context gathered with minimal questions to the controller

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Controller provides "Task:" prefix | This is NOT an email. Redirect: "That looks like a task, not an email. Capturing to task management inbox." Route to inbox capture. |
| Recipient not identifiable | Ask: "Who should this go to?" Cannot proceed without a recipient. |
| CRM unavailable | Proceed without CRM context. Note: "No CRM data available -- drafting from provided context only." |
| Email thread search fails | Ask the controller: "Is this a reply to an existing thread? If so, what was the last exchange about?" |
| Voice file missing or changed | If VOICE.md is unavailable, use the known conventions from the workflow.md initialization section. Flag: "Voice file unavailable -- using cached conventions." |

---

## NEXT STEP

Read fully and follow: `step-02-draft.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
