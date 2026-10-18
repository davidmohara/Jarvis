---
name: ynab-data
description: YNAB data extraction — the canonical pull into data/ynab-unified.json plus shared read primitives (per-account payee totals, spend ranking). Trigger on 'pull ynab', 'ynab spend', 'what did I spend at', or as boot step-01.2 Pull E.
owning_agent: chase
model: haiku
trigger_keywords: [ynab, budget, spend, payee, you need a budget]
trigger_agents: [chase]
---

# YNAB Data

**Canonical producer of `data/ynab-unified.json`.** This is the single writer for the YNAB cache, and the read path for every consumer that needs spend data (card offer filtering, spend reviews, budget questions).

## Why this exists

YNAB spend used to be pulled ad hoc by whichever skill needed it, with a token path that had drifted wrong, re-fetching the same 12 months every time. The cache makes the data available centrally at boot, like the calendar, email, and OmniFocus pulls.

## Access

The YNAB MCP connector is the primary path where available (Claude Desktop). It is not available in every session, so the pull script uses the REST API directly with `YNAB_API_TOKEN` from the repo's `config/.env`. That is the documented token location. The token is never written to the output or logged.

## Usage

```bash
python3 skills/ynab-data/scripts/ynab_data.py pull [--out PATH] [--months N]
python3 skills/ynab-data/scripts/ynab_data.py payees --account amex-blue [--limit 30]
```

`pull` writes `data/ynab-unified.json` and prints a summary. It exits non-zero when `status` is not `available`, so a dead token is never mistaken for a quiet spending month.

## Output contract

```json
{
  "pulled_at": "2026-10-16T22:38:39Z",
  "status": "available",
  "window_months": 12,
  "since": "2025-10-21",
  "account_count": 30,
  "accounts": {
    "amex-blue": {"account_id": "...", "account_name": "Amex - Blue", "type": "creditCard",
                  "payee_count": 90,
                  "payees": [{"name": "H-E-B", "total": 6314.55, "count": 42, "last": "2026-10-11"}]}
  },
  "all_accounts": {"payee_count": 711, "payees": [...]}
}
```

`status` is always present. A failed or unauthenticated pull is distinguishable from an empty one.

## Invariants

1. **Transfers, card payments, deposits, and balance adjustments are excluded.** They are money movement, not spending, and would otherwise appear as merchants. See `NON_SPEND_PAYEE_PATTERNS`.
2. **Only spending account types feed `all_accounts`** (checking, savings, creditCard, cash, lineOfCredit). Investment, loan, mortgage, and tracking accounts are excluded, or a Rydex rebalance dominates the list.
3. **Amounts are dollars**, converted from YNAB milliunits.
4. **12-month default window.** A merchant bought from at any point in the year is a legitimate target; a 90-day window is too narrow for offer matching.

## Consumers

- `workflows/card-walkthrough/steps/step-02-offers.md` and the `chase-card-offers-*` skills — filter card offers against real spend.
- Boot step-01.2 Pull E — refresh the cache each boot so it is current when needed.
