# IES Agent Manifest

**Established:** 2026-10-08 (Phase 5A, Stage 5 remediation) · **Maintained by:** Rigby · **Companion docs:** `agents/routing.md` (dispatch rules), `agents/adversarial-isolation.md` (adversarial layer), `agents/conventions.md` (shared protocols)

## Dispatch model (post coordinator-purity refactor, 2026-10-08)

The coordinator is Jarvis, the Master agent (`agents/master.md`). Jarvis routes, synthesizes across domains, and spawns sub-agents: it does not execute specialist tasks itself. Every workflow step names the agent that owns it and runs as a spawned sub-agent, never inline in the coordinator's session (documented exceptions: `workflows/boot/steps/step-01-load-context.md`, where boot context must land in the coordinator's own session, and the Master-owned error-log write sanctioned by `agents/conventions.md`). Git operations run only through `skills/git/SKILL.md` under Rigby. OmniFocus task creation runs only through `skills/omnifocus-tasks/SKILL.md`.

## Agents

| Agent | Role | Definition | Owns (workflow steps, skills) | Distinct from | Conflict resolution |
|-------|------|-----------|-------------------------------|----------------|---------------------|
| **Jarvis** (Master) | Coordinator | `agents/master.md` | Routing, cross-domain synthesis, quick capture, error-log write, boot step-01 | Dispatches everything below; owns no specialist domain | `agents/routing.md` Hard Stops govern; ambiguous requests route rather than act |
| **Chief** | Chief of Staff | `agents/chief.md` | Daily operations: boot steps 02-06 (data gathering, meeting context, briefing synthesis), morning-briefing steps 01-04, daily-review steps 01-03, inbox processing | Owns the day's operation; Chase owns revenue outcomes, Quinn owns strategy | Chief runs the calendar and briefing; revenue questions hand to Chase |
| **Chase** | Closer | `agents/chase.md` | Pipeline, deals, accounts, revenue pulls (rock1-revenue-monthly, rock4-pipeline-weekly, pipeline-review, client-meeting-prep), credit cards | Revenue/outcomes; Chief owns process, Harper owns messaging | Deal questions route to Chase even when surfaced in a briefing |
| **Knox** | Knowledge Manager | `agents/knox.md` | plaud-ingest steps 01-05 end-to-end, Teams/Plaud transcripts, reMarkable sync, vault search and health, boot step-08 (knox spawn) | Ingestion and vault curation; Harper consumes content, Knox captures it | Capture requests route to Knox; publishing to Harper |
| **Shep** | Coach | `agents/shep.md` | 1:1 prep, delegation tracking, team health, training, follow-up nudges | People development; Quinn owns strategy, not people | People questions route to Shep |
| **Quinn** | Strategist | `agents/quinn.md` | Rocks, quarterly/annual planning, goal alignment, initiative tracking, strategy development | Strategy and goals; Shep owns people, Chase owns execution of revenue | Strategy questions route to Quinn; both strategy and revenue concerns get Quinn framing with Chase numbers |
| **Harper** | Storyteller | `agents/harper.md` | Content calendar, email drafting, decks, talking points, podcast prep, watchtower content, campaign messaging | Outbound communication; Chase owns the deal, Harper owns the words | Anything David-signature-adjacent routes to Harper |
| **Rigby** | System Operator | `agents/rigby.md` | All system changes: workflows, skills, scripts, connectors, eval harness, evolution packaging, shutdown-cleanup end-to-end (git via `skills/git/SKILL.md`), error analysis | Infrastructure only; every other agent's domain is its user-facing work | Any request involving building/changing IES routes to Rigby immediately (highest-violation category) |
| **Sterling** | Concierge | `agents/sterling.md` | Travel, dining, wine, personal errands, /Jarvis email inbox, subscriptions, purchases | Personal operations; everything else is work | Personal vs work ambiguity defaults to asking David |
| **Galen** | Longevity Advisor | `agents/galen.md` | WHOOP analysis, bloodwork interpretation, protocols, physician visit prep | Health only | Health data questions route to Galen |
| **Ralph** | Boot Verification (adversarial) | `agents/ralph.md` + `workflows/boot-verification/` | Verifies boot completion claims against ground truth (boot step-03 spawns Ralph) | Adversarial reviewer; producing agents build, Ralph checks their claims | See `agents/adversarial-isolation.md` |

## Non-agent participants (explicit, to prevent examiner misreads)

- **David O'Hara** — the human operator/controller. Not an agent. He is the punch-out target for escalations, the approver of gated actions (new OmniFocus projects/tags, evolutions, PRs), and the source of corrections logged to `systems/error-tracking/`.
- **Verification loops** — the eval harness's guardrail/assertion machinery (`systems/eval-harness/`) is deterministic infrastructure, not an agent. Ralph is the agent that operates boot verification.

## Ownership decisions recorded at manifest creation

1. **shutdown-cleanup** belongs to Rigby end-to-end (frontmatter and registry aligned 2026-10-08; see `agents/master.md` Task Portfolio). Previously misregistered to Master.
2. **boot step-01** (context load) is the one documented inline exception: context must land in the coordinator's session.
3. **Master-owned error-log write** (`systems/error-tracking/entries/`) is a knowing exception sanctioned by `agents/conventions.md`.
4. Residual purity risks awaiting David's decision are listed in `projects/stage5-certification-remediation.md` (personal-block exit instruction still describes direct staging by Master).
