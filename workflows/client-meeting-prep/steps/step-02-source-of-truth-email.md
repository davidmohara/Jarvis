---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 02: Establish Ground Truth from Email — Before Any Web Research

## MANDATORY EXECUTION RULES

1. You MUST query the connected email/calendar tool for the introduction thread or the most recent thread with the external attendee(s) BEFORE doing any web research. This order is non-negotiable.
2. You MUST ground the "reason for the call" in actual email/calendar evidence — cite the specific thread (sender, subject line, date) that supports your conclusion.
3. You MUST NOT invent or infer a sales narrative, a business relationship, or a title/role from web presence alone if email evidence is available and says otherwise (or says nothing at all).
4. You MUST explicitly classify the meeting type (see Classification below) using email evidence as the primary signal, calendar/invite metadata as secondary.
5. You MUST state plainly what NOT to assume — this is not optional filler, it is a required output field for the next two steps.
6. Do NOT proceed to step 03 until reason_for_call and meeting_classification are both populated from evidence, not guesswork.

This step exists because of `err-20260720T144623-LSBA9A`: a prep sheet was built from web research and calendar data alone, producing a wrong title, an invented sales narrative, and a wrong reason for the call — when the actual introduction email (findable with one search) told the true story. Web research supplements identity and company context. It never substitutes for available first-party email context on **why the meeting exists**.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Attendee name(s)/company from step 01, connected email/calendar tool
**Output:** Reason for the call (evidence-cited), meeting classification, contact depth (first-touch vs. repeat-meeting), explicit "do not assume" list — stored in accumulated-context

---

## CONTEXT BOUNDARIES

- Search the actual mailbox/calendar content — not just the calendar invite's subject line. The invite subject is often generic ("Sync," "Intro Call," "Catch up") and tells you nothing about the real reason.
- If no email evidence exists at all (truly cold/unsolicited meeting, or a controller-provided context with no digital trail), say so explicitly rather than filling the gap with invented context. Use whatever the controller told you directly as the only source in that case, and flag the absence of email corroboration.
- Do not do web research in this step. That is step 03, and it happens only after classification is set here.

---

## YOUR TASK

### Sequence

1. **Query the connected email/calendar tool** (per SYSTEM.md connector resolution — the active Superhuman-style connector's `get_thread` / `list_threads` / `query_email_and_calendar`, or M365 MCP mail search when authorized) for:
   - The introduction email, if one exists (search for the attendee's name and/or company, and for common intro phrasing: "connecting you with," "introduction," "meet," the organizer's name alongside the attendee's).
   - The most recent thread involving the attendee(s), if no clear introduction thread is found.
   - Search by attendee name, by company domain, AND by organizer name if the first search comes up empty — apply the same "exhaust 3 search strategies before declaring not found" rule from SYSTEM.md.

2. **Extract the evidence.** For whatever thread(s) you find, capture:
   - Sender, recipients, subject line, date(s)
   - The actual stated reason/context for the meeting, in the correspondents' own words
   - Who introduced whom, and through what channel or context (e.g., a named mutual contact, a shared group/association, an event, a referral, a sales/marketing touch)
   - Any stated titles, roles, or affiliations mentioned in the thread itself (these take priority over web-sourced titles if they conflict)

3. **Classify the meeting.** Based on the evidence — not assumption — assign one of:
   - **Sales/prospect-sourced lead** — evidence shows outbound/inbound sales motion, a marketing touch, a demo request, or a CRM-sourced opportunity.
   - **Peer/relationship/referral intro** — evidence shows a mutual contact, professional group (e.g., YPO, industry association, mastermind), event connection, or personal/professional network referral with no sales framing.
   - **Internal review or existing engagement** — evidence shows an existing client/partner relationship, project, or recurring cadence.
   - **Unclear/insufficient evidence** — no thread found, or the thread found doesn't clarify intent. State this honestly rather than picking the most likely-sounding category.

4. **Write the reason-for-call statement**, grounded in evidence:
   ```
   reason_for_call: "{One or two sentences stating why this meeting exists, citing the specific thread: sender, subject, date}"
   meeting_classification: "sales-sourced | peer-relationship-referral | internal-review | unclear-insufficient-evidence"
   evidence_cited:
     - source: "email"
       sender: "{name}"
       subject: "{subject line}"
       date: "{date}"
       key_quote_or_paraphrase: "{what it actually says}"
   do_not_assume:
     - "{Explicit thing not to assume, e.g., 'Do not assume this is a sales opportunity — no CRM record, no sales touch found in email.'}"
     - "{e.g., 'Do not assume urgency — no deadline or decision timeline mentioned anywhere.'}"
   ```

5. **Set contact_depth** — this is a second, orthogonal classification alongside `meeting_classification`, and it gates research depth in step 03/04 (specifically the Company Overview section — full depth for a first touch, brief refresh for a repeat meeting with an existing account). Derive it from step 01's `prior_relationship` field plus whatever the email evidence in this step adds (e.g., an email thread showing multiple prior meetings even if step 01's knowledge-layer check came up empty):
   ```yaml
   contact_depth: "first-touch | repeat-meeting"
   contact_depth_basis: "{One line citing what set this — e.g., 'step 01 found no prior 1:1 history and no thread predates this introduction' or 'email thread shows this is the third meeting with this account this quarter'}"
   ```
   - **first-touch**: no prior 1:1 history (per step 01) AND no email evidence of an established relationship with this person/account. Covers cold intros, first sales touches, and first-time peer/referral meetings.
   - **repeat-meeting**: step 01 found prior 1:1 history, OR email evidence shows an ongoing thread/cadence with this person or account, OR meeting_classification is "internal-review" (existing engagement implies repeat by definition).
   - If evidence conflicts (e.g., step 01 found no prior doc but the email thread clearly references earlier meetings), trust the email thread — it's closer to ground truth than the knowledge-layer search.

5. **If no evidence is found after 3 search strategies** (name, company/domain, organizer — per SYSTEM.md's search exhaustion rule), set `meeting_classification: "unclear-insufficient-evidence"` and write `reason_for_call` as: "No introduction or prior thread found via [strategies tried]. Reason for call is based solely on [controller-provided context / calendar subject line], which should be treated as provisional."

---

## SUCCESS METRICS

- Email/calendar tool was queried BEFORE any web research occurred
- reason_for_call cites a specific, real thread (or explicitly states none was found)
- meeting_classification is set from evidence, with an honest "unclear" fallback when warranted
- contact_depth is set (first-touch or repeat-meeting) with a one-line basis, not left blank or guessed silently
- do_not_assume list is populated with at least one explicit guardrail
- No title, role, or narrative is asserted that contradicts or goes beyond what the email evidence supports

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Email connector unauthorized/unavailable | Tell the controller explicitly: "Email connector isn't available — I can't verify why this meeting exists from first-party sources. Proceeding on calendar metadata and whatever you tell me, flagged as provisional." Set meeting_classification to unclear-insufficient-evidence. |
| Thread found but ambiguous (multiple plausible readings) | Present the ambiguity in do_not_assume rather than picking one interpretation and asserting it as fact. |
| Web research was already done out of habit before this step | Discard any conclusions about "reason for the call" drawn from that research. Web findings from company/attendee identity are fine to carry forward to step 03, but must not have shaped the classification here. |
| Thread confirms a title/role different from what's on LinkedIn or the company website | Trust the email thread. First-party correspondence outranks public web profiles for role/title accuracy at time of contact. |

---

## NEXT STEP

Read fully and follow: `step-03-research-company-and-attendee.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
