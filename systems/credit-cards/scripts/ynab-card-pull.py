#!/usr/bin/env python3
"""
ynab-card-pull.py — YNAB REST API fallback for card walkthrough

Used when portal authentication is unavailable. Pulls last 90 days of
transactions per card, derives spend by category, estimates credit usage.

Budget ID: 5185d50a-d25e-47f8-b9d0-283ef6a89d2b
Auth: YNAB_API_TOKEN env var (or passed as first argument)

Usage:
    YNAB_API_TOKEN=<token> python3 ynab-card-pull.py
    python3 ynab-card-pull.py <token>
    python3 ynab-card-pull.py <token> --card citi-aa-exec
    python3 ynab-card-pull.py <token> --days 60
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from collections import defaultdict

# ── Config ──────────────────────────────────────────────────────────────────

BUDGET_ID = "5185d50a-d25e-47f8-b9d0-283ef6a89d2b"
BASE_URL = "https://api.ynab.com/v1"

# Map YNAB account names → card keys used in benefits-tracker.json
# Update these if YNAB account names change
CARD_MAP = {
    "Amex Platinum":            "amex-plat",
    "Amex Blue Cash Preferred": "amex-bcp",
    "Citi AAdvantage Exec":     "citi-aa-exec",
    "Discover it":              "discover-it",
    "Chase Sapphire":           "chase-sapphire",
    "Atlas Visa":               "atlas-visa",
}

# Discover rotating categories by quarter
# Update each January when Q1 is announced
DISCOVER_ROTATING = {
    2026: {
        "Q1": {"categories": ["Groceries", "Wholesale Clubs", "Streaming"], "cap": 1500, "rate": 0.05},
        "Q2": {"categories": ["Restaurants", "Home Improvement"],           "cap": 1500, "rate": 0.05},
        "Q3": {"categories": ["TBD"],                                        "cap": 1500, "rate": 0.05},
        "Q4": {"categories": ["TBD"],                                        "cap": 1500, "rate": 0.05},
    }
}

# YNAB category name fragments → normalized spend categories
# Used to estimate credit eligibility (e.g., Grubhub credit requires Grubhub spend)
CATEGORY_KEYWORDS = {
    "groceries":        ["grocery", "groceries", "supermarket", "whole foods", "kroger", "heb", "costco", "sam's"],
    "restaurants":      ["restaurant", "dining", "food", "grubhub", "doordash", "uber eats", "chipotle"],
    "streaming":        ["netflix", "disney", "hulu", "spotify", "apple tv", "youtube", "streaming", "wsj", "chatgpt"],
    "home_improvement": ["home depot", "lowe's", "ace hardware", "home improvement"],
    "travel":           ["airline", "hotel", "airbnb", "vrbo", "car rental", "uber", "lyft", "transit"],
    "wholesale":        ["costco", "sam's club", "bj's wholesale"],
}


# ── YNAB API helpers ─────────────────────────────────────────────────────────

def ynab_get(token: str, endpoint: str) -> dict:
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"YNAB API error {e.code} on {endpoint}: {body}")


def get_accounts(token: str) -> list:
    data = ynab_get(token, f"/budgets/{BUDGET_ID}/accounts")
    return data["data"]["accounts"]


def get_transactions(token: str, since_date: str) -> list:
    endpoint = f"/budgets/{BUDGET_ID}/transactions?since_date={since_date}"
    data = ynab_get(token, endpoint)
    return data["data"]["transactions"]


# ── Quarter helpers ──────────────────────────────────────────────────────────

def get_quarter(date: datetime) -> str:
    return f"Q{(date.month - 1) // 3 + 1}"


def quarter_date_range(year: int, quarter: str) -> tuple:
    q = int(quarter[1])
    start_month = (q - 1) * 3 + 1
    end_month = start_month + 2
    start = datetime(year, start_month, 1)
    # Last day of end_month
    if end_month == 12:
        end = datetime(year, 12, 31)
    else:
        end = datetime(year, end_month + 1, 1) - timedelta(days=1)
    return start, end


# ── Spend analysis ───────────────────────────────────────────────────────────

def milliunits_to_dollars(milliunits: int) -> float:
    """YNAB stores amounts as milliunits (1000 = $1.00). Outflows are negative."""
    return abs(milliunits) / 1000.0


def categorize_payee(payee_name: str) -> list:
    """Return matching spend categories for a payee."""
    name_lower = (payee_name or "").lower()
    matched = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in name_lower for kw in keywords):
            matched.append(category)
    return matched


def analyze_card(account_id: str, account_name: str, transactions: list, days: int) -> dict:
    """Summarize spend for a single card account."""
    card_txns = [t for t in transactions if t["account_id"] == account_id and t["amount"] < 0]

    total_spend = sum(milliunits_to_dollars(t["amount"]) for t in card_txns)
    txn_count = len(card_txns)

    # Spend by YNAB category name
    by_category = defaultdict(float)
    for t in card_txns:
        cat = t.get("category_name") or "Uncategorized"
        by_category[cat] += milliunits_to_dollars(t["amount"])

    # Spend by normalized keyword category
    by_keyword_category = defaultdict(float)
    for t in card_txns:
        payee = t.get("payee_name", "")
        for kcat in categorize_payee(payee):
            by_keyword_category[kcat] += milliunits_to_dollars(t["amount"])

    # Top payees
    by_payee = defaultdict(float)
    for t in card_txns:
        payee = t.get("payee_name", "Unknown")
        by_payee[payee] += milliunits_to_dollars(t["amount"])
    top_payees = sorted(by_payee.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "account_name": account_name,
        "period_days": days,
        "total_spend": round(total_spend, 2),
        "transaction_count": txn_count,
        "spend_by_ynab_category": {k: round(v, 2) for k, v in sorted(by_category.items(), key=lambda x: x[1], reverse=True)},
        "spend_by_keyword_category": {k: round(v, 2) for k, v in by_keyword_category.items()},
        "top_payees": [{"payee": p, "total": round(t, 2)} for p, t in top_payees],
    }


def analyze_discover_rotating(card_txns: list, year: int) -> dict:
    """Quarter-aware Discover bonus category analysis."""
    results = {}
    rotating = DISCOVER_ROTATING.get(year, {})

    for quarter, config in rotating.items():
        q_start, q_end = quarter_date_range(year, quarter)
        q_txns = [
            t for t in card_txns
            if t["amount"] < 0
            and q_start <= datetime.strptime(t["date"], "%Y-%m-%d") <= q_end
        ]

        bonus_cats = [c.lower() for c in config["categories"]]
        bonus_spend = 0.0
        bonus_txns = []

        for t in q_txns:
            payee = t.get("payee_name", "")
            kw_cats = categorize_payee(payee)
            if any(kc in bonus_cats or any(bc in kc for bc in bonus_cats) for kc in kw_cats):
                amount = milliunits_to_dollars(t["amount"])
                bonus_spend += amount
                bonus_txns.append({"date": t["date"], "payee": payee, "amount": round(amount, 2)})

        cap = config["cap"]
        eligible_spend = min(bonus_spend, cap)
        bonus_earned = round(eligible_spend * config["rate"], 2)
        cap_remaining = max(0, cap - bonus_spend)

        results[quarter] = {
            "categories": config["categories"],
            "rate": f"{int(config['rate']*100)}%",
            "cap": cap,
            "bonus_spend_ytd": round(bonus_spend, 2),
            "cap_remaining": round(cap_remaining, 2),
            "bonus_earned_est": bonus_earned,
            "transactions": bonus_txns,
            "note": "Spend derived from payee name matching — verify against portal for exact figures",
        }

    return results


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    # Token from env or arg
    token = os.environ.get("YNAB_API_TOKEN") or (sys.argv[1] if len(sys.argv) > 1 else None)
    if not token:
        print("ERROR: YNAB_API_TOKEN not set. Pass as env var or first argument.")
        sys.exit(1)

    # Parse optional flags
    target_card = None
    days = 90
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--card" and i + 1 < len(args):
            target_card = args[i + 1]; i += 2
        elif args[i] == "--days" and i + 1 < len(args):
            days = int(args[i + 1]); i += 2
        else:
            i += 1

    since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    today = datetime.now()
    year = today.year
    current_quarter = get_quarter(today)

    print(f"Pulling YNAB data — last {days} days (since {since_date})")
    print(f"Budget: {BUDGET_ID}\n")

    # Fetch data
    accounts = get_accounts(token)
    transactions = get_transactions(token, since_date)

    # Build account lookup
    account_lookup = {a["name"]: a for a in accounts}

    output = {
        "generated_at": datetime.now().isoformat(),
        "period_days": days,
        "since_date": since_date,
        "source": "ynab_fallback",
        "current_quarter": current_quarter,
        "cards": {}
    }

    for ynab_name, card_key in CARD_MAP.items():
        if target_card and card_key != target_card:
            continue

        account = account_lookup.get(ynab_name)
        if not account:
            # Try partial match
            matches = [a for a in accounts if ynab_name.lower() in a["name"].lower()]
            account = matches[0] if matches else None

        if not account:
            output["cards"][card_key] = {
                "status": "NOT_FOUND",
                "note": f"No YNAB account matched '{ynab_name}'. Check CARD_MAP in script.",
            }
            print(f"  [{card_key}] NOT FOUND in YNAB — check CARD_MAP name")
            continue

        account_id = account["id"]
        balance_dollars = account["balance"] / 1000.0  # negative = owe money

        analysis = analyze_card(account_id, ynab_name, transactions, days)
        analysis["ynab_account_id"] = account_id
        analysis["current_balance_ynab"] = round(balance_dollars, 2)
        analysis["status"] = "YNAB_FALLBACK"

        # Discover-specific rotating category analysis
        if card_key == "discover-it":
            card_txns = [t for t in transactions if t["account_id"] == account_id]
            analysis["discover_rotating_categories"] = analyze_discover_rotating(card_txns, year)

        output["cards"][card_key] = analysis
        print(f"  [{card_key}] ${analysis['total_spend']:.2f} spend over {days}d — {analysis['transaction_count']} txns")

    print(f"\nDone. {len(output['cards'])} cards analyzed.")
    print(json.dumps(output, indent=2))

    # Write output file for benefits-tracker update
    out_path = os.path.join(os.path.dirname(__file__), "ynab-fallback-output.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nOutput written to: {out_path}")


if __name__ == "__main__":
    main()
