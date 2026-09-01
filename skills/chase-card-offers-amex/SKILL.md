---
name: chase-card-offers-amex
description: Autonomously log in and add offers on American Express cards (Platinum ••••21001 and Blue Cash Preferred ••••73008) via Chrome automation. Retrieves credentials from 1Password, handles login, navigates to the offers page via clicks only, and adds YNAB-validated offers.
owning_agent: chase
model: haiku
trigger_keywords: [amex offers, american express, amex deals]
trigger_agents: [chase]
---

# Amex Offers — Read & Add

**Portal:** `https://global.americanexpress.com/offers/eligible`

**Cards:** Platinum ••••21001 | Blue Cash Preferred ••••73008

---

## Navigation Rules

**Rule:** Navigate exclusively by clicking links and buttons via `execute_javascript`. Do NOT use `open_url` or `window.location.href` for any navigation — this breaks React SPA routing and triggers redirects or logouts. The only exception is the very first tab load to get onto americanexpress.com (Step 0 below).

**Do not open new tabs.** All navigation happens within the existing active tab.

---

## Step 0 — Login via 1Password

Run this before doing anything in the browser. Uses Desktop Commander to call `op` on the host Mac (no tmux required when tmux is unavailable — Desktop Commander provides an equivalent isolated shell).

### 0a — Retrieve credentials

```bash
cat > /tmp/op-amex-login.sh << 'SCRIPT'
#!/usr/bin/env bash
set +x
set -euo pipefail
USER=$(/opt/homebrew/bin/op item get "American Express" --account my.1password.com --fields label=UserID 2>/dev/null)
PASS=$(/opt/homebrew/bin/op item get "American Express" --account my.1password.com --fields label=Password 2>/dev/null)
echo "USER_LEN:${#USER}"
echo "PASS_LEN:${#PASS}"
# Write to temp files readable by the browser step — never log values
echo "$USER" > /tmp/.amex_user
echo "$PASS" > /tmp/.amex_pass
chmod 600 /tmp/.amex_user /tmp/.amex_pass
SCRIPT
chmod 700 /tmp/op-amex-login.sh
bash /tmp/op-amex-login.sh; rm -f /tmp/op-amex-login.sh
```

Verify output shows `USER_LEN` and `PASS_LEN` both > 0 before proceeding.

### 0b — Navigate to login page and sign in

Check current tab URL first:

```javascript
document.title + ' | ' + window.location.href
```

If already on `global.americanexpress.com` and authenticated (no login form visible), skip to Step 1.

If not authenticated, find and click the Log In link:

```javascript
var links = document.querySelectorAll('a');
for (var i = 0; i < links.length; i++) {
  var txt = (links[i].textContent || '').trim();
  var href = links[i].href || '';
  if (txt === 'Log In' || href.indexOf('account/login') > -1) {
    links[i].click(); break;
  }
}
'navigated to login'
```

Wait for the login page to load, then fill credentials using values from the temp files:

```bash
# Read credentials from temp files (shape-check only, never print)
USER=$(cat /tmp/.amex_user)
PASS=$(cat /tmp/.amex_pass)
echo "USER_LEN:${#USER} PASS_LEN:${#PASS}"
```

Inject into the login form via JavaScript (read the values from temp files in the same Desktop Commander process, then pass into the browser via execute_javascript — do not log values):

```javascript
// Fill username field
var userField = document.querySelector('#UserID, [name="UserID"], [name="userID"], input[type="text"]');
if (userField) {
  userField.value = 'INJECT_USER';
  userField.dispatchEvent(new Event('input', {bubbles: true}));
  userField.dispatchEvent(new Event('change', {bubbles: true}));
}
'filled username'
```

```javascript
// Fill password field
var passField = document.querySelector('#Password, [name="Password"], [name="password"], input[type="password"]');
if (passField) {
  passField.value = 'INJECT_PASS';
  passField.dispatchEvent(new Event('input', {bubbles: true}));
  passField.dispatchEvent(new Event('change', {bubbles: true}));
}
'filled password'
```

**Important:** Replace `INJECT_USER` and `INJECT_PASS` with the actual values read from `/tmp/.amex_user` and `/tmp/.amex_pass` in the same Desktop Commander shell step — construct the JS string in bash before passing to `execute_javascript`. Never log or print the values.

Click the submit button:

```javascript
var btns = document.querySelectorAll('button, input[type="submit"]');
for (var i = 0; i < btns.length; i++) {
  var txt = (btns[i].textContent || btns[i].value || '').trim().toLowerCase();
  if (txt === 'log in' || txt === 'sign in' || txt === 'submit') {
    btns[i].click(); break;
  }
}
'submitted login'
```

### 0c — Verify authentication

Wait 3-4 seconds, then confirm:

```javascript
document.title + ' | ' + window.location.href
// Expected: title contains "Overview" or "Dashboard" and URL is global.americanexpress.com
```

If still on login page, check for error message:

```javascript
var body = document.body.innerText;
var errIdx = body.indexOf('incorrect') > -1 || body.indexOf('Invalid') > -1 || body.indexOf('error') > -1;
errIdx ? 'Login error detected — check credentials' : 'No error visible'
```

### 0d — Clean up temp files

```bash
rm -f /tmp/.amex_user /tmp/.amex_pass
```

Once authenticated and on `global.americanexpress.com`, proceed to Step 1.

---

## Step 1 — Confirm You're on the Offers Page

```javascript
document.title + ' | ' + window.location.href
```

Expected: `"American Express - Offers & Benefits | https://global.americanexpress.com/offers/eligible"`

If not there, navigate via click:
```javascript
// From the Amex dashboard, click the Offers & Benefits nav item
var links = document.querySelectorAll('a');
for (var i = 0; i < links.length; i++) {
  if ((links[i].textContent || '').trim().indexOf('Offers') > -1) {
    links[i].click(); break;
  }
}
```

---

## Step 2 — Check Which Card Is Active

```javascript
var switcher = document.querySelector('[class*="simple-switcher-combobox-input"]');
switcher ? switcher.innerText.trim() : 'switcher not found'
```

Returns e.g. `"Blue Cash Preferred®\n••••73008"` or `"Platinum Card®\n••••21001"`

---

## Step 3 — Switch Cards (if needed)

```javascript
// 1. Open the dropdown
var switcher = document.querySelector('[class*="simple-switcher-combobox-input"]');
switcher.click();

// 2. Read available options
var opts = document.querySelectorAll('[class*="simple-switcher"] li, [role="option"]');
for (var i = 0; i < opts.length; i++) {
  console.log(i + ': ' + opts[i].innerText.trim().substring(0, 60));
}

// 3. Click the target card option (adjust index as needed)
opts[3].click(); // 2 = BCP, 3 = Platinum (confirm by reading innerText first)
```

Confirm switch:
```javascript
document.querySelector('[class*="simple-switcher-combobox-input"]').innerText.trim()
```

---

## Step 4 — Read All Available Offers

```javascript
var rows = document.querySelectorAll('[class*="_listViewRow_"]');
var offers = [];
for (var i = 0; i < rows.length; i++) {
  var text = rows[i].innerText.trim().replace(/\n/g, ' | ').substring(0, 150);
  if (text) offers.push(i + ': ' + text);
}
offers.join('\n')
```

This returns every offer with its row index. Note the index — you'll use it to click specific tiles.

**To check "New" offers only:** Look for rows containing the text `NEW` in the output.

**To check "Added to Card" status:** Rows containing `Added to Card` are already enrolled — skip them.

---

## Step 5 — Filter Against YNAB Spend

Before adding any offer, run the YNAB card pull for the card being reviewed:

```bash
# BCP (account: b4b7a7c8)
YNAB_TOKEN=$(grep YNAB_API_TOKEN $HOME/develop/jarvis/config/.env | cut -d= -f2)
curl -s "https://api.youneedabudget.com/v1/budgets/5185d50a-d25e-47f8-b9d0-283ef6a89d2b/accounts/b4b7a7c8-32f5-4503-baf5-207d87050813/transactions?since_date=$(date -v-90d +%Y-%m-%d)" \
  -H "Authorization: Bearer $YNAB_TOKEN" | \
  python3 -c "import sys,json; txns=json.load(sys.stdin)['data']['transactions']; p={}; [p.update({t['payee_name']: p.get(t['payee_name'],0)+abs(t['amount'])/1000}) for t in txns if t.get('payee_name')]; [print(f'{v:.0f} | {k}') for k,v in sorted(p.items(),key=lambda x:-x[1])[:30]]"

# Platinum (account: 69de6bb6) — use same pattern with account ID 69de6bb6-...
# Note: Platinum has historically returned no transactions. If empty, skip YNAB step
# and rely on known spend patterns (travel, hotels, dining).
```

**Only add offers where the vendor appears in YNAB spend history**, or where spend is highly probable based on known patterns (e.g., hotels on Platinum).

---

## Step 6 — Open an Offer's Detail Panel

Find the row index from Step 4, then:

```javascript
var rows = document.querySelectorAll('[class*="_listViewRow_"]');
var row = rows[INDEX]; // replace INDEX with the row number
var btns = row.querySelectorAll('button');
for (var j = 0; j < btns.length; j++) {
  if (btns[j].innerText.trim() === 'View Details') {
    btns[j].click(); break;
  }
}
```

Confirm the detail panel opened by reading around the merchant name:
```javascript
var body = document.body.innerText;
var idx = body.indexOf('MERCHANT_NAME'); // replace with actual merchant
body.substring(idx, idx + 200)
```

Expected: panel shows merchant name, cashback amount, expiry, and **"Add to Card"** button.

**Important:** If it shows `"Added to card (-XXXXX)"` instead of `"Add to Card"`, this offer is already enrolled on that card — skip it.

---

## Step 7 — Add the Offer

```javascript
var btns = document.querySelectorAll('button');
for (var i = 0; i < btns.length; i++) {
  if (btns[i].innerText && btns[i].innerText.trim() === 'Add to Card') {
    btns[i].click(); break;
  }
}
```

Confirm enrollment:
```javascript
var body = document.body.innerText;
var idx = body.indexOf('MERCHANT_NAME');
body.substring(idx, idx + 200)
// Should now read: "Added to card (-73008)" or "Added to card (-21001)"
```

---

## Step 8 — Close Panel and Continue

```javascript
var btns = document.querySelectorAll('button');
for (var i = 0; i < btns.length; i++) {
  if (btns[i].innerText && btns[i].innerText.trim() === 'Close') {
    btns[i].click(); break;
  }
}
```

Repeat Steps 6–8 for each target offer. Then switch cards (Step 3) and repeat for the other card.

---

## Single-Enrollment Offers

Some offers can only be added to **one card** — once added to BCP, the Platinum panel will show `"Added to card (-73008)"` with no "Add to Card" button. This is by design — pick the card you're more likely to trigger the offer on.

**BCP is preferred** for single-enrollment offers (grocery, streaming, everyday spend).
**Platinum is preferred** for hotel, travel, and luxury merchant offers.

---

## YNAB Account IDs (Amex)

| Card | YNAB Account ID |
|------|----------------|
| Blue Cash Preferred ••••73008 | `b4b7a7c8-32f5-4503-baf5-207d87050813` |
| Platinum ••••21001 | `69de6bb6-...` (historically returns no transactions — rely on spend patterns) |

**Budget ID:** `5185d50a-d25e-47f8-b9d0-283ef6a89d2b`
**Token location:** `config/.env` → `YNAB_API_TOKEN`

---

## Update After Walkthrough

Update `systems/credit-cards/benefits-tracker.json`:
- `card_linked_offers.amex-bcp.last_reviewed` → today
- `card_linked_offers.amex-plat.last_reviewed` → today
- Add newly enrolled offers to `newly_added_[DATE]` arrays
- Add urgent expirations to `upcoming_deadlines`

## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/chase-card-offers-amex-latest.json
```

Content:
```json
{
  "skill": "chase-card-offers-amex",
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
python3 systems/eval-harness/grade_skill_run.py --skill chase-card-offers-amex
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/chase-card-offers-amex.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

