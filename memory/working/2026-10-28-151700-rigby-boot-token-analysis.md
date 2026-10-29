---
type: working
task_id: "session"
session_id: "rigby-2026-10-28-151700"
agent-source: rigby
created: 2026-10-28T15:17:00-05:00
expires: 2026-10-30T15:17:00-05:00
status: active
context: "Boot token performance analysis expanded to 10/26-10/28 boots — 2026-10-28"
---

# Boot Token Performance Analysis — 2026-10-28 (supersedes 2026-10-26 note)

Read-only analysis. Requested by David per boot reminder rem-20261023T141926-H6H5JB. Baselines: `memory/episodic/2026-10-23-091858-master-boot-token-analysis.md` (10/23, archived by dream-cycle) and `memory/working/2026-10-26-boot-token-analysis.md`. Method: `export-step-audit.py` (160 runs exported to /tmp), `fully_loaded_cost.py --dry-run`, `version-trend.py boot --json`, plus hand-parsing of fields no script emits (record-level totals, `parent_window`, frontmatter stamps via git history, subagent transcript usage sums from `~/.claude/projects/.../subagents/*.jsonl`). All transcript-derived numbers are labeled estimates.

## Finding zero: the 10/27 and 10/28 boots have no authoritative workflow-level record

- **10/26**: authoritative record exists: eval-20261026T141311-O84R10 (workflow boot, status `partial`, 11 steps, 12,205,154 in / 141,651 out, FL 12,230,836 / 143,414). A duplicate incomplete record (B7W765) also exists.
- **10/27**: NO complete workflow record. Q0REQ2 (workflow boot, `incomplete`, only step-01, no record-level totals) and YB6YAM (workflow boot, `success`, only steps 07/08, no totals). Per-step costs live on separate agent records. The boot also stalled ~3 hours mid-run (14:56Z start, phase-2 steps ran 18:09-18:25Z).
- **10/28**: NO complete workflow record. 26QC3W (workflow boot, `incomplete`, only step-01, no totals). VG43U3 (agent, `incomplete`, 8 steps listed, no totals). Per-step costs live on separate agent records; the 05-08 briefing agent has no record at all (see D-i).

## Per-run summary

| Date | Record | Status | Input | Output | Fully-loaded in/out |
|---|---|---|---|---|---|
| 10/23 | eval-20261023T131721-QQIZKW | partial | 5,869,892 | 66,237 | 7,639,504 / 71,074 |
| 10/26 | eval-20261026T141311-O84R10 | partial | 12,205,154 | 141,651 | 12,230,836 / 143,414 |
| 10/27 | Q0REQ2 + YB6YAM | incomplete / success | none recorded | none recorded | none |
| 10/28 | 26QC3W | incomplete | none recorded | none recorded | none |

10/27 and 10/28 totals: UNKNOWN from eval records. Partial floors (eval-recorded boot-tagged executors only, excluding Knox): 10/27 = 1,436,591 in (01.2+02+03+04 records) with step-01 windowed 948,658 on top and the 05-08 + 04.5 + 01.5 blocks unrecorded; 10/28 = 3,986,181 in / 65,763 out (01.5, 01.2, 02, 03, 04, and the step-08 windowed slice) plus step-01 windowed 732,666 and the unrecorded 05-08 agent (estimate 3.09M incl cache). Wall clock: 10/23 = 2,167s; 10/26 = 1,142s; 10/27 = ~14,700s gross with a ~3h stall; 10/28 = 2,709s (16:45:42Z-17:30:51Z).

## [A] Per-step trend (input / output tokens)

Basis: dedicated executor eval-record totals (the baseline's method). "est" = transcript-derived estimate (sums `usage` incl cache-read tokens from the subagent's own .jsonl) where no eval record exists. Deltas are only meaningful within the same basis.

| Step | 10/23 | 10/26 | 10/27 | 10/28 |
|---|---|---|---|---|
| 01 (inline) | not attributed | stamped but null (stale-window) | 948,658 / 1,483 (windowed) | 732,666 / 797 (windowed) |
| 01.5 calendar | 371,940 / 7,419 | 1,140,826 / 25,454 | ABSENT (2 stalled subagents, est 628K + 439K incl cache; inline fallback uncounted) | 758,545 / 26,463 |
| 01.2 data pull | 590,599 / 11,148 | 564,912 / 9,226 | 496,400 / 6,016 | 1,504,692 / 13,221 |
| 02 gather | 586,064 / 8,061 | 1,026,705 / 17,118 | 360,745 / 6,101 | 748,815 / 7,981 |
| 03 verify | 347,024 / 3,946 | 272,784 / 1,466 | 163,516 / 1,116 | 265,405 / 1,671 |
| 04 meeting ctx | 656,267 / 4,973 | 1,097,904 / 10,642 | 415,930 / 6,071 (stamps 04+06) | 505,639 / 3,844 |
| 04.5 watchtower | (not separate) | merged into 05-08 record | est 5,014,765 / 50,424 (stopped mid-run per err-20261027T184315-93PIYQ) | REMOVED from boot |
| 05-08 briefing | 1,528,972 / 20,055 | 4,646,400 / 59,629 (04.5 merged in) | est 6,274,500 / 45,515, NO eval record | est 3,093,108 / 26,696 (raw 306,929), NO eval record |
| Knox plaud | 817,194 / 8,818 (no-op) | 1,650,896 / 13,806 (no-op) | 10,466,230 / 47,435 + verify 2,553,375 / 7,759 (NOT no-op, 1 recording) | 10,362,717 / 44,631 + continuations 3,882,633 + verification 1,737,114 (NOT no-op, 2 recordings) |
| plaud-discover skill | 59,952 / 58 | CV37G4 (no totals) | inside Knox run | inside Knox run |

Attribution quality by run, with the deciding field:
- **10/23: REAL.** Steps carry `token_source: windowed` / `windowed-partition` with per-step values (backfilled 10/26, correlation_id corr-20261026T224541-PWTM). First fully-attributed run.
- **10/26: PRESENT BUT CORRUPTED.** Same `token_source: windowed`/`windowed-partition` fields, but the windows derive from fabricated round-minute stamps (step-01 stamped `2026-10-26T00:00:00Z`, verified in git at commit 68c32eb01; step-01 `token_source: stale-window`, tokens null). Do not read step rows as real.
- **10/27: PARTIAL/ABSENT.** Executor records are `token_source: windowed`; workflow records carry no totals; 49MKPI (the 04.5 watchtower agent record) is `incomplete` with a broken 6,220,758-token windowed slice on step-01.5 over an 11,070s window.
- **10/28: PARTIAL/ABSENT.** Same pattern: executors windowed; 26QC3W/VG43U3 no totals; step-05 windowed shows 0 tokens on VG43U3 while the real 05-08 agent went unrecorded.

Method changes mid-series (do not read as apples-to-apples):
1. 04.5 was merged into the briefing agent on 10/26 only, and removed from boot entirely mid-run on 10/27 (commit b9a04ca34).
2. 01.5 on 10/27 ran as two stalled subagents plus an inline Master pull (5 API stalls per the 10/27 briefing note) — no comparable basis.
3. 05-08 figures for 10/27/10/28 are transcript estimates including cache-read tokens; 10/23/10/26 figures are harness record totals. Directionally comparable, not exact.
4. 10/26 multi-step executor records (XKL3HO, UMLAM9, V42X7P) carry cumulative repeat windows — their step rows must not be summed.

## [B] measure.py fix verification — PASS for 10/27; 10/26 UNVERIFIABLE; 10/28 is a NEW failure mode, not a regression

Fix confirmed in code: `default=str` present at all three json.dumps calls (measure.py lines 29, 48, 82); lines 48 and 82 were added by commit b30413103 (committed 10/24, applied 10/23). Pre-fix vs post-fix diff:
- measurement-state-20261023T133722.json / 133738 (320 B): `{"error": "while parsing a block collection ... state.yaml line 94 ... expected <block end>, but found '?'"} — a YAML syntax failure, a different failure.
- measurement-state-20261023T133845.json / 133903 (61 B): `{"error": "Object of type date is not JSON serializable"}` — the value-level date failure the fix targeted.
- measurement-state-20261023T135854.json (10,843 B): full content, keys workflow/total_size_bytes/accumulated_context/field_breakdown, 70 field entries, total_size 14,097.

10/27 snapshot (measurement-state-20261027T182009.json, 7,172 B): PASS. Valid JSON, no error key, no truncation, identical top-level schema and nested key sets to the 10/23 validation snapshot (set diff empty both directions), 46 field_breakdown entries, total_size 8,491 — smaller because the 10/26 state.yaml purge (328 to 221 lines) stuck. Field coverage equal-or-better in structure; fewer entries reflect less state, not lost coverage.

10/26 snapshot: CANNOT VERIFY. No measurement-state-20261026* exists on disk or in git history. Rigby's 10/26 cleanup note records that the mid-run snapshot measurement-state-20261026T142055.json was untracked, deleted by an over-glob, and is unrecoverable. Stated plainly: the 10/26 boot's measurement evidence is absent.

10/28 snapshot (measurement-state-20261028T172414.json, 78 B): `{"error": "keys must be str, int, float, bool or None, not datetime.date"}`. NOT a regression of the default=str fix: `default=str` only converts VALUES; json.dumps rejects non-string KEYS outright. The 10/28 state.yaml introduced UNQUOTED date keys under the new `accumulated-context.task-g-72hr-lookahead` block (lines 139/149/158: `2026-10-29:`, `2026-10-30:`, `2026-10-31:`), which YAML 1.1 parses to datetime.date keys. The 10/27 state used string keys under `phase2.lookahead` (snapshot shows field `phase2.lookahead.2026-10-28`), so it serialized fine. Further fix needed (described, NOT applied per read-only scope): either (a) harness-side — recursively stringify mapping keys before every json.dumps in measure.py (a `_str_keys()` sanitize in measure_object_size / measure_dict_fields / measure_boot_state), or (b) convention-side — require quoted date-like keys in state.yaml writes from whichever step emits task-g-72hr-lookahead. (a) is the robust fix.

## [C] Step-01 stamping — landed on 10/27 and 10/28; 10/26 stamped but fabricated

Stamping instruction: step-01-load-context.md line 35 makes frontmatter stamping Master's responsibility (Edit tool, real `date -u` clock). Evidence from step-file frontmatter in git history plus the eval records:

| Run | Stamped? | Values | Harness attributed step-01? |
|---|---|---|---|
| 10/23 | NO — frontmatter still carried stale 2026-10-09T15:47:07Z stamps at commit b30413103 | n/a | NO — QQIZKW steps array starts at 01.5 |
| 10/26 | YES but fabricated | started-at = completed-at = `2026-10-26T00:00:00Z` (midnight placeholder, commit 68c32eb01) | NO — O84R10 step-01 `token_source: stale-window`, tokens_input None. Missing: real timestamps (boot-verify now hard-fails midnight stamps) |
| 10/27 | YES | `2026-10-27T14:56:38Z` / `2026-10-27T14:57:26Z` (commit fc5a60e04) | YES — Q0REQ2 step-01 tokens_input 948,658 / output 1,483, `token_source: windowed`, dur 48s |
| 10/28 | YES | `2026-10-28T16:46:39Z` / `2026-10-28T16:48:05Z` (current working tree) | YES — 26QC3W step-01 tokens_input 732,666 / output 797, `token_source: windowed`, dur 86s |

Caveat: the step-01 windowed numbers are inflated by design — the window opens at session start, so it counts Master's full context load (system prompt, CLAUDE.md, identity files), not just step-01 work. Use them as an upper bound.

## [D] Optimization target status

### (i) 05-08 briefing subagent split — NOT SHIPPED

workflows/boot/workflow.md line 95 still mandates "exactly one briefing subagent" for steps 05-08, and both boots complied: one agent each ("Boot briefing steps 05-08" spawned 10/27 18:44:41Z; "Boot steps 05-08 briefing" spawned 10/28 17:27:06Z, verified in session transcripts). New finding: THE EVAL HARNESS DID NOT RECORD THE 05-08 AGENT ON EITHER 10/27 OR 10/28 — both were async background spawns and no eval record exists for either. Costs recovered from subagent transcripts (estimates, incl cache-read tokens): 10/27 = 6,274,500 in / 45,515 out, 116 turns, 18:44:46-19:01:40Z; 10/28 = 3,093,108 in / 26,696 out (raw non-cache input 306,929), 58 turns, 17:27:06-17:31:33Z, model kimi-k3. Against the 10/23 baseline of 1,528,972 / 20,055 (CMONGZ): the block GREW (est 4.1x on 10/27, est 2.0x on 10/28), though bases differ (record totals vs transcript incl-cache). The 10/28 record L6FHVT (203,085 / 12,583, steps=[step-08]) is NOT the briefing agent — no Agent spawn exists at its 17:28:25Z window start; it is a windowed parent-slice keyed to step-08's stamp.

### (ii) Knox no-op path slimming — SHIPPED, UNVERIFIED (no no-op since)

Shipped: `workflows/plaud-ingest/verify/noop-preflight.py` (one-API-call verdict vs `data/.plaud-last-seen.json`, committed 68c32eb01 10/27 09:34), wired into plaud-ingest/workflow.md (NOOP verdict exits before persona/vault walk, explicit "do NOT read step-01 ... do NOT load a persona, do NOT walk the vault"), and step-01-discover.md refreshes the marker every run (current: checked_at 2026-10-28T17:06:00Z, outcome new-recordings, api_total 156). BUT: no no-op run has occurred since it shipped — 10/27 had 1 new recording (8SDUBS, 10,466,230 in), 10/28 had 2 (1SI5VG, 10,362,717 in). The last real no-op remains 10/26 at 1,650,896 (VKOMMT), UP from the 817,194 baseline on 10/23 (pre-preflight both times). New no-op cost: UNKNOWN until the first zero-recording day exercises the preflight. Note: the task brief's "206K input for the resumed run" figure matches no 10/28 eval record (closest: 0XRNN0 103,945; L6FHVT 203,085 is boot step-08, not plaud) — treat 206K as unverified. Non-no-op data points instead: 10/27 Knox = 10.47M + 2.55M verify; 10/28 Knox = 10.36M + 3.88M continuations (Q4RJKA 972,764; S5588B 1,784,735; JYUC62 1,021,189; 0XRNN0 103,945) + 1.74M verification agents.

## Data quality notes

- **Grading**: no tier-3 grade on any boot workflow record (QQIZKW, O84R10, Q0REQ2, YB6YAM, 26QC3W all have `assessment.grading`/`tier3` null and controller_feedback rating null). One exception: 49MKPI carries controller_feedback rating `negative` (David, presumably for the stopped watchtower run).
- **Duplicate plaud records**: 10/23 kept its five conflicting plaud-discover fork records (known issue). 10/28 has SIX plaud-ingest workflow records quarantined in `runs/_phantoms/` (K5JOB8, 8NN8H0, P0NIWS, GNNC0Z, L2UPEF, XYGZFC) — the duplicate-record problem is not fixed.
- **Misattribution**: P7D859 (2,655,734 in, tagged workflow=boot, no steps) is the Shep "Tim Rayburn 1:1" prep agent — its window_start 18:58:38.749Z matches the Shep spawn 18:58:38.672Z in the session transcript, and its 19:00:56Z window end truncates an agent that ran to 19:17Z. ACUY9F and 24S0E1 (~70K each) are windowed slices in the 05-08 agent's tail. None are boot steps.
- **Missing days**: no boot records 10/24-10/25 (weekend, expected). 10/26 has a duplicate incomplete workflow record (B7W765).
- **10/28 serializer error**: measurement-state-20261028T172414.json contains only the datetime.date-key error (see B).
- **Harness gap**: async background subagents escape eval recording (05-08 agent missed twice; the 10/27 step-01.5 subagents also have no records).
- version-trend.py boot output is too thin/polluted to use (10/23 version bucket dbce83160042 shows avg 117.9M tokens across 2 runs — contaminated by misattributed windows).

## Follow-ups (cheapest cuts first, with token math)

1. **Record async background subagents in the eval harness.** Not a token cut — the prerequisite for measuring anything else. The single biggest boot block (05-08, est 3.1-6.3M) has been invisible two boots running. Without this, every future trend table has a hole where the biggest number belongs.
2. **Script the plaud step-06 verify.** step-06-verify-ingest cost 2,553,375 input on 10/27 (U0RAKB) and 1,021,189 on 10/28 (JYUC62). A deterministic vault-count/file_id diff script plus a short LLM spot-check would run ~50-100K. Saving: ~1.0-2.5M input per ingest day; at the observed cadence (both days this week had recordings) that is ~5-12M/month.
3. **Apply the measure.py key-sanitize fix (B).** Zero token savings; restores the 10/28+ measurement series. One-function change.
4. **Watch for the first real Knox no-op** to validate the preflight. Expected shape if it works: one API call + marker write, order ~10-50K input vs the 1.65M last no-op — a ~97% cut on zero-recording days. If the next no-op still burns >500K, the spawn prompt in SYSTEM.md is the next cut (already queued in Rigby's 10/26 follow-ups).
5. **Knox non-no-op accumulation.** Both ingest days cost ~10.4M for the main agent; windowed slices show late steps re-carrying ~8.8M of context (8SDUBS steps 02-05b all stamped 8,824,798). Splitting ingest per-recording or truncating transcript context between steps is the big structural cut (~30-50% of the 10.4M, est 3-5M/ingest day) but is a redesign, not a tweak — do it after follow-up 1 makes the cost visible.
