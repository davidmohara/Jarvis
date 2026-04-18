# IES Skill Index

Last updated: 2026-04-18 | Total skills: 24

| ID | Name | Owner | Model | Trigger Keywords (sample) |
|----|------|-------|-------|---------------------------|
| omnifocus-tasks | OmniFocus Task Creation | chief | haiku | create task, new task, omnifocus |
| plaud-transcripts | Plaud Transcript Ingest | knox | haiku | plaud, transcript, recording |
| plaud-discover | Plaud Discovery | knox | haiku | plaud discover, find recordings |
| plaud-speaker-id | Plaud Speaker ID | knox | sonnet | speaker id, who was on the call |
| plaud-trigger | Plaud Transcription Trigger | knox | haiku | trigger transcription |
| teams-transcripts | Teams Transcript Ingest | knox | haiku | teams transcript, teams meeting |
| jarvis-inbox | Jarvis Outlook Inbox | chief | sonnet | jarvis inbox, inbox folder |
| pipeline-snapshot | Pipeline Snapshot | chase | sonnet | pipeline, deal status, crm |
| revenue-tracker | Revenue Tracker | chase | sonnet | revenue, bookings, target vs actual |
| new-clients | New Client Onboarding | chase | sonnet | new client, onboard, kickoff |
| co-sell-pipeline | Co-Sell Pipeline | chase | sonnet | co-sell, partner pipeline, microsoft |
| bookings-review | Bookings Review | chase | sonnet | bookings, weekly bookings |
| quinn-strategy | Quinn Strategy Analysis | quinn | opus | strategy, rocks, quarterly, planning |
| rigby-error-analysis | Rigby Error Pattern Analysis | rigby | sonnet | error analysis, error patterns |
| galen-bloodwork | Galen Bloodwork Analysis | galen | sonnet | bloodwork, labs, blood panel |
| galen-whoop-analysis | Galen WHOOP Analysis | galen | sonnet | whoop, hrv, recovery, strain |
| galen-morning-snapshot | Galen Morning Health Snapshot | galen | haiku | health snapshot, how did i sleep |
| galen-visit-prep | Galen Doctor Visit Prep | galen | sonnet | doctor, visit prep, appointment |
| galen-protocols | Galen Protocol Management | galen | sonnet | protocol, supplement, stack |
| chase-card-offers-amex | Amex Card Offers | chase | haiku | amex offers, american express |
| chase-card-offers-chase | Chase Card Offers | chase | haiku | chase offers, chase card |
| chase-card-offers-citi | Citi Card Offers | chase | haiku | citi offers, citi card |
| chase-card-offers-discover | Discover Card Offers | chase | haiku | discover offers, discover card |
| dream-cycle | Dream Cycle | knox | sonnet | dream, memory consolidation |

## Adding a New Skill

1. Create `skills/{id}/SKILL.md` with the standard frontmatter block.
2. Add one line to `skills/_manifest.jsonl` with all required fields.
3. Update this index (increment total count).
4. Run: Rigby validate-manifest (checks all paths exist and JSON is valid).

## Skill File Frontmatter Template

```yaml
---
name: skill-id
owning_agent: chief | chase | quinn | shep | harper | rigby | knox | galen
model: haiku | sonnet | opus
trigger_keywords: [keyword1, keyword2, keyword3]
trigger_agents: [agent1, agent2]
description: "One sentence — what this skill does and when to use it"
---
```
