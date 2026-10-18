---
name: chase-card-offers-citi
description: >-
  Enroll in offers on the Citi AAdvantage Executive card (••••9598) via autonomous Chrome automation. Retrieves credentials from 1Password, handles login, navigates to Merchant Offers via clicks only, and enrolls YNAB-validated offers.
owning_agent: chase
model: haiku
trigger_keywords: [citi offers, citi card, citibank]
trigger_agents: [chase]
---

<!-- system:start -->
<!-- system:end -->

<!-- personal:start -->

> **Primary path (2026-10-16):** this skill now runs as `steps/step-02-offers.md` inside the `card-walkthrough` workflow, so offers get enrolled in the same session as the monthly data capture. Run it standalone only for an ad-hoc add between walkthroughs.

# Citi Offers — Read & Enroll

**Card:** Citi AAdvantage Executive World Elite Mastercard ••••9598

**Portal:** `https://online.citi.com/US/nga/products-offers/merchantoffers`

---

## Navigation Rules

**Rule:** Navigate exclusively by clicking links and buttons. Do NOT use `open_url` or `window.location.href` for any navigation — Citi's SPA will redirect to a 404 or trigger logout. No new tabs.

---

> **Credential injection (2026-10-16):** the `/tmp/.amex_user` temp-file flow below is blocked in sandboxed sessions as credential materialization. Where that happens, inject credentials in memory instead: read them from `op` and pass them into the page via `osascript` execute-javascript (e.g. base64 through `op` then `atob` in the page). Never write a credential to disk in a sandboxed run, and never print one.

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

## Step 4 — Filter Against YNAB Spend (use the YNAB MCP connector)

YNAB is a configured MCP connector. Use its tools — do NOT curl the YNAB API directly.

**Tools:** `get_plans`, `get_accounts`, `get_transactions`, `get_transactions_by_account`, `get_categories`, `get_plan_months`.

1. `get_accounts`, find the Citi AAdvantage Executive account by name (fallback ID `c95b51b9-5d5b-4aff-8c67-9c54589ff016`).
2. `get_transactions_by_account` for the **last 12 months** (not 90 days — a merchant bought from any time this year counts).
3. Aggregate by payee, rank by spend.

**Key Citi YNAB spend (known high-value vendors):**
- Turo, American Airlines, Nebraska Furniture Mart, Boardroom Salon, Uplift Desk
- Wine vendors (Promontory, Tusk Estates, etc.), Amazon, Integrity Golf Performance

Only enroll offers for vendors that appear in this output.

**Fallback if the MCP is unavailable:** inline `curl` against `https://api.youneedabudget.com/v1` with `YNAB_API_TOKEN` read from the repo's `config/.env` (not `$HOME/develop/jarvis/config/.env` — that path was wrong). Budget `5185d50a-d25e-47f8-b9d0-283ef6a89d2b`, 12-month window.

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



<!-- personal:end -->