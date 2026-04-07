---
name: chase-card-offers-amex
description: Read and add offers on American Express cards (Platinum ••••21001 and Blue Cash Preferred ••••73008) via Chrome automation. Covers the full flow from landing on the offers page to adding individual offers.
agent: chase
---

# Amex Offers — Read & Add

**Portal:** `https://global.americanexpress.com/offers/eligible`

**Cards:** Platinum ••••21001 | Blue Cash Preferred ••••73008

**Requires David logged in** to americanexpress.com before this skill runs.

---

## Navigation Rules

**Rule:** Once authenticated, navigate exclusively by clicking links and buttons via `execute_javascript`. Do NOT use `open_url` or `window.location.href` for in-portal navigation — this breaks React SPA routing and triggers redirects. `open_url` is only allowed for the initial jump to `global.americanexpress.com` if not already there.

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
YNAB_TOKEN=$(grep YNAB_API_TOKEN /Users/davidohara/develop/jarvis/config/.env | cut -d= -f2)
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
