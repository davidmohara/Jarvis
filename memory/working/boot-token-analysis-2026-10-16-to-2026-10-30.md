# Boot Workflow Token Analysis — 2026-10-16 through 2026-10-30

Source: `systems/eval-harness/runs/` (per-run JSON). Window has **20 closed boot eval records**
(10-16 through 10-18 and 10-24/25 had no boot runs). Six are excluded as attribution artifacts;
14 are clean.

## Method

Run total = inline step tokens (steps with no `executed_by_agent_id`, i.e. not partitioned from a
subagent) + `subagents[]` tokens + orphan executor agent records in the same session whose window
falls inside the run and whose agent_id is not already in `subagents[]`.

This reproduces the records' own `total_tokens_input` / `total_tokens_output` exactly on all eight
non-artifact records that carry those fields (IA1AX8, QNQLC5, IP36P9, QQIZKW, O84R10, VXWWK6,
BK458M, QUYFPJ). The ninth (L9PFZ9) carries them too but is a window artifact and does not
reconcile. `parent_window` is NOT additive — it is the same transcript the steps are sliced from.

## 1. Per-run and per-day totals

### Clean runs

| Day | Run | Status | In | Out | Cost | Wall | Note |
|---|---|---|---:|---:|---:|---:|---|
| 10-19 | eval-20261019T203151-IA1AX8 | success | 16,954,420 | 87,061 | $7.759 | 61m | lenient_fallback x10 — inflated, see below |
| 10-21 | eval-20261021T151330-QNQLC5 | success | 2,536,301 | 9,201 | $0.682 | 28m | pre-refactor baseline |
| 10-22 | eval-20261022T005939-7OUMW0 | incomplete | 363,194 | 4,895 | $0.018 | 2.0h | |
| 10-22 | eval-20261022T114238-IP36P9 | partial | 4,471,902 | 31,320 | $0.180 | 5m | |
| 10-22 | eval-20261022T180318-TPZO43 | incomplete | 1,908,326 | 16,293 | $1.239 | 1.6h | |
| 10-23 | eval-20261023T131721-QQIZKW | partial | 5,869,892 | 66,237 | $3.146 | 36m | |
| 10-26 | eval-20261026T141311-O84R10 | partial | 12,205,154 | 141,651 | $0.718 | 19m | |
| 10-26 | eval-20261026T150015-B7W765 | incomplete | 18,682,480 | 96,233 | $0.894 | 4.5h | |
| 10-26 | eval-20261026T221723-NMXCZV | incomplete | 140,498 | 2,312 | $0.017 | 13h | open record, nothing attached |
| 10-27 | eval-20261027T145618-Q0REQ2 | incomplete | 5,924,418 | 44,204 | $1.206 | 38m | |
| 10-27 | eval-20261027T185559-YB6YAM | success | 0 | 0 | $0.000 | 22s | degenerate, 2 steps, no tokens |
| 10-28 | eval-20261028T164542-26QC3W | incomplete | 5,972,974 | 73,615 | $2.432 | 45m | |
| 10-29 | eval-20261029T135634-QUYFPJ | success | 11,640,026 | 79,705 | $0.699 | 12m | |
| 10-30 | eval-20261030T140251-G668EK | success | 8,160,423 | 90,939 | $0.654 | 14m | |
| **Σ** | **14 runs** | | **94,830,008** | **743,666** | **$19.64** | | |

### Excluded as attribution artifacts (6 records, 281.9M in / $43.6)

| Run | In | Why |
|---|---:|---|
| eval-20261023T202035-L9PFZ9 | 252,560,557 | `close_reason`: state.yaml completion predates record open by 2.1h — spurious open. Swallowed 37 session subagents. |
| eval-20261029T000322-ZUIMG1 | 23,664,087 | 11.3h window opened 00:03, closed 11:22 — swallowed the whole overnight session. |
| eval-20261022T194016-5C4OEY | 3,893,686 | spurious open (3.6h) |
| eval-20261028T192259-BK458M | 1,098,225 | spurious open (2.1h) |
| eval-20261026T194100-VXWWK6 | 634,056 | spurious open (2.5h) |
| eval-20261020T153125-J42OVZ | 0 | spurious open (2.0h) |

All six carry `monitoring.close_reason`; the first two are the ones that matter for the number.
As-recorded window total (all 20): **376,680,619 in / 2,342,850 out / $63.23** — dominated by one
misattributed record and not a usable figure.

### Per-day (clean)

| Day | Runs | In | Out | Cost | Avg in/run |
|---|---:|---:|---:|---:|---:|
| 10-19 | 1 | 16,954,420 | 87,061 | $7.76 | 16,954,420 |
| 10-21 | 1 | 2,536,301 | 9,201 | $0.68 | 2,536,301 |
| 10-22 | 3 | 6,743,422 | 52,508 | $1.44 | 2,247,807 |
| 10-23 | 1 | 5,869,892 | 66,237 | $3.15 | 5,869,892 |
| 10-26 | 3 | 31,028,132 | 240,196 | $1.63 | 10,342,711 |
| 10-27 | 2 | 5,924,418 | 44,204 | $1.21 | 2,962,209 |
| 10-28 | 1 | 5,972,974 | 73,615 | $2.43 | 5,972,974 |
| 10-29 | 1 | 11,640,026 | 79,705 | $0.70 | 11,640,026 |
| 10-30 | 1 | 8,160,423 | 90,939 | $0.65 | 8,160,423 |

## 2. Per-step breakdown

Of the 94.8M clean input, only **28.6M (30%)** carries step-level attribution. The rest sits in
`subagents[]` entries with no step detail. Shares below are of step-attributable tokens.

| Step group | In | Out | Cost | Share | Runs with data |
|---|---:|---:|---:|---:|---:|
| 01.5 calendar pull | 7,373,897 | 39,590 | $3.55 | 25.8% | 5 |
| 01.2 data pull | 6,356,252 | 35,209 | $3.53 | 22.2% | 5 |
| 04 gather meeting context | 3,572,784 | 6,044 | $0.10 | 12.5% | 4 |
| 02 gather data | 3,350,444 | 10,959 | $0.13 | 11.7% | 6 |
| 01 load context (inline, Master) | 2,476,969 | 5,063 | $0.06 | 8.7% | 4 |
| 05 synthesize briefing | 2,004,803 | 13,567 | $0.32 | 7.0% | 3 |
| 07 verify completion | 1,276,763 | 4,955 | $0.06 | 4.5% | 2 |
| 03 verify phase 2 | 905,275 | 2,490 | $0.07 | 3.2% | 5 |
| 08 knox completion check | 688,404 | 2,949 | $0.04 | 2.4% | 2 |
| 06 scan workflows | 575,684 | 2,757 | $0.03 | 2.0% | 2 |

Spawn-side view (clean runs, 62.7M spawn input total):

| Spawn class | Count | In | Share | Cost |
|---|---:|---:|---:|---:|
| boot-executor spawns | 29 | 42,774,711 | 68.2% | $7.15 |
| plaud-ingest (Knox) spawns | 8 | 7,733,729 | 12.3% | $1.03 |
| unattributed (no agent record / no step detail) | 32 | 12,228,767 | 19.5% | $3.30 |

Note: plaud-ingest per-step rows only appear where the Knox step record survived; in clean runs the
plaud spawns are captured as whole-run subagent totals, not per step.

## 3. Trend callouts

**10-29 vs 10-30** (both success):

| | 10-29 QUYFPJ | 10-30 G668EK | Δ |
|---|---:|---:|---:|
| Input | 11,640,026 | 8,160,423 | −29.9% |
| Output | 79,705 | 90,939 | +14.1% |
| Cost | $0.699 | $0.654 | −6.5% |
| Wall clock | 694s | 831s | +20% |
| Spawns | 9 (9.57M) | 8 (7.94M) | |

The 10-29 excess is concentrated in step-02 gather-data (1,117k in for 3,095 out) and step-01
load-context (575k). 10-30 moved the weight into the briefing subagent: step-05 1,212k and step-07
858k, but the gather chain dropped to 305k for step-02.

**Dedicated-subagent refactor (landed 2026-10-22).** `workflows/boot/workflow.md` documents it: every
step except step-01 now runs as its own bounded spawn with a literal `workflows/boot/workflow.md`
reference in the prompt (without that string the harness drops per-step attribution) and a
"do not read any other step file" line. Before it, one long-lived executor walked steps 01.2–04:

- 10-21 QNQLC5 (pre): one executor subagent, 1,654,697 input for steps 01.2/02/03/04 at
  82k/545k/495k/531k — i.e. 500–545k input per step to produce 300–1,000 output tokens.
- Post: 10-23 QQIZKW steps 01.5/01.2/02/03/04 at 212k/301k/156k/80k/163k.
- workflow.md also records the prior failure modes the refactor fixed: a one-call calendar pull that
  became a 57-turn walk of the whole workflow at 6.27M tokens, and a 2026-10-22 executor that did
  everything through 42 Bash calls and left zero per-step records.
- Effect on the numbers: pre/post clean averages are 9.75M vs 6.28M input per run, but n=2 pre, so
  treat as directional. The structural change is real: pre-refactor input was concentrated in one
  executor at ~500k/step; post-refactor the gather chain runs 80–300k/step.

**Spikes:** 10-26 (31.0M across 3 runs, avg 10.3M) is the highest real day — B7W765 alone at
18.7M, effectively one executor subagent that accumulated 15.3M input over a 4.5h window. 10-19's 16.95M is not a real spike: ten steps carry
`token_source: lenient_fallback`, the retired method the schema says "stamped whole-transcript
fabrications onto steps whose windows matched nothing." Two steps got the identical 5,249,805 and
seven got the identical 418,613. Do not use 10-19 as a baseline.

**Attribution hygiene is the dominant error source, not token spend.** Six of 20 records (30%) are
window artifacts worth 75% of the raw token total. Any report that reads `total_tokens_input`
without the `monitoring.close_reason` filter will be wrong by an order of magnitude.

## 4. Cost

Derivable: `systems/eval-harness/model-pricing.json` carries every model in these records
(glm-5p3-flash $0.15/$0.50 per Mtok, glm-5p3 $1.40/$4.40, kimi-k3 $3.00/$15.00,
deepseek-v4p1-flash $0.30/$1.20).

| Basis | n | Avg in | Avg out | Avg cost | Median cost |
|---|---:|---:|---:|---:|---:|
| Clean runs | 14 | 6,773,572 | 53,119 | $1.40 | $0.70 |
| Clean + success | 5 | 7,858,234 | 53,381 | $1.96 | $0.65 |
| All records (uncorrected) | 20 | 18,970,306 | 118,012 | $3.22 | — |

Success-only mean is dragged up by the lenient-fallback 10-19 run ($7.76). Excluding it:
4 runs, $0.51 average, $0.67 median. **A representative boot costs about $0.70 and 6–8M input
tokens**; anything an order of magnitude above that is an attribution artifact, not spend.
