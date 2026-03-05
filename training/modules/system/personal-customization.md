# Module: Personal Customization

<!-- system:start -->

## Metadata

| Field | Value |
|-------|-------|
| ID | personal-customization |
| Category | system |
| Tier | Strategic Mode |
| Duration | 20 minutes |
| Mastery Threshold | 1 |

## What You'll Learn

How to customize IES to your specific needs using the personal block system. System blocks provide the foundation; personal blocks are your modifications that survive upgrades.

## Before We Start

Complete System Orientation. The user should understand agents and file structure.

## Walkthrough

### Step 1: The Block System (5 min)

Open any agent file (e.g., `agents/chief.md`) and show the HTML comment structure:

```
<!-- system:start -->
Content managed by evolutions. Don't edit this.
<!-- system:end -->

<!-- personal:start -->
Your customizations go here. Safe from upgrades.
<!-- personal:end -->
```

**Coaching prompt:** "IES evolves — new capabilities get added, agents get smarter. But YOUR customizations are protected. Anything inside personal blocks is yours. Evolutions will never touch it."

### Step 2: Types of Customizations (5 min)

Walk through what can be personalized:

- **Agent behavior** — Add tool bindings, data sources, specific instructions
- **Workflows** — Add steps, modify outputs, change data requirements
- **Skills** — Add personal context or tool configurations
- **System operations** — Add personal steps to boot, review, or other operations

Show a concrete example: "If you always want your morning briefing to include a specific metric or check a specific system, you'd add that in Chief's personal block."

### Step 3: Make a Customization (7 min)

Guide the user through adding their first personal block:

1. Pick an agent that's most relevant to their daily work
2. Identify something they want added — a data source, a habit, a check
3. Write the personal block together
4. Save it

**Coaching prompt:** "Start small. Don't try to customize everything. Add one thing, use it for a week, then add another. The best customizations come from real frustrations — 'I wish the system also checked X.'"

### Step 4: Verify Protection (3 min)

Explain the evolution contract: "When an evolution comes in, Rigby processes it. System blocks get updated. Personal blocks are copied forward untouched. Your customizations persist."

**Coaching prompt:** "This is the deal: you contribute your expertise about how YOU work, and the system contributes capabilities. Neither overwrites the other."

## Reflection

Ask: "What's one thing about your workflow that's unique to you — something no other executive would do the same way?"

That's the seed of their next customization.

## Success Criteria

Add a personal block to one agent. The user understands the system/personal block contract.
<!-- system:end -->
