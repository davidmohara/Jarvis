---
type: working
task_id: "one-texas-scorecard-goals"
session_id: "jarvis-2026-04-20-afternoon"
agent_source: master
created: 2026-04-20T20:00:00
expires: 2026-04-22T20:00:00
status: active
context: "One Texas scorecard workflow, goals file, PPTX, skill rewrites, Plaud ingest, 1:1 prep"
---

# Session Summary — April 20, 2026 (Afternoon/Evening)

## What Was Built

### 1:1 Prep Sheets
- **Scott McMichael** (MD, North America): Built with March 2026 actuals from Obsidian. Pushed to reMarkable at `/Improving/One-on-ones/Scott McMichael 1on1 Prep Apr 2026`
- **Don McGreal** (President, Dallas): Built with Wendy's transition (Tonya Guadiz), LiftNet, Convergence AI, scheduling flag (Don can't do 3 PM — available 3:30+). Pushed to reMarkable.

### Plaud Ingest
- Auth token refreshed via Chrome localStorage extraction. Stored at `~/.config/plaud/token.json` (expires Dec 21, 2026).
- Knox agent ingested 2 recordings from Apr 17: SMU collaboration meeting + onboarding training.
- Speakers confirmed: Speaker 1 = David O'Hara, Speaker 4 = David O'Hara (both confirmed by David this session).

### Four Chase Skills — Rewritten
All four PowerBI skills updated to use Chrome MCP as primary (replacing Playwright):
- `skills/revenue-tracker/SKILL.md` — Phase 0 Obsidian cache check (30-day freshness)
- `skills/co-sell-pipeline/SKILL.md` — Phase 0 cache check (7-day freshness)
- `skills/pipeline-snapshot/SKILL.md` — Phase 0 cache check (7-day freshness)
- `skills/new-clients/SKILL.md` — Phase 0 cache check (30-day freshness)
Each skill checks Obsidian first; only hits PowerBI if snapshot is stale.

### One Texas Scorecard PPTX
- Built: `mnt/IES/One Texas Q1 2026 Scorecard.pptx`
- Single slide, three columns: Revenue (G1), Pipeline + Co-Sell (G1+G4), Goal Scorecard summary (G1–G5)
- Data: April 17 Obsidian snapshot (within all freshness windows — no PowerBI pull needed)
- Goal-aligned: shows actuals vs. 2026 annual One Texas targets, not per-enterprise splits

### 2026 Goals File
- Created: `Mind/One Texas/2026 Goals.md` in Obsidian vault
- All five goal pillars from Texas Goals 2026 slide (Dec 29, 2025)
- **Correction applied:** Goals are One Texas totals, no per-enterprise splits
- Annual targets: 3 new anchors (OTX total), $15M co-sell (Q2 deadline), 10 speaking engagements, 2 large + 4 medium accounts, 1 EDP H2
- Scorecard alignment map included

### Scorecard Workflow Updated
- `workflows/one-texas-scorecard/workflow.md` — references goals file, Chrome MCP (not Playwright)
- `steps/step-05-save-to-obsidian.md` — now appends Goal Alignment table to every Obsidian snapshot

## Key Data (Q1 End, March 31, 2026)

| Metric | Value | vs Goal |
|--------|-------|---------|
| Dallas Revenue March | $3.1M | +3% vs target, 101% 90-day |
| South Texas Revenue March | $2.8M | -16% vs target, 83% 90-day |
| One Texas Revenue March | $5.9M | -7% vs combined target |
| One Texas 90-day Weighted Pipeline | $21.6M | On track (Rock 1) |
| New Logos Q1 | 4 of 9 Q1 target | Annual target: not formally set |
| New Anchors Q1 | 1 of 3 annual target | 33% — recoverable Q2–Q3 |
| Co-Sell Total | $1.1M of $15M | 7.5% — CRITICAL, Q2 deadline |

## Errors Logged This Session
- err-20260420-001: Missed Obsidian context for One Texas data (Scott prep built from email only)
- err-20260420-002: Wrong logo/anchor numbers reported (0/0 vs actual 4/1)
- err-20260420-003: Plaud ingest skipped at boot — third recurrence

## Open Items Carried Forward
- Google follow-ups (Kapil Dai, Salah, David Faircloth) — 16+ days cold, unresolved
- Tomorrow Fund Breakfast closing remarks — due/overdue
- Don McGreal 1:1 time — needs confirming at 3:30 PM
- EA hire — common blocker across rocks
- Tonight's OmniFocus due list (8 items, most likely to slip)
