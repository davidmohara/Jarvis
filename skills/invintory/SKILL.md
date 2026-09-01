---
id: invintory
name: Invintory Wine Cellar
owning_agent: sterling
model: haiku
trigger_keywords:
  - invintory
  - cellar
  - wine collection
  - bottles
  - drink window
  - cellar inventory
  - log shipment
  - wine value
  - cellar search
trigger_agents:
  - sterling
  - master
description: >
  Provides Sterling with read/write access to David's Invintory wine cellar via
  the Invintory MCP server (https://api.invintory.com/mcp). Handles OAuth token
  management autonomously — reads access token from config/.env, refreshes
  before expiry, and writes updated tokens back without intervention.
---

<!-- system:start -->
# Invintory Wine Cellar Skill

**Owner:** Sterling. Every Invintory operation goes through this skill.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->

---

## MCP Server

| Field | Value |
|-------|-------|
| **URL** | `https://api.invintory.com/mcp` |
| **Protocol** | JSON-RPC 2.0 over HTTPS |
| **Auth** | OAuth 2.0 Bearer token |
| **Plans** | Paid plans only (Premium / Elite) |

---

## config/.env Keys

The following keys must be present in `config/.env`. Read the file before every call — never hardcode values.

```
INVINTORY_ACCESS_TOKEN=<access token from OAuth flow>
INVINTORY_REFRESH_TOKEN=<refresh token from OAuth flow>
INVINTORY_TOKEN_EXPIRES=<unix timestamp when access token expires>
INVINTORY_CLIENT_ID=<OAuth client id — from Invintory OAuth app registration>
INVINTORY_CLIENT_SECRET=<OAuth client secret — from Invintory OAuth app registration>
INVINTORY_TOKEN_URL=https://api.invintory.com/oauth/token
```

`INVINTORY_TOKEN_EXPIRES` is a Unix timestamp (integer seconds). If missing or 0, treat as expired and refresh immediately.

---

## Initial Setup (one-time)

This is the only step that requires David's involvement. Everything after is autonomous.

1. In Claude.ai → Settings → Connectors → Add custom connector
2. Name: `InVintory`, URL: `https://api.invintory.com/mcp`
3. Click Connect — sign in with Invintory account
4. After successful auth, run the bootstrap script below to capture tokens into `.env`:

```bash
# Run in Desktop Commander (host process, not sandbox)
# Invintory's OAuth app credentials come from app.invintory.com → Settings → Developer
# Paste client_id and client_secret when prompted, then run the authorize flow
```

**Practical bootstrap path:** After connecting in Claude.ai, Invintory issues a refresh token via the browser OAuth session. The Claude.ai connector stores it internally. To make it available to Jarvis (outside Cowork), you'll need to:
- Run the initial auth flow via Claude Code's `/mcp` command: `claude mcp add invintory https://api.invintory.com/mcp`
- After auth completes, Claude Code stores the OAuth tokens. Extract the refresh token from `~/.claude/mcp_tokens.json` (or equivalent location Claude Code uses) and paste into `config/.env` alongside the expiry timestamp.

Once `INVINTORY_REFRESH_TOKEN` is in `.env`, this skill takes over permanently.

---

## Token Management (fully autonomous)

Every call to the Invintory MCP must first validate and, if needed, refresh the access token. Use this Python logic — execute via `mcp__Desktop_Commander__start_process` (never sandbox bash, which blocks egress).

```python
#!/usr/bin/env python3
"""
invintory-token.py
Reads config/.env, refreshes INVINTORY_ACCESS_TOKEN if within 5 min of
expiry or already expired, writes updated values back to .env.
Prints the valid access token to stdout.
"""
import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = REPO_ROOT / "config" / ".env"
TOKEN_URL_DEFAULT = "https://api.invintory.com/oauth/token"


def load_env():
    env = {}
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


def write_env_key(key, value):
    lines = ENV_PATH.read_text().splitlines()
    updated = False
    new_lines = []
    for line in lines:
        if line.startswith(f"{key}="):
            new_lines.append(f"{key}={value}")
            updated = True
        else:
            new_lines.append(line)
    if not updated:
        new_lines.append(f"{key}={value}")
    ENV_PATH.write_text("\n".join(new_lines) + "\n")


def refresh_access_token(env):
    payload = json.dumps({
        "grant_type": "refresh_token",
        "refresh_token": env["INVINTORY_REFRESH_TOKEN"],
        "client_id": env["INVINTORY_CLIENT_ID"],
        "client_secret": env["INVINTORY_CLIENT_SECRET"],
    }).encode()
    url = env.get("INVINTORY_TOKEN_URL", TOKEN_URL_DEFAULT)
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read())
    new_token = result["access_token"]
    expires_in = result.get("expires_in", 3600)
    expires_at = int(time.time()) + expires_in
    write_env_key("INVINTORY_ACCESS_TOKEN", new_token)
    write_env_key("INVINTORY_TOKEN_EXPIRES", str(expires_at))
    if "refresh_token" in result:
        write_env_key("INVINTORY_REFRESH_TOKEN", result["refresh_token"])
    return new_token


def get_valid_token():
    env = load_env()
    expires = int(env.get("INVINTORY_TOKEN_EXPIRES", "0"))
    if time.time() > expires - 300:  # refresh if within 5 min of expiry
        return refresh_access_token(env)
    return env["INVINTORY_ACCESS_TOKEN"]


if __name__ == "__main__":
    print(get_valid_token())
```

**Usage pattern for any agent:**

```python
# Step 1 — get valid token (refreshes automatically if needed)
# Resolve IES_ROOT from env (set by hooks) or fall back to git rev-parse
import os, subprocess
ies_root = os.environ.get("IES_ROOT") or subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], text=True).strip()
token_result = mcp__Desktop_Commander__start_process(
    command="python3 skills/invintory/invintory-token.py",
    cwd=ies_root
)
access_token = token_result.stdout.strip()

# Step 2 — call MCP tool
import json, urllib.request

def invintory_call(method, params, token):
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": f"tools/call",
        "params": {"name": method, "arguments": params},
        "id": 1
    }).encode()
    req = urllib.request.Request(
        "https://api.invintory.com/mcp",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())
```

**In Cowork / Claude Code sessions** where `mcp__invintory__*` tools appear in the tool list: use them directly — no need to manually handle tokens. This script is the fallback for scheduled tasks, Python orchestrator, and any context where the MCP connector isn't loaded.

---

## Available Tools

The exact tool names surface after auth. Based on Invintory's documented capabilities, expect these (names may vary slightly from what the server returns — enumerate with `tools/list` on first authenticated call if uncertain):

### Read

| Expected Tool | What It Does |
|--------------|-------------|
| `search_collection` | Search bottles by any field — vintage, producer, varietal, region, appellation |
| `get_bottle` | Get full detail on a specific bottle by ID |
| `list_collection` | List all bottles, optionally filtered/sorted |
| `get_drink_windows` | Bottles currently in peak drinking window |
| `get_collection_value` | Total market value of collection |
| `get_bottle_value` | Market value for a specific bottle |
| `get_food_pairings` | Suggest bottles from collection for a food/dish |
| `get_collection_insights` | Stats — by region, varietal, vintage distribution |
| `get_drinking_soon` | Bottles entering drink window in next N days |

### Write

| Expected Tool | What It Does |
|--------------|-------------|
| `add_bottle` | Add a bottle (or case) to the collection |
| `remove_bottle` | Remove / consume a bottle — marks as drunk |
| `update_bottle` | Update location, quantity, notes, tags |
| `add_tasting_note` | Log a tasting note and rating for a bottle |
| `create_list` | Create a custom list (e.g., "Dinner Party Picks") |
| `add_to_list` | Add a bottle to an existing list |

---

## Sterling Usage Patterns

### Wine Monitor — deal scoring against collection

When Last Bottle surfaces a deal, Sterling checks for overlap with existing inventory before recommending:

```
1. get_valid_token()
2. search_collection(varietal=<deal varietal>, region=<deal region>)
3. If owned: note quantity, average cost, compare to deal price
4. Score accordingly — don't recommend buying if cellar already has 12+
```

### Shipment arrival — log to cellar

When a shipment confirmation hits the /Jarvis inbox:

```
1. Extract: producer, vintage, varietal, quantity, price per bottle, storage location (wine locker: 10400 Clarence Dr, Frisco TX)
2. get_valid_token()
3. add_bottle(producer, vintage, varietal, quantity, location, purchase_price)
4. Confirm in Slack: "Logged [N] bottles of [wine] to Invintory — cellar now current."
```

### What's drinking well right now

```
1. get_valid_token()
2. get_drink_windows() — filter for currently in-window bottles
3. Present top picks sorted by score / value
```

### What's in the cellar (ad hoc queries)

```
"Do I have any 2015 Napa Cab?"
→ search_collection(vintage=2015, region="Napa Valley", varietal="Cabernet Sauvignon")

"What's my most valuable bottle?"
→ list_collection(sort_by="market_value", order="desc", limit=5)

"What should I open with steak tonight?"
→ get_food_pairings(dish="steak")
```

---

## Error Handling

| Situation | Action |
|-----------|--------|
| Token refresh fails (network) | Retry once after 5s. If second attempt fails, alert David via Slack and skip the Invintory step — do not block the larger workflow. |
| Token refresh fails (401/403) | Refresh token likely expired. Alert David: "Invintory auth needs re-authorization — run `claude mcp add invintory https://api.invintory.com/mcp` in Claude Code to re-auth." |
| Tool returns empty collection | Return "No bottles found matching criteria" — not an error. |
| Add/remove fails (404) | Bottle ID not found — surface to David, do not silently fail. |
| Rate limited (429) | Wait 10s, retry once. If still throttled, log and skip. |

---

## Token File Location

The token refresh script lives at `skills/invintory/invintory-token.py`.

---

## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/invintory-latest.json
```

Content:
```json
{
  "skill": "invintory",
  "agent": "sterling",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from the morning briefing or a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output, `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action.

After writing the signal file, also write a working memory file to `memory/working/` using this filename pattern:

```
invintory-YYYY-MM-DD-HHmmss.md
```

The file must begin with this YAML frontmatter (all fields required):

```yaml
---
type: working
task_id: "session"
session_id: "sterling-{YYYY-MM-DD}-{HHmmss}"
agent-source: sterling
created: {YYYY-MM-DD}T{HH:MM:SS}
expires: {YYYY-MM-DD+2}T{HH:MM:SS}
status: active
context: "Invintory cellar operation — {YYYY-MM-DD}"
---
```

Body: 3-5 bullet points summarizing key outputs, decisions, and any flags from this run. Keep it under 200 words.
<!-- system:end -->

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill invintory
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/invintory.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
