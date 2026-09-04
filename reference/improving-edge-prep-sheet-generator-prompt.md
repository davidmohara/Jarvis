# The Improving Edge — Episode Prep Sheet Generator Prompt

A generative prompt template. Fill in the four inputs at the top, hand the whole thing to Claude (or another model), and it returns a complete, ready-to-use episode prep sheet in one shot. Distinct from `reference/podcast-prep-pdf-template.md`, which is the condensed single-page format printed for the studio on filming day. This is the research and thinking layer that feeds that condensed version, useful whenever you want deeper prep than the studio one-pager (first pass on a new guest, a topic you don't know well, or when you want the thematic-thread depth for follow-up content).

Use as-is for a quick prep. Edit the bracketed inputs each time.

---

## THE PROMPT

```
You are prepping me to host an episode of The Improving Edge, my company's
podcast. Audience: business and technical leaders, AI-forward, credibility-
focused — they can tell within 90 seconds if a guest is real or reciting talking
points, and they lose interest fast if the host asks generic questions. Format
is 30 minutes, conversational, one host and one guest.

INPUTS:
- Topic: [TOPIC]
- Guest: [GUEST NAME AND TITLE]
- Industry/domain: [INDUSTRY OR DOMAIN]
- Specific angle: [SPECIFIC ANGLE — what makes this conversation worth having
  now, or what's unresolved/contested about the topic that this guest can
  speak to]

Infer anything not given above from the guest's title and the domain. If the
guest's title suggests a CTO/technical practitioner, weight the thematic
threads toward implementation reality, tradeoffs, and what broke along the
way. If it suggests a CEO/executive, weight toward strategic bets, org
change, and what they'd do differently with what they know now. If it
suggests a practitioner/individual contributor, weight toward ground-level
detail, workarounds, and the gap between what leadership thinks is happening
and what's actually happening.

Produce a complete prep sheet with every section below. Do not write a
script or full dialogue anywhere — every question is something the host
reads once and asks in their own words. Keep it scannable: tables where a
table beats prose, short bullets, no filler paragraphs.

---

## 1. EPISODE METADATA
- Working title (one line, specific enough to differentiate from a generic
  "AI in [industry]" episode)
- Guest name, title, company
- Domain / industry
- Format: 30 min, single guest
- One-line hook (the sentence that would appear in a show notes teaser)

## 2. EPISODE PHILOSOPHY (2 sentences)
What this episode is actually for, beyond "talk about the topic." State the
belief or tension the episode is built around, and what the audience should
walk away believing or reconsidering. This is the north star the host can
glance at mid-conversation to stay oriented if the discussion drifts.

## 3. PRE-EPISODE RESEARCH FRAME (5 bullets)
Five bullets on what's happening right now in this domain that makes the
topic and angle timely. Each bullet: a specific, current development, debate,
or shift (not a timeless truism) plus why it matters to this audience. This
is the host's "why now" — the frame that makes the conversation feel current
rather than evergreen-generic.

## 4. GUEST EXPERTISE BREAKDOWN
A table mapping how this specific guest is likely to think about the topic,
based on their role and domain. Do not invent biographical facts about them —
reason from role, industry, and the stated angle.

| Dimension | How this guest likely approaches it |
|---|---|
| Core lens | [The frame they default to — technical, financial, operational, cultural, etc.] |
| Where they'll go deep | [The sub-topic they can speak to with the most specificity] |
| Likely blind spot or bias | [What their vantage point makes them less likely to see or say] |
| Credibility signal to listen for | [The kind of detail that would prove they've actually done this, not just overseen it] |
| Where they may hedge | [The area they're most likely to give a diplomatic non-answer, and why] |

## 5. SHOW FLOW & TIMING (5 segments)
A table. Guiding questions only, not dialogue. Each segment gets a time
allocation that sums to roughly 30 minutes including a buffer.

| Segment | Time | Purpose | Guiding question(s) |
|---|---|---|---|
| 1. Open / context | ~4 min | Establish who the guest is and why this conversation matters now | ... |
| 2. Thematic thread 1 | ~6 min | ... | ... |
| 3. Thematic thread 2 | ~6 min | ... | ... |
| 4. Forward-looking | ~6 min | ... | ... |
| 5. Close / memorable moment | ~5 min | ... | ... |

(Adjust segment count/labels only if the four thematic threads below don't
map cleanly to two show-flow segments — otherwise keep this 5-row structure.)

## 6. FOUR THEMATIC THREADS
Generate four threads by decomposing the [SPECIFIC ANGLE] into its
constituent tensions or decision points — not four generic sub-topics.
A good thread is built around a choice, tradeoff, or disagreement in the
domain, not just a topic label ("scaling AI adoption" is a topic; "why most
AI pilots die in the gap between IT and the business unit that owns the
budget" is a thread).

For each thread, produce:

### Thread N: [Name]
- **Why this thread matters for this angle:** one sentence
- **Questions (2-3):** open-ended, no yes/no, phrased so the guest can take
  them somewhere the host didn't fully anticipate. Order them loosest-first —
  start broad, tighten only if the guest's answer stays surface-level.
- **Listening notes:** what to listen for that signals the guest is about to
  say something worth following up on, not a script for what to say next.
  Frame these as recognition cues (a shift in specificity, a named failure,
  a number instead of a generality, a moment where they contradict the
  "safe" industry answer), never as a scripted follow-up line. The host
  should be listening for signal, not waiting for a cue to read the next
  line.

(Repeat for all four threads. Threads should be sequenced so each one raises
a question the next thread can answer, giving the conversation a throughline
rather than four disconnected segments.)

## 7. SEGMENT 4: FORWARD-LOOKING QUESTIONS
3-4 questions that move the conversation from "what happened" to "what's
next" — for the guest's org, their industry, or the broader domain. These
should be speculative enough to produce a real opinion, not so speculative
that the guest retreats to platitudes ("hard to say, we'll see"). Include one
question that asks the guest to take a position they could be wrong about.

## 8. SEGMENT 5: CLOSING / MEMORABLE MOMENT QUESTIONS
2-3 questions designed to produce the clip-able or quotable moment of the
episode. At least one should ask for a concrete story or specific number
rather than a summary opinion (people don't quote summaries). Always include
a version of a takeaway question, phrased in the host's own voice rather
than the canned "what do you want listeners to walk away with."

## 9. POST-EPISODE INTELLIGENCE CAPTURE FRAMEWORK
A short structured framework (bullets or a table) for what to capture
immediately after recording, before it's forgotten:
- The strongest verbatim quote or claim (word for word, for reuse in content)
- Any pain point, objection, or buyer signal surfaced that maps to a real
  offering or ICP (this is what feeds pipeline/content work downstream, not
  just the episode itself)
- Any credibility-signaling phrase the guest used that's worth noting as a
  domain-fluency marker for future guest vetting or thread-building
- One thing the host would do differently next time (question that landed,
  question that didn't, thread that should've been cut or extended)

State explicitly: this capture is what turns one episode into reusable
material for future episodes, follow-up content, and (where relevant)
account or persona intelligence. It should take under 5 minutes to fill out
right after recording, while it's fresh.

## 10. PHRASES THAT SIGNAL CREDIBILITY / DEPTH IN THIS DOMAIN
5-8 short phrases or types of statements that, if this guest says something
like them unprompted, indicate real depth rather than rehearsed talking
points. These are pattern-matches for the host to recognize live, not things
to ask for directly. Examples of the kind of thing to generate (tailor to
the actual domain, do not use these verbatim): a specific failure mode named
without being asked, a number that's oddly precise rather than round, a
disagreement with a vendor or analyst consensus, a story where the guest was
wrong first.

---

FORMATTING RULES:
- Use tables wherever a table is faster to scan than prose.
- No em dashes anywhere in the output.
- Every question is a question the host can ask in their own words — never
  scripted dialogue, never a guest's imagined answer.
- Total output should be readable and usable within 15 minutes, and prep-
  ready (host could walk into the recording within 1 hour of receiving this).
- If any input is missing or too vague to infer from, state the assumption
  you made in one line at the top of the relevant section rather than
  stalling to ask.
```

---

## Usage notes

- Minimum viable input is topic, guest name/title, and angle. Industry can usually be inferred from the guest's title/company if not given.
- For a CTO or technical practitioner guest, expect the model to weight threads 2 and 3 toward implementation detail. For a CEO, expect more strategic/org-change framing. Override this by naming the guest type explicitly in the angle if the default framing doesn't fit.
- The post-episode capture section (9) is the connective tissue to the rest of the podcast-to-pipeline pipeline (`workflows/episode-campaign-brief`, `pain-point-extraction`, `offering-match`). Filling it out consistently is what makes later episodes easier to prep and gives Harper's content calendar and audience-profile work real material instead of a cold start each time.
- This produces the deep prep document. Once the episode is scheduled and you're ready for the studio floor sheet, run the output of this prompt (or the guest research behind it) through the condensed single-page format in `reference/podcast-prep-pdf-template.md` — this prompt is not a replacement for that filming-day one-pager, it's the layer that makes that one-pager sharper.
