---
name: chase-card-offers-citi
description: Read and enroll in offers on the Citi AAdvantage Executive card (••••9598) via Chrome automation. Covers the Citi Merchant Offers portal flow — navigation, reading the offer list, enrolling, and confirming.
agent: chase
model: haiku
---

# Citi Offers — Read & Enroll

**Card:** Citi AAdvantage Executive World Elite Mastercard ••••9598

**Portal:** `https://online.citi.com/US/nga/products-offers/merchantoffers`

**Requires David logged in** to online.citi.com before this skill runs.

---

## Navigation Rules

**Rule:** Once authenticated, navigate exclusively by clicking links and buttons. Do NOT use `open_url` or `window.location.href` — Citi's SPA will redirect to a 404. The only exception is the initial jump to `online.citi.com` if not already there.

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
