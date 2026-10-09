---
name: political-monitor
description: Daily build of the political news monitor - scan all sources twice consecutively via WebSearch, cluster, analyze L/R framing with a 0-100 correlation score plus a relevance score that decays for topics repeated across consecutive days, surface gap topics, render the Watchtower dashboard. Mondays also propose new sources.
agent: rigby
model: sonnet
---

<!-- system:start -->
# Political News Monitor - Run Workflow

**Goal:** Produce a fresh `dashboard.html` that shows, neutrally, how the left and the right are covering the same stories (side-by-side framing + a 0-100 correlation score) and which topics only one side is covering.

**Owner:** Rigby (Platform Infrastructure).

**System dir:** `systems/political-monitor/` (sandbox mount: `/sessions/.../mnt/IES/systems/political-monitor/`).

**Build spec (authoritative):** `specs/political-monitor.md`. Read it if anything here is ambiguous.

**Hard rules:**
- Fetch ONLY via the `WebSearch` tool with `allowed_domains`. RSS-from-sandbox 403s; never use it. Never `curl`/`requests` a blocked outlet.
- Fetch only sources where `active` AND `accessible` are both true in `sources.json`.
- **Every source (and every beat search) is scanned twice, consecutively, every run — no exceptions.** This happens before clustering or scoring; it is not a retry-on-failure, it always runs.
- Analysis stays neutral and descriptive. The correlation label explains divergence in framing; it never says which side is right.
- Every topic (shared and gap) gets a `relevance` score from `topic_history.json`: new topics score high; topics seen on 2+ consecutive days score progressively lower. Scoring happens before deciding what makes the final dashboard ordering.
- Public news only. No Protected/Confidential data is involved.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

**Dispatch model:** This workflow runs as a **Rigby** subagent spawned by the coordinator, never inline in the coordinator's session. Rigby executes the steps below in order; the git commit in step-09 routes through `skills/git/SKILL.md`.

### Steps

| # | File | Executed by |
|---|------|-------------|
| 1 | `steps/step-01-load-roster.md` | spawned subagent (Rigby) |
| 2 | `steps/step-02-harvest.md` | spawned subagent (Rigby) |
| 3 | `steps/step-03-write-harvest.md` | spawned subagent (Rigby) |
| 4 | `steps/step-04-pre-cluster.md` | spawned subagent (Rigby) |
| 5 | `steps/step-05-analyze.md` | spawned subagent (Rigby) |
| 6 | `steps/step-06-source-suggestions.md` | spawned subagent (Rigby) |
| 7 | `steps/step-07-render-validate.md` | spawned subagent (Rigby) |
| 8 | `steps/step-08-send-dashboard.md` | spawned subagent (Rigby) |
| 9 | `steps/step-09-cleanup-commit.md` | spawned subagent (Rigby) |

Begin: `steps/step-01-load-roster.md`
<!-- system:end -->
