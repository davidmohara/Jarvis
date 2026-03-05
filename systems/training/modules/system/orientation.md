# Module: System Orientation

<!-- system:start -->

## Metadata

| Field | Value |
|-------|-------|
| ID | orientation |
| Category | system |
| Tier | Getting Started |
| Duration | 20 minutes |
| Mastery Threshold | 1 |

## What You'll Learn

How IES is structured — the agents, file system, and how everything connects. By the end, you'll know who does what and where things live.

## Before We Start

Nothing needed. This is the starting point.

## Walkthrough

### Part 1: The Agents (5 min)

Walk the user through each agent's domain. Read `agents/chief.md`, `agents/chase.md`, `agents/quinn.md`, `agents/shep.md`, and `agents/harper.md` — but don't dump the full files. Summarize each in 1-2 sentences tailored to the user's role.

**Coaching prompt:** "You don't need to remember which agent does what — just talk to the system naturally. If you say 'prep my 1:1 with Sarah,' Shep picks it up. If you say 'how's my pipeline,' Chase handles it. The routing is automatic."

Ask: "Which of these sounds most useful to you right now?" This tells Shep where to focus early training.

### Part 2: The File System (5 min)

Walk through SYSTEM.md's file map. Focus on what matters for their role:

- **Everyone**: `context/quarterly-objectives.md` (their rocks), `delegations/tracker.md` (what they've handed off)
- **People managers**: `reference/sops/` (how recurring tasks are done)
- **Revenue roles**: `context/` directory (where Chase pulls account context)

**Coaching prompt:** "You'll never need to navigate these files yourself. The agents read them automatically. But knowing they exist helps you trust the system — everything is tracked, nothing is in someone's head."

### Part 3: How to Talk to the System (5 min)

Demonstrate the core interaction pattern:

1. Natural language → "Start my day" / "Prep for my meeting with John" / "What's overdue?"
2. Operations → `/boot`, `/capture`, `/status`, `/prioritize`
3. Direct agent → "Ask Chase about the pipeline" / "Have Shep prep my 1:1"

**Coaching prompt:** "Start with natural language. If you want to be specific, use the operation names. But honestly, just talk like you'd talk to a chief of staff."

### Part 4: The Daily Loop (5 min)

Preview the daily rhythm they'll build:

1. **Morning** — `/boot` or "start my day" → Chief briefs you
2. **During the day** — `/capture` anything that comes up → it goes to inbox
3. **Before meetings** — "prep for [meeting]" → relevant agent builds a brief
4. **End of day** — `/review-daily` or "daily review" → Chief closes the loop

**Coaching prompt:** "You don't have to do all of this on day one. Start with the morning briefing. That's the keystone habit — everything else builds on it."

## Reflection

Ask one question:

"What's the first thing you'd want to use this for tomorrow morning?"

Note the answer — it informs which module Shep recommends next.

## Success Criteria

The user can name all 5 agents and describe their domains in their own words.
<!-- system:end -->
