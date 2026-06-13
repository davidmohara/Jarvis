# Module: Delegation System

<!-- system:start -->

## Metadata

| Field | Value |
|-------|-------|
| ID | delegation-system |
| Category | system |
| Tier | Building Rhythm |
| Duration | 15 minutes |
| Mastery Threshold | 2 |

## What You'll Learn

How the delegation system works under the hood — the tracker, the lifecycle, how delegations connect to 1:1 preps and performance reviews. This is the system view, not just the agent interaction.

## Before We Start

Complete Core Operations. Ideally have one delegation already created.

## Walkthrough

### Step 1: The Tracker (5 min)

Open `delegations/tracker.md`. Walk through the structure:
- Active delegations with owner, description, due date, status
- Completed delegations (recent)
- How status changes work (pending → in progress → complete / overdue)

**Coaching prompt:** "This file is the single source of truth for accountability. When you delegate through the system, it lands here. When Shep preps your 1:1, it reads from here. When Chief runs your morning briefing, it checks here for overdue items. Everything is connected."

### Step 2: The Lifecycle (5 min)

Walk through a delegation's full lifecycle:

1. **Create** — `/delegate [task] to [person]` → appears in tracker as pending
2. **Track** — shows in morning briefing, 1:1 preps, and nudge system
3. **Follow up** — Shep surfaces overdue items and drafts nudges
4. **Close** — mark complete or cancel → moves to completed section
5. **Review** — completion data feeds into performance reviews

**Coaching prompt:** "The power isn't in creating the delegation — it's in the system remembering it when you forget. Every delegation you create is now woven into your briefings, your 1:1s, and your reviews. You don't have to track it manually."

### Step 3: Practice the Full Cycle (5 min)

Create a delegation, view it in the tracker, simulate a follow-up, then close it.

If the user already has a delegation they can close, use that. If not, create a small one for practice.

## Reflection

Ask: "Before this system, how did you track delegations?"

Most answer: "in my head" or "in email." Both lose things. The system doesn't.

## Success Criteria

Create, track, and close delegations using `/delegate` and the tracker. Mastered after 2 full cycles.
<!-- system:end -->
