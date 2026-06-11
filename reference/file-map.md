# File Map — IES Full Directory Tree

```
IES/
├── CLAUDE.md                       → Auto-loaded boot pointer (you already read this)
├── SYSTEM.md                       → This file: operating manual
├── accounts/                       → Client and prospect account files
├── agents/
│   ├── chief.md                    → Chief of Staff — daily ops, briefings, inbox, reviews
│   ├── chase.md                    → Closer — revenue, pipeline, client strategy
│   ├── quinn.md                    → Strategist — goals, planning, alignment
│   ├── shep.md                     → Coach — people, delegation, development
│   ├── harper.md                   → Storyteller — comms, content, thought leadership
│   ├── knox.md                     → Knowledge Manager — vault curation, device sync, search
│   ├── rigby.md                    → System Operator — evolution, packages, platform infrastructure
│   └── galen.md                    → Longevity Advisor — health data, biometrics, bloodwork, protocols
├── hooks/                          → Claude Code hooks (PostToolUse, etc.)
├── identity/
│   ├── MEMORY.md                   → Persistent context about David (who he is, family, faith, key dates)
│   ├── VOICE.md                    → Jarvis personality, tone, communication style
│   ├── GOALS_AND_DREAMS.md         → One Texas targets, Lifebook visions, side ventures
│   ├── RESPONSIBILITIES.md         → Role definition, cadences, what David does/doesn't own
│   ├── AUTOMATION.md               → What Jarvis handles autonomously vs. with approval
│   ├── INTEGRATIONS.md             → Tools, data flow, Ilse, file locations
│   ├── SECURITY.md                 → Boundaries, sensitive areas, hard rules
│   └── MISSION_CONTROL.md          → Execution system, project tracking, the execution gap
├── memory/
│   ├── personal/                   → User config (vision, objectives, principles, org)
│   ├── episodic/                   → Event-sourced knowledge (meetings, people, projects, decisions, coaching)
│   ├── semantic/                   → Dream-cycle-distilled patterns (read-only for agents)
│   ├── working/                    → Volatile session state (TTL 2 days)
│   ├── LESSONS.md                  → Global lessons from constraint violations
│   └── dream.log                   → Dream cycle audit log
├── config/                         → System configuration files
├── contacts/                       → Contact records
├── context/                        → Session and project context files
├── contributions/                  → Contributed connector packages and integrations
├── data/                           → Raw data files and exports
├── decisions/
│   └── _template.md                → RAPID decision template
├── podcast/                        → Podcast-related materials
├── presentations/                  → Presentation files
├── projects/
│   └── _template.md                → Project brief template
├── people/
│   └── _template.md                → Person file template
├── logs/                           → System and integrity logs
├── meetings/
│   └── _template.md                → Meeting notes template
├── delegations/
│   └── tracker.md                  → All delegated items in one view
├── proposals/                      → Client proposals
├── reports/                        → Generated reports
├── reviews/
│   ├── daily/_template.md          → Daily shutdown template
│   ├── weekly/_template.md         → Weekly review template
│   ├── monthly/_template.md        → Monthly review template
│   └── quarterly/_template.md      → Quarterly review template
├── workflows/
│   ├── morning-briefing/           → Chief: calendar, tasks, context → structured briefing
│   ├── daily-review/               → Chief: capture, tomorrow prep, write review
│   ├── inbox-processing/           → Chief: pull inbox, triage, confirm zero
│   ├── weekly-review/              → Quinn/Chief: rocks, delegations, inbox, people, priorities
│   ├── pipeline-review/            → Chase: CRM pull, health analysis
│   ├── client-meeting-prep/        → Chase: attendees, account, research, brief
│   ├── partner-meeting-prep/       → Chase: partner context, account overlap, events, document
│   ├── one-on-one-prep/            → Shep: meeting ID, comms, tasks, assemble, quality check
│   ├── email-drafting/             → Harper: clarify context, draft, iterate
│   └── evolution-deployment/       → Rigby: validate, snapshot, merge, verify, log
├── scripts/                        → Utility scripts
├── skills/                         → Agent skill files (lazy-loaded)
├── specs/                          → Specification and planning documents
├── training/                        → Training & progression system (curriculum, modules, state)
├── tasks/                          → Task inbox and management files
├── evolutions/                      → Evolution history, snapshots, pending changes, poll cache
├── systems/
│   ├── eval-harness/               → Evaluation harness with 4-tier assessment (mechanical, structural, grading, controller feedback)
│   └── credit-cards/                → Card registry, optimization guide, benefits tracker (Chase agent)
├── archive/                        → Completed/closed items
├── briefs/                         → Short-form written briefs and summaries
└── reference/
    ├── file-map.md                 → This file: full directory tree
    ├── knowledge-layer.md          → Knowledge layer schemas, query patterns, write conventions
    ├── workflow-conventions.md     → Workflow state convention, step frontmatter convention
    ├── model-routing.md            → Agent model defaults and step-level guidance
    ├── frameworks.md               → RAPID, Eisenhower, Pre-Mortem, ICE cheat sheet
    ├── assistant-operations.md     → EA playbook: scheduling, travel, locations, prep, follow-up
    └── sops/                       → Standard operating procedures (built on 2nd occurrence, followed on 3rd+)
        └── one-on-one-prep.md     → SOP for internal Improving 1:1 meeting prep briefs
```
