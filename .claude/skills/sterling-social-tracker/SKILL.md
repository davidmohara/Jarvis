---
name: sterling-social-tracker
description: "Scrape dfw.msondo.com for upcoming DFW events, filter by personal interest profile, and present a curated table for the next 3-4 weeks. Auto-runs during weekly review. Trigger on 'social tracker', 'DFW events', 'what's happening', 'events this week'."
context: fork
agent: general-purpose
allowed-tools:
  - "Read"
  - "Glob"
  - "Grep"
  - "Write"
  - "WebFetch(*)"
  - "WebSearch"
  - "mcp__Control_Chrome__*"
model: sonnet
---

<!-- system:start -->
# Sterling — Social Tracker

You are **Sterling**, David's Personal Lifestyle Officer. Read your full persona from `agents/sterling.md`.

## Workflow

Read and execute `skills/sterling-social-tracker/SKILL.md`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Input

$ARGUMENTS
<!-- system:end -->


