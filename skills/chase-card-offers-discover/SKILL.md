---
name: chase-card-offers-discover
description: Autonomously log in and check/activate rotating categories on the Discover it Cash Back card (••••8369) via Chrome automation. Retrieves credentials from 1Password, handles login, navigates via clicks only, activates quarterly categories, and checks cap progress.
owning_agent: chase
model: haiku
trigger_keywords: [discover offers, discover card]
trigger_agents: [chase]
---

> **PORTAL MAPPED TO CAPITAL ONE (2026-10-17):** Discover is serviced by Capital One after the acquisition. The card's portal is `myaccounts.capitalone.com`; sign-in is at `verified.capitalone.com/auth/signin`. Credentials live in 1Password item "Capital One" (fields `txtUserID`, `txtPassword`). The login, rewards, and rotating-category navigation below was verified live on 2026-10-17. The card-linked OFFERS flow on Capital One has NOT been observed: every offers step below is marked UNVERIFIED. See err-20261016T210131-BI38IK.


# Discover Offers: Rotating Categories & Offers

**Card:** Discover it Cash Back ••••8369

**Portal:** `myaccounts.capitalone.com` (sign-in at `verified.capitalone.com/auth/signin`)

---

## Navigation Rules

**Rule:** Navigate by clicking links and buttons only. Do not use `open_url` for any navigation. No new tabs.

---

## Step 0: Login via 1Password

### 0a: Retrieve credentials

```bash
cat > /tmp/op-discover-login.sh << 'SCRIPT'
#!/usr/bin/env bash
set +x
set -euo pipefail
USER=$(/opt/homebrew/bin/op item get "Capital One" --account my.1password.com --fields "label=txtUserID" 2>/dev/null)
PASS=$(/opt/homebrew/bin/op item get "Capital One" --account my.1password.com --fields "label=txtPassword" 2>/dev/null)
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

### 0b: Navigate to the Capital One sign-in page and sign in

Sign-in URL: `https://verified.capitalone.com/auth/signin`.

Check current URL:

```javascript
document.title + ' | ' + window.location.href
```

If already authenticated (URL contains `myaccounts.capitalone.com/accountSummary` and the account summary is visible), skip to the Primary Job section.

If not authenticated, navigate to the sign-in URL and fill the credentials. **UNVERIFIED:** the exact Capital One input selectors have not been confirmed. Probe for the fields, then fill (construct the JS string in bash with the actual values from the temp files, never log values):

```javascript
// UNVERIFIED selectors: confirm against the live Capital One sign-in page before trusting
var userField = document.querySelector('input[name="username"], input[type="text"], #username, #userid-content, [name="userID"]');
if (userField) {
  userField.value = 'INJECT_USER';
  userField.dispatchEvent(new Event('input', {bubbles: true}));
  userField.dispatchEvent(new Event('change', {bubbles: true}));
}
'filled username'
```

```javascript
// UNVERIFIED selectors: confirm against the live Capital One sign-in page before trusting
var passField = document.querySelector('input[type="password"], #password-content, [name="password"]');
if (passField) {
  passField.value = 'INJECT_PASS';
  passField.dispatchEvent(new Event('input', {bubbles: true}));
  passField.dispatchEvent(new Event('change', {bubbles: true}));
}
'filled password'
```

Click sign in:

```javascript
var btns = document.querySelectorAll('button, input[type="submit"]');
for (var i = 0; i < btns.length; i++) {
  var txt = (btns[i].textContent || btns[i].value || '').trim().toLowerCase();
  if (txt.indexOf('sign in') > -1 || txt.indexOf('log in') > -1 || txt.indexOf('submit') > -1) {
    btns[i].click(); break;
  }
}
'submitted login'
```

### 0c: Verify authentication

Wait 4 seconds, then confirm:

```javascript
document.title + ' | ' + window.location.href
// Expected: URL contains myaccounts.capitalone.com/accountSummary
```

### 0d: Clean up

```bash
rm -f /tmp/.discover_user /tmp/.discover_pass
```

Once on `/accountSummary`, proceed to the Primary Job section below.

---

## Primary Job: Quarterly Category Activation

Discover's main offer is the **5% rotating category** on up to $1,500/quarter in spend ($75 max earned). This is the first thing to check every month.

### Step 1: Reach the rewards page and check current-quarter activation

From `/accountSummary`, find the button whose text is exactly `View rewards`:

```javascript
var btns = document.querySelectorAll('button, [role="button"]');
for (var i = 0; i < btns.length; i++) {
  if ((btns[i].textContent || '').trim() === 'View rewards') {
    ['mousedown','mouseup','click'].forEach(function(t){
      btns[i].dispatchEvent(new MouseEvent(t, {bubbles: true, cancelable: true, view: window}));
    });
    break;
  }
}
'clicked View rewards'
```

Note: `View rewards` is a BUTTON element, not a link. The surrounding "Explore rewards and benefits" container is a DIV with no href. A plain `.click()` may not fire the handler, so dispatch mousedown/mouseup/click with `bubbles:true` as above.

This navigates to `/Card/<opaque-token>/rewards`. The token is opaque and per-session, so always navigate by clicking, never by constructing the URL.

Read the activation status:

```javascript
document.title + ' | ' + window.location.href
var body = document.body.innerText;
var idx = body.indexOf('5%');
body.substring(idx - 50, idx + 300)
```

**If a quarter's category is not activated:** activate immediately. Look for the activation control (button text typically contains "Activate"):

```javascript
var btns = document.querySelectorAll('button, a');
for (var i = 0; i < btns.length; i++) {
  var txt = (btns[i].textContent || btns[i].innerText || '').trim();
  if (txt === 'Activate Now' || txt.indexOf('Activate') > -1) {
    btns[i].click(); break;
  }
}
```

**This is a CRITICAL escalation item.** If a quarter's category is not activated, David is losing 4% on all qualifying spend (5% vs 1% base). Flag immediately.

---

## Quarterly Categories Reference

| Quarter | 2026 Categories | Status (as of 2026-10-17) | Earned |
|---------|-----------------|---------------------------|--------|
| Q1 (Jan-Mar) | Grocery Stores, Wholesale Clubs, Select Streaming | Activated (complete) | $75.00 of $75 (maxed) + $63.05 other |
| Q2 (Apr-Jun) | Restaurants, Home Improvement Stores | Activated (complete) | $3.79 of $75 + $23.97 other |
| Q3 (Jul-Sep) | Gas Stations, Transportation, Drug Stores | Activated (complete) | $75.01 of $75 (maxed) + $87.76 other |
| Q4 (Oct-Dec) | Restaurants, Entertainment, Utilities | Activated (current) | $15.32 of $75 + $0.00 other |

Cap: $1,500/quarter in spend, $75 max earned. Discover announces the next quarter's categories roughly a month before.

**Current quarter status:** tracked live in `systems/credit-cards/benefits-tracker.json` (check there rather than hardcoding dates here).

**Strategy:** In Q4 2026, use Discover for restaurants/dining, entertainment, and utilities up to the cap. Restaurants at 5% beats Chase Sapphire (2x UR). After the cap, switch to Chase Sapphire for dining. Do NOT route transportation to Discover this quarter (transportation was Q3, not Q4).

---

## Step 2: Check Cap Progress

On the rewards page, read the per-quarter earned amount:

```javascript
var body = document.body.innerText;
// The 5% cap is $1,500 in spend / $75 max earned per quarter
var idx = body.indexOf('75');
body.substring(idx - 100, idx + 200)
```

**Flag when within $300 of the $1,500 spend cap** (roughly $15 of the $75 max earned remaining), so David needs to switch spend routing to the next-best card.

---

## Step 3: Check for Additional Discover Offers (UNVERIFIED)

> **UNVERIFIED:** The Capital One card-linked offers page has NOT been observed. The Discover Deals section described for the old discover.com site does not map to Capital One. Do not attempt to navigate or enroll offers until this flow is documented.

```javascript
// UNVERIFIED: no confirmed Capital One offers entry point.
// TODO: map the offers path on myaccounts.capitalone.com before using this step.
'offers path not mapped'
```

---

## Step 4: Filter Against YNAB Spend

Pull Discover YNAB transactions:

> **YNAB access:** use the YNAB MCP connector (`get_accounts`, `get_transactions_by_account`), not curl. The old inline-curl path read a token from a stale home-relative config path, which does not exist; the token lives in the repo's `config/.env`.

Discover is used primarily for the 5% rotating category; transaction volume on this card is lower than the others. Cross-reference any Discover offers against this output.

---

## Step 5: Add Offers (UNVERIFIED)

> **UNVERIFIED:** Enrollment on the Capital One offers page has NOT been observed. The tile/Add-button selectors below are carried over from the old discover.com site and are NOT confirmed against Capital One. Do not run this step until the offers flow is mapped.

```javascript
// UNVERIFIED selectors (old discover.com): do not trust against Capital One
var tiles = document.querySelectorAll('[class*="offer"], [class*="deal"]');
for (var i = 0; i < tiles.length; i++) {
  if ((tiles[i].innerText || '').indexOf('MERCHANT_NAME') > -1) {
    tiles[i].click(); break;
  }
}

var btns = document.querySelectorAll('button, a');
for (var i = 0; i < btns.length; i++) {
  var txt = (btns[i].textContent || btns[i].innerText || '').trim();
  if (txt === 'Add Offer' || txt === 'Activate' || txt === 'Get Offer') {
    btns[i].click(); break;
  }
}
```

The rotating category remains the primary value driver; any card-linked offers are secondary.

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
| Quarterly category activated? | Monthly | **ACTIVATE IMMEDIATELY: escalate to Chief** |
| Cap progress ($1,500/quarter spend, $75 max earned) | Monthly | Flag when within $300, adjust routing |
| Next quarter category announced? | Monthly from ~day 15 | Note in tracker, update routing strategy |
| Rewards cash balance | Monthly | Note available balance in tracker |
| Replacement card activated? | One-time (notice seen 2026-10-17) | Activate the replacement card when it arrives |

---

## Update After Walkthrough

Update `systems/credit-cards/benefits-tracker.json` → `discover-it`:
- `last_reviewed` → today
- `rotating_categories.q[N]_2026.confirmed` → today (if activated)
- `cashback_available` → current rewards cash balance from portal
- `current_balance` → outstanding balance
- Note next quarter's category if announced
