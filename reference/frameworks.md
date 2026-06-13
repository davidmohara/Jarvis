# Frameworks Cheat Sheet

Quick reference for the decision and prioritization frameworks used across this OS.

---

## RAPID Decision Framework

Use for any decision involving multiple stakeholders.

| Role | Description |
|------|-------------|
| **R** — Recommend | Drives the analysis and proposes a recommendation. Does the legwork. |
| **A** — Agree | Must agree to the recommendation (has veto). Use sparingly — max 1-2 people. |
| **P** — Perform | Will execute once the decision is made. |
| **I** — Input | Consulted for expertise or perspective. No veto power. |
| **D** — Decide | Makes the final call. Exactly one person. |

**Rules**:
- One D per decision. Always.
- A's have veto — only assign when necessary (legal, compliance, safety).
- I's provide input but don't slow the process. Set a deadline for input.
- The R drives the timeline. No R = no progress.

**Template**: `decisions/_template.md`

---

## Eisenhower Matrix

Use for triaging inbox items and daily prioritization.

|  | **Urgent** | **Not Urgent** |
|--|-----------|---------------|
| **Important** | **DO** — Handle now or today | **SCHEDULE** — Block time this week |
| **Not Important** | **DELEGATE** — Who else can do this? | **DELETE** — Say no or drop it |

**Rules**:
- Most things that feel urgent aren't important. Pause before reacting.
- "Schedule" quadrant is where the real leverage lives.
- If you're always in "Do" quadrant, you're firefighting — step back.
- Review against quarterly rocks: if it doesn't serve a rock, it's probably not important.

---

## Pre-Mortem

Use before committing to a major decision or project.

**Process** (15 minutes):
1. Assume the decision/project has **failed spectacularly** 6 months from now.
2. Write down all the reasons it failed. Don't hold back.
3. For each failure reason, ask: **Can we prevent or mitigate this now?**
4. Update the plan based on what you find.

**Prompts**:
- What assumption are we most wrong about?
- What external event could derail this?
- Where will execution break down?
- Who will resist this and why?
- What will we wish we had measured?

---

## ICE Scoring

Use for prioritizing projects and large tasks.

| Factor | Question | Scale |
|--------|----------|-------|
| **I** — Impact | How much will this move the needle if it works? | 1-10 |
| **C** — Confidence | How sure are we that it will work? | 1-10 |
| **E** — Ease | How easy is this to execute? (10 = trivial, 1 = massive effort) | 1-10 |

**Score** = (I + C + E) / 3

**Rules**:
- Score relative to each other, not in absolute terms.
- Re-score monthly — confidence changes as you learn more.
- Don't over-optimize the scoring. It's a sorting heuristic, not a decision.
- Tiebreaker: pick the one you'll learn the most from.

**Template**: `projects/_template.md` (ICE section built in)

---

## When to Use What

| Situation | Framework |
|-----------|-----------|
| Deciding between options with stakeholders | RAPID |
| Triaging my inbox / daily tasks | Eisenhower |
| About to commit to a big decision | Pre-Mortem |
| Prioritizing projects against each other | ICE |
| All of the above at once | Start with Eisenhower → ICE → RAPID → Pre-Mortem |
