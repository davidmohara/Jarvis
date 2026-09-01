# Grammarly Polish

**ID:** `grammarly-polish`
**Owning agent:** harper
**Callable by:** Any agent (master, harper, chase, quinn, shep, chief, knox, rigby, sterling, galen)
**Model:** sonnet
**Type:** On-demand tool skill — NOT a default pipeline step

---

## Purpose

Final content polish via Grammarly in Chrome. Call this explicitly when David wants a Grammarly pass on high-stakes content — Forbes articles, board deck copy, podcast scripts, emails, LinkedIn posts, and similar. Do not auto-invoke this skill. Only run it when David explicitly asks or a trigger keyword is detected.

**Trigger keywords:** "grammarly", "polish this", "final polish", "run grammarly", "grammarly check", "proof this"

---

## Pre-flight

- Content to polish must be passed in-context by the calling agent.
- David is already logged into Grammarly in Chrome. No auth step needed.
- This skill requires Chrome to be running and accessible via `mcp__Control_Chrome__*` tools.

---

## Execution Steps

### Step 1 — Open Grammarly editor

```
mcp__Control_Chrome__open_url
url: https://app.grammarly.com/docs/new
```

Wait ~3 seconds for the editor to load.

### Step 2 — Confirm editor is ready

```
mcp__Control_Chrome__get_page_content
```

Look for the Grammarly editor text area or the phrase "Start writing" / "Untitled document". If the page is not ready, wait 3 more seconds and check again.

**Login/marketing page detection:** If the page instead shows a login form, contains "Log in" or "Sign in" text, or the URL contains `/signin` or is the Grammarly marketing homepage (i.e., does NOT contain `/docs`), do not go to the fallback — proceed to **Step 2a** to auto-login via Google OAuth, then return here.

If not ready after 10 seconds total and no login page is detected, go to the fallback procedure (Chrome/Grammarly did not load).

### Step 2a — Auto-Login (Google → 1Password fallback)

Run this when Step 2 detects a login page instead of the editor.

**2a-i: Navigate to Grammarly signin**

```
mcp__Control_Chrome__open_url
url: https://www.grammarly.com/signin
```

Wait 3 seconds. Get page content.

**2a-ii: Try Google OAuth (non-interactive only)**

```
mcp__Control_Chrome__execute_javascript
script: |
  const btn = Array.from(document.querySelectorAll('button, a, [role="button"]'))
    .find(el => /google/i.test(el.textContent) || /google/i.test(el.getAttribute('aria-label') || ''));
  if (btn) { btn.click(); true; } else { false; }
```

Wait 4 seconds. Get page content and check URL:
- If URL contains `/docs` or Grammarly editor is visible → success, return to Step 2.
- If URL is `accounts.google.com` and shows an account chooser (no password/passkey prompt) → click the daveohara@gmail.com tile:
  ```javascript
  const tiles = document.querySelectorAll('[data-email], [data-identifier], .JDAKTe, .XY7kcd');
  const target = Array.from(tiles).find(el =>
    el.textContent.includes('daveohara@gmail.com') ||
    (el.getAttribute('data-email') || '').includes('daveohara')
  );
  if (target) { target.click(); true; } else { false; }
  ```
  Wait 5 seconds. If URL contains `/docs` → success, return to Step 2.
- If Google is asking for a passkey, password, or any interactive prompt → do NOT attempt. Proceed immediately to 2a-iii (1Password fallback).
- If no Google button was found on the Grammarly page → proceed to 2a-iii.

**2a-iii: 1Password fallback — retrieve credentials**

Write and execute a temp script via Desktop Commander:

```bash
#!/usr/bin/env bash
set +x
set -euo pipefail
EMAIL=$(/opt/homebrew/bin/op item get "Grammarly" --account my.1password.com --fields label=username 2>/dev/null)
PASS=$(/opt/homebrew/bin/op item get "Grammarly" --account my.1password.com --fields label=password 2>/dev/null)
echo "EMAIL_LEN:${#EMAIL}"
echo "PASS_LEN:${#PASS}"
echo "$EMAIL" > /tmp/.grammarly_email
echo "$PASS" > /tmp/.grammarly_pass
chmod 600 /tmp/.grammarly_email /tmp/.grammarly_pass
```

Use `mcp__Desktop_Commander__write_file` to write to `/tmp/grammarly_login.sh`, then `mcp__Desktop_Commander__execute_command` to run `bash /tmp/grammarly_login.sh && rm -f /tmp/grammarly_login.sh`.

Check output: both EMAIL_LEN and PASS_LEN must be > 0. If either is 0 or op fails, go to fallback procedure with reason "1Password credential retrieval failed — ensure a 'Grammarly' item exists in 1Password Personal vault with username and password fields."

**2a-iv: Navigate to Grammarly email login and inject credentials**

```
mcp__Control_Chrome__open_url
url: https://www.grammarly.com/signin
```

Wait 3 seconds. Read temp files via Desktop Commander, then inject:

```javascript
// Look for email/password fields — Grammarly may show email first, then password on next screen
const emailField = document.querySelector('input[type="email"]')
  || document.querySelector('input[name="email"]')
  || document.querySelector('input[placeholder*="email" i]');
const passField = document.querySelector('input[type="password"]');

if (emailField) {
  emailField.focus();
  emailField.value = EMAIL_VALUE;
  emailField.dispatchEvent(new Event('input', { bubbles: true }));
  emailField.dispatchEvent(new Event('change', { bubbles: true }));
}
if (passField) {
  passField.focus();
  passField.value = PASS_VALUE;
  passField.dispatchEvent(new Event('input', { bubbles: true }));
  passField.dispatchEvent(new Event('change', { bubbles: true }));
}
```

If only the email field appears (no password field yet), submit the email first:
```javascript
const continueBtn = document.querySelector('button[type="submit"]')
  || Array.from(document.querySelectorAll('button')).find(b => /continue|next/i.test(b.textContent));
if (continueBtn) continueBtn.click();
```

Wait 3 seconds, then fill the password field and submit.

**2a-v: Clean up and verify**

```bash
rm -f /tmp/.grammarly_email /tmp/.grammarly_pass
```

Wait 5 seconds. Get page content. If URL contains `/docs` or editor is visible → return to Step 2. Otherwise → fallback procedure with reason "1Password login submitted but Grammarly editor did not load."

### Step 3 — Paste content into the editor

Use JavaScript to insert the content into the Grammarly editor:

```
mcp__Control_Chrome__execute_javascript
script: |
  const editor = document.querySelector('[contenteditable="true"]')
    || document.querySelector('.ql-editor')
    || document.querySelector('[data-testid="editor-content"]');
  if (editor) {
    editor.focus();
    document.execCommand('selectAll');
    document.execCommand('insertText', false, CONTENT_PLACEHOLDER);
  }
```

Replace `CONTENT_PLACEHOLDER` with the actual content string, properly escaped. If `execute_javascript` cannot locate the editor, attempt a keyboard paste via `mcp__Control_Chrome__execute_javascript` using `navigator.clipboard.writeText()` followed by a Ctrl+V simulation.

### Step 4 — Wait for Grammarly analysis

Poll `mcp__Control_Chrome__get_page_content` every 3 seconds, up to 5 polls (15 seconds total). Look for:
- A numeric score (e.g., "Score: 87" or a score badge)
- Suggestion counts or highlighted underlines in the DOM
- The word "suggestions" appearing in the page content

If suggestions appear before timeout, proceed to Step 5. If timeout is reached with no suggestions, note "No suggestions detected" and proceed anyway — the corrected text may still be clean.


### Step 5 — Extract Grammarly results

Use `mcp__Control_Chrome__get_page_content` to capture the full page state. Extract:

1. **Overall score** — numeric score if visible (0–100)
2. **Flagged issues** — each issue with: flagged text, issue type (spelling / grammar / clarity / engagement / delivery), and Grammarly's suggested correction
3. **Tone detection** — any tone label Grammarly surfaces (e.g., "Confident", "Formal", "Friendly")
4. **Critical alerts** — anything flagged as a hard error (spelling, punctuation, sentence fragment)

Use `mcp__Control_Chrome__execute_javascript` if needed to extract suggestion panel data:

```
mcp__Control_Chrome__execute_javascript
script: |
  const cards = document.querySelectorAll('[data-name="suggestion-card"]');
  return Array.from(cards).map(c => c.innerText);
```

Adapt the selector to whatever DOM structure Grammarly is using at time of execution — the structure may vary. Capture what is readable from `get_page_content` if JavaScript extraction fails.

### Step 6 — Build corrected version

Apply accepted corrections to produce a corrected version of the content. Default behavior:
- Accept all **spelling** and **grammar** corrections automatically.
- Accept **clarity** suggestions that don't change meaning or voice.
- Flag (but do not auto-apply) **style / tone / engagement** suggestions — present them to David for review.

### Step 7 — Return polish report

Return the following structured report to the calling agent:

```
## Grammarly Polish Report

**Score:** [X/100 or "Not detected"]
**Tone:** [detected tone or "Not detected"]

### Corrections Applied
| # | Original | Corrected | Type |
|---|----------|-----------|------|
| 1 | ...      | ...       | ...  |

### Suggestions for David's Review (not auto-applied)
- [Style/tone suggestions listed here]

### Critical Alerts
- [Any hard errors listed here, or "None"]

---

### Corrected Content

[Full corrected text here]
```

---

## Fallback Procedure

If Grammarly fails to load or the login flow cannot complete, return the following to the calling agent. Use the appropriate reason block based on the failure mode detected.

**Failure mode A — Google OAuth attempted but required interactive credentials, and 1Password fallback also failed:**

```
Grammarly Polish — UNAVAILABLE

Grammarly redirected to the login/marketing page. Google OAuth was attempted but required an interactive passkey or password prompt (non-interactive only policy). The 1Password fallback was also attempted and failed.

Reason: Google OAuth attempted but required interactive passkey/password — 1Password fallback also failed: [reason]

Original content returned unchanged.

### Original Content (unmodified)

[original content here]
```

**Failure mode B — Google OAuth skipped, 1Password fallback failed:**

```
Grammarly Polish — UNAVAILABLE

Google OAuth was skipped (no Google button found or non-interactive path unavailable). The 1Password fallback was attempted and failed.

Reason: Google OAuth skipped, 1Password fallback failed: [reason]

Original content returned unchanged.

### Original Content (unmodified)

[original content here]
```

**Failure mode C — Chrome or Grammarly did not load at all:**

```
Grammarly Polish — UNAVAILABLE

Chrome or Grammarly did not load successfully. Original content returned unchanged.

Reason: Chrome or Grammarly did not load at all

### Original Content (unmodified)

[original content here]
```

Do not retry more than once. Surface the failure cleanly and let the calling agent decide how to proceed.

---

## Calling Convention

Calling agents pass content in-context using this pattern:

```
Run the grammarly-polish skill on the following content:

---
[CONTENT TO POLISH]
---
```

The skill returns the polish report inline. No files are written by this skill — output is in-context only.

---

## Constraints

- Never auto-invoke. Explicit call only.
- Do not run on content that contains API keys, credentials, PII, or client confidential data — flag and abort if detected.
- Do not store or log the content externally.
- One document per invocation. If multiple pieces of content are provided, polish them sequentially and return separate reports.


<!-- system:start -->
## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/grammarly-polish-latest.json
```

Content:
```json
{
  "skill": "grammarly-polish",
  "agent": "grammarly",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output, `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action, immediately followed by the grading step below.
<!-- system:end -->

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill grammarly-polish
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/grammarly-polish.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->
