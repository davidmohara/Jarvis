# Eval Authoring Guide

How to author useful evals for Rigby capability builds. Read this before Step 6 of `SKILL.md`.

## The two kinds of evals Rigby runs

**Assertion evals** — concrete, verifiable prompts where you can write checks like "the output file exists at X" or "the markdown contains the executive's title." These are graded automatically by `subagents/grader.md`.

**Subjective evals** — prompts whose output quality can only be judged by reading it. Drafted emails, talking points, persona-voice work, anything where two correct outputs can look different. Leave `assertions` empty and let `subagents/comparator.md` blind-compare iterations.

Most IES capabilities need a mix.

## Eval count

2-3 evals per build. More is rarely worth the time. The point is to catch obvious failures and surface improvement directions, not to exhaustively benchmark.

## Writing the prompt

Realistic. Verbatim. The way the executive would actually phrase the request. If the capability is `harper-thank-you-note`, don't write `"Draft a thank you note"` — write `"Send a thank-you to Sarah Chen at Cinemark for the strategy session yesterday. Reference the part about the loyalty program experiment specifically."`

Include the **context the agent would actually have** when invoked. For IES skills, that almost always means:

- The current date (use a fixed date in eval prompts, not "today")
- Any people involved (with enough handle for the executor to know who they are)
- Any external systems the skill will hit
- Any prior context the request implicitly depends on

If the prompt is vague, the executor will produce vague output, and the grader will pass it because vague output technically meets vague assertions.

## Writing assertions

Assertions are strings. The grader reads them and decides pass/fail. Examples that work:

```
"Output file is written to drafts/<id>.md"
"Output references Cinemark by name, not as 'the client'"
"Output is under 150 words"
"Output does not contain em-dashes"
"Output cites a specific moment from the meeting, not a generic 'good discussion'"
```

The hard part is writing assertions that *discriminate*. An assertion that passes for any plausibly-correct output is worse than no assertion — it creates false confidence. Examples that look fine but don't discriminate:

```
"Output is in markdown format"            # Trivially satisfied by any .md file
"Output is professional in tone"          # Subjective; grader will guess
"Output addresses the recipient"          # Any draft does this
```

Better versions of the same checks:

```
"Output includes a YAML frontmatter block with 'recipient:' and 'sent:' fields"
"Output is at most 4 paragraphs; no paragraph exceeds 5 sentences"
"Output's salutation uses the recipient's first name only (not 'Mr.' or 'Ms.')"
```

## Case study: the UTB plan typo (real example, iteration 1 trial)

The first Rigby trial run against the `remarkable-upload` skill produced this assertion set for one eval:

```
1. Plan targets the /UTB/Board Meeting folder (not /UTB or any other folder)
2. Plan includes a Finder duplicate step that copies the file from CloudStorage to /tmp before invoking rmapi
3. Plan includes a verification step (rmapi ls) before the upload to confirm the target folder exists
4. Plan includes a mkdir fallback only if the verification step finds the folder missing
5. Plan uses the absolute rmapi path /opt/homebrew/bin/rmapi rather than bare 'rmapi'
6. Plan does not contain any direct Bash invocation of rmapi (must go through osascript do shell script)
```

Pass rate: **6/6 (100%)**. But the executor's plan contained a typo in its user-facing report step: `2026-Q2-Q2-Board-Materials` instead of `2026-Q2-Board-Materials`. No assertion caught it. The grader's claim-verification logic flagged the typo (`claims[3].verified = false`) but pass rate is computed only from assertions, so the score stayed at 100%.

Every assertion here is a **presence check** — does the plan *contain* a thing — not a **substance check**. Substance checks would have caught it:

```
1. Target folder is exactly /UTB/Board Meeting (string match; case-sensitive)
2. Finder duplicate step's destination is /tmp (not /tmp/foo, not /var/tmp)
3. rmapi ls verification names the target folder, not just any folder
4. mkdir step is inside an `if entry doesn't exist` branch, not unconditional
5. Every rmapi invocation in the plan uses /opt/homebrew/bin/rmapi (count must match total rmapi calls)
6. Every rmapi call is inside an osascript `do shell script` wrapper (no bare bash)
7. (NEW) The plan's user-facing report step contains the source filename verbatim — no typos, no synthesis from memory
8. (NEW) The plan includes a post-upload rmapi ls verification, not just a pre-upload one
9. (NEW) If the target folder is missing, the plan branches into a mkdir step; if present, it skips mkdir
```

The pattern: **add an assertion for every step where the plan transforms input data**, not just for steps where the plan should contain a particular structural element. The typo happened in a transformation step (turning the filename into a report sentence), and no assertion checked that transformation.

Rule of thumb: if your assertion could be satisfied by a plan with a typo, a swapped variable, or an off-by-one error in a path, it's not discriminating. Tighten until it isn't.

## The MCP context problem

Many IES skills call MCP servers — Microsoft 365 for calendar, Clay for contacts, OmniFocus for tasks, WHOOP for health data. Eval prompts that assume live MCP access produce non-deterministic runs. The same prompt run today vs. tomorrow returns different calendar data, and grading becomes meaningless.

Two options:

**Option A — Fabricate context in the prompt.** Embed the MCP response inline so the executor never calls the server:

```
"You just finished a meeting with Sarah Chen at Cinemark. Calendar said: 
'2026-05-22 10:00-11:00, Sarah Chen (sarah.chen@cinemark.com), topic: 
loyalty program experiment design.' Plaud transcript says the conversation 
covered three things: ... Send a thank-you note."
```

Mark these evals `"mcp_mode": "fabricated"` in the eval JSON.

**Option B — Live integration eval.** Mark the eval `"mcp_mode": "live"` and accept that the assertions can't check specific content (Sarah might not be in your calendar today). Live evals are useful for catching integration breakage but not for grading content quality. Keep these to 1 per build at most.

If you don't specify, the executor will assume `"mcp_mode": "fabricated"` and refuse to make live MCP calls.

## The persona requirement

Every IES skill belongs to an agent. The executor loads the persona file *regardless of config* — even `without_skill` runs adopt the persona. This isolates the value of the skill from the value of the persona.

When authoring evals, you don't need to do anything special for personas. The orchestrator passes `agent_persona_path` automatically based on the skill name (`harper-*` → `agents/harper.md`).

If your skill doesn't belong to an agent (very rare in IES), set `agent_persona_path: null` in the eval metadata.

## Trigger eval queries (Step 9)

Different beast from assertion evals. 20 short queries, each labeled `should_trigger: true` or `false`. Half and half.

**Should-trigger queries** are user phrasings that should cause Rigby's description matcher to pick this skill:

```
{"query": "send sarah a quick thanks for yesterday", "should_trigger": true}
{"query": "thank you note for cinemark visit", "should_trigger": true}
{"query": "draft a follow-up after the loyalty meeting", "should_trigger": true}
```

**Should-not-trigger queries** are the dangerous half. The trick is they share keywords with should-trigger queries but are different intents. Obvious negatives ("what's on my calendar") teach the description nothing. Near-misses do:

```
{"query": "send sarah the deck from yesterday", "should_trigger": false}      # different action (attachment, not thanks)
{"query": "thank the team for hitting Q1", "should_trigger": false}           # internal, not external client
{"query": "follow up with cinemark on the contract", "should_trigger": false} # business follow-up, not thank-you
```

Aim for 8-10 each side. Mix formal and casual phrasings. Include typos. Include very short ("ty note for sarah") and very long queries.

The `run_loop.py` optimizer holds out 40% of the set as a test set, so the actual training signal is ~12 queries. Don't go below 20 total.

## When to skip the trigger optimization (Step 9)

Skip if the skill is invoked by explicit syntax (`/skill-name` or `chase-card-which`-style direct calls) rather than by Rigby matching against a phrase. In those cases the description only affects discovery in the skill list, not invocation, and tuning it is wasted effort.

Document the skip in the Step 11 summary: `"Description optimization: skipped (skill is invoked by explicit /name syntax)."`
