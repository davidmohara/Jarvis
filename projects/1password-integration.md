# Project: Secret Management for IES

**Created**: 2026-03-30
**Status**: Proposed
**Owner**: David O'Hara
**Rocks**: IES platform maturity

## Objective

Build a provider-agnostic secret management layer for IES. Default is on-disk local files. 1Password is an opt-in upgrade, like Obsidian or Clay. The system never assumes which provider the executive has chosen.

## ICE Score

| Factor | Score (1-10) | Notes |
|--------|-------------|-------|
| **I**mpact | 8 | Cleaner onboarding, no scattered plain-text secrets, upgradeable for security-conscious execs |
| **C**onfidence | 9 | `op` CLI is mature, local `.env` is proven, abstraction layer is simple |
| **E**ase | 7 | Thin abstraction, no breaking changes, local default works today without any migration |
| **Average** | 8.0 | |

## Problem

Secrets are scattered across plain-text files (`config/.env`, `config/.credentials`, `.mcp.json` env vars) and protected only by `.gitignore`. The system has no concept of a secret provider, making it hard to upgrade without touching every integration point. New connectors write secrets wherever convenient — no single story.

## Design Principle

Secret management follows the same pattern as other optional integrations (Obsidian, Clay):

- **Local (default)**: On-disk `.env` file, gitignored, works everywhere, no dependencies
- **1Password (opt-in)**: User's personal vault via `op` CLI, biometric auth, no shared vault, each exec manages their own
- **Extensible**: Architecture supports adding other providers later (macOS Keychain, etc.) without changing how the rest of the system asks for secrets

The system is written agnostically. No agent, skill, or workflow knows which provider is active. They ask for a secret by name; the secret layer returns it.

## Architecture

```
+------------------------------------------+
|  Executive's Secret Store                |
|  (1Password personal vault  OR  .env)    |
+--------------------+---------------------+
                     | provider-agnostic interface
                     v
+------------------------------------------+
|  systems/secrets/                        |
|  - provider.json  (which provider)       |
|  - resolve.sh     (dispatcher)           |
|  - providers/local.sh                    |
|  - providers/1password.sh                |
+--------------------+---------------------+
                     | env vars injected per-call
                     v
+------------------------------------------+
|  IES Skills, Workflows, MCP Configs      |
|  ask for secrets by name, get values     |
|  never know or care which provider ran   |
+------------------------------------------+
```

**Key constraint noted from review**: Claude Code doesn't maintain a persistent shell environment across tool calls. Secrets resolved in one Bash call don't propagate to the next. This means `resolve.sh` is a per-invocation wrapper, not a session-level pre-loader. Each script or MCP server command that needs secrets wraps its call via `resolve.sh`. The boot "Phase 0" idea is dropped.

## Provider Config

Stored in `config/secrets-provider.json` (gitignored):

```json
{
  "provider": "local",
  "configured": "2026-03-30",
  "1password": {
    "vault": "Personal",
    "op_version": null
  }
}
```

- `provider`: `"local"` or `"1password"`
- `1password.vault`: the exec's vault name (they pick it, no hardcoded "IES")
- File is gitignored. A new instance defaults to `local` if the file is absent.

## File Changes

### New files

| File | Classification | Purpose |
|------|---------------|---------|
| `systems/secrets/resolve.sh` | System | Dispatcher: reads provider config, delegates to the right provider script |
| `systems/secrets/providers/local.sh` | System | Sources `config/.env`, execs the wrapped command |
| `systems/secrets/providers/1password.sh` | System | Runs `op run --env-file=config/.env.tpl`, execs the wrapped command |
| `systems/secrets/README.md` | System | How to use the layer, how to add a secret, how to switch providers |
| `config/.env.tpl` | Personal | `op://` URI references for 1Password provider. Only used when provider is 1password. |
| `config/secrets-provider.json` | Personal | Active provider config. Gitignored. |

### Modified files

| File | Classification | Change |
|------|---------------|--------|
| `.claude/skills/shep-onboard/SKILL.md` | System | Add Step 0.5: secret provider selection |
| `identity/INTEGRATIONS.md` | System | Add secret management to integrations table |
| `.gitignore` | System | Add `config/secrets-provider.json` and `config/.env.tpl` |

### `resolve.sh` design

```bash
#!/bin/bash
# Secret resolver — dispatches to the configured provider.
# Usage: resolve.sh <command> [args...]
# The wrapped command runs with secrets available as env vars.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG="$SCRIPT_DIR/../../config/secrets-provider.json"

if [ -f "$CONFIG" ]; then
    PROVIDER=$(python3 -c "import json,sys; print(json.load(open('$CONFIG'))['provider'])" 2>/dev/null || echo "local")
else
    PROVIDER="local"
fi

exec "$SCRIPT_DIR/providers/$PROVIDER.sh" "$@"
```

### `providers/local.sh` design

```bash
#!/bin/bash
ENV_FILE="$(cd "$(dirname "$0")" && pwd)/../../config/.env"
if [ -f "$ENV_FILE" ]; then
    set -a; source "$ENV_FILE"; set +a
fi
exec "$@"
```

### `providers/1password.sh` design

```bash
#!/bin/bash
TPL_FILE="$(cd "$(dirname "$0")" && pwd)/../../config/.env.tpl"

if ! command -v op &>/dev/null; then
    echo "[secrets] 1Password CLI not found. Falling back to local." >&2
    exec "$(dirname "$0")/local.sh" "$@"
fi

if ! op account list &>/dev/null 2>&1; then
    echo "[secrets] 1Password not authenticated. Falling back to local." >&2
    exec "$(dirname "$0")/local.sh" "$@"
fi

exec op run --env-file="$TPL_FILE" -- "$@"
```

### MCP server usage

Each MCP server that needs secrets wraps its command via `resolve.sh`. Example for a connector:

```json
{
  "command": "/path/to/ies/systems/secrets/resolve.sh",
  "args": ["node", "/path/to/mcp-server/dist/index.js"]
}
```

This is the mechanism that actually works within Claude Code's per-call execution model. No session-level pre-loading required.

## Shep Onboarding: Step 0.5

New step between Step 0 (Rigby registration) and Step 1 (Welcome & Intake). Framed as a choice, not an assumption.

### Flow

1. **Ask which secret provider to use**

   > "IES needs to store some credentials for your connected services. By default I'll keep them in a local file on your machine, which is fine. If you use 1Password, I can store them there instead so nothing sits in plain text on disk. Which do you prefer: local file or 1Password?"

2. **If local (or no answer)**: write `secrets-provider.json` with `provider: "local"`, done. Tell them:
   > "Got it. Credentials will be stored in `config/.env` on your machine."

3. **If 1Password**:
   - Check if `op` is installed (`which op`)
   - If missing: `brew install --cask 1password-cli`
   - If install fails: fall back to local, note it
   - Check auth: `op account list`
   - If no accounts: walk them through enabling CLI integration in 1Password app (Settings > Developer)
   - Ask: "What's the name of the vault you want to use for IES credentials?" (they name it themselves)
   - Verify vault exists: `op vault list --format=json`
   - Write `secrets-provider.json` with `provider: "1password"` and their vault name
   - Tell them: "1Password is set up. New credentials will go into your '[vault]' vault."

4. **This choice is not permanent**: they can switch providers later, and the system will respect it.

### Failure modes

| Scenario | Behavior |
|----------|----------|
| User doesn't have 1Password | Default to local without friction |
| No Homebrew | Skip install, default to local |
| Install fails | Default to local |
| App integration not enabled | Coach through it, don't block |
| Named vault doesn't exist | Ask them to create it first or choose a different vault |
| User cancels | Default to local |

## `config/.env.tpl` design

Only relevant when provider is `1password`. The vault name and item names come from the executive's own vault, so this file is generated during onboarding based on their answers. It is personal and gitignored.

Example for an exec who named their vault "Personal":

```bash
# IES Secret References -- resolved at runtime by op run
# Generated by Shep onboarding. Edit to match your 1Password vault items.
SLACK_BOT_TOKEN=op://Personal/slack-bot/token
WHOOP_CLIENT_ID=op://Personal/whoop-mcp/client_id
WHOOP_CLIENT_SECRET=op://Personal/whoop-mcp/client_secret
```

Note: item names use hyphens, not spaces, to avoid shell parsing edge cases.

## Secret Inventory

| Secret | Current Location | Local Provider | 1Password Provider |
|--------|-----------------|---------------|-------------------|
| `SLACK_BOT_TOKEN` | `config/.env` | stays in `.env` | `op://[vault]/slack-bot/token` |
| `WHOOP_CLIENT_ID` | shell env | move to `.env` | `op://[vault]/whoop-mcp/client_id` |
| `WHOOP_CLIENT_SECRET` | shell env | move to `.env` | `op://[vault]/whoop-mcp/client_secret` |
| Future MCP creds | varies | `.env` | `op://[vault]/[item]/[field]` |
| Azure tokens | `config/.credentials` | stays (device code flow manages) | Phase 2 |

## `/rigby-connector-setup` Integration

When a new connector is set up, the final step writes the credential to the active provider:

- **local**: append to `config/.env`
- **1password**: run `op item create` or `op item edit` to store in vault, then append the `op://` reference to `config/.env.tpl`

This makes the provider choice transparent to connector setup. Rigby writes to wherever the exec configured.

## Evolution Classification

| Component | Classification | Rationale |
|-----------|---------------|-----------|
| `systems/secrets/resolve.sh` | System | Generic dispatcher, any user benefits |
| `systems/secrets/providers/local.sh` | System | Generic local file resolution |
| `systems/secrets/providers/1password.sh` | System | Generic 1Password resolution |
| `systems/secrets/README.md` | System | Documentation |
| `config/.env.tpl` | Personal | User-specific vault/item references |
| `config/secrets-provider.json` | Personal | User's provider choice |
| Shep Step 0.5 | System | Onboarding flow, any user benefits |
| Vault name, item names | Personal | User's own 1Password organization |

## Key Milestones

- [ ] Build `systems/secrets/` directory: `resolve.sh`, `providers/local.sh`, `providers/1password.sh`, `README.md`
- [ ] Add `config/secrets-provider.json` and `config/.env.tpl` to `.gitignore`
- [ ] Add Step 0.5 to Shep onboarding skill
- [ ] Update `/rigby-connector-setup` to write credentials to active provider
- [ ] Update MCP server configs (Slack, WHOOP) to wrap command via `resolve.sh`
- [ ] Move WHOOP credentials from shell env to `config/.env` (local provider baseline)
- [ ] David: run Step 0.5 manually to configure his own instance (1Password)
- [ ] Phase 2: migrate `config/.credentials` Azure token handling

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `resolve.sh` path hardcoded in MCP configs | M | M | Use relative path from IES root, document convention |
| 1Password app not running when MCP server launches | M | M | `1password.sh` falls back to local silently |
| exec's vault name changes after setup | L | M | `secrets-provider.json` stores vault name, easy to update manually or via a skill |
| `op://` URI item name spaces cause parse errors | M | L | Convention: use hyphens in all 1Password item names for IES secrets |
| New contributor writes secrets to `.env` directly | M | M | `README.md` and `rigby-connector-setup` are the forcing functions |

## What This Unlocks

1. **Provider-agnostic secret layer**: skills and workflows never know how secrets are stored
2. **Clean onboarding**: one question during setup, system adapts
3. **Upgrade path**: exec can switch from local to 1Password without rebuilding anything
4. **Connector setup writes to the right place**: no manual coordination
5. **System evolutions don't touch secret storage**: it's personal config, fully isolated

## Updates

### 2026-03-30
- Project renamed from "1Password Integration" to "Secret Management" to reflect provider-agnostic scope
- Revised architecture: local is default, 1Password is opt-in (same model as Obsidian, Clay)
- Dropped boot Phase 0 pre-loader: doesn't work in Claude Code's per-call execution model
- Correct mechanism: `resolve.sh` wraps per-command calls, MCP servers use it in their `command` config
- Each exec uses their own vault (personal), no shared IES vault
- Provider config stored in `config/secrets-provider.json` (gitignored, personal)
- `config/.env.tpl` generated during onboarding based on exec's vault name, not committed
