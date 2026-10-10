# Commentary Cleanup Plan, 2026-10-10

**EXECUTION STATUS (2026-10-10, same day): ALL PHASES EXECUTED.** Content family (decision 2) fixed first; then Phase A (commit 800c6c2e), Phase F hook-based capture (cccbcddc), Phase B centralization (35b54c86), Phase C+D (f5058fb3), all pushed to origin/main. Verification clean throughout: marker balance 0 imbalances across all trees, both guard validators pass (176 skill files, 295 step files), capture-chain tests pass, no residual err-narratives in instructional files. Coverage correction: `.claude/skills/` is a separate live tree of ~97 agent skills (not a mirror) and was audited and cleaned in the execution passes. Remaining open items: the frontmatter state-field migration (step-complete.py reads step frontmatter; full migration belongs with the eval-harness instrumentation work), the three verifier-side step-01-verify scaffolds (the caller-side protocol does not cover them), departed-EA references in identity files (personnel data, David's call), and eval-signal-write skill retirement (superseded by hooks, kept pending David's decision).

Audit of all instructional files (skills, workflows, agents, identity, SYSTEM.md, CLAUDE.md) for non-instructional text. Seven read-only audit agents, full coverage. This plan is the audit deliverable; the execution record lives in git history and memory/working/2026-10-10-102707-master-content-family-fix.md.

## Headline

- Audited: ~70,500 lines across 76 skills, 74 workflows (373 files), 16 agent files, 10 identity files, SYSTEM.md, CLAUDE.md.
- Removable within system blocks: **~6,600 lines (~9-10%)**
  - Firm residue/narrative/in-file duplication deletions: ~1,700 lines
  - Cross-file boilerplate centralization: ~4,900 lines
- Additional inside personal blocks (flag-only, needs your approval): **~1,600 lines**

## Decisions, status (updated 2026-10-10)

1. **DECIDED, prune frontmatter.** Run narratives AND structured `outputs:` mirrors retire from step frontmatter entirely. State lives in `state.yaml`; run outcomes live in harness records, `logs/`, or `memory/working/`. Applies to: plaud-ingest (6 step files, ~268 lines of stacked run archives), shutdown-cleanup (3 step files, dated `note:` transcripts), boot/dream-cycle (`prior-run-*` blocks with full deleted-file lists), morning-briefing/one-on-one-prep (single-run `outputs:` summaries, ~90 lines). Precondition: migrate any `verify/*.py` readers to `state.yaml`/eval records first (F4).
2. **RESOLVED AND EXECUTED (2026-10-10), content-pipeline family.** David confirmed all three workflows (content-pipeline, content-discovery, content-approval) run regularly; the "retired/superseded" story was wrong. Executed fix: content-pipeline/workflow.md rewritten as the live end-to-end orchestrator delegating to the two gated sub-workflows (326 to ~85 lines); its step-01/step-02 ungated duplicates (~1,100 lines) replaced with delegation stubs that execute the gated sub-workflow steps in full; step-03 run transcript rewritten as a proper git-finalize instruction; step-04 RETIRED note removed; pipeline verifiers and content-pipeline-verification repointed from the deleted local pending-drafts.json to the live shared file (workflows/content-approval/pending-drafts.json); stale copies deleted (local pending-drafts.json, step-02-status.log, ghost_update_v2.py duplicate); false "retired"/lineage claims fixed in content-discovery, content-approval, their steps, verifier docstrings, and config/scheduled-tasks.json. Remaining from this cluster, deferred to Phase F4: step frontmatter `outputs:` mirrors (still the verification workflow's data source; purge gated on F4 reader migration).
3. **DECIDED, centralize with shared reference files.** Spawned step agents demonstrably read repo files (every step file already ends with "Read fully and follow: `<next-step-file>`" and `reference/post-step-protocol.md` already exists with pointing precedent), so self-containment is not a constraint. Consolidate STATE CHECK, STEP COMPLETION TRACKING (superseded by Phase F hooks anyway), WRITE WORKING MEMORY, and the adversarial-verify scaffold into shared `reference/` protocols; each file keeps a one-line pointer plus its per-workflow deltas only.
4. **DECIDED, canonical owners locked:**
   - Error-logging rule → `agents/conventions.md` (one statement; CLAUDE.md and SYSTEM.md keep one-line pointers)
   - Git rules → `skills/git/SKILL.md` (sole authority; all other git guidance is dead code)
   - Eval outcome capture → Phase F hooks (no file owner needed)
   - Exit/shutdown protocol → `SYSTEM.md`
   - Working-memory YAML schema → `agents/master.md` (conventions.md keeps the tier-access table)
   - Activation protocol → `agents/conventions.md`, parameterized per agent
   - OmniFocus two-skill rule → CLAUDE.md as owner; pointers in SYSTEM.md and master.md
   - Naming-convention tables → `agents/conventions.md`
   - Spawn-first prohibitions + Rigby routing rule → `agents/routing.md`

## Phase A, Unambiguous deletions (no design decisions, ~1,700 lines)

### A1. Eval-harness contradictions and broken append artifacts (~230 lines)
- `skills/powerbi-navigate-slicer/SKILL.md:236-260`, DELETE appended SKILL COMPLETE block (contradicts line 226's "does not write its own signal file"). Same for `skills/powerbi-extract-kpis/SKILL.md:92-116` and `skills/vault-freshness-check/SKILL.md:90-114`.
- Double completion protocols (keep the newer skill-runs JSON version, delete the older; fix stale `agent:` values): `skills/revenue-tracker/SKILL.md:426-462`, `skills/new-clients/SKILL.md:287-323`, `skills/pipeline-snapshot/SKILL.md:206-221`, `skills/co-sell-pipeline/SKILL.md:229-266`, `skills/bookings-review/SKILL.md:125-161`, `workflows/golf-booking/workflow.md:165-192`, `workflows/golf-preview/workflow.md:129-156`, `skills/dream-cycle/SKILL.md:254-276`.
- `skills/podcast-transcript-extract/SKILL.md:16`, misplaced `<!-- system:start -->` wraps entire body; re-scope markers to the completion section.
- `skills/plaud-transcripts/SKILL.md:315,343`, two sections numbered "### 7"; renumber.

### A2. Dead/broken references from refactors (~45 lines)
- `workflows/evolution-deployment/steps/step-04-benchmark-snapshot.md`, DELETE deprecated 30-line stub; fix 4 stale cross-references (workflow.md:95 table row; step-05:9 mislabeled header; step-05:191 NEXT STEP points to nonexistent `step-05-apply-evolution.md`; step-07:27 stale input).
- `skills/dream-cycle/SKILL.md:16-45`, DELETE pre-git-gate git rule set (~30 lines); now contradicts and is blocked by the enforced `skills/git/SKILL.md` gate. Replace with one-line pointer.
- `workflows/comp-tracker/steps/step-08-close.md:183-201,236-245`, DELETE stale WorkDay-email instructions (~15 lines) from the superseded design.
- `workflows/comp-tracker/steps/step-04:372-374`, `step-03:279-282`, orphaned EXECUTION PROTOCOL fragments dangling after `<!-- system:end -->`. Same class: "Agent: Rigby" line outside all blocks in all 8 skill-optimize step files (~16 lines).

### A3. Err-ID backstories and dated provenance (~150 lines, ~45 sites)
Keep the rule, delete the incident story and/or reduce to a bare err-ID pointer. Sites: CLAUDE.md:19,27,44; SYSTEM.md:427,554,558,562,573; agents/master.md:150,205,206,674; agents/adversarial-isolation.md:3,20-28,51-53; agents/manifest.md:3,5,30-35; agents/galen.md:52,89,92; agents/chase.md:145; agents/harper.md:152; skills/plaud-speaker-id:27-33,199-204,297-302,312-321; skills/plaud-discover:31-41,151-152; skills/plaud-transcripts:331; skills/omnifocus-data:25-34; skills/omnifocus-tasks:12-16,43,97,141; skills/revenue-tracker:408; skills/powerbi-navigate-slicer:218; skills/git:39,44-45,82,86,120; skills/chase-card-offers-chase:126; skills/amazing-race-monitor:34-35,120-121; skills/campaign-setup:24-27; skills/campaign-send:59,113; skills/account-targeting:70; workflows/watchtower/workflow.md:17, weekly-step-01:15, weekly-step-05:56-67 (~12 lines: incident history + duplicated mechanism, keep one mechanism statement + gate sentence); workflows/morning-briefing/workflow.md:95-96; workflows/plaud-ingest/workflow.md:56-63,112-115 + steps (112-122,173-179; 93,100; 159-171); workflows/client-meeting-prep/workflow.md:26 + step-02:22 (same story told twice); workflows/dream-cycle/workflow.md:58,62 + step-01:38; workflows/golf-booking/step-00:22-24, step-01:21-23, workflow.md:28-37; workflows/lead-review/workflow.md:37; workflows/boot/step-01.2:114; workflows/shutdown-cleanup/step-01:144, step-04:67,72.

### A4. Real run data pasted as examples/templates (~130 lines)
- `skills/galen-visit-prep/SKILL.md:261-298,345-370` and `skills/galen-bloodwork/SKILL.md:145-158,209-222,249-306`, placeholder-ize; RELOCATE real values (ApoB 72→80, E2, DHEA timing) to `data/health/metrics-log.json`. Also galen-visit-prep:149-152 (personal goals in system block → `data/health/` goals file).
- `skills/galen-protocols/SKILL.md:38-138` (~100 lines, worst single file), dated stack inventory, bloodwork flags, dose-finalization narrative, directly beneath its own "do not hardcode, read tracking.json" rule. RELOCATE state to `data/health/tracking.json` + `metrics-log.json`; RELOCATE clinical rationale to `memory/semantic/domain-knowledge/` or `data/health/` spec file.
- `workflows/comp-tracker/workflow.md:36-37,49,119-131` + `step-01:172-175` + `step-04:102-107,197-210,318-322` (~35 lines), dated screen coordinates and real revenue figures contradicting the files' own "never hardcode" rules. Placeholder-ize; RELOCATE figures to `systems/compensation/` data file if needed.
- `skills/chase-card-offers-discover/SKILL.md:182`, dated Q2 activation status → `systems/credit-cards/benefits-tracker.json`.
- `workflows/watchtower/steps/weekly-step-04-weekly-note.md:24,124`, stale W38/W40 week references; in-place fix to "current week."

### A5. Narrative rationale, "Why This Exists" backstories, rebuild changelogs (~200 lines)
- Email-drafting:26-34; episode-campaign-brief:39-46; episode-prep-generator:80-89,48-51,57-59,174-175 (+ step-03:17-21,27-29; step-04:60-61,90-92), "unlike the previous version" rebuild history (~24 lines); golf-booking/workflow.md:28-37 conversion backstory; golf-booking/step-05:114-116; error-improvement/workflow.md Phase A/B story 3× (~10 lines); audience-target-outreach:44-61 (~10, RELOCATE full rationale to skills/campaign-setup); chase-call-prep:8-24 (RELOCATE migration map to memory/episodic/); boot/workflow.md:39-46 (RELOCATE eval-record mechanics to systems/eval-harness/schema.md); boot/step-08:78-92 self-correcting "Actually,..." edit note; master.md:493-546 synthesis restatement + example overflow (~15); master.md:642-646; adversarial-isolation.md:55-58; teams-transcripts:22-28; campaign-response-log:20-31; agents/manifest.md:30-35 ownership changelog.
- `workflows/boot/steps/step-01.2-unified-data-pull.md:337-352` and `step-01.5-unified-calendar-pull.md:125-145`, build-time "Implementation Notes for Consuming Steps" refactor TODOs addressed to editors (~37 lines). DELETE (facts already stated in CONTEXT BOUNDARIES).

### A6. Stale data in every-boot identity files (~30 lines)
- identity/MEMORY.md:10 (correction changelog), :197 (Feb 2026 phase), :147-154 (past-dated concert watchlist → data/ file or delete); identity/MISSION_CONTROL.md:40,43 (completed-season records), :59-66 (Feb/Mar past events); skills/harper-podcast-review:25. Data-consistency (not deletion): identity/INTEGRATIONS.md:79-84 + AUTOMATION.md:33 still reference departed EA Ilse Perez.

### A7. In-file duplication (~330 lines)
- Workflow.md EXECUTION sections duplicating their own steps/ files: card-walkthrough (~150), card-review (~90), card-which (~55), comp-tracker Step-0 protocol (~45). Keep steps/ as owner, keep 10,000-foot view in workflow.md.
- "Output Persistence" schemas stated twice per file: client-meeting-prep steps 01-05 (~70), one-on-one-prep steps 01-05, partner-meeting-prep steps 01-04, podcast-prep steps 01-05 (~170), talking-points steps 01-03 (~8). Keep one statement per file.
- Within-file: plaud-speaker-id gate stated 3× (~25); golf-booking/step-04 time-window rule 3× (~4) and step-06 same dated note 3× (~12); error-improvement Phase story; political-monitor hard rules restated in steps (~15); SYSTEM.md:578-585 appendix duplicates SYSTEM.md:233-239 (~8); plaud-transcripts:159-286 duplicates plaud-speaker-id mandate (~100, replace with pointer); plaud-transcripts:503-507 duplicates plaud-trigger (~5); offering-match no-fabrication discipline ~6× (~13); harper-blog-linkedin-post:115-117; harper.md:92-101 vs 145 (personal block, flag-only).
- Lens checklists duplicated workflow.md ↔ step-01: client-meeting-prep-verification, dream-cycle-verification (~17); boot.md:35-37 exception wording (~trim to 4 lines).

## Phase B, Cross-file boilerplate centralization (~4,900 lines; gated on decision 3)

| Boilerplate | Current footprint | Canonical owner | Saving |
|---|---|---|---|
| SKILL COMPLETE signal JSON | ~25 lines × ~62 of 76 skills | `skills/eval-signal-write/SKILL.md` (exists; 4+ files already use the short form) | ~1,500 |
| GRADE THIS RUN section | ~13 lines × 76 skills | eval-harness convention doc | ~900 |
| Activation protocol | ~34 lines × 6 agent files | `agents/conventions.md` (parameterized) | ~200 |
| Error-logging rule (new-entry.py) | 5 statements incl. CLAUDE.md, SYSTEM.md ×2, master.md, conventions.md, AUTOMATION.md | `agents/conventions.md`; one-line pointers elsewhere | ~55 |
| STATE CHECK 4-case block | ~20 lines × ~40 workflow.md files | shared `reference/` protocol | ~700 |
| STEP COMPLETION TRACKING (record-step.py) | ~7 lines × ~50 step files | shared reference | ~300 |
| WRITE WORKING MEMORY spec | ~27 lines × ~14 files (+ agent-source copy-paste bugs) | `agents/master.md` or conventions; fix `agent-source: master` in Quinn workflow steps | ~250 |
| Adversarial-verify scaffold | ~40 lines × ~17 files | shared template w/ lens parameter | ~500 |
| Verification workflow.md templates | ~70 lines × 8 near-identical | parameterized template | ~400 |
| Exit/shutdown protocol | 4 locations (CLAUDE.md, SYSTEM.md, master.md ×2) | SYSTEM.md owner + pointers | ~35 |
| OmniFocus two-skill rule | 4 locations | CLAUDE.md owner + pointers | ~10 |
| Naming-convention tables | SYSTEM.md:290-317 vs conventions.md:176-197 | conventions.md | ~22 |
| Working-memory YAML schema | conventions.md:61-91 vs master.md:620-648 | master.md | ~12 |
| Spawn-first prohibitions | master.md:201-207 vs routing.md:25-29 | routing.md | ~6 |
| Rigby routing rule | master.md:122-138 + 292-300 vs routing.md:75-87 | routing.md (Pre-Write Gate already operationalizes) | ~14 |
| Plan-Only Mode section | 8 Podcast-to-Pipeline skills | shared reference | ~70 |
| Desktop Commander/Slack init warning | 6 copies in content family | one reference | ~40 |
| Buyer-persona SharePoint URL | chase.md:60 + harper.md:151 | `reference/` or data file | ~2 |

Note on evaluation: CLAUDE.md + SYSTEM.md + agents/ + identity/ load at every boot, so their ~370 lines of removable content are paid every session. Skill tails are paid per skill invocation; workflow boilerplate per step spawn. The SKILL COMPLETE / GRADE THIS RUN consolidation is the highest-leverage single move for day-to-day cost.

**Phase F supersedes the consolidation approach for the two biggest rows.** If the harness captures outcomes itself (hooks, F2), the SKILL COMPLETE and GRADE THIS RUN rows stop being "centralize to one referenced copy" and become "delete from all 76 files outright" (~2,400 lines instead of ~2,400 reduced to ~200 of pointers). Execute Phase F before Phase B's first two rows to avoid consolidating tails that are about to be removed entirely.

## Phase C, Flag-only (personal blocks; needs your explicit approval, ~1,600 lines)

1. RESOLVED AND EXECUTED 2026-10-10, see decision 2. Personal blocks preserved throughout.
2. OmniFocus task-management binding block duplicated across workflow steps (morning-briefing/step-03, one-on-one-prep/step-03, email-drafting/step-03, inbox-processing/step-01).
3. sequential-thinking tool binding block repeated 3× (one-on-one-prep/step-04, pipeline-review/step-02, step-03).
4. podcast-prep workflow: whole bodies in personal blocks; "Why This Exists" + triple-explained episode-prep-generator relationship (~13 lines).
5. skill-optimize step files: "Agent: Rigby" line outside both blocks (~16 lines).
6. Empty personal-block marker pairs (~30 files, 2-3 lines each), trivially removable, flagged per rule.
7. omnifocus-tasks:198-222 read patterns duplicating omnifocus-data mandate; quinn-strategy:216-223 vs 225-236 duplicate tool bindings.
8. master.md:685-698 personal purge-pattern table duplicating SYSTEM.md:345-352; master.md:685 dated attribution note.
9. shutdown-cleanup/step-02:124-135 One Texas deliverable routing (live instruction, in a personal block, duplicating same-file system checks).
10. Dated narratives inside personal blocks of SYSTEM.md (61, 102, 116-121, 145, 151, 455-467), the OmniFocus-misdiagnosis narrative at 116-121 is the strongest residue candidate anywhere.

## Phase D, Close the leak (without this, the cleanup reverts within a month)

1. **Amend the Error Accountability protocol** (SYSTEM.md ~88,159: "add the rule here"): fixes must write *rules*, not rule-plus-incident-history. Error IDs are pointers into `systems/error-tracking/`, never inline content. This single wording change kills the largest residue source (~45 sites and counting).
2. **Add a frontmatter pruning rule**: step frontmatter carries `status`/`started-at`/`completed-at`/structured `outputs:` only. No `note:`, `notes_prior_run`, `previous-run-results` narrative, run notes go to `memory/working/`. plaud-ingest layers a new archive every boot run.
3. **Superseded by Phase F**, the eval-harness is decoupled from instruction files entirely (see Phase F); this leak disappears with the redesign rather than being patched.
4. **Refactor protocol**: splits/rebuilds/renumberings must delete the superseded copy in the same change (content-pipeline's 273-line "historical" duplicate, evolution-deployment's stub, WorkDay leftovers). Changelogs go to evolutions/history or a build log, never the instruction file.
5. **Template stamping**: new skills/workflows are created from `agents/conventions.md` / shared references, not cloned from an existing file. Kills the per-file boilerplate tax at the source and the copy-paste bugs it spreads (`agent-source: master` in Quinn files, `agent: "co"`, misnumbered steps).

## Phase F, Eval-harness decoupling: the harness never touches instruction files; outcomes live in logs

Confirmed from the harness source: `add-skill-signals.py` and `add-step-tracking.py` rewrite SKILL.md and workflow step files directly (both `skills/` and `.claude/skills/` trees) to stamp "SKILL COMPLETE," "GRADE THIS RUN," and record-step.py blocks into them, these scripts are the origin of the two largest boilerplate masses in Phase B, of the three self-contradicting skills, and of the duplicated completion protocols. `record-step.py` itself already writes only to eval records; only its stamped invocation blocks pollute the files. The redesign makes the harness an outside observer.

### F1. Retire the file-writing stamping scripts
- `add-skill-signals.py`, stop stamping. Either delete, or convert to a read-only validator (fail if any SKILL.md contains a stamped section, so a regression is caught). Its `has_skill_run_signal`/`has_grading_step` checks survive as the validator's detection logic.
- `add-step-tracking.py`, same: delete or convert to validator.
- Rule going forward (fold into Phase D.5): no `systems/` script may write to `skills/`, `workflows/`, `agents/`, or `identity/`. Harness state belongs in `systems/eval-harness/` records; instructional content changes go through the evolution/Rigby path.

### F2. Move outcome capture out of the files, two options, hook-first
- **DECIDED (David, 2026-10-10): hooks.** The harness already runs as hooks elsewhere (`guardrail-checkpoint.py`, `hook_utils.py`). Capture skill/workflow completions via Claude Code `Stop`/`SubagentStop` hooks that write `skill-runs/<name>-latest.json` and invoke `grade_skill_run.py` automatically. Zero per-file content, zero reliance on agents remembering to self-report, and grading happens on every run instead of when instructed.
- **Central convention is NOT the plan.** No per-file or SYSTEM.md instruction for eval outcome capture. Only if hook coverage is later proven incomplete for some execution path (inline coordinator runs, background tasks) does a gap-fill get considered, and it would be added to the harness's detection, not written back into the files. Delete every per-file SKILL COMPLETE and GRADE THIS RUN section regardless.

### F3. Step completion tracking
`record-step.py` already writes only to `runs/` eval records, the problem is purely its ~7-line invocation block stamped into ~50 step files. Same treatment as F2: capture via hook, or move the invocation to one line per `workflow.md` (the coordinator, which spawns steps, is the natural caller). Step files carry no tracking machinery.

### F4. Frontmatter outputs move to logs
Step frontmatter stops being an eval-output mirror (ties to decision 1). The harness reads outcomes from its own records (`runs/`, `skill-runs/`, `git-ops.jsonl`) and from `memory/working/`; the structured `outputs:` mirror in frontmatter is retired along with the narrative `note:` fields. If any verifier script (`verify/*.py`, plaud-ingest et al.) reads step frontmatter `outputs:`, migrate it to read `state.yaml` or the eval record first, that migration is the precondition for the plaud-ingest frontmatter purge in A-decisions.

### F5. Logs are the single source of truth
After F1-F4, all harness outcomes live in `systems/eval-harness/runs/`, `skill-runs/`, `records/`, and `git-ops.jsonl`; `dashboard.html`, `grade_skill_run.py`, `eval-health.py`, `daily-cost-check.py`, and the Tier-3 grading sweep already read from there and need no changes. Nothing in `skills/`, `workflows/`, `agents/`, or `identity/` references the harness's write path, the harness references the files, never the reverse.

### Sequencing impact
Execute F1-F2 before Phase B's first two rows (they convert ~2,400 lines of "consolidate to referenced copy" into "delete outright"). F4 must precede the plaud-ingest frontmatter purge. F1 can land immediately, the stamping scripts are one-time rollout tools whose job is done.

## Phase E, Verification (per the system's own gates)

1. `rigby-integrity` scan after each phase.
2. Boot test after Phase A/B edits (boot reads the heaviest files).
3. Adversarial-verify pass (Ralph) over a sample of edited files: confirm no standing instruction was lost, every deletion in this plan keeps the rule and cuts only the story.
4. Eval-harness run before/after to confirm no skill/workflow regression.
5. One-week re-audit of the seven sets to confirm the leak rules hold.

## Sequencing recommendation

Phase A first (pure win, no design risk), then Phase F (harness decoupling, retires the stamping scripts, moves capture to hooks per the 2026-10-10 decision, and upgrades ~2,400 lines from "consolidate" to "delete outright"), then decision 3 + the remainder of Phase B as one evolution package, Phase C as a separate David-approved change, Phase D as edits to SYSTEM.md/conventions wording, Phase E throughout. Suggested owner: Rigby (capability/structure changes are its gate), with the git skill's commit protocol for each phase.

The F2 design choice is settled: hooks (2026-10-10). Remaining open decisions: 1 (frontmatter run-archives), 2 (content-pipeline personal-block family), 3 (step-file self-containment before Phase B), 4 (canonical owners).
