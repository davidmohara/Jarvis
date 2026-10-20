<!-- system:start -->
# Master — Workflow Registry

This table maps workflow name → assigned agent → trigger context. Master uses this to determine whether to pass a workflow reference in the spawn payload before checking skills.

| Workflow | Agent | Trigger Context |
|----------|-------|-----------------|
| account-pursuit-map | Chase | Strategic new-business pursuit map for landing/expanding work at a target company (active-but-underleveraged or cold/lost re-entry). Use for "strategic account map", "pursuit plan for [company]", "how do we land [company]". Distinct from account-strategy — see that row. |
| account-strategy | Chase | Deep-dive on an account already in an active relationship/CRM: history, open opportunities, competitive landscape. Use for "deep-dive on [company]", "account history for [company]". Not for new-business pursuit strategy — see account-pursuit-map. |
| audience-target-outreach | Harper | Podcast-to-Pipeline campaign execution: account targeting, contact targeting, message drafting, campaign setup and send |
| calendar-prep | Chief | Meeting prep, attendee research, brief building |
| card-review | Chase | Monthly credit card benefits audit, optimization |
| card-walkthrough | Chase | Guided monthly portal walkthrough, benefit discovery |
| card-which | Chase | Card selection optimization for a specific purchase |
| client-meeting-prep | Chase | Client/prospect meeting prep with attendee research |
| comp-tracker | Chase | Monthly compensation tracking update from PowerBI |
| content-calendar | Harper | Content calendar review, deadline management, publishing schedule |
| content-discovery | Harper | Content discovery from #content Slack, drafting in David's voice, Ghost draft submission (scheduled daily 6am) |
| content-approval | Harper | Content approval decisions, publishing to Ghost, delivery verification (scheduled hourly) |
| content-pipeline | Harper | End-to-end content pipeline: discovery, approval, and git-finalized publishing |
| daily-review | Chief | End-of-day shutdown, capture completions and tomorrow's priorities |
| dream-cycle | Master | Nightly memory consolidation: compress working memory, promote to semantic, episodic archiving (scheduled nightly) |
| delegation-tracker | Shep | View all delegations, check status, flag overdue items |
| email-drafting | Harper | Draft a professional email, calibrated for recipient and voice |
| episode-campaign-brief | Harper | Four-step episode campaign brief: transcript intake, pain points, audience profile, offering match |
| episode-prep-generator | Harper | Generate a full Improving Edge episode prep sheet + guest research brief from topic/guest/angle inputs, before a filming date exists |
| error-improvement | Rigby | Error log analysis, pattern detection, tiered systemic-fix proposals |
| evolution-deployment | Rigby | Deploy evolution packages with personal block preservation |
| evolution-training-sync | Shep | Sync training curriculum with newly applied evolution components |
| follow-up-nudges | Shep | Surface overdue delegations, draft calibrated follow-up messages |
| galen-monthly-health-review | Galen | Monthly health review, WHOOP + bloodwork + DEXA analysis |
| goal-alignment | Quinn | Check activity against annual and quarterly goals, detect drift |
| golf-booking | Sterling | Weekly tee time booking at Frisco Lakes Golf Club |
| golf-preview | Sterling | Weekend golf preview scoring and Slack delivery |
| inbox-processing | Chief | Triage task inbox to zero, assign dispositions |
| initiative-tracker | Quinn | View strategic initiatives, status, owners, blockers |
| knowledge-ingest | Knox | Unified ingestion pipeline for captured content, tagging, vault filing |
| lead-log | Chase | Log new leads to My Leads.xlsx when prospects surface |
| lead-review | Chase | Review and surface unassigned leads from tracker |
| leadership-prep | Quinn | Build materials for board meetings, quarterly reviews, town halls |
| morning-briefing | Chief | Start-of-day briefing, calendar, priorities, delegations, context |
| one-on-one-prep | Shep | Build comprehensive prep brief for internal 1:1 meeting |
| one-texas-scorecard | Chase | Pull consolidated One Texas revenue + pipeline + co-sell snapshot |
| partner-meeting-prep | Chase | Partner/QBR meeting prep, account overlap, collaboration |
| pipeline-review | Chase | Pipeline health check, stage analysis, risk flags, forecast |
| plaud-ingest | Knox | Full Plaud recording ingestion, transcription, speaker ID, vault fetch |
| podcast-prep | Harper | Generate episode prep documents for The Improving Edge |
| political-monitor | Rigby | Both-sides political news monitoring with double-scan harvest and relevance decay |
| presentation-builder | Harper | Convert source materials into polished slide-by-slide text structure |
| rock-review | Quinn | Quarterly rock review, evidence-based status, risk flags, actions |
| rock1-revenue-monthly | Chase | Monthly Rock 1 revenue pull, Dallas + South Texas snapshot |
| rock4-pipeline-weekly | Chase | Weekly Rock 4 pipeline pull, co-sell + pipeline snapshot |
| shutdown-cleanup | Rigby | Session exit cleanup, purge artifacts, organize deliverables, commit (git via skills/git/SKILL.md) |
| skill-optimize | Rigby | Skill reflection and bounded procedural edits from eval trajectories |
| system-eval | Rigby | Eval-harness system evaluation: record analysis, grading sweeps, dashboard refresh |
| talking-points | Harper | Generate talking points for meetings, panels, podcasts, events |
| training-module-runner | Shep | Load curriculum, coach through guided walkthrough, record mastery |
| training-onboarding | Shep | First-launch onboarding, intake interview, orientation, first task |
| training-status | Shep | Training dashboard, progress bar, mastery counts, next recommendation |
| win-loss-analysis | Chase | Post-decision debrief, pattern recognition, lessons applied |
| watchtower | Knox | Standing intelligence: daily gather/dedupe/score/summarize, weekly synthesis and draft publishing to #content |

<!-- system:end -->

<!-- personal:start -->
| boot | Master | Full session boot sequence — context load, data gather, verification, briefing, workflow scan |
| boot-verification | Ralph | Post-Phase-2 boot audit; verifies all Phase 2 tasks completed |
<!-- personal:end -->

<!-- system:start -->
## Verification sub-workflows (Ralph)

Sibling verification workflows, not portfolio items and not candidate workflows: `boot-verification`, `daily-review-verification`, `morning-briefing-verification`, `plaud-ingest-verification`, `shutdown-cleanup-verification`. Each is spawned by its producing workflow's adversarial verification step; lenses and isolation mechanics live in `agents/adversarial-isolation.md`.
<!-- system:end -->
