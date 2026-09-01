---
name: chase-card-offers-discover
description: Autonomously log in and check/activate rotating categories on the Discover it Cash Back card (••••8369) via Chrome automation. Retrieves credentials from 1Password, handles login, navigates via clicks only, activates quarterly categories, and checks cap progress.
owning_agent: chase
model: haiku
trigger_keywords: [discover offers, discover card]
trigger_agents: [chase]
---

# Discover Offers — Rotating Categories & Offers

**Card:** Discover it Cash Back ••••8369

**Portal:** `https://www.discover.com/credit-cards/cash-back/activate.html`

---

## Navigation Rules

**Rule:** Navigate by clicking links and buttons only. Do not use `open_url` for any navigation. No new tabs.

---

## Step 0 — Login via 1Password

### 0a — Retrieve credentials

```bash
cat > /tmp/op-discover-login.sh << 'SCRIPT'
#!/usr/bin/env bash
set +x
set -euo pipefail
USER=$(/opt/homebrew/bin/op item get "discover.com" --account my.1password.com --fields "label=userID" 2>/dev/null)
PASS=$(/opt/homebrew/bin/op item get "discover.com" --account my.1password.com --fields "label=password" 2>/dev/null)
echo "USER_LEN:${#USER}"
echo "PASS_LEN:${#PASS}"
echo "$USER" > /tmp/.discover_user
echo "$PASS" > /tmp/.discover_pass
chmod 600 /tmp/.discover_user /tmp/.discover_pass
SCRIPT
chmod 700 /tmp/op-discover-login.sh
bash /tmp/op-discover-login.sh; rm -f /tmp/op-discover-login.sh
```

Verify `USER_LEN` and `PASS_LEN` both > 0.

### 0b — Navigate to login and sign in

Check current URL:

```javascript
document.title + ' | ' + window.location.href
```

If already on `card.discover.com` and authenticated (Account Center visible), skip to the Primary Job section.

If not authenticated, find and click Log In:

```javascript
var links = document.querySelectorAll('a, button');
for (var i = 0; i < links.length; i++) {
  var txt = (links[i].textContent || '').trim().toLowerCase();
  var href = links[i].href || '';
  if (txt === 'log in' || txt === 'sign in' || href.indexOf('login') > -1 || href.indexOf('logon') > -1) {
    links[i].click(); break;
  }
}
'navigated to login'
```

Wait for login page, then fill credentials (construct JS string in bash with actual values from temp files — never log values):

```javascript
// Fill username
var userField = document.querySelector('#userid-content, [name="userId"], [name="userID"], input[type="text"]');
if (userField) {
  userField.value = 'INJECT_USER';
  userField.dispatchEvent(new Event('input', {bubbles: true}));
  userField.dispatchEvent(new Event('change', {bubbles: true}));
}
'filled username'
```

```javascript
// Fill password
var passField = document.querySelector('#password-content, [name="password"], input[type="password"]');
if (passField) {
  passField.value = 'INJECT_PASS';
  passField.dispatchEvent(new Event('input', {bubbles: true}));
  passField.dispatchEvent(new Event('change', {bubbles: true}));
}
'filled password'
```

Click log in:

```javascript
var btns = document.querySelectorAll('button, input[type="submit"]');
for (var i = 0; i < btns.length; i++) {
  var txt = (btns[i].textContent || btns[i].value || '').trim().toLowerCase();
  if (txt.indexOf('log in') > -1 || txt.indexOf('sign in') > -1 || txt.indexOf('submit') > -1) {
    btns[i].click(); break;
  }
}
'submitted login'
```

### 0c — Verify authentication

Wait 4 seconds, then confirm:

```javascript
document.title + ' | ' + window.location.href
// Expected: "Account Center Home" or similar, URL contains card.discover.com
```

### 0d — Clean up

```bash
rm -f /tmp/.discover_user /tmp/.discover_pass
```

Once on the Discover Account Center, proceed to the Primary Job section below.

---

## Primary Job: Quarterly Category Activation

Discover's main offer is the **5% rotating category** on up to $1,500/quarter. This is the first thing to check every month.

### Step 1 — Check Current Quarter Activation Status

```javascript
document.title + ' | ' + window.location.href
// Navigate to activation page if needed
```

From the Discover dashboard:
```javascript
var links = document.querySelectorAll('a');
for (var i = 0; i < links.length; i++) {
  var txt = (links[i].textContent || '').trim();
  var href = links[i].href || '';
  if (txt.indexOf('Cash Back') > -1 || txt.indexOf('Activate') > -1 || href.indexOf('activate') > -1) {
    links[i].click(); break;
  }
}
```

Read the activation status:
```javascript
var body = document.body.innerText;
// Look for current quarter category and activation status
var idx = body.indexOf('5%');
body.substring(idx - 50, idx + 300)
```

**If not activated:** Activate immediately. Look for the "Activate Now" button:
```javascript
var btns = document.querySelectorAll('button, a');
for (var i = 0; i < btns.length; i++) {
  var txt = (btns[i].textContent || btns[i].innerText || '').trim();
  if (txt === 'Activate Now' || txt.indexOf('Activate') > -1) {
    btns[i].click(); break;
  }
}
```

**This is a CRITICAL escalation item.** If the quarter's category is not activated, David is losing 4% on all qualifying spend (5% vs 1% base). Flag immediately.

---

## Quarterly Categories Reference

| Quarter | 2026 Categories | Cap |
|---------|----------------|-----|
| Q1 (Jan–Mar) | Grocery Stores, Wholesale Clubs, Select Streaming | $1,500 |
| Q2 (Apr–Jun) | Restaurants, Home Improvement Stores | $1,500 |
| Q3 (Jul–Sep) | TBD (check portal — Discover announces ~1 month before) | $1,500 |
| Q4 (Oct–Dec) | TBD | $1,500 |

**Current Q2 2026:** Restaurants + Home Improvement — ACTIVATED as of 2026-04-01.

**Strategy:** Use Discover for all dining under $1,500/quarter cap. Beats Atlas 2x. After cap, switch back to Atlas or Chase.

---

## Step 2 — Check Cap Progress

```javascript
var body = document.body.innerText;
// Look for cap usage text like "You've earned $X of your $1,500 cap"
var idx = body.indexOf('1,500');
body.substring(idx - 100, idx + 200)
```

**Flag when within $300 of the $1,500 cap** — David needs to switch spend routing to the next-best card.

---

## Step 3 — Check for Additional Discover Offers (Discover Deals)

Discover also has card-linked merchant offers separate from the rotating category:

```javascript
// Navigate to Discover Deals / Offers section
var links = document.querySelectorAll('a');
for (var i = 0; i < links.length; i++) {
  var txt = (links[i].textContent || '').trim();
  var href = links[i].href || '';
  if (txt.indexOf('Deals') > -1 || txt.indexOf('Shop') > -1 || href.indexOf('deals') > -1) {
    links[i].click(); break;
  }
}
```

Read available offers:
```javascript
var body = document.body.innerText;
body.substring(0, 3000) // scan for offer content
```

---

## Step 4 — Filter Against YNAB Spend

Pull Discover YNAB transactions:

```bash
YNAB_TOKEN=$(grep YNAB_API_TOKEN $HOME/develop/jarvis/config/.env | cut -d= -f2)
curl -s "https://api.youneedabudget.com/v1/budgets/5185d50a-d25e-47f8-b9d0-283ef6a89d2b/accounts/0ff3092d-c9ea-4f56-b558-c760e6da7b04/transactions?since_date=$(date -v-90d +%Y-%m-%d)" \
  -H "Authorization: Bearer $YNAB_TOKEN" | \
  python3 -c "import sys,json; txns=json.load(sys.stdin)['data']['transactions']; p={}; [p.update({t['payee_name']: p.get(t['payee_name'],0)+abs(t['amount'])/1000}) for t in txns if t.get('payee_name')]; [print(f'{v:.0f} | {k}') for k,v in sorted(p.items(),key=lambda x:-x[1])[:30]]"
```

Discover is used primarily for the 5% rotating category — transaction volume on this card is lower than the others. Cross-reference any Discover Deals offers against this output.

---

## Step 5 — Add Discover Deal Offers

If Discover renders clickable offer tiles:

```javascript
// Find and click the offer tile, then look for Add/Activate button
var tiles = document.querySelectorAll('[class*="offer"], [class*="deal"]');
for (var i = 0; i < tiles.length; i++) {
  if ((tiles[i].innerText || '').indexOf('MERCHANT_NAME') > -1) {
    tiles[i].click(); break;
  }
}

// Then find the activation button
var btns = document.querySelectorAll('button, a');
for (var i = 0; i < btns.length; i++) {
  var txt = (btns[i].textContent || btns[i].innerText || '').trim();
  if (txt === 'Add Offer' || txt === 'Activate' || txt === 'Get Offer') {
    btns[i].click(); break;
  }
}
```

**Note:** Discover's Deals section has a limited number of offers vs. Amex/Citi. The rotating category is the primary value driver — Discover Deals are secondary.

---

## YNAB Account ID (Discover)

| Card | YNAB Account ID |
|------|----------------|
| Discover it ••••8369 | `0ff3092d-c9ea-4f56-b558-c760e6da7b04` |

**Budget ID:** `5185d50a-d25e-47f8-b9d0-283ef6a89d2b`
**Token location:** `config/.env` → `YNAB_API_TOKEN`

---

## What to Check Each Month

| Check | Frequency | Action if Issue |
|-------|-----------|----------------|
| Quarterly category activated? | Monthly | **ACTIVATE IMMEDIATELY — escalate to Chief** |
| Cap progress ($1,500/quarter) | Monthly | Flag when within $300 — adjust routing |
| Next quarter category announced? | Monthly from ~day 15 | Note in tracker, update routing strategy |
| Cashback balance | Monthly | Note available balance in tracker |

---

## Update After Walkthrough

Update `systems/credit-cards/benefits-tracker.json` → `discover-it`:
- `last_reviewed` → today
- `rotating_categories.q[N]_2026.confirmed` → today (if activated)
- `cashback_available` → current balance from portal
- `current_balance` → outstanding balance
- Note next quarter's category if announced

## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/chase-card-offers-discover-latest.json
```

Content:
```json
{
  "skill": "chase-card-offers-discover",
  "agent": "chase",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from the morning briefing or a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output, `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action.

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill chase-card-offers-discover
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/chase-card-offers-discover.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

