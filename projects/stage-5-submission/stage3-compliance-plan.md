# Stage 3 Compliance Plan — All Agents

**Created:** 2026-10-15 · **Goal:** every agent in `agents/manifest.md` passes all four of its own Stage 3 quality criteria by measured evidence, not assertion. Data window closes 2026-10-21.

## Current state (gap analysis, 2026-10-15)

| Agent | Records | Criteria passing | Blocking gaps |
|---|---|---|---|
| Master | 113 | J1 | J3 (64.7% < 90%), J4 (69.2% < 80%), J2 needs post-refactor A/B run; two-label split pollutes data |
| Chief | 82 | C2, C3 | C4 (50.8% < 80%); 16 F-grades on thin-content runs |
| Chase | 3 | H4 (n=1) | H1-H3 never asserted; needs ≥10 records |
| Harper | 6 | none | P3 (74.3% < 90%), P4 (75.0% < 80%); P1/P2 never asserted |
| Knox | 48 | K4 | K3 (68.7% < 90%); 18 records misattributed to `general-purpose` |
| Quinn | 1 | none | Q1-Q4 all unmeasured; weekly-review retired |
| Ralph | 0 | none | Zero attributed records — attribution broken |
| Rigby | 35 | R1, R2 | R3 (89.1%, 0.9pts short), R4 (70.0% < 80%) |
| Shep | 2 | none | S1-S4 completely unmeasured |
| Sterling | 3 | T3 | T1/T2 never asserted, T4 zero graded |
| Galen | 0 | none | Never instrumented |

## Phase 0 — Fix the plumbing (blocks everything else)

**Owner: Rigby. Do first — no measured run is trustworthy until this lands.**

1. **Agent attribution normalization.** `general-purpose` records (471) hide real owners. Every step record must carry `owning_agent` from the agent manifest. Ralph's boot-verification runs and Galen's runs currently vanish into wrong labels. Fix `record-step.py`/`eval-agent-start.py` attribution, then re-tag Ralph's boot-verification history where the owning agent is recoverable from transcripts.
2. **Normalize the master/jarvis label split.** Records carry both labels for the one coordinator agent; the canonical agent name is `master` ("Jarvis" is the system name, not an agent — David, 2026-10-16). Merge in reporting only — do not rewrite historical records (existing policy), but make the rollup query treat them as one.
3. **Populate `mechanical.completed`** (schema gap found in the Oct 15 recompute — reads as 0% everywhere). Backfill logic in `eval-agent-stop.py` derives it from step evidence.
4. **Define measurement hooks per agent** (see Phase 2) as assertions in `systems/eval-harness/assertions/` — a criterion with no assertion cannot be measured, and today 16 of 44 criteria have zero coverage.

## Phase 1 — Structural criteria coverage (assertion wiring)

Each agent's criteria that are currently unasserted need a sentinel assertion file or step-verifier. Rigby builds these:

| Agent | Unasserted criteria | What the assertion checks |
|---|---|---|
| Master | J2 | Routing-assertion hook: fails if coordinator executes a specialist task inline (post-Phase-1 A/B evidence) |
| Chase | H1, H2, H3 | Prep completeness (attendee research present), reason-for-call field used, data-grounding (citations per section) |
| Harper | P1, P2 | Voice calibration (matches identity/VOICE.md patterns), source merge (multiple sources cited in output) |
| Knox | K1, K2 | Full-ingestion accounting (staged count == ingested count), tag compliance (all required tags on new notes) |
| Quinn | Q1, Q2, Q3 | Strategy artifacts follow kernel structure, initiative tracker current, rock deltas recorded |
| Shep | S1-S3 | Delegation tracker updated + OmniFocus mirror in sync, 1:1 prep sheet sections present |
| Sterling | T1, T2 | Inbox triage decision per item, event tracker rows complete |
| Galen | G1-G4 | Protocol conflict flags, WHOOP pull freshness, bloodwork comparison present, question list generated |
| Ralph | A1-A3 | Verification runs recorded per boot, escalations surfaced, assertion file freshness |

## Phase 2 — Measured runs per agent (the data window)

3-5 instrumented runs per agent with `token_source=windowed`, exported via `export-step-audit.py`. Triggers per agent — mostly these happen naturally inside the four candidate workflows; the rest need scheduled or on-demand invocation:

| Agent | How the runs happen | Runs needed |
|---|---|---|
| Master | Boot runs (already instrumented) | 3 |
| Chief | Morning-briefing runs (already instrumented) | 3 |
| Knox | Plaud-ingest runs (already instrumented) | 3 |
| Rigby | Error-analysis runs — schedule or invoke via rigby-error-analysis on existing error entries | 3 |
| Harper | Podcast-prep batch (2) + email drafts (2) + deck build (1) | 5 |
| Chase | Client-meeting-prep on a real upcoming meeting | 3 |
| Quinn | quinn-strategy on a real question; quarterly review if a rock review lands before the 21st | 3 |
| Shep | 1:1 prep sheets for upcoming 1:1s + delegation tracker update | 3 |
| Sterling | Jarvis inbox sweeps + social tracker refresh | 3 |
| Galen | Morning WHOOP snapshots (scheduled — enable/verify the harness wiring first) | 3-5 |
| Ralph | Automatic on every boot verification — needs only the attribution fix from Phase 0, then 3 boots supply the data | 3 |

## Phase 3 — Recompute and remediate below-threshold agents

After Phase 2 runs land, recompute all 44 criteria with the same apples-to-apples method (strict and mech, per period). For agents still below their own bars:

- **Master J3/J4:** the dream-cycle assertion load pulls the combined rate down; report J3 on coordination runs only (already disclosed in stage3/master.md) or split the criterion.
- **Chief C4:** the 16 F-grades on thin-content scheduled runs are a measurement artifact as much as a quality problem — either grade scheduled runs against a scheduled-run rubric or exclude no-op scheduled runs from C4's denominator (disclose the choice either way).
- **Knox K3:** the 18 misattributed records, once re-owned in Phase 0, may close most of the 20-point gap. Re-run the K3 query after attribution lands, before doing anything else.
- **Rigby R3 (0.9pts):** one more clean run likely closes it. R4 (70%): the D/F grades are on eval/error-analysis runs — remediate those skills or split R4 by skill family.
- **Harper P3/P4:** needs the Phase 1 assertions first, then fresh graded runs.

Threshold changes are David's call, not the system's — if a threshold proves miscalibrated, surface it; do not quietly lower a bar to pass.

## Phase 4 — Finalize artifacts

1. Update all 11 `stage3/<agent>.md` files with final measured results, repro commands, and iteration histories; flip `status: draft` → `complete` only where all 4 criteria pass or the gap is honestly disclosed and signed off.
2. Fold the final numbers into `projects/stage-5-submission/index.md` row 5.
3. Roll into Phase 6 of the Stage 5 bundle (v2.0.0 tag, resubmission to Tim).

## Sequencing and dates

| When | What |
|---|---|
| Oct 16 | Phase 0 complete (attribution, merge-report, mechanical.completed, assertion skeletons) |
| Oct 17-19 | Phase 1 assertion wiring + Phase 2 runs start (boot/briefing/plaud give Master/Chief/Knox data automatically; scheduled tasks carry Galen) |
| Oct 20 | Phase 3 recompute + remediation |
| Oct 21 | Phase 4 finalize, fold into Phase 6 bundle |

## Honest limits

- Some agents (Chase, Quinn, Shep) need real events to occur before the 21st — a 1:1, a client meeting, a strategy question. If no natural event lands, an on-demand invocation of the skill on real current data is the substitute; a synthetic run would be measurement theater.
- Ralph/Galen have zero history, so their criteria start from first principles — no trend, single-window evidence only.
- Historical records are not rewritten (existing policy); attribution fixes apply going forward plus recoverable back-tagging only.
