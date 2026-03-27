#!/usr/bin/env python3
"""
Last Bottle Wines Monitor — polls the lastbottlewines.com homepage for the
current active flash offer, scores it against David's taste profile, and
sends Slack alerts via Jarvis bot when a buy is found.

The active offer is embedded in the page HTML as a <script type="application/json">
block (Shopify pattern). No headless browser needed.

Usage:
    python3 monitor.py              # single poll
    python3 monitor.py --daemon     # continuous polling during drop windows
    python3 monitor.py --test       # dry run, prints score without alerting

OPERATIONAL NOTES (from 2026-03-26 Marathon session):

1. EGRESS: Python urllib may be blocked in sandboxed environments (Cowork VM).
   Fallback: Use Chrome MCP to load lastbottlewines.com and extract product JSON
   via JS: document.querySelectorAll('script[type="application/json"]')

2. PURCHASE AUTOMATION: Use Shopify cart API for instant purchases — NOT DOM
   manipulation (too slow, wines flip in seconds during Marathon):
     fetch('/cart/add.js', {method:'POST', headers:{'Content-Type':'application/json'},
       body: JSON.stringify({items:[{id: VARIANT_ID, quantity: QTY}]})})
     .then(() => window.location.href = '/checkout')
   Then click "Pay Now" on checkout page. Ship to wine locker: 10400 Clarence Dr,
   Frisco, TX 75034. Pay with Discover card.

3. SLACK: Always send alerts to #jarvis (C0AN2PQNXBR) via Jarvis bot (post.py),
   never via Slack MCP connector (posts as David, no notifications). Read replies
   from #jarvis using bot token + conversations.history API.

4. REPLY CHECKING: For always_alert_score (20+) wines, check Slack replies every
   20-30 seconds for 3-5 min after alerting. For lower scores, check every 40-60s.
   Missing a "Buy X" reply because the wine flipped is the worst failure mode.

5. TRY-IT RULE: If discount >60% AND price <$50, alert even if below min_score.
   Label as "Worth a Try". David added this during Marathon skeleton crew window.

6. MARATHON MODE: Wines flip instantly when sold out. During Marathon events,
   poll as fast as every 30-60 seconds. Skeleton crew (18:00-23:59) is slower
   but still active — some offers linger 5-10 minutes.
"""

import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from html import unescape
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROFILE_PATH = SCRIPT_DIR / "taste-profile.json"
SEEN_PATH = SCRIPT_DIR / "data" / "seen.json"
LOG_PATH = SCRIPT_DIR / "data" / "monitor.log"
SLACK_BOT = SCRIPT_DIR.parent / "slack-bot" / "post.py"

SITE_URL = "https://lastbottlewines.com"

# Slack channels
CHANNEL_JARVIS = "C0AN2PQNXBR"   # #jarvis
CHANNEL_DM     = "U0ANHV5UXEW"   # DM to David


# ── Helpers ──────────────────────────────────────────────────────────────────

def log(msg: str):
    """Append timestamped message to log file."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def load_profile() -> dict:
    with open(PROFILE_PATH) as f:
        return json.load(f)


def load_seen() -> dict:
    """Load seen wines. Structure: { product_id: { alerted: bool, score: int, ts: str } }"""
    if SEEN_PATH.exists():
        try:
            with open(SEEN_PATH) as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_seen(seen: dict):
    SEEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SEEN_PATH, "w") as f:
        json.dump(seen, f, indent=2)


def fetch_active_offer() -> dict | None:
    """Fetch the current active flash offer from the Last Bottle homepage.

    Shopify embeds the active product as JSON in a <script type="application/json">
    block. We parse the HTML to extract it — no JS rendering needed.
    """
    req = urllib.request.Request(SITE_URL + "/", headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
    })
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode("utf-8")
    except Exception as e:
        log(f"ERROR fetching homepage: {e}")
        return None

    # Extract all JSON blocks from <script type="application/json"> tags
    json_blocks = re.findall(
        r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>',
        html, re.DOTALL
    )

    for block in json_blocks:
        block = block.strip()
        if not block:
            continue
        try:
            data = json.loads(block)
        except (json.JSONDecodeError, ValueError):
            continue

        # Look for product-shaped data: must have id, title, price, handle
        if isinstance(data, dict) and all(k in data for k in ("id", "title", "handle", "price")):
            return data

    log("WARNING: No active product found in page HTML")
    return None



def strip_html(text: str) -> str:
    """Remove HTML tags and decode entities."""
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", " ", text)
    return unescape(clean).strip()


def extract_score(text: str) -> int | None:
    """Extract wine score from description text. Returns the first/most prominent score found."""
    if not text:
        return None

    pattern = r'\b(9[0-9]|100)\s*(?:points?|pts?\.?\b|\+|-point)'
    scores = []
    for m in re.finditer(pattern, text, re.IGNORECASE):
        val = int(m.group(1))
        start = max(0, m.start() - 50)
        context_before = text[start:m.start()].lower()

        # Skip scores about the winemaker, not this wine
        if any(w in context_before for w in ["earning", "winemaker", "winemaking", "maker", "earned"]):
            continue
        after = text[m.end():m.end() + 15].strip()
        if after.startswith(("-year", "%", "-acre", " acre", " year", " earning")):
            continue

        scores.append(val)

    if scores:
        return scores[0]

    # Fallback: "rated 97" patterns
    matches = re.findall(r'(?:rated|rating|score[ds]?)\s+(9[0-9]|100)\b', text, re.IGNORECASE)
    if matches:
        return int(matches[0])
    return None


def extract_varietal(title: str, wine_type: str = "", tags: list = None) -> str:
    """Best-effort varietal extraction from product title, type, and tags."""
    combined = f"{title} {wine_type} {' '.join(tags or [])}".lower()

    varietals = [
        "cabernet sauvignon", "pinot noir", "nebbiolo", "sangiovese",
        "syrah", "shiraz", "malbec", "grenache", "zinfandel", "merlot",
        "chardonnay", "sauvignon blanc", "rosé", "rose",
    ]
    for v in varietals:
        if v in combined:
            if v == "shiraz":
                return "syrah"
            if v == "rose":
                return "rosé"
            return v

    # Wine type field (e.g., "Rosé Wine", "Red Wine")
    if "rosé" in wine_type.lower() or "rose" in wine_type.lower():
        return "rosé"

    # Blend indicators
    blend_words = ["red blend", "red wine", "blend", "meritage", "cuvee", "cuvée"]
    for b in blend_words:
        if b in combined:
            return "red blend"

    return "unknown"


def score_wine(product: dict, profile: dict) -> dict:
    """Score a wine product against the taste profile. Returns scoring breakdown.

    Scoring uses title, type, tags, price, and discount only — the homepage
    embed has no description/tasting notes (those are JS-rendered).
    """
    title = product.get("title", "")
    title_lower = title.lower()
    wine_type = product.get("type", "")
    tags = product.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]

    # Prices from the embedded JSON are in cents
    raw_price = product.get("price", 0) or 0
    raw_compare = product.get("compare_at_price", 0) or 0
    # Detect cents vs dollars: Shopify embeds prices in cents (>= 100 for a $1 wine)
    price = raw_price / 100.0 if raw_price >= 100 else float(raw_price)
    compare_price = raw_compare / 100.0 if raw_compare >= 100 else float(raw_compare)

    # If product has variants, use variant pricing as fallback
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

    # 1. Varietal
    varietal = extract_varietal(title, wine_type, tags)
    varietal_score = profile.get("varietals", {}).get(varietal, 0)
    if varietal_score > 0:
        score += varietal_score
        reasons.append(f"Varietal ({varietal}): +{varietal_score}")

    # 2. Region — match title only to avoid body false positives
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

    # 3. Critic score — not available from homepage embed (JS-rendered)
    wine_score = extract_score(title)  # rare, but sometimes in title

    if wine_score:
        for threshold_str in sorted(profile.get("score_bonuses", {}).keys(), key=int, reverse=True):
            if wine_score >= int(threshold_str):
                bonus = profile["score_bonuses"][threshold_str]
                score += bonus
                reasons.append(f"Score ({wine_score}pts): +{bonus}")
                break

    # 4. Discount percentage
    if compare_price > 0 and price > 0:
        discount_pct = round((1 - price / compare_price) * 100)
        for threshold_str in sorted(profile.get("discount_bonuses", {}).keys(), key=int, reverse=True):
            if discount_pct >= int(threshold_str):
                bonus = profile["discount_bonuses"][threshold_str]
                score += bonus
                reasons.append(f"Discount ({discount_pct}% off): +{bonus}")
                break

    # 5. Cult producer — title only (no description available)
    for producer in profile.get("cult_producers", []):
        if producer.lower() in title_lower:
            score += 8
            reasons.append(f"Cult producer ({producer}): +8")
            break

    # 6. Library vintage bonus
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


def format_alert(result: dict) -> str:
    """Format a Slack alert message for a wine match."""
    title = result["title"]
    price = result["price"]
    compare = result["compare_price"]
    wine_score = result["wine_score"]
    composite = result["composite_score"]
    handle = result["handle"]

    discount_pct = round((1 - price / compare) * 100) if compare > 0 and price > 0 else 0
    link = f"{SITE_URL}/products/{handle}" if handle else SITE_URL

    alert_label = result.get("alert_label", "BUY THIS")
    lines = [
        f"*Last Bottle Alert — {alert_label}*",
        f"",
        f"*{title}*",
        f"*${price:.0f}* (was ${compare:.0f} — {discount_pct}% off)" if compare > 0 else f"*${price:.0f}*",
    ]

    if wine_score:
        lines.append(f"Critic score: *{wine_score} points*")

    lines.append(f"Match strength: {composite}/50")
    lines.append(f"")

    for reason in result["reasons"]:
        lines.append(f"  {reason}")

    lines.append(f"")
    lines.append(f"<{link}|Buy Now>")

    return "\n".join(lines)


def send_alert(message: str, channel: str = CHANNEL_JARVIS):
    """Send Slack alert via Jarvis bot to #jarvis channel (default).

    IMPORTANT: Always send to #jarvis (CHANNEL_JARVIS) so David can reply
    in-channel. Only DM for urgent/private items. The Slack MCP connector
    posts as David — never use it for outbound messages.
    """
    try:
        result = subprocess.run(
            [sys.executable, str(SLACK_BOT), channel, message],
            capture_output=True, text=True, timeout=15,
        )
        output = result.stdout.strip()
        log(f"Slack alert sent to {channel}: {output}")
    except Exception as e:
        log(f"ERROR sending Slack alert: {e}")


def current_window() -> str | None:
    """Return the current drop window name, or None if outside windows."""
    now = datetime.now()
    current_time = now.hour * 60 + now.minute

    windows = {
        "pinot_hour":       (11 * 60, 12 * 60 + 59),
        "hour_of_power":    (13 * 60, 14 * 60 + 59),
        "steals_and_deals": (15 * 60, 16 * 60 + 59),
        "five_oclock":      (17 * 60, 17 * 60 + 59),
        "skeleton_crew":    (18 * 60, 23 * 60 + 59),
    }

    for name, (start, end) in windows.items():
        if start <= current_time <= end:
            return name
    return None


def poll_interval_seconds(window: str | None) -> int:
    """Return poll interval based on current window relevance."""
    if window == "hour_of_power":
        return 120      # Every 2 min — this is THE window
    elif window in ("pinot_hour", "five_oclock"):
        return 180      # Every 3 min
    elif window == "steals_and_deals":
        return 300      # Every 5 min
    elif window == "skeleton_crew":
        return 600      # Every 10 min
    else:
        return 900      # Every 15 min between windows


def run_poll(profile: dict, seen: dict, dry_run: bool = False) -> dict:
    """Single poll cycle — fetch the active offer, score it, alert if worthy."""
    product = fetch_active_offer()
    if not product:
        return seen

    pid = str(product.get("id", ""))
    title = product.get("title", "unknown")

    # Skip already-alerted wines
    if pid in seen and seen[pid].get("alerted"):
        log(f"Already alerted: {title}")
        return seen

    result = score_wine(product, profile)

    min_score = profile.get("min_score_to_alert", 15)
    max_price = profile.get("max_price", 250)

    # Record in seen (even if we don't alert)
    seen[pid] = {
        "title": result["title"],
        "score": result["composite_score"],
        "price": result["price"],
        "ts": datetime.now().isoformat(),
        "alerted": False,
    }

    # Determine alert tier
    always_alert = profile.get("always_alert_score", 20)
    try_it_rule = profile.get("try_it_rule", {})
    try_it_enabled = try_it_rule.get("enabled", False)
    try_it_min_discount = try_it_rule.get("min_discount_pct", 60)
    try_it_max_price = try_it_rule.get("max_price", 50)

    discount_pct = 0
    if result["compare_price"] > 0 and result["price"] > 0:
        discount_pct = round((1 - result["price"] / result["compare_price"]) * 100)

    # Check try-it rule: >60% off AND <$50, even if below min_score
    qualifies_try_it = (
        try_it_enabled
        and discount_pct > try_it_min_discount
        and result["price"] < try_it_max_price
        and result["composite_score"] < min_score
    )

    if not result["available"]:
        log(f"SOLD OUT: {title}")
    elif result["price"] > max_price and result["price"] > 0:
        log(f"TOO EXPENSIVE: {title} — ${result['price']}")
    elif result["composite_score"] >= min_score or qualifies_try_it:
        # Determine alert label
        if result["composite_score"] >= always_alert:
            alert_label = "BUY THIS"
        elif qualifies_try_it and result["composite_score"] < min_score:
            alert_label = "Worth a Try"
        else:
            alert_label = "Worth a Look"
        result["alert_label"] = alert_label

        msg = format_alert(result)
        if dry_run:
            print(f"\n{'='*60}")
            print(f"WOULD ALERT (score {result['composite_score']}, label: {alert_label}):")
            print(msg)
            print(f"{'='*60}")
        else:
            log(f"ALERT [{alert_label}]: {title} — score {result['composite_score']}, ${result['price']}")
            send_alert(msg)
        seen[pid]["alerted"] = True
    else:
        log(f"SKIP: {title} — score {result['composite_score']}, ${result['price']}")

    if not dry_run:
        save_seen(seen)

    return seen


def daemon_loop(profile: dict):
    """Continuous polling loop that adjusts frequency by drop window."""
    log("Daemon starting — monitoring Last Bottle active offers")
    seen = load_seen()

    # Clean seen entries older than 24 hours
    cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
    seen = {k: v for k, v in seen.items() if v.get("ts", "") > cutoff}
    save_seen(seen)

    while True:
        window = current_window()
        interval = poll_interval_seconds(window)

        if window:
            log(f"Active window: {window} — polling every {interval}s")
        else:
            log(f"Between windows — next poll in {interval}s")

        seen = run_poll(profile, seen)
        time.sleep(interval)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    profile = load_profile()

    if "--test" in sys.argv:
        log("Test mode — scoring active offer without alerting")
        run_poll(profile, {}, dry_run=True)
        return

    if "--daemon" in sys.argv:
        daemon_loop(profile)
        return

    # Single poll
    seen = load_seen()
    run_poll(profile, seen)


if __name__ == "__main__":
    main()
