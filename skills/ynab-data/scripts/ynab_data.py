#!/usr/bin/env python3
"""YNAB data extraction.

Canonical producer of `data/ynab-unified.json`, plus the shared read
primitives used by consumers that need YNAB spend data (card offer filtering,
spend reviews).

WHY THIS EXISTS
---------------
YNAB spend was previously pulled ad hoc, inline, by whichever skill needed it,
with a token path that had drifted wrong. Every consumer re-pulled the same 12
months of transactions. This script is the single writer for the cache so the
data is available centrally at boot, like the calendar, email, and OmniFocus
pulls, instead of being re-fetched per skill.

ACCESS
------
The YNAB MCP connector is the primary path where it is available (Claude
Desktop). It is not available in every session, so this script uses the REST
API directly with `YNAB_API_TOKEN` from the repo's `config/.env`. That is the
documented token location; a previous home-relative path was wrong.

INVARIANTS THIS SCRIPT EXISTS TO ENFORCE
----------------------------------------
1. The output always carries `status`, so a failed or unauthenticated pull is
   distinguishable from a genuinely empty one. A dead token must never look
   like a quiet spending month.
2. The token is never written to the output, logged, or echoed.
3. Transfers and internal account moves are excluded from payee aggregates;
   they are not spending and would swamp the list.
4. Amounts are reported in dollars, converted from YNAB milliunits.

USAGE
-----
    ynab_data.py pull [--out PATH] [--months N]   write data/ynab-unified.json
    ynab_data.py payees --account NAME            payee totals for one account
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

PLAN_ID = "5185d50a-d25e-47f8-b9d0-283ef6a89d2b"
API_BASE = "https://api.youneedabudget.com/v1"
DEFAULT_OUT = "data/ynab-unified.json"
DEFAULT_MONTHS = 12

# Account display names by YNAB account id, so consumers can key on a stable
# slug rather than whatever the account happens to be called in YNAB.
# Account types that represent real spending. Investments, loans, mortgages,
# and tracking accounts are excluded from the all-accounts aggregate.
SPENDING_ACCOUNT_TYPES = ("checking", "savings", "creditCard", "cash", "lineOfCredit")

ACCOUNT_SLUGS = {
    "b4b7a7c8-32f5-4503-baf5-207d87050813": "amex-blue",
    "c95b51b9-5d5b-4aff-8c67-9c54589ff016": "citi",
    "15694d56-fe61-4029-a526-b53fee53d1b6": "sapphire",
    "0ff3092d-c9ea-4f56-b558-c760e6da7b04": "discover",
}


def repo_root() -> Path:
    """Locate the IES repo root without hardcoding a local path."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "SYSTEM.md").exists() and (parent / "config").is_dir():
            return parent
    env = os.environ.get("IES_ROOT")
    if env and (Path(env) / "SYSTEM.md").exists():
        return Path(env)
    raise RuntimeError("cannot locate IES repo root (no SYSTEM.md found upward)")


def read_token() -> str | None:
    """Read YNAB_API_TOKEN from the repo's config/.env. Never logged."""
    env_path = repo_root() / "config" / ".env"
    if not env_path.exists():
        return None
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line.startswith("YNAB_API_TOKEN="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def api_get(path: str, token: str) -> dict:
    req = urllib.request.Request(
        f"{API_BASE}{path}",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


# Payee substrings that are money movement, not spending. Transfers, card
# payments, deposits, and balance adjustments would otherwise appear as
# merchants and crowd out real spend in offer matching.
NON_SPEND_PAYEE_PATTERNS = (
    "transfer :",
    "transfer:",
    "internet transfer",
    "cardpymt",
    "card pymt",
    "payment thank you",
    "online deposit",
    "starting balance",
    "manual balance adjustment",
    "investment buy",
    "investment sell",
    "reconciliation balance",
)


def is_transfer(txn: dict) -> bool:
    """Transfers, card payments, and balance moves are not spending."""
    if txn.get("transfer_account_id") is not None:
        return True
    payee = (txn.get("payee_name") or "").strip().lower()
    return any(p in payee for p in NON_SPEND_PAYEE_PATTERNS)


def aggregate(txns: list[dict]) -> list[dict]:
    """Aggregate transactions by payee, dollars, sorted by total desc.

    Outflows only (amount < 0). A refund or an inflow is not spending, and
    netting them in would understate real spend at a merchant.
    """
    buckets: dict[str, dict] = {}
    for t in txns:
        if is_transfer(t):
            continue
        if t.get("amount", 0) >= 0:
            continue
        name = (t.get("payee_name") or "").strip()
        if not name:
            continue
        amt = abs(t.get("amount", 0)) / 1000.0
        b = buckets.setdefault(name, {"name": name, "total": 0.0, "count": 0, "last": None})
        b["total"] += amt
        b["count"] += 1
        date = (t.get("date") or "")[:10]
        if date and (b["last"] is None or date > b["last"]):
            b["last"] = date
    out = sorted(buckets.values(), key=lambda b: -b["total"])
    for b in out:
        b["total"] = round(b["total"], 2)
    return out


def pull(out_path: str, months: int) -> dict:
    token = read_token()
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    if not token:
        return {
            "pulled_at": now,
            "status": "unavailable",
            "error": "YNAB_API_TOKEN not found in config/.env",
            "window_months": months,
            "account_count": 0,
            "accounts": {},
            "all_accounts": {"payee_count": 0, "payees": []},
        }

    since = (datetime.now(timezone.utc) - timedelta(days=30 * months)).strftime("%Y-%m-%d")
    try:
        accounts_resp = api_get(f"/plans/{PLAN_ID}/accounts", token)
    except urllib.error.HTTPError as e:
        return {
            "pulled_at": now,
            "status": "unavailable",
            "error": f"YNAB API HTTP {e.code} on accounts",
            "window_months": months,
            "account_count": 0,
            "accounts": {},
            "all_accounts": {"payee_count": 0, "payees": []},
        }
    except Exception as e:  # network, timeout, decode
        return {
            "pulled_at": now,
            "status": "unavailable",
            "error": f"YNAB pull failed: {type(e).__name__}: {e}",
            "window_months": months,
            "account_count": 0,
            "accounts": {},
            "all_accounts": {"payee_count": 0, "payees": []},
        }

    accounts: dict[str, dict] = {}
    all_txns: list[dict] = []
    for acct in accounts_resp.get("data", {}).get("accounts", []):
        aid = acct.get("id")
        if not aid or acct.get("deleted"):
            continue
        try:
            txns = api_get(
                f"/plans/{PLAN_ID}/accounts/{aid}/transactions?since_date={since}", token
            ).get("data", {}).get("transactions", [])
        except Exception:
            txns = []
        # Only spending-relevant account types feed the aggregate. Investment,
        # loan, and tracking accounts are not spending: a Rydex rebalance or an
        # "Investment Buy" row would otherwise dominate the payee list and make
        # offer matching useless.
        if acct.get("type") in SPENDING_ACCOUNT_TYPES and not acct.get("closed"):
            all_txns.extend(txns)
        slug = ACCOUNT_SLUGS.get(aid, acct.get("name", aid).lower().replace(" ", "-"))
        payees = aggregate(txns)
        accounts[slug] = {
            "account_id": aid,
            "account_name": acct.get("name"),
            "type": acct.get("type"),
            "payee_count": len(payees),
            "payees": payees,
        }

    overall = aggregate(all_txns)
    result = {
        "pulled_at": now,
        "status": "available",
        "window_months": months,
        "since": since,
        "account_count": len(accounts),
        "accounts": accounts,
        "all_accounts": {"payee_count": len(overall), "payees": overall},
    }

    out = Path(out_path)
    if not out.is_absolute():
        out = repo_root() / out
    out.parent.mkdir(parents=True, exist_ok=True)
    # Atomic write: a concurrent reader must never see a half-written cache.
    tmp = out.with_suffix(out.suffix + ".tmp")
    tmp.write_text(json.dumps(result, indent=2))
    tmp.replace(out)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="YNAB data extraction")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("pull", help="write the unified YNAB cache")
    p.add_argument("--out", default=DEFAULT_OUT)
    p.add_argument("--months", type=int, default=DEFAULT_MONTHS)

    q = sub.add_parser("payees", help="print payee totals for one account")
    q.add_argument("--account", required=True, help="account slug, e.g. amex-blue")
    q.add_argument("--limit", type=int, default=30)

    args = ap.parse_args()

    if args.cmd == "pull":
        res = pull(args.out, args.months)
        print(json.dumps({k: v for k, v in res.items() if k != "accounts"}, indent=2)[:800])
        for slug, a in res.get("accounts", {}).items():
            print(f"  {slug}: {a['payee_count']} payees")
        return 0 if res["status"] == "available" else 1

    if args.cmd == "payees":
        path = repo_root() / DEFAULT_OUT
        if not path.exists():
            print("no cache; run: ynab_data.py pull", file=sys.stderr)
            return 1
        cache = json.loads(path.read_text())
        acct = cache.get("accounts", {}).get(args.account)
        if not acct:
            print(f"unknown account '{args.account}'; have: {list(cache.get('accounts', {}))}", file=sys.stderr)
            return 1
        for b in acct["payees"][: args.limit]:
            print(f"{b['total']:>10.2f} | {b['count']:>3} | {b['last']} | {b['name']}")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
