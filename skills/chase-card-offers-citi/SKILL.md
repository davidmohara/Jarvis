---
name: chase-card-offers-citi
description: Autonomously log in and enroll in offers on the Citi AAdvantage Executive card (••••9598) via Chrome automation. Retrieves credentials from 1Password, handles login, navigates to Merchant Offers via clicks only, and enrolls YNAB-validated offers.
owning_agent: chase
model: haiku
trigger_keywords: [citi offers, citi card, citibank]
trigger_agents: [chase]
---

# Citi Offers — Read & Enroll

**Card:** Citi AAdvantage Executive World Elite Mastercard ••••9598

**Portal:** `https://online.citi.com/US/nga/products-offers/merchantoffers`

---

## Navigation Rules

**Rule:** Navigate exclusively by clicking links and buttons. Do NOT use `open_url` or `window.location.href` for any navigation — Citi's SPA will redirect to a 404 or trigger logout. No new tabs.

---

## Step 0 — Login via 1Password

### 0a — Retrieve credentials

```bash
cat > /tmp/op-citi-login.sh << 'SCRIPT'
#!/usr/bin/env bash
set +x
set -euo pipefail
USER=$(/opt/homebrew/bin/op item get "citi.com" --account my.1password.com --fields "label=User ID" 2>/dev/null)
PASS=$(/opt/homebrew/bin/op item get "citi.com" --account my.1password.com --fields "label=password" 2>/dev/null)
echo "USER_LEN:${#USER}"
echo "PASS_LEN:${#PASS}"
echo "$USER" > /tmp/.citi_user
echo "$PASS" > /tmp/.citi_pass
chmod 600 /tmp/.citi_user /tmp/.citi_pass
SCRIPT
chmod 700 /tmp/op-citi-login.sh
bash /tmp/op-citi-login.sh; rm -f /tmp/op-citi-login.sh
```

Verify `USER_LEN` and `PASS_LEN` both > 0.

### 0b — Navigate to login and sign in

Check current URL:

```javascript
document.title + ' | ' + window.location.href
```

If already on `online.citi.com` and authenticated (dashboard visible, no login form), skip to Step 1.

If not authenticated, find and click Log In:

```javascript
var links = document.querySelectorAll('a, button');
for (var i = 0; i < links.length; i++) {
  var txt = (links[i].textContent || '').trim().toLowerCase();
  var href = links[i].href || '';
  if (txt === 'log in' || txt === 'sign on' || href.indexOf('login') > -1 || href.indexOf('signon') > -1) {
    links[i].click(); break;
  }
}
'navigated to login'
```

Wait for the login page, then fill credentials (construct JS string in bash with actual values from temp files — never log values):

```javascript
// Fill username
var userField = document.querySelector('#username, [name="username"], #userId, input[type="text"]');
if (userField) {
  userField.value = 'INJECT_USER';
  userField.dispatchEvent(new Event('input', {bubbles: true}));
  userField.dispatchEvent(new Event('change', {bubbles: true}));
}
'filled username'
```

```javascript
// Fill password
var passField = document.querySelector('#password, [name="password"], input[type="password"]');
if (passField) {
  passField.value = 'INJECT_PASS';
  passField.dispatchEvent(new Event('input', {bubbles: true}));
  passField.dispatchEvent(new Event('change', {bubbles: true}));
}
'filled password'
```

Click sign on:

```javascript
var btns = document.querySelectorAll('button, input[type="submit"]');
for (var i = 0; i < btns.length; i++) {
  var txt = (btns[i].textContent || btns[i].value || '').trim().toLowerCase();
  if (txt.indexOf('sign on') > -1 || txt.indexOf('log in') > -1 || txt.indexOf('submit') > -1) {
    btns[i].click(); break;
  }
}
'submitted login'
```

### 0c — Verify authentication

Wait 4 seconds, then confirm:

```javascript
document.title + ' | ' + window.location.href
// Expected: "Citibank Account Dashboard" or similar, URL contains online.citi.com/US/ag/
```

### 0d — Clean up

```bash
rm -f /tmp/.citi_user /tmp/.citi_pass
```

Once on the Citi dashboard, proceed to Step 1.

---

## Step 1 — Navigate to Merchant Offers

From the Citi dashboard, click through the nav:

```javascript
// 1. Click "Rewards & Offers" in the top nav
var links = document.querySelectorAll('a, button, [role="button"]');
for (var i = 0; i < links.length; i++) {
  if ((links[i].textContent || '').trim() === 'Rewards & Offers') {
    links[i].click(); break;
  }
}
```

Then click "Merchant Offers" from the dropdown:
```javascript
var links = document.querySelectorAll('a');
for (var i = 0; i < links.length; i++) {
  if ((links[i].textContent || '').trim() === 'Merchant Offers') {
    links[i].click(); break;
  }
}
```

Confirm you're there:
```javascript
document.title + ' | ' + window.location.href
// Expected: "Citibank Online - Merchant Offers | https://online.citi.com/US/nga/products-offers/merchantoffers"
```

---

## Step 2 — Confirm Card and Read Savings

```javascript
var body = document.body.innerText;
body.substring(body.indexOf('Citi'), body.indexOf('Citi') + 200)
// Should show: "Citi®/AAdvantage® Executive World Elite Mastercard®-9598" and "Your savings to date: $XX.XX"
```

---

## Step 3 — Read All Available Offers

Offers are rendered as `cds-tile` elements grouped by category (Featured, Travel, Dining, Shopping, Health & Wellness, Other):

```javascript
var tiles = document.querySelectorAll('cds-tile[class*="mo-offer"]');
var offers = [];
var seen = {};
for (var i = 0; i < tiles.length; i++) {
  var text = tiles[i].innerText.trim().replace(/\n/g, ' | ').substring(0, 120);
  if (text && !seen[text]) {
    seen[text] = true;
    offers.push(i + ': ' + text);
  }
}
offers.join('\n')
```

This returns unique offers with their tile index. Duplicates appear due to Citi rendering each offer in multiple category sections — the dedup handles that.

**To filter by category**, first click the category tab:
```javascript
// Click a category filter (e.g., "Travel")
var btns = document.querySelectorAll('button');
for (var i = 0; i < btns.length; i++) {
  if ((btns[i].innerText || '').trim() === 'Travel') {
    btns[i].click(); break;
  }
}
// Available: All, Featured, Travel, Dining, Shopping, Entertainment, Health & Wellness, Other
```

---

## Step 4 — Filter Against YNAB Spend

Before enrolling, pull Citi's YNAB transactions:

```bash
YNAB_TOKEN=$(grep YNAB_API_TOKEN $HOME/develop/jarvis/config/.env | cut -d= -f2)
curl -s "https://api.youneedabudget.com/v1/budgets/5185d50a-d25e-47f8-b9d0-283ef6a89d2b/accounts/c95b51b9-5d5b-4aff-8c67-9c54589ff016/transactions?since_date=$(date -v-90d +%Y-%m-%d)" \
  -H "Authorization: Bearer $YNAB_TOKEN" | \
  python3 -c "import sys,json; txns=json.load(sys.stdin)['data']['transactions']; p={}; [p.update({t['payee_name']: p.get(t['payee_name'],0)+abs(t['amount'])/1000}) for t in txns if t.get('payee_name')]; [print(f'{v:.0f} | {k}') for k,v in sorted(p.items(),key=lambda x:-x[1])[:30]]"
```

**Key Citi YNAB spend (known high-value vendors):**
- Turo, American Airlines, Nebraska Furniture Mart, Boardroom Salon, Uplift Desk
- Wine vendors (Promontory, Tusk Estates, etc.), Amazon, Integrity Golf Performance

Only enroll offers for vendors that appear in this output.

---

## Step 5 — Open an Offer's Detail Panel

Click the tile by index from Step 3:

```javascript
var tiles = document.querySelectorAll('cds-tile');
tiles[INDEX].click(); // replace INDEX with tile number
```

Confirm the detail panel opened:
```javascript
var body = document.body.innerText;
// Look for "Expires [Month]" near the merchant name to confirm detail pane is open
var idx = body.indexOf('Expires');
body.substring(idx - 100, idx + 200)
```

The panel shows: merchant name, cashback amount, expiry date, card (should show -9598), and the **"Enroll in Offer"** button.

**If already enrolled:** The panel will NOT have an "Enroll in Offer" button — it was previously added (by you or David).

---

## Step 6 — Enroll in the Offer

```javascript
var btns = document.querySelectorAll('button');
for (var i = 0; i < btns.length; i++) {
  if ((btns[i].innerText || '').trim() === 'Enroll in Offer') {
    btns[i].click(); break;
  }
}
```

Confirm enrollment — the "Enroll in Offer" button should disappear:
```javascript
var btns = document.querySelectorAll('button');
var found = false;
for (var i = 0; i < btns.length; i++) {
  if ((btns[i].innerText || '').trim() === 'Enroll in Offer') { found = true; break; }
}
found ? 'Still showing — check for error message' : 'Enrolled ✅'
```

**If enrollment fails:** Check for the error text:
```javascript
var body = document.body.innerText;
body.indexOf('Unable to enroll') > -1 ? 'Citi backend error — retry once, then skip' : 'No error'
```

If `"Unable to enroll merchant offer"` appears: retry once. If it fails again, skip and note in tracker. This is a Citi-side intermittent error, not a navigation problem.

---

## Step 7 — Return to Offer List

After enrolling, click the "All" tab to return to the full list:

```javascript
var btns = document.querySelectorAll('button');
for (var i = 0; i < btns.length; i++) {
  if ((btns[i].innerText || '').trim() === 'All') {
    btns[i].click(); break;
  }
}
```

Repeat Steps 5–7 for each target offer.

---

## YNAB Account ID (Citi)

| Card | YNAB Account ID |
|------|----------------|
| Citi AA Exec ••••9598 | `c95b51b9-5d5b-4aff-8c67-9c54589ff016` |

**Budget ID:** `5185d50a-d25e-47f8-b9d0-283ef6a89d2b`
**Token location:** `config/.env` → `YNAB_API_TOKEN`

---

## Update After Walkthrough

Update `systems/credit-cards/benefits-tracker.json`:
- `card_linked_offers.citi-aa-exec.last_reviewed` → today
- Add newly enrolled offers to `enrolled` array with `added_by: "Jarvis"` and `added_date`
- If any offers failed to enroll, add to `enrollment_failures_[DATE]` array
- Add expiring offers to `upcoming_deadlines`

## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/chase-card-offers-citi-latest.json
```

Content:
```json
{
  "skill": "chase-card-offers-citi",
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

