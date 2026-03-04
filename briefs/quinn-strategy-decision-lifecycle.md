# Design Brief: Strategy-to-Decision Lifecycle

**Date:** 2026-03-01
**Type:** System evolution
**Agent:** Quinn
**Status:** Approved for build
**Depends on:** `skills/quinn-strategy/SKILL.md` (exists), `decisions/_template.md` (exists), `reference/frameworks.md` (RAPID — exists)

---

## Problem

The quinn-strategy skill builds rigorous strategy but stops at the action agenda. There's no mechanism to record the bet, assign accountability, or evaluate the quality of strategic thinking after the fact. Without a written record at decision time, quarterly reviews devolve into outcome-only evaluation — "did we hit the number?" — which conflates lucky outcomes with good thinking and punishes good thinking that met bad luck.

Three gaps:

1. **No decision record.** The action agenda is a conversation artifact. It doesn't persist as a reviewable document with stated assumptions, diagnosis, and expected horizon.
2. **No stakeholder routing.** When a strategy requires buy-in beyond the person who built it, there's no structured path from action agenda to RAPID decision process.
3. **No retrospective scoring.** Quinn reviews rocks quarterly but has no mechanism to pull strategy-linked decisions and evaluate the quality of the thinking that produced them.

---

## Design

### Piece 1: Phase 6 — Decide & Record (Skill Extension)

**What:** Add a sixth phase to `skills/quinn-strategy/SKILL.md` that fires after Phase 5 (Sharpen for Action).

**Always runs.** Every strategy session produces a decision document. No exceptions. The paper trail is the feedback loop.

**Phase 6 behavior:**

1. Quinn asks two routing questions:
   - "What are the stakes of getting this wrong?"
   - "Who else has to buy in for this to move forward?"

2. Regardless of answers, Quinn generates a decision document from the action agenda:
   - **Diagnosis** — carried from Phase 2
   - **Guiding policy** — carried from Phase 3
   - **Coherent actions** — carried from Phase 3, refined in Phase 5
   - **Off the table** — carried from Phase 5
   - **Pre-mortem** — carried from Phase 4 (create-destroy output)
   - **Horizon** — new field. Quinn asks: "When do you expect to see signal that this is working or not?" Records the prediction as a date or timeframe.
   - **RAPID roles** — if solo, auto-fill: D = user, R = user, P = user. If multi-stakeholder, Quinn prompts for each role.
   - **Decision rationale** — why this path over alternatives
   - **Reversibility** — easy to reverse, hard to reverse, or one-way door

3. Decision doc saved to `decisions/YYYY-MM-DD-[slug].md` using the existing template structure (extended with horizon field).

4. Coherent actions pushed to task management (OmniFocus in personal bindings) with tags linking back to the decision doc.

**Solo/low-stakes path:** Steps 1–4 complete the flow. Quinn closes it out.

**Multi-stakeholder/high-stakes path:** Steps 1–4 still happen, but step 2 identifies that RAPID roles involve other people. Quinn flags this and offers to hand off to the workflow (Piece 2).

---

### Piece 2: Strategy-to-Decision Workflow (New Workflow)

**What:** A new workflow at `workflows/strategy-to-decision/` that handles the multi-stakeholder escalation path.

**When it fires:** Only when Phase 6 identifies that the decision involves stakeholders beyond the user — people who need to provide Input, have Agree (veto) authority, or will Perform actions they haven't yet committed to.

**Architecture:** Sequential 4-step workflow, Quinn as primary agent.

| Step | Name | Description |
|------|------|-------------|
| 1 | **Capture** | Ingest the decision doc from Phase 6. Validate all fields are populated. Confirm RAPID roles are assigned with real names. |
| 2 | **Collect Input** | Draft input request messages for each I-role. Set a deadline. Surface relevant context for each person (what they need to know to give useful input, pulled from relationship intelligence and prior interactions). |
| 3 | **Route for Decision** | Present the D with the complete package: decision doc, input received, pre-mortem, and Quinn's assessment of where disagreement exists. D decides. Record the decision and rationale. |
| 4 | **Activate** | Push coherent actions to each P-role's task stream. Create delegation entries in `delegations/tracker.md`. Set follow-up cadence. Link everything back to the decision doc. |

**Trigger:** Manual — invoked from Phase 6 when routing questions indicate multi-stakeholder. Not scheduled.

**Agent routing:** Quinn drives all steps. Chief handles delegation creation in Step 4 (existing capability). Shep handles relationship context lookup in Step 2 if needed.

---

### Piece 3: Decision Template Extension

**What:** Extend `decisions/_template.md` with two new fields.

**Horizon field:**
```markdown
## Horizon

**Expected signal by:** _date or timeframe_
**Horizon rationale:** _why this timeframe — what specifically will we be looking for?_
**Actual signal date:** _filled at review time_
```

**Strategy link field:**
```markdown
## Strategy Link

**Diagnosis:** _one-sentence diagnosis from the strategy session_
**Guiding policy:** _the guiding policy_
**Source of power:** _which of the 9 sources this strategy leverages_
```

These fields create the bridge between the strategy skill output and the decision record, making quarterly scoring possible.

---

### Piece 4: Quarterly Decision Review (Quinn Review Extension)

**What:** Extend Quinn's quarterly review capability (currently rocks-focused) to include strategy-linked decision scoring.

**When it runs:** During the existing quarterly review cadence (weekly-review workflow already routes rocks to Quinn). This adds a decision review section.

**Two buckets:**

**Bucket 1 — Ready to Score.** Decisions from any quarter where the horizon date has passed or outcomes are now observable.

Quinn pulls the decision doc and asks the user for outcomes, then scores four dimensions:

| Dimension | Question | Scale |
|-----------|----------|-------|
| **Diagnosis accuracy** | Did we correctly identify what was going on? Was the crux actually the crux? | 1–5 |
| **Policy effectiveness** | Was the guiding policy the right response to the diagnosis? Did it channel action effectively? | 1–5 |
| **Action coherence** | Did the actions support the policy? Did they get executed? Did they work as a coordinated system? | 1–5 |
| **Horizon calibration** | How far off was the time-to-signal estimate? | Ratio (estimated ÷ actual) |

Horizon calibration is tracked as a ratio, not a score — 1.0 means perfect calibration, >1.0 means you overestimated (thought it would take longer), <1.0 means you underestimated (the optimism bias). Over time, Quinn surfaces the user's average calibration ratio and patterns (e.g., "You underestimate people-dependent timelines by 1.6x on average").

Each scored decision gets a **lesson learned** field — one sentence about what the user would do differently.

Decision is then marked as `Scored` in the doc.

**Bucket 2 — In Flight.** Decisions where the horizon hasn't arrived or outcomes aren't yet observable.

Quinn surfaces these for a health check, not scoring:

- Is the guiding policy still holding, or has it been abandoned?
- Have conditions changed that invalidate the diagnosis?
- Are the coherent actions being executed, or have they stalled?
- Is the decision past its expected horizon with no signal? If so, flag it.

User can choose to: revise the horizon, score early with partial information, or acknowledge and continue.

**Bucket 3 — Silent.** Decisions past their horizon date with no outcome recorded and no review in the last quarter. Quinn escalates these — they represent strategic drift or forgotten bets.

**Meta-pattern surfacing:** After 4+ scored decisions, Quinn can compute:

- Average scores by dimension (are you consistently weak on action coherence?)
- Horizon calibration trend (are you getting better or worse at predicting timelines?)
- Diagnosis accuracy vs. outcome correlation (are your best diagnoses actually producing better outcomes?)
- Domain patterns (do you diagnose people problems better than market problems?)

---

## Decision Template (Extended)

The full template after all changes. This replaces `decisions/_template.md`:

```markdown
# Decision: _Title_

**Date**: YYYY-MM-DD
**Status**: Draft | In Review | Decided | Scored | Revisit by _date_
**Decider**: _who has final call_

## Strategy Link

**Diagnosis:** _one-sentence diagnosis from the strategy session_
**Guiding policy:** _the guiding policy_
**Source of power:** _which of the 9 sources this strategy leverages_
**Off the table:** _what we're explicitly not doing_

## Context

<!-- What's happening that requires a decision? Keep it to 2-3 sentences. -->

## Options

### Option A: _name_
- **Pros**:
- **Cons**:
- **Risks**:

### Option B: _name_
- **Pros**:
- **Cons**:
- **Risks**:

### Option C: _name_ (if applicable)
- **Pros**:
- **Cons**:
- **Risks**:

## RAPID Roles

| Role | Person | Notes |
|------|--------|-------|
| **R**ecommend | _who_ | Drives the analysis, proposes a path |
| **A**gree | _who_ | Must agree (has veto — use sparingly) |
| **P**erform | _who_ | Will execute the decision |
| **I**nput | _who_ | Consulted for expertise/perspective |
| **D**ecide | _who_ | Makes the final call |

## Pre-Mortem

<!-- Assume this decision failed badly. What went wrong? -->

-

## Horizon

**Expected signal by:** _date or timeframe_
**Horizon rationale:** _why this timeframe — what specifically will we be looking for?_
**Actual signal date:** _filled at review time_

## Decision

**Chosen option**: _which one_
**Rationale**: _why_
**Reversibility**: Easily reversible | Hard to reverse | One-way door

## Next Actions

- [ ] _action_ — _owner_ — _by when_

---

## Scoring (Completed at Review)

**Scored on:** _date_
**Scored by:** Quinn quarterly review

| Dimension | Score | Notes |
|-----------|-------|-------|
| Diagnosis accuracy | _/5_ | |
| Policy effectiveness | _/5_ | |
| Action coherence | _/5_ | |
| Horizon calibration | _ratio_ | Estimated: _X_ · Actual: _Y_ · Ratio: _actual ÷ estimated_ |

**Lesson learned:** _one sentence_
```

---

## Build Sequence

When ready to implement, build in this order:

1. **Decision template extension** — update `decisions/_template.md` with horizon and strategy link fields. Lowest risk, immediate value.
2. **Phase 6 skill extension** — add to `skills/quinn-strategy/SKILL.md`. This is the core — every strategy session now produces a persistent record.
3. **Strategy-to-decision workflow** — `workflows/strategy-to-decision/`. Only matters once Phase 6 is working and multi-stakeholder decisions arise.
4. **Quarterly review extension** — extend Quinn's review capability. Requires scored decisions to exist first, so this naturally comes last.

Each piece ships as a separate system evolution entry in `evolutions/history.md`.

---

## Resolved Decisions

- **Scoring model location:** `reference/scoring-model.md` — shared reference file. Applied via the quinn-strategy skill when the evolution is installed.
- **Pre-mortem handling:** Carry Phase 4 (create-destroy) output forward into the decision doc. No re-run at decision time.
- **Calibration ratio direction:** Actual ÷ estimated. A ratio of 1.6 reads as "it took 1.6x longer than you thought." >1.0 = optimism bias. <1.0 = conservative estimate. 1.0 = nailed it.
