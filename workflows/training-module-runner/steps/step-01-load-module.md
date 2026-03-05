---
step: 1
name: Load Module
next: step-02-context-setting.md
---

<!-- system:start -->
# Step 1: Load Module

**Goal:** Find the module in the curriculum and load all required data.

## Process

### 1.1 Resolve Module

Take the `module_identifier` input and find the matching module in `curriculum.json`:
- Try exact match on `id` field
- Try case-insensitive match on `display_name`
- Try fuzzy match: "daily review" → "chief-daily-review", "delegation" → "shep-delegation"
- If ambiguous, ask the user to clarify by listing matching display_names

### 1.2 Load Module Definition

From `curriculum.json`, extract:
- `id`, `display_name`, `nudge_phrase`
- `category`, `tier`, `duration_minutes`
- `guided_file` path
- `mastery_threshold`, `success_criteria`
- `role_notes` for the user's `role_key`
- `prerequisites`

### 1.3 Load Guided Walkthrough

Read the file at `guided_file` path (relative to project root).

### 1.4 Load Mastery History

Check `mastery.json` for this module ID:
- If exists: note `attempts`, `last_attempt`, `skill_level`, `notes`
- If not exists: this is the first attempt

### 1.5 Check Prerequisites (soft)

If the module has prerequisites, check mastery.json for each:
- If not attempted: mention it conversationally ("This builds on {prerequisite_display_name}, which you haven't tried yet. That's fine — we can still do this, but you might want to try that one first.")
- Never block — just inform

## Next Step

Proceed to `step-02-context-setting.md`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
