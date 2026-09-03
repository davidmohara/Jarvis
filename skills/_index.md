# IES Skill Index

Last updated: 2026-09-03 | Total skills: 65

| ID | Name | Owner | Model | Trigger Keywords (sample) |
|----|------|-------|-------|---------------------------|
| schema-validator | Schema Validator | rigby | haiku | validate schema, schema validation, content validation |
| delivery-router | Delivery Router | rigby | sonnet | delivery router, route delivery, deliver content |
| visual-verification | Visual Verification | rigby | sonnet | visual verification, manual approval, human sign-off |
| calendar-handler | Calendar Handler | rigby | sonnet | conflict check, date calculate, calendar block, create event |
| powerbi-navigate-slicer | PowerBI Navigate & Slicer Filter | rigby | sonnet | powerbi navigate, powerbi slicer, filter report |
| powerbi-extract-kpis | PowerBI KPI & Table Extraction | rigby | sonnet | powerbi kpi, read kpi tile, extract report values |
| vault-freshness-check | Vault Freshness Check | rigby | haiku | cache check, freshness check, stale cache |
| eval-signal-write | Eval Signal Write | rigby | haiku | skill run signal, eval harness signal, skill complete |
| add-reminder | Boot Reminder Registry | master | haiku | remind, reminder, boot reminder, add reminder, set reminder |
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
| weather | Weather | none | haiku | weather, forecast, temperature, rain |
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
| rigby-eval-grade | Rigby Eval Grade | rigby | sonnet | grade evals, eval grading |
| rigby-eval-analyze | Rigby Eval Analyze | rigby | sonnet | eval analysis, eval trends |
| rigby-eval-dashboard | Rigby Eval Dashboard | rigby | sonnet | eval dashboard, generate dashboard |
| obsidian-source-note | Obsidian Source Note | harper | sonnet | save to obsidian, source note, talk research, save podcast notes |
| podcast-transcript-extract | Podcast Transcript Extract | knox | haiku | podcast, transcript, episode, spotify transcript |
| episode-transcript-intake | Episode Transcript Intake | harper | sonnet | episode intake, podcast to pipeline, turn this episode into a campaign |
| pain-point-extraction | Pain Point Extraction | harper | sonnet | pain points, extract pain points, episode pain points |
| audience-profile-builder | Audience Profile Builder | harper | sonnet | audience profile, ICP for this episode |
| offering-match | Offering Match | harper | sonnet | offering match, match pain points to services |
| account-targeting | Account Targeting | harper | sonnet | find target accounts, account targeting |
| contact-targeting | Contact Targeting | harper | sonnet | find contacts, contact targeting |
| prospect-message-draft | Prospect Message Draft | harper | sonnet | draft campaign message, prospect message |
| campaign-setup | Campaign Setup | harper | sonnet | set up the campaign, create the journey |
| campaign-send | Campaign Send | harper | sonnet | send the campaign email, trigger the journey send |
| campaign-response-log | Campaign Response Log | harper | sonnet | log this reply, log campaign response |

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
