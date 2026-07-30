---
  last-promoted-check: 2026-07-26
  last-promoted-check: 2026-07-26
  last-promoted-check: 2026-07-26
  last-promoted-check: 2026-07-27
  last-promoted-check: 2026-07-27
  last-promoted-check: 2026-07-27
  last-promoted-check: 2026-07-28
  last-promoted-check: 2026-07-29
salience:
  score: 0
  last-promoted-check: 2026-07-30
---


## WHOOP — 30-Day Summary (Apr 25 – May 25, 2026)

**Recovery trend:** Improving. Monthly avg ~51%, but last 7 days averaging ~62%. Recent green days indicate accumulated strain is resolving.

**HRV:** Down ~8% from baseline earlier in month; recovering. Watch for further improvement this week.

**Resting HR:** Up ~4 bpm at low point; trending back down.

**Sleep:** Chronic debt is the primary driver of poor recovery days. Sleep efficiency and duration consistently suboptimal. No single acute stressor — pattern of accumulated shortfall.

**Strain/Workouts:** Training lopsided. Cardio/Zone 2 work present, but only **one strength/lifting session in the last 30 days**. Significant gap. Muscle mass protection requires consistent resistance work, especially given longevity goals.

---

## DEXA — Latest Scan (2026-04-01, March 24, 2026)

**File:** `~/Dropbox/Family/Health/David - DEXA/2026-04 bodyspec-results.pdf`

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total weight | 237.8 lbs | 210 lbs | ⚠️ 27.8 lbs over |
| Body fat % | 19.6% | 17% | ⚠️ 2.6% over |
| Lean mass | 182.0 lbs | — | Stable |
| Fat mass | 46.6 lbs | — | — |
| VAT | 2.60 lbs | <1.95 lbs (2024 baseline) | 🔴 33% above baseline |
| A/G ratio | 1.51 | <1.0 | 🔴 Elevated |

**VAT trend:** 1.95 lbs (2024 baseline) → peaked 3.12 lbs → 2.60 lbs current. Trending down from peak but still elevated. VAT is the most important metabolic risk marker here — visceral fat directly correlates with cardiovascular and metabolic disease risk.

**Body fat trend:** Flat at ~19–20% for approximately one year. No meaningful progress toward 17% goal. Requires either dietary intervention, significant training volume increase, or both.

**Key concern for Dr. Randol:** Bring VAT trend and A/G ratio to June 1 Function Health visit (or follow-up). These map directly to 4 Horsemen metabolic risk.

---

## Bloodwork

**Last draw:** 2025-12-05 (Function Health)
**File:** `~/Dropbox/Family/Health/David - Bloodwork/2025/2025-12-05.pdf`
**Next draw:** June 1, 2026 (scheduled)

Outstanding items to surface at/after June 1 draw:
- ApoB trend (was 60th percentile in prior review)
- hsCRP / inflammatory markers given elevated VAT
- Hormone panel (Total T, Free T, E2) — DHEA 50mg daily; check for imbalance
- Vitamin D3, Omega-3 Index
- Correlate with body comp changes since December

---

## Infrastructure Fix This Session

**WHOOP MCP server** — fully repaired:
1. **State parameter bug fixed** — `mcp-server.ts` patched to generate 32-char hex state and pass to `getAuthorizationUrl()`
2. **Token persistence fixed** — post-exchange, token now written back to `.env`; also added `WHOOP_ACCESS_TOKEN` to `.mcp.json` env block so it auto-loads on restart
3. **Rebuilt** with Node 20 (nvm) — `npm run build` successful
4. **Re-authenticated** — fresh token active as of this session

Next WHOOP session should connect seamlessly without re-auth.

---

## Pending Action Items

| Item | Priority | Notes |
|------|----------|-------|
| Schedule next DEXA | High | Due ~June 24 (quarterly from March 24). Book now. |
| Function Health draw | Confirmed | June 1 — no action needed |
| Bring VAT/A/G to Dr. Randol | High | At or after June 1 visit |
| Add strength sessions | High | Only 1 in last 30 days. Minimum 2x/week target. |
| Review peptide protocols | Medium | Obsidian `projects/Peptides.md` — not reviewed this session |
| Review Lifebook health goals | Medium | Confirm weight/body fat targets still calibrated correctly |

---

## Data Source Map (for next session)

- WHOOP: `mcp__whoop__*`
- Bloodwork: `~/Dropbox/Family/Health/David - Bloodwork/[YEAR]/[DATE].pdf`
- DEXA: `~/Dropbox/Family/Health/David - DEXA/[YEAR-MM] bodyspec-results.pdf`
- Body comp: `~/Dropbox/Family/Health/David - Health Tracking.xlsx`
- Protocols: `projects/Peptides.md` + Obsidian `Mind/Health/`
- Physician notes: `~/Dropbox/Family/Health/` + Obsidian `Mind/Health/`
- Lifebook goals: Obsidian Lifebook
