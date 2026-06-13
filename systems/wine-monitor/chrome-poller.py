#!/usr/bin/env python3
"""
Chrome-based Last Bottle poller for sandboxed environments.
Since direct HTTP is blocked, this script is meant to be driven
by the Cowork agent calling Chrome MCP + JS execution in a loop.

This file just holds the scoring logic so the agent can call it
on extracted product JSON without re-implementing scoring each time.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROFILE_PATH = SCRIPT_DIR / "taste-profile.json"
SEEN_PATH = SCRIPT_DIR / "data" / "seen.json"

def load_profile():
    with open(PROFILE_PATH) as f:
        return json.load(f)

def load_seen():
    if SEEN_PATH.exists():
        try:
            with open(SEEN_PATH) as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_seen(seen):
    SEEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SEEN_PATH, "w") as f:
        json.dump(seen, f, indent=2)

def extract_varietal(title, wine_type="", tags=None):
    combined = f"{title} {wine_type} {' '.join(tags or [])}".lower()
    varietals = [
        "cabernet sauvignon", "pinot noir", "nebbiolo", "sangiovese",
        "syrah", "shiraz", "malbec", "grenache", "zinfandel", "merlot",
        "chardonnay", "sauvignon blanc", "rosé", "rose",
    ]
    for v in varietals:
        if v in combined:
            if v == "shiraz": return "syrah"
            if v == "rose": return "rosé"
            return v
    blend_words = ["red blend", "red wine", "blend", "meritage", "cuvee", "cuvée"]
    for b in blend_words:
        if b in combined:
            return "red blend"
    return "unknown"

def score_wine(product, profile):
    title = product.get("title", "")
    title_lower = title.lower()
    wine_type = product.get("type", "")
    tags = product.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]

    raw_price = product.get("price", 0) or 0
    raw_compare = product.get("compare_at_price", 0) or 0
    price = raw_price / 100.0 if raw_price >= 100 else float(raw_price)
    compare_price = raw_compare / 100.0 if raw_compare >= 100 else float(raw_compare)

    variants = product.get("variants", [])
    if variants and isinstance(variants[0], dict):
        v = variants[0]
        v_price = v.get("price", 0) or 0
        v_compare = v.get("compare_at_price", 0) or 0
        if v_price and not raw_price:
            price = float(v_price) / 100.0 if v_price >= 100 else float(v_price)
        if v_compare and not raw_compare:
            compare_price = float(v_compare) / 100.0 if v_compare >= 100 else float(v_compare)

    score = 0
    reasons = []

    varietal = extract_varietal(title, wine_type, tags)
    varietal_score = profile.get("varietals", {}).get(varietal, 0)
    if varietal_score > 0:
        score += varietal_score
        reasons.append(f"Varietal ({varietal}): +{varietal_score}")

    best_region = ""
    best_region_score = 0
    for region, pts in profile.get("regions", {}).items():
        if region.lower() in title_lower:
            if pts > best_region_score:
                best_region_score = pts
                best_region = region
    if best_region_score > 0:
        score += best_region_score
        reasons.append(f"Region ({best_region}): +{best_region_score}")

    # Critic score from title or passed in via page_score
    wine_score = product.get("page_score")
    if not wine_score:
        pattern = r'\b(9[0-9]|100)\s*(?:points?|pts?\.?\b|\+|-point)'
        for m in re.finditer(pattern, title, re.IGNORECASE):
            wine_score = int(m.group(1))
            break

    if wine_score:
        for threshold_str in sorted(profile.get("score_bonuses", {}).keys(), key=int, reverse=True):
            if wine_score >= int(threshold_str):
                bonus = profile["score_bonuses"][threshold_str]
                score += bonus
                reasons.append(f"Score ({wine_score}pts): +{bonus}")
                break

    if compare_price > 0 and price > 0:
        discount_pct = round((1 - price / compare_price) * 100)
        for threshold_str in sorted(profile.get("discount_bonuses", {}).keys(), key=int, reverse=True):
            if discount_pct >= int(threshold_str):
                bonus = profile["discount_bonuses"][threshold_str]
                score += bonus
                reasons.append(f"Discount ({discount_pct}% off): +{bonus}")
                break

    for producer in profile.get("cult_producers", []):
        if producer.lower() in title_lower:
            score += 8
            reasons.append(f"Cult producer ({producer}): +8")
            break

    vintage_match = re.search(r'\b(19[89]\d|20[0-2]\d)\b', title)
    if vintage_match:
        vintage_year = int(vintage_match.group(1))
        age = datetime.now().year - vintage_year
        min_age = profile.get("library_vintage_min_age", 8)
        if age >= min_age:
            bonus = profile.get("library_vintage_bonus", 5)
            score += bonus
            reasons.append(f"Library vintage ({vintage_year}, {age}yr): +{bonus}")

    return {
        "product_id": str(product.get("id", "")),
        "title": title,
        "varietal": varietal,
        "price": price,
        "compare_price": compare_price,
        "wine_score": wine_score,
        "composite_score": score,
        "reasons": reasons,
        "handle": product.get("handle", ""),
        "available": product.get("available", False),
    }

if __name__ == "__main__":
    # Read product JSON from stdin
    product = json.load(sys.stdin)
    profile = load_profile()
    result = score_wine(product, profile)
    print(json.dumps(result, indent=2))
