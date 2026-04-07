---
name: chase-card-offers-chase
description: Read and add offers on the Chase Sapphire Preferred card via Chrome automation. Covers the Chase "Offers for You" portal — navigation, reading the offer list, adding via the + button, and confirming.
agent: chase
---

# Chase Sapphire Offers — Read & Add

**Card:** Chase Sapphire Preferred

**Portal:** `https://account.chase.com/consumer/activity/offers`

**Requires David logged in** to chase.com before this skill runs.

---

## Navigation Rules

**Rule:** Once authenticated, navigate exclusively by clicking links and buttons. Do NOT use `open_url` or `window.location.href` for in-portal navigation — use link clicks only. `open_url` is only for the initial jump to `chase.com` if not already there.

---

## Step 1 — Navigate to Offers

From the Chase dashboard:

```javascript
// Click "More" or "Offers" in the account nav
var links = document.querySelectorAll('a');
for (var i = 0; i < links.length; i++) {
  var txt = (links[i].textContent || '').trim();
  var href = links[i].href || '';
  if (txt === 'Offers' || href.indexOf('offers') > -1) {
    links[i].click(); break;
  }
}
```

Or navigate directly to the offers page if already on a Chase domain page:
```javascript
// Only use this if already on chase.com — do NOT use open_url
window.location.href = 'https://account.chase.com/consumer/activity/offers';
```

Confirm:
```javascript
document.title + ' | ' + window.location.href
// Expected: something containing "Offers" in title, URL contains "offers"
```

---

## Step 2 — Read All Available Offers

Chase renders offers as tiles. Read them all:

```javascript
var tiles = document.querySelectorAll('[class*="offer"], [data-testid*="offer"]');
var offers = [];
for (var i = 0; i < tiles.length; i++) {
  var text = (tiles[i].innerText || '').trim().replace(/\n/g, ' | ').substring(0, 150);
  if (text && text.length > 10) offers.push(i + ': ' + text);
}
offers.slice(0, 50).join('\n')
```

If that doesn't work (Chase updates their DOM regularly), use:
```javascript
// Broader sweep — find any element with offer-like content
var body = document.body.innerText;
body.substring(0, 3000) // scan the top of the page for offer tiles
```

**Note:** Chase currently shows ~117 offers. Scroll the page to load all offers before reading:
```javascript
window.scrollTo(0, document.body.scrollHeight);
// Wait ~2 seconds, then re-read
```

---

## Step 3 — Filter Against YNAB Spend

Pull Chase Sapphire YNAB transactions:

```bash
YNAB_TOKEN=$(grep YNAB_API_TOKEN /Users/davidohara/develop/jarvis/config/.env | cut -d= -f2)
curl -s "https://api.youneedabudget.com/v1/budgets/5185d50a-d25e-47f8-b9d0-283ef6a89d2b/accounts/15694d56-fe61-4029-a526-b53fee53d1b6/transactions?since_date=$(date -v-90d +%Y-%m-%d)" \
  -H "Authorization: Bearer $YNAB_TOKEN" | \
  python3 -c "import sys,json; txns=json.load(sys.stdin)['data']['transactions']; p={}; [p.update({t['payee_name']: p.get(t['payee_name'],0)+abs(t['amount'])/1000}) for t in txns if t.get('payee_name')]; [print(f'{v:.0f} | {k}') for k,v in sorted(p.items(),key=lambda x:-x[1])[:30]]"
```

Only add offers for vendors that appear in YNAB spend. Do not add based on guesses.

---

## Step 4 — Add an Offer

**Chase is different from Amex.** There is no "View Details" → "Add to Card" flow. Instead:

> **Click the `+` button in the bottom-right corner of the offer tile.** This simultaneously adds the offer AND navigates you to the offer detail page.

```javascript
// Find the offer tile by merchant name, then click its + button
var allEls = document.querySelectorAll('[class*="offer"], [data-testid*="offer"]');
for (var i = 0; i < allEls.length; i++) {
  if ((allEls[i].innerText || '').indexOf('MERCHANT_NAME') > -1) {
    // Find the + (add) button within this tile
    var addBtns = allEls[i].querySelectorAll('button');
    for (var j = 0; j < addBtns.length; j++) {
      var txt = (addBtns[j].innerText || addBtns[j].getAttribute('aria-label') || '').trim();
      if (txt === '+' || txt.toLowerCase().indexOf('add') > -1) {
        addBtns[j].click();
        break;
      }
    }
    break;
  }
}
```

**CRITICAL — Verify Before Clicking:**
Before clicking add, confirm the modal/tile shows the correct merchant name. A prior session accidentally added Starlink (err-20260404-002) because a featured offer button intercepted the click. Always read the offer context first:

```javascript
// Confirm merchant name before clicking +
var el = // ... your target tile
el.innerText.substring(0, 100) // read it — verify it says what you expect
```

---

## Step 5 — After Adding, Go Back to the List

Clicking `+` navigates to the offer detail page. Go back:

```javascript
history.back();
// Or click the Back button in the Chase UI
var links = document.querySelectorAll('a, button');
for (var i = 0; i < links.length; i++) {
  var txt = (links[i].innerText || links[i].textContent || '').trim();
  if (txt === 'Back' || txt === '← Back') { links[i].click(); break; }
}
```

Repeat Steps 4–5 for each target offer.

---

## Step 6 — Confirm Offers Are Added

After adding, verify by checking if the offer now shows as enrolled/added:

```javascript
// The + button should be replaced with a checkmark or "Added" state
// Check the offer tile area for the merchant
var body = document.body.innerText;
var idx = body.indexOf('MERCHANT_NAME');
body.substring(idx, idx + 150)
```

---

## YNAB Account ID (Chase Sapphire)

| Card | YNAB Account ID |
|------|----------------|
| Chase Sapphire | `15694d56-fe61-4029-a526-b53fee53d1b6` |

**Budget ID:** `5185d50a-d25e-47f8-b9d0-283ef6a89d2b`
**Token location:** `config/.env` → `YNAB_API_TOKEN`

---

## Known Issue — DOM Intercept (err-20260404-002)

The Chase offers page renders a "Featured Offer" section at the top with large buttons. When clicking a tile lower on the page, the featured offer's button can intercept the click if it overlaps the viewport.

**Mitigation:** Scroll to the target tile before clicking, and always verify the merchant name in the DOM before adding.

---

## Update After Walkthrough

Update `systems/credit-cards/benefits-tracker.json`:
- `card_linked_offers.chase-sapphire.last_reviewed` → today
- Add newly enrolled offers to `high_value_offers` with `status: "added"` and `added_date`
- Update `total_offers_available` count
- Add expiring offers to `upcoming_deadlines`
