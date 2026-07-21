---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 04: Build the Prep Sheet

## MANDATORY EXECUTION RULES

1. You MUST assemble the document using the exact structure specified below, in order.
2. You MUST NOT include a YAML frontmatter block at the top of the output file. The deliverable starts directly with the H1 title. (David explicitly asked for frontmatter to be removed from this deliverable — this is a hard rule, not a style preference.)
3. You MUST NOT include a "Next Steps" or post-call action item section anywhere in the document. This is a pre-call prep sheet only — it does not presume outcomes. (David explicitly asked for this to be removed.)
4. You MUST include a Calibration Note near the top that states plainly what kind of meeting this is (per step 02's meeting_classification) and what NOT to assume or do (e.g., "do not pitch a solution today").
5. You MUST calibrate talking points, tone, and any Improving-service-mapping content to the meeting_classification — never default to sales/discovery framing for a peer or internal-review meeting.
6. You MUST include the disambiguation note from step 03 if company identity was ambiguous.
7. You MUST include an Open Questions section covering every unresolved item from steps 01-03 (logistics gaps, relationship trajectory, unconfirmed business context) — state them as unknowns, never as facts.
8. You MUST include a "Common Connections" section, placed after "Who {He/She/They} Is" and before "Reason for the Call," reflecting step 03's `common_connections` data. It MUST stay compact — an inline list or tight 2-3 column table, names and companies only, no bios or speculation. Never omit this section silently — if LinkedIn access failed or returned zero mutual connections, say so plainly in the section itself.
9. You MUST include a "Company Overview" section, placed after "Who They Are" and before "Who {He/She/They} Is," reflecting step 03's `company_overview` data. Depth must match `contact_depth` from step 02 — a full narrative for first-touch, a brief refresh (or an explicit "nothing material has changed" statement) for repeat-meeting. Never omit this section silently, and never pad it with generic filler if research came up thin — say so plainly instead.
10. Do NOT make new data calls in this step. Assembly and quality-check only.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** All accumulated-context from steps 01-03
**Output:** Complete prep sheet saved to the knowledge layer / working directory

---

## CONTEXT BOUNDARIES

- This is an internal-only prep document for the controller, not a shareable artifact (contrast with partner-meeting-prep, which produces a document meant to be shared with a partner team).
- The document's job is to make the controller more prepared, not to look impressive. If data is thin, say so plainly rather than padding sections.
- Tone follows Chase's voice for internal framing (confident, direct) but the content itself must stay strictly evidence-based per steps 02-03.

---

## YOUR TASK

### Document Structure

Assemble the document using this exact structure (no frontmatter, starts directly with the H1):

```markdown
# Call Prep: {Attendee Name} — {Company} ({Meeting Type, e.g., "Intro Call", "QBR", "Catch-up"})

**{Start time}–{End time} {Timezone} ({duration} min) | {Format/location, or "Format/location not on the invite — confirm before the call" if unconfirmed} | {Prior relationship status, e.g., "New contact — no prior 1:1 history" or "Ongoing — last met {date}"}**

**Calibration note:** {One to two sentences stating the meeting_classification plainly and what NOT to assume or do — e.g., "This is a first-time call, sourced from an email introduction — not a sales-sourced lead. Treat as a peer/relationship conversation, not a discovery call for a deal. Do not pitch a solution today."}

## Who They Are

{Company profile table from step 03}

| | |
|---|---|
| **Company** | {name} |
| **Industry** | {industry} |
| **HQ** | {city, state/country} |
| **Founded** | {year or "not found"} |
| **Size** | {employee count / revenue band, or "not found"} |
| **Known tech stack** | {if findable, else omit row} |
| **Email domain** | {domain} |

{If company_disambiguation.ambiguous was true: include a one-line disambiguation flag here, e.g., "Note: {Company} was confirmed via email domain match — not to be confused with {other entity of same name/acronym}."}

## Company Overview

{Rendering of step 03's `company_overview`. This is the deeper narrative layer — recent news, strategic initiatives, competitive/market pressures — not a repeat of the facts already in "Who They Are." Depth follows `contact_depth`:
- **first-touch:** Full narrative (2-4 sentences) plus bullet lists for recent news, strategic initiatives, and competitive/market pressures where findable.
- **repeat-meeting:** Brief refresh only — 1-2 sentences on what's changed since the last touchpoint, or a plain statement that nothing material has changed. Do not re-render stable background already covered in a prior prep sheet.
If research came up thin, say so plainly (per `company_overview.narrative`) rather than padding.}

## Who {He/She/They} Is

{Attendee bio bullets from step 03: title, education, location, affiliations, public-facing work, LinkedIn}

**"Read on {him/her/them}":** {one-line interpretation from step 03 of what this person's role means for how to calibrate the conversation}

## Common Connections

{Compact rendering of step 03's `common_connections`. Use a tight inline list or a 2-3 column table — never one connection per bullet/paragraph. If status is "found": "{Name} ({Company}), {Name} ({Company}), {Name} ({Company})" — or a compact table if more than 4-5 names. If capped, add the note, e.g., "Showing top 6 of 14 mutual connections." If status is "zero": state plainly, e.g., "No mutual connections shown on LinkedIn." If status is "unavailable": state plainly, e.g., "LinkedIn profile not accessible — mutual connections could not be pulled for this run." This section always appears, in one of these three states — never silently omitted.}

## Reason for the Call

{The reason_for_call statement from step 02, grounded in actual email/calendar evidence — cite the thread (sender, subject, date). State plainly whether this is a sales-sourced lead, a peer/relationship call, an internal review, etc. — and explicitly flag what NOT to assume, per step 02's do_not_assume list.}

## Suggested Talking Points / Questions

{Calibrated to the actual reason for the call and meeting_classification — not a generic discovery script. For a peer/relationship call: shared-context questions, mutual interests, no pitch framing. For a sales-sourced lead: needs-discovery questions, calibrated to Improving's buyer persona repository if relevant. For an internal review: status/progress framing.}

1. {Point/question 1}
2. {Point/question 2}
3. {Point/question 3}

## Landmines / Notes

{What to avoid — e.g., "Don't pitch," "Don't assume urgency," "Don't lead with jargon," "Don't assume this is a deal in progress." Pull directly from the do_not_assume list in step 02 plus anything else surfaced in research.}

## Open Questions Going In

{Every unresolved item from steps 01-03, stated explicitly as unknowns — never presented as fact:}

- {Logistics gap, e.g., "Format/location not confirmed — Teams vs. phone unclear from the invite."}
- {Relationship trajectory, e.g., "Unclear whether this is a one-off conversation or the start of an ongoing relationship."}
- {Unconfirmed business context, e.g., "No stated agenda beyond the intro — topic may shift once the call starts."}
- {Any unresolved company disambiguation, if applicable}
```

### Assembly Rules

1. **No frontmatter, no exceptions.** The file starts at `# Call Prep: ...`.
2. **No Next Steps section, no exceptions.** Do not add action items, follow-up plans, or "what to do after" content anywhere in the document.
3. **Calibration note is mandatory and specific.** Never write a generic calibration note — it must name the actual classification and the actual thing not to do (e.g., not "be prepared" but "do not pitch a solution today").
4. **Every fact traces to a step.** The company table, bio, and reason-for-call content must be traceable to steps 02-03's accumulated-context — do not add new claims at assembly time.
5. **Unknowns stay unknowns.** If step 01 flagged a logistics gap or step 03 flagged an unresolved disambiguation, it must appear in Open Questions, not silently dropped or silently resolved with a guess.
6. **Common Connections stays compact.** Inline list or tight 2-3 column table only — never a bulleted narrative with one connection per line/paragraph. If more than 5-8 names exist, show the top 5-8 senior/relevant ones and note the total count. The section always states one of: names found (with count if capped), zero found, or unavailable — never silently dropped.
7. **Company Overview depth matches contact_depth.** Full narrative for first-touch, brief refresh (or explicit "nothing material has changed") for repeat-meeting. Never render a full first-touch-depth overview for a repeat meeting, and never shortchange a genuine first-touch with a one-liner just because research was light — in that case say research was light instead.

### Quality Checks

Before saving, verify:

- [ ] No YAML frontmatter block present in the output file
- [ ] No "Next Steps" or action-item section present anywhere
- [ ] Calibration note states the classification and at least one explicit "do not" instruction
- [ ] Reason for the Call cites a specific email thread (sender, subject, date) or explicitly states none was found
- [ ] Company disambiguation note included if ambiguity existed in step 03
- [ ] Common Connections section present, placed after "Who {He/She/They} Is" and before "Reason for the Call," compact (inline list or tight table, names/companies only), and reflects step 03's actual status (found/zero/unavailable) rather than being omitted
- [ ] Company Overview section present, placed after "Who They Are" and before "Who {He/She/They} Is," depth matches `contact_depth` (full for first-touch, brief refresh for repeat-meeting), and reflects step 03's actual `company_overview` data rather than being padded or omitted
- [ ] Talking points are calibrated to the classification, not generic
- [ ] Open Questions section captures every unresolved item from steps 01-03
- [ ] Meeting time is the verified local time from step 01, not a raw/unverified timestamp

### Save and Deliver

1. **Save to knowledge base / working directory:** `{Person Name} — {Company} — {YYYY-MM-DD}.md`
2. **Present the file to the controller.**
3. **Present a short summary:**
   ```
   Prep sheet ready for {Attendee} at {Company}, {time} {timezone}.

   Classification: {meeting_classification}
   {One sharp line: the single most important thing to know going in.}
   {If any Open Questions exist: "N open items — worth a quick look before the call."}
   ```

---

## SUCCESS METRICS

- Document assembled in the exact structure above, no frontmatter, no Next Steps section
- Calibration note present and specific
- All content traceable to steps 01-03's accumulated-context — no new claims invented at assembly time
- Open Questions section complete and honest
- Document saved and summary delivered to the controller

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Data is thin across all sections | Deliver what you have. Be honest in the summary: "Data is thin here — the conversation itself will fill most of these gaps." Do not pad sections with generic filler to look complete. |
| Knowledge base save fails | Present the document inline. Offer to retry save or output as a file. |
| Classification from step 02 was "unclear-insufficient-evidence" | Calibration note must say so plainly: "Reason for this meeting could not be confirmed from email — treat with appropriate caution; do not assume it is either a sales conversation or a routine catch-up until the controller clarifies." |

---

## STEP COMPLETION TRACKING

Record step completion for eval harness:

```bash
python3 systems/eval-harness/record-step.py client-meeting-prep step-04-build-prep-sheet complete "${{frontmatter.started-at}}" "${{frontmatter.completed-at}}"
```

## NEXT STEP

The prep sheet markdown has been delivered and saved. Update `state.yaml`: set `current-step: step-05`. Proceed to `steps/step-05-remarkable-delivery.md` to render the PDF and push it to David's reMarkable tablet. Do not mark the workflow complete yet — that happens at the end of step 05.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
