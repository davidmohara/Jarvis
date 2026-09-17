---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 00: Prior-Booking Cancellation (Override Redirect) — Destructive Action Gate

## MANDATORY EXECUTION RULES

1. **This step is idempotent.** If there is no prior booking (no `booking-id` in
   `state.yaml`), or the prior booking's date/time already equals the new target,
   this step is a logged no-op — record `cancellation: not-required` and proceed
   directly to step-01.
2. **NEVER click a cancel button based on visual position, proximity, or "the one
   next to the right date."** Every cancel click is wrapped in the destructive-action
   gate from SYSTEM.md ("Destructive action gate"): screenshot the page, read the
   target booking's OWN booking ID from the DOM, and verify that ID equals the
   booking intended for cancellation before clicking. This is the exact failure that
   canceled the wrong reservation on 2026-09-04
   (`err-20260904T151500-CANCEL`, critical).
3. **When the ID is ambiguous or does not match, STOP.** Surface to David and ask
   him to cancel manually. Uncertainty is a stop condition, not a best-effort
   condition. Do not automate anything this workflow did not create.
4. **Never cancel a prior booking before its replacement is actually bookable.** If
   the new target date is outside the 8-day booking window, keep the existing
   booking and defer cancellation to the run when the window opens.

---

## EXECUTION PROTOCOL

**Agent:** Sterling
**Input:** `workflows/golf-booking/state.yaml` (`booking-id`, `booking-date`,
`booking-time` from the prior successful run) + `workflows/golf-booking/preview-output.json`
(`override_instructions`, `top_options`)
**Output:** Prior booking either cancelled (DOM-verified) or explicitly
determined not to require cancellation — this is **QUALITY GATE 0**

---

## YOUR TASK

Write `status: in-progress` and `started-at` to this file's frontmatter before
executing.

### 1. Detect whether a re-book is happening

Read `state.yaml` and `preview-output.json`.

Determine the new target date/time the same way step-01 does: from
`override_instructions` if present, otherwise the top-ranked option in
`top_options`.

- **No `booking-id` in state.yaml** (no prior booking, or it was already
  cancelled): no-op. Log `[Gate 0] No prior booking — cancellation not required ✓`.
  Proceed to step-01.
- **Prior booking date/time equals the new target** (same date, same time): no-op.
  Log `[Gate 0] Prior booking [booking-id] matches target — cancellation not
  required ✓`. Proceed to step-01.
- **Prior booking differs from the new target:** a re-book is happening. Continue
  to step 2 below.

### 2. Window check before cancelling

Compute whether the new target date is within 8 days of today (same `date`
arithmetic as Gate 1 — use `date +%Y-%m-%d` at runtime).

- **Target MORE than 8 days out:** do NOT cancel. The replacement cannot be
  booked this run, and cancelling now would leave David with no booking at all.
  Record `pending-cancellation: true`, `pending-cancel-booking-id`, and
  `pending-cancel-date` in this file's outputs and `state.yaml`'s
  `accumulated-context` so the next run (once the window opens) executes the
  cancellation. Log `[Gate 0] Re-book target outside window — cancellation
  deferred, prior booking retained ✓`. Proceed to step-01, which will set
  `status: awaiting-window`.
- **Target within 8 days:** continue to the cancellation protocol.

### 3. Cancellation protocol — QUALITY GATE 0 (HARD, BLOCKING, DESTRUCTIVE-ACTION GATED)

**3a. Navigate to the Bookings page:**

```bash
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
window.location.href = \"https://www.chronogolf.com/dashboard/#/bookings\";
\"navigating-to-bookings\"
"'
```

Wait 3 seconds for the page to load.

**3b. Screenshot the Bookings list** (Peekaboo skill or
`mcp__Control_your_Mac__osascript`). This is required evidence for the
destructive-action gate — no cancel click may happen without it.

**3c. Read each booking's OWN ID from the DOM.** Do not trust visual layout.
Enumerate the booking entries and return each one's booking reference (the
ChronoGolf booking ID, format like `2M0G-8C0F`) together with its displayed
date/time text:

```bash
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var entries = [];
document.querySelectorAll(\"[class*=booking], [class*=reservation], li, tr\").forEach(function(el){
  var t = el.innerText || \"\";
  var m = t.match(/[A-Z0-9]{4}-[A-Z0-9]{4}/);
  if (m && t.length < 400) { entries.push(m[0] + \" :: \" + t.replace(/\\n+/g,\" | \").substring(0,120)); }
});
entries.length ? entries.join(\"\\n\") : \"NO-BOOKING-IDS-FOUND-ON-PAGE\"
"'
```

(Adapt the selector to the live DOM if the first pass returns
`NO-BOOKING-IDS-FOUND-ON-PAGE` — inspect the page structure, then re-run. Never
proceed to a click on the strength of the screenshot alone.)

**3d. Match the ID.** Compare the DOM-read booking IDs against the prior
`booking-id` from `state.yaml`:

- **Exact ID match, exactly one entry, and that entry's displayed date matches
  the stored `booking-date`** → the target is unambiguously identified. Continue
  to 3e.
- **ID not found anywhere on the page** → the prior booking is already cancelled
  (or never landed). Idempotent success: log `[Gate 0] Prior booking [ID] no
  longer present — already cancelled ✓`. Clear `booking-id`/`booking-date`/
  `booking-time` in state, proceed to step-01.
- **Multiple entries carrying the same ID, or the ID matches an entry whose
  displayed date does NOT match the stored `booking-date`** → **STOP. Hard
  failure.** Do not click anything. Send the Slack alert in the Failure Modes
  table below, set `status: aborted` with a resolution note naming the mismatch,
  and surface to David to cancel manually.

**3e. Click cancel scoped to the matched booking's own container.** Locate the
single DOM element whose text contains the matched booking ID, and invoke the
cancel control INSIDE that element — never a cancel button found by page
position:

```bash
osascript -e 'tell application "Google Chrome" to tell active tab of front window to execute javascript "
var target = null;
document.querySelectorAll(\"[class*=booking], [class*=reservation], li, tr\").forEach(function(el){
  var t = el.innerText || \"\";
  if (t.includes(\"[PRIOR_BOOKING_ID]\") && t.match(/[A-Z0-9]{4}-[A-Z0-9]{4}/)[0] === \"[PRIOR_BOOKING_ID]\") { target = el; }
});
if (!target) { \"CANCEL-TARGET-NOT-FOUND-ABORT\"; }
else {
  var btn = target.querySelector(\"[class*=cancel] button, button[class*=cancel], a[class*=cancel], [data-test*=cancel]\");
  btn ? (btn.click(), \"CANCEL-CLICKED-[PRIOR_BOOKING_ID]\") : \"CANCEL-BUTTON-NOT-FOUND-IN-TARGET-ABORT\";
}
"'
```

(Substitute `[PRIOR_BOOKING_ID]` with the matched ID.) If the result is
`CANCEL-TARGET-NOT-FOUND-ABORT` or `CANCEL-BUTTON-NOT-FOUND-IN-TARGET-ABORT`:
**STOP** — treat exactly as a 3d mismatch (Slack alert, `status: aborted`,
surface to David). Handle any confirmation dialog that appears with the same
ID-verification discipline before confirming.

**3f. Verify the cancellation landed.** Wait 3 seconds, re-run the 3c DOM read:

- The prior booking ID no longer appears anywhere on the page → log
  `[Gate 0] PASS — prior booking [ID] ([date] [time]) cancelled, verified absent
  from Bookings page ✓`.
- The prior booking ID still appears → **STOP.** Slack alert, `status: aborted`,
  surface to David. Do not click cancel a second time.

**3g. Reset state.** Only after a verified cancellation (or a verified
already-absent booking): clear `booking-id`, `booking-date`, `booking-time` in
`state.yaml`, and record `cancelled-booking-id` and `cancellation-verified: true`
in this file's outputs and `state.yaml`'s `accumulated-context`. The state is now
clean for step-01 to validate the new target and the workflow to re-book.

After completing, write `status: complete`, `completed-at`, and the populated
`outputs` keys to this file's frontmatter, mirror those outputs into
`state.yaml`'s `accumulated-context`, and set `current-step: step-01`.

---

## SUCCESS METRICS

- A cancel click never happens without a screenshot plus a DOM-read booking ID
  that exactly matches the intended prior booking
- Cancellation is safe to run when no prior booking exists (idempotent no-op)
- A prior booking is never cancelled while its replacement is outside the
  booking window

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Prior booking ID appears multiple times, or its entry's displayed date does not match the stored `booking-date` | **STOP. Hard failure — do not click.** Slack alert: `*⛳ BOOKING CANCELLATION BLOCKED* Override targets [new date/time], but the prior booking [ID] could not be uniquely identified on the Bookings page (ambiguous or mismatched ID). Please cancel [date] [time] manually — I will not click cancel on an uncertain target.` Set `status: aborted` with a resolution note. Surface to David. |
| Cancel target/button not found inside the matched booking's own container | **STOP.** Same alert and abort as an ambiguous ID — never fall back to clicking a cancel button by page position. |
| Prior booking ID still present after cancel click | **STOP.** Slack alert with the 3c DOM dump (first 500 chars). `status: aborted`. Do not click cancel a second time. |
| Re-book target outside 8-day window | Defer: record `pending-cancellation` in accumulated-context, retain the prior booking, proceed to step-01 (`awaiting-window`). |

## NEXT STEP

Read fully and follow: `step-01-read-preview-and-window-precheck.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
