# Module: Decision Framework

<!-- system:start -->

## Metadata

| Field | Value |
|-------|-------|
| ID | decisions |
| Category | system |
| Tier | Building Rhythm |
| Duration | 20 minutes |
| Mastery Threshold | 1 |

## What You'll Learn

How to use the `/decide` operation to work through important decisions using a structured framework. Decisions are first-class objects in IES — they're captured, reasoned through, and stored for future reference.

## Before We Start

The user should have a real decision they're facing — not hypothetical. If they can't think of one, prompt: "What's a decision you've been putting off?"

## Walkthrough

### Step 1: Frame the Decision (5 min)

Trigger `/decide [topic]` or say "help me think through [decision]."

The system prompts for:
- **What's the decision?** — State it as a question ("Should we…", "Which option for…")
- **Why now?** — What's forcing this decision? Deadline, opportunity, risk?
- **Who's affected?** — Stakeholders, teams, customers
- **What are the options?** — At least 2, ideally 3+

**Coaching prompt:** "A well-framed decision is half-solved. If you can't state the question clearly, you're not ready to decide — you need more information."

### Step 2: Apply the Framework (7 min)

Walk through using the RAPID framework from `reference/frameworks.md`:

- **Recommend** — Who should recommend the path?
- **Agree** — Who must agree before it moves forward?
- **Perform** — Who does the work once decided?
- **Input** — Who provides information or perspective?
- **Decide** — Who makes the final call?

For each role, ask the user to name a person. If all roles map to the user: "That's a sign this decision is either too small for a framework or you need to involve more people."

**Coaching prompt:** "RAPID isn't bureaucracy — it's clarity. Most decisions stall because no one knows who has the final call. Name the decider. Everything else follows."

### Step 3: Evaluate Options (5 min)

For each option, assess:
- **Reversibility** — Can we undo this if wrong?
- **Risk** — What's the worst case?
- **Alignment** — Does it advance a rock?
- **Cost** — Time, money, political capital

**Coaching prompt:** "For reversible decisions, move fast. Speed matters more than precision. For irreversible decisions, slow down. Precision matters more than speed. Most decisions are more reversible than executives think."

### Step 4: Record and Act (3 min)

Save the decision record:
- The decision question
- Options considered
- Rationale for the chosen option
- Who decides, who acts
- Review date (to check if the decision was right)

**Coaching prompt:** "Recording decisions is about learning, not documentation. In 90 days, you'll look back at this and know whether your reasoning was sound. Over time, you get better at decisions — but only if you have the evidence."

## Reflection

Ask: "What made this decision hard? Was it lack of information, conflicting priorities, or fear of being wrong?"

Each answer points to a different coaching theme.

## Success Criteria

Work through one real decision using the RAPID framework via `/decide`. The decision should have a recorded rationale and assigned owner.
<!-- system:end -->
