# Module: Evolution System

<!-- system:start -->

## Metadata

| Field | Value |
|-------|-------|
| ID | evolution-system |
| Category | system |
| Tier | Full System |
| Duration | 20 minutes |
| Mastery Threshold | 1 |

## What You'll Learn

How IES evolves — how new capabilities get added, how your personal customizations are protected, and what the upgrade lifecycle looks like.

## Before We Start

Complete Personal Customization. The user should already have at least one personal block in place.

## Walkthrough

### Step 1: The Evolution Model (5 min)

Explain the core concept:

IES is a living system. It gets better over time through evolutions — packaged updates that add new agent capabilities, workflows, skills, or system features.

The contract:
- **System blocks** (`<!-- system:start/end -->`) are managed by evolutions
- **Personal blocks** (`<!-- personal:start/end -->`) are managed by you
- Neither overwrites the other

**Coaching prompt:** "Think of it like a phone OS update. The operating system improves, but your apps and settings stay intact. Evolutions upgrade the system. Your customizations are your settings."

### Step 2: What's in an Evolution (5 min)

Walk through the evolution manifest structure:

- **Version** — semantic versioning (e.g., 2026.04)
- **File actions** — add, replace, merge, delete
- **Training prompts** — new modules registered in the curriculum
- **Dependencies** — what must be in place before applying
- **Release notes** — what changed and why

Show `reference/evolution-system.md` for the full spec.

**Coaching prompt:** "Every evolution comes with release notes written for humans, not engineers. You'll know what changed and what it means for your workflow."

### Step 3: The Merge Process (5 min)

Walk through how merge works for files with both system and personal blocks:

1. Rigby reads the current file
2. Extracts personal blocks
3. Replaces system blocks with the evolution's new content
4. Reinserts personal blocks in their original positions
5. Validates the result

**Coaching prompt:** "Your personal blocks are sacred. Even if the system block around them completely changes, your customizations are carefully preserved. This is the core promise."

### Step 4: Training Module Registration (3 min)

When an evolution adds a new capability, it also adds a training module:

1. New entry in `curriculum.json` with `evolution_source` set
2. Walkthrough file in `modules/{category}/`
3. Shep surfaces "New capability available" in your next `/training-next`

**Coaching prompt:** "You don't need to discover new features. The system tells you about them and offers to teach you. That's the flywheel: capability → training → mastery → more capability."

### Step 5: Your Role (2 min)

What the user needs to do during an evolution:
- Nothing mandatory — evolutions are applied automatically
- Review release notes (recommended)
- Check that personal blocks survived (the system validates this, but trust and verify)
- Try new capabilities via `/training-next`

## Reflection

Ask: "How comfortable are you with a system that updates itself? What would make you more confident?"

Honest answers improve the evolution process.

## Success Criteria

Understand system vs. personal blocks, the evolution lifecycle, and how updates are applied. The user should be able to explain the contract in their own words.
<!-- system:end -->
