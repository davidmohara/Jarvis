---
type: working
task_id: "session"
session_id: "master-2026-10-29-143643"
agent-source: master
created: 2026-10-29T14:36:43Z
expires: 2026-10-31T14:36:43Z
status: active
context: "Boot token usage 2026-10-15..10-29: per-run totals, per-step attribution, trend vs the 10-22 dispatch change, Sonnet cost, dated 2026-10-29"
---

# Boot Token Performance Analysis: 2026-10-29

Scope: `systems/eval-harness/runs/` records for 2026-10-15 through 2026-10-29, workflow `boot`, plus the dedicated step-subagent records and the boot-triggered Knox `plaud-ingest` runs. Baseline for comparability: `memory/episodic/2026-10-23-091858-master-boot-token-analysis.md` (10/23) and `memory/working/2026-10-28-151700-rigby-boot-token-analysis.md`.

## Method (and why the numbers differ from prior analyses)

Two bases, both reported. Neither is new math: both use the harness's own definition of a fully-loaded run, which is `parent_window` (Master's own session turns inside the run window) plus every subagent transcript started in that window, each deduped by `message.id`, where `tokens_input` = raw input + cache-read + cache-write.

1. **Record basis**: the `fully_loaded_*` fields already on the eval record.
2. **Transcript basis**: recomputed with `systems/eval-harness/token_usage.py` against `~/.claude/projects/<session>.jsonl` and `<session>/subagents/*.jsonl`, attributing each subagent by its `.meta.json` `description`.

The transcript basis is the one to trust, for a reason found this run: **the record's subagent windows are captured at close time and truncate when an agent outlives the record close.** On 10/23 the record charged Knox 817,194 while the Knox subtree actually burned 2,271,642 (its nested `/plaud-discover` child, 817,194, was hidden). On 10/29 the record charged Knox 730,232 against a real 804,221, and the 01.2 child fork 51,136 against a real 260,034. Where the boot closed promptly and the agents died before the record, the two bases agree exactly (10/21: 3,215,908 both ways; 10/26: 12,230,836 both ways).

Also fixed this run: the 10/27 and 10/28 boots, which the 10/28 analysis had to leave as UNKNOWN, are now recoverable in full from the session transcripts. Those numbers below are measured, not estimated. Two prior estimates are corrected: 10/27's 05-08 block was estimated at 6.27M, it is 2.80M plus a 4.32M nested "Chief: synthesize morning briefing" child; 10/28's was estimated at 3.09M, it is 1.36M plus a 0.20M child.

**Correction to the 10-23 baseline.** The baseline used 10/19's record total of 16,954,420 as the pre-restructure anchor and concluded the new dispatch shape came in at "~35% of 10/19". That anchor is an artifact: `lenient_fallback` stamped the same window on nine steps and the harness summed them (steps 16,592,190, subagents 362,230). Reconstructed from the session transcript, the 10/19 boot actually cost **4,457,579 in / 14,881 out**, one long-lived executor ("Run boot steps 01.2-08", 2,925,334) plus five nested children. The direction reverses: the 10-22 change did not cut cost to a third of 10/19, it roughly **doubled** it (10/23 = 9,034,000 all-in, 2.03x of 10/19). The baseline's 10/13 anchor (11,772,962) is inflated the same way (steps 11,521,289 + subs 1,387,756 of overlapping windows); reconstructed, 10/13 was **2,604,336**. Its 10/21 figure (3,215,908) is sound, and the transcript basis reproduces it to the token.

## 1. Per-run table

Full boots only (one row per morning run). `boot` = Master parent window + boot step agents and their nested children. `Knox` = the boot-triggered `plaud-ingest` subtree, shown separately because it is a different workflow that boot merely spawns.

| Date | Boot tokens (transcript) | of which Master parent | of which step agents | Knox subtree | All-in | Out | Rec. FL | Wall clock | Attribution quality |
|---|---|---|---|---|---|---|---|---|---|
| 10/15 | 0 (aborted) | 0 | 0 | 0 | 0 | 0 | 0 | n/a | no run |
| 10/16 | no valid measurement | - | - | - | - | - | none | n/a | **mis-tagged**: the record's 2,392,000 window belongs to "Re-run card walkthrough with 1Password access", stamped on all 12 boot steps by `lenient_fallback`. That session never ran a boot |
| 10/19 | 4,209,291 | 491,697 | 3,717,594 | 248,288 | 4,457,579 | 14,881 | 16,954,420 (artifact) | 3,648s | **dropped**: `lenient_fallback`. Record total is the sum of overlapping fallback windows (steps 16,592,190 + subs 362,230), not a measurement |
| 10/20 | 0 (aborted, 7,315s) | 0 | 0 | 0 | 0 | 0 | 0 | 7,315s | no run |
| 10/21 | 3,179,184 | 679,607 | 2,499,577 | 36,724 | 3,215,908 | 14,269 | 3,215,908 | 1,690s | partial: 4 of 10 steps at 0 (01, 01.5, 05-08 fell outside their windows) |
| 10/22 | 5,174,037 | 1,221,982 | 3,952,055 | 1,366,038 | 6,540,075 | 49,168 | 5,565,310 | 329s | **dropped**: `steps: []`, executor used 42 Bash calls, zero per-step rows |
| 10/23 | 6,762,358 | 2,681,492 | 4,080,866 | 2,271,642 | 9,034,000 | 82,708 | 7,639,504 | 2,167s | **real**: first fully-attributed run, `windowed`/`windowed-partition` |
| 10/26 | 10,579,940 | 1,830,409 | 8,749,531 | 1,650,896 | 12,230,836 | 143,414 | 12,230,836 | 1,142s | present but corrupted: `windowed` off fabricated midnight stamps; step-01 `stale-window`, null |
| 10/27 | 24,741,457 | 11,702,930 | 13,038,527 | 14,176,020 | 44,883,731 | 286,671 | none | ~4h14m gross, ~2h stall | **no parent record**; executors `windowed` on separate agent records |
| 10/28 | 9,153,344 | 3,804,406 | 5,348,938 | 19,757,392 | 28,910,736 | 167,077 | none | ~3,028s | **no parent record**; executors `windowed`, step-05 slice 0 |
| 10/29 | 10,964,103 | 1,920,263 | 9,043,840 | 804,221 | 11,768,324 | 82,163 | 11,485,437 | 694s | mostly real: 5 of 6 stamped steps carry values, step-04 row is 0, and no 05-08 rows exist on the parent |

10/27's parent figure is an upper bound: that window contains 4h14m of session, and 9 parent turns belonging to concurrent Shep/Chase/Rigby work were excluded (2.53M of non-boot agents excluded from the agent column).

### Per-step breakdown, 10/29 (the current shape)

Two columns, because on post-10/22 runs they measure different things. The record's `steps[]` rows are Master's own turns per step window (total 2,440,134, matching the 1.92M parent window). The step's actual cost lives on its own agent record.

| Step | Agent record | Tokens in | Out | Turns | Share of run |
|---|---|---|---|---|---|
| 01 load context | none (inline by design) | inside parent 1,920,263 | - | - | 16.3% (with all Master turns) |
| 01.5 calendar | LH4XRP | 1,133,761 | 7,987 | 19 | 9.6% |
| 01.2 data pull | 80C73V | 1,087,217 | 10,630 | 17 | 9.2% |
| 01.2 nested fork | FEB0FB ("Placeholder not used", depth 2) | 260,034 | 2,254 | 6 | 2.2% |
| 02 gather | 2H8M71 | 956,803 | 11,521 | 14 | 8.1% |
| 03 verify | HTRW6C | 365,282 | 1,946 | 10 | 3.1% |
| 04 meeting context | 216OUF | 2,099,878 | 13,252 | 31 | 17.8% |
| 05-08 briefing | GQLD5I | 2,512,369 | 15,742 | 39 | 21.3% |
| 05-08 nested synthesis | JXHCGH ("Chief: synthesize morning briefing", depth 2) | 628,496 | 11,445 | 13 | 5.3% |
| Knox plaud-ingest | SAKN92 (fork) | 804,221 | 1,434 | 10 | 6.8% |

Attribution notes for 10/29: JXHCGH and FEB0FB are real boot cost that the record tagged `workflow: None`, so they appear only in the parent's `subagents` array and in no workflow total. The parent record carries no 05-08 step rows at all, and its step-04 row is 0 with `token_source: None` even though the 04 agent burned 2.10M. Both are harness gaps, not boot regressions.

### Attribution dropped, by run shape

- **Bash-only executor** (10/22): zero rows. The harness keys attribution on Edit/Write calls.
- **Lenient fallback** (10/16, 10/19): the same window is stamped on every step. Do not read those rows as per-step.
- **Fabricated stamps** (10/26): `windowed` fires against a midnight placeholder, so windows are wrong even though they are populated.
- **Async background spawns** (10/27, 10/28): the 05-08 agent, the single largest block, produced no eval record on either day. 10/29 is the first boot where it did (GQLD5I), so the biggest hole in the series is closed as of today.
- **Untagged depth-2 spawns** (10/29): two nested children, 888,530 tokens combined, carry no workflow tag.

## 2. Trend, 10/13 to 10/29

Boot-only tokens (Master + step agents + nested children, Knox excluded), transcript basis:

| Date | Boot tokens | x vs 10/19 | x vs 10/21 | Sonnet $ | What changed |
|---|---|---|---|---|---|
| 10/13 | 2,513,866 | 0.60x | 0.79x | $0.89 | pre-change shape: one executor walks 01.2-08 (1,588,566). Executor window runs 3h42m, so this may include post-boot work |
| 10/19 | 4,209,291 | 1.00x | 1.32x | $1.46 | pre-change: one executor 2,925,334 plus five nested children |
| 10/21 | 3,179,184 | 0.76x | 1.00x | $1.08 | pre-change: one executor walks steps 01.2-08 (1,654,697) |
| 10/22 | 5,174,037 | 1.23x | 1.63x | $2.43 | **10-22 dispatch change** (commit a6ec2bf73): single-purpose subagents per step. Two attempts ran; the first (846,191) failed and was never recorded |
| 10/23 | 6,762,358 | 1.61x | 2.13x | $2.85 | first fully-attributed run; six executors |
| 10/26 | 10,579,940 | 2.51x | 3.33x | $4.70 | step-04.5 Watchtower merged into the briefing agent (4,646,400 on its own) |
| 10/27 | 24,741,457 | 5.88x | 7.78x | $11.50 | Watchtower removed from boot mid-run (b9a04ca34); ~2h stall; Rigby ran concurrently in-session. Upper bound |
| 10/28 | 9,153,344 | 2.17x | 2.88x | $4.44 | post-fix shape: no Watchtower, real stamps, 05-08 back to 1.36M |
| 10/29 | 10,964,103 | 2.60x | 3.45x | $5.24 | same shape as 10/28; step-04 and 05-08 both grew |

All-in including the boot-triggered Knox subtree, in table order: 2.60M (10/13) / 4.46M (10/19) / 3.22M (10/21) / 6.54M (10/22) / 9.03M (10/23) / 12.23M (10/26) / 44.88M (10/27) / 28.91M (10/28) / 11.77M (10/29).

Reading the trend:

1. **The 10-22 change did what it was built to do, and it cost roughly 2x in tokens.** Per-step attribution went from zero rows (10/22) to a fully attributed run (10/23), and wall clock collapsed from 1,690s to 329s. The price: one agent that walked steps 01.2-08 for 1,654,697 tokens became six agents at 4,080,866 for the same work. Six fresh contexts each reload boot state. That is the central trade and it is structural, not a regression to fix.
2. **The executor block has been stable since 10/23, and Knox is what moves the total.** Step executors excluding the briefing subtree: 4,080,866 on 10/23, 4,103,131 on 10/26, 3,783,096 on 10/28, 5,902,975 on 10/29. The 10/29 rise is concentrated in step-04 (2.10M vs 0.51M on 10/28) plus step-01.5 (1.13M vs 0.76M).
3. **The 10-26/10-27 fixes bought correctness, not savings.** Real timestamps restored attribution; removing step-04.5 from boot took the single biggest line off the boot record (4.65M on 10/26) but Watchtower now pays that cost elsewhere, so it is a reclassification. The Knox no-op preflight is still unverified: 10/29 was a genuine no-op (Y2LB49, 0 tokens) and the Knox fork still burned 804,221, which is a 51% cut against the 10/26 no-op (1,650,896) but nowhere near the ~10-50K the preflight was supposed to deliver. The preflight exits the workflow before the persona walk, but the spawn still pays for the fork's own context build.
4. **The briefing block is not fixed.** It went 1,528,972 (10/23) to 4,646,400 (10/26, Watchtower merged) to 1,362,757 (10/28) to 2,512,369 (10/29). The 10-28 analysis flagged that the single-briefing-agent rule concentrates cost; 10/29 shows the same agent spawning a nested synthesis child, so the block is 3,140,865 all-in, 26.7% of the run.

## 3. Where the tokens go now (10/29 shape, 11,768,324 all-in)

1. **The 05-08 briefing subtree: 3,140,865 (26.7%).** Briefing agent 2,512,369 plus its nested "Chief: synthesize morning briefing" child 628,496. 52 turns across the two. This is the largest block and the only one that is one logical unit doing two jobs (synthesize, then verify/close).
2. **Step-04 meeting context: 2,099,878 (17.8%).** 31 turns, 113s. Same step cost 505,639 on 10/28 and 656,267 on 10/23, so this is a 4x outlier and the clearest per-step regression in the series.
3. **Master's own orchestration: 1,920,263 (16.3%).** 28 turns, 95% cache reads. This is the cost of step-01 living in the main session plus dispatching six agents.

Close behind: the read-only pull chain 01.5 + 01.2 + its fork at 2,481,012 (21.1%), which produces two JSON files. With step-02 the three deterministic blocks (01.5, 01.2, 02) are 3,177,781, or 27.0% of the boot, for work that makes zero API calls beyond the pulls themselves.

## 4. Cost per full boot in dollars

Records carry `cost_usd` at the *provider* rates this instance is routed to (Fireworks: glm-5p3-flash at $0.15/$0.50, kimi-k3 at $3/$15, deepseek-v4p1-flash at $0.30/$1.20, per `systems/eval-harness/model-pricing.json`). Those are not Sonnet dollars and cannot be used. Re-priced from the transcripts, which carry the cache split the records flatten:

10/29 full boot, 11,768,324 in / 82,163 out, 89.4% of input served as cache reads:

| Basis | Boot only | Boot + Knox |
|---|---|---|
| **Current Sonnet list ($2 / $10 per MTok, cache read $0.20, cache write $2.50/$4.00)** | **$5.24** | **$5.43** |
| Sonnet 4.6 rates ($3 / $15, the harness table's `sonnet` key) | $7.85 | $8.15 |
| Naive, every input token at $2 with no cache discount (upper bound) | $22.74 | $24.36 |

Composition at current Sonnet: Master $0.60, step agents $4.64, Knox $0.19. Per-step: 05-08 subtree $1.61, step-04 $0.90, 01.5 $0.71, 01.2 $0.59 + fork $0.21, 02 $0.43, 03 $0.17, Knox $0.19.

For contrast, the record's own `total_cost_usd` for this run is **$0.70**, because it prices the run at glm-5p3-flash rates. Anyone reading eval cost fields and believing they are Sonnet dollars is understating by roughly 8x.

Caveat: the cache-read share is what makes this number small. If the boot were run without prompt caching, the same shape costs $22.74 to $24.36 per boot. Caching is doing about 78% of the cost reduction here, more than every workflow optimization combined.

## Data quality notes

- **Recovered**: 10/27 and 10/28 boot totals, previously UNKNOWN. No parent eval record exists for either; both are fully reconstructable from session plus subagent transcripts.
- **10/27 was not one boot**: 14:56Z start, a ~2h stall, phase-2 steps at 18:10-18:25Z, close at ~19:01Z, with a Rigby code change (Watchtower removal) and three Shep/Chase preps interleaved in the same session. Its 44.9M all-in is real spend, not real boot shape.
- **Kimi-k3 is the Sonnet-tier route** here, so 10/27 and 10/28 dollar figures at provider rates are closer to Sonnet than the glm/deepseek days are. Not corrected for in this analysis; the transcript re-price is the comparable number.
- **Duplicate/misattributed records** (carried from the 10/28 analysis, still true): P7D859 tagged `workflow: boot` is the Shep "Tim Rayburn 1:1" agent; ACUY9F and 24S0E1 are windowed tail slices, not boot steps.
- **Phantom zero-token records**: 151 of the 175 records dated 10/29 carry zero tokens (mostly `type: agent, name: unknown`). They inflate record counts and carry nothing.
- **No tier-3 grade** exists on any boot record in the window, including today's QUYFPJ (success). Controller feedback rating is null on all of them.
- **Version-trend.py remains unusable** for boot: buckets blend misattributed windows.

## Recommendation (ranked by tokens recoverable)

1. **Step-04 regression first (cheapest, ~1.6M/boot).** 2,099,878 today against 505,639 on 10/28 for the same output. Read that agent's transcript before anything else; a 4x jump in one step is a bug or a runaway search, not a design cost.
2. **Collapse the read-only chain (~1.0-1.5M/boot).** 01.5, 01.2, and 02 are three fresh agents costing 3,177,781 to produce deterministic file reads. One executor for 01.5+01.2 (they share the pull-file-formats context) reclaims roughly a third of that without touching the attribution property, because each still stamps its own step.
3. **Split the briefing agent (0.6-1.0M/boot).** 05-08 is 3,140,865 and already internally delegating synthesis to a child. Make that split explicit in `workflow.md` so the child is tagged and the verify/close tail runs in a fresh, small context.
4. **Knox fork context (~0.5M/boot on no-op days).** The preflight works (0-token workflow record, NOOP verdict) but the fork still pays 804,221 for its own context before the preflight runs. Move the preflight call into the parent so the fork only spawns on a NEW verdict. This is the one item that pays off on every no-recording day, which is most days.
