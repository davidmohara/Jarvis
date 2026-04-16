# Jarvis — New Machine Setup

Follow this guide exactly when setting up Jarvis on a new Mac. Should take ~15 minutes.

---

## Prerequisites

Before starting, confirm these are installed and synced:

- [ ] **Homebrew** — `brew --version`
- [ ] **Node.js** (v18+) — `node --version`
- [ ] **OneDrive** — mounted and fully synced at `~/Library/CloudStorage/OneDrive-Improving/`
- [ ] **iCloud / Obsidian** — vault accessible at `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian/`
- [ ] **Claude Code** — installed and authenticated

---

## Step 1 — Clone the repo

```bash
mkdir -p ~/develop
cd ~/develop
git clone https://github.com/[YOUR_REPO_URL] my-os
cd my-os
```

---

## Step 2 — Create `.claude/mcp.json`

This file is gitignored (it contains API keys). Create it from the template:

```bash
cp .claude/mcp.json.template .claude/mcp.json
```

Then fill in the actual values. See **`.claude/mcp.json.template`** for required keys and where to find each one.

> **Note**: Microsoft 365 and Mermaid Chart are Claude.ai cloud connectors — configure those in the Claude.ai UI (Settings → Connectors), not in mcp.json.

---

## Step 3 — Create `config/settings.json`

Required by Rigby package and evolution skills. Create the file:

```bash
mkdir -p config
```

Then create `config/settings.json` with this structure (fill in your values):

```json
{
  "ies_app_url": "https://[IES-APP-URL]",
  "api_token": "[YOUR-IES-API-TOKEN]",
  "evolution_management": {
    "backup_before_apply": true
  }
}
```

> Get the `ies_app_url` and `api_token` from the IES portal or a working machine's config. This file must **not** be committed — add it to `.gitignore` if it isn't already.

---

## Step 4 — Verify git status is clean

```bash
git status
```

Should show: `nothing to commit, working tree clean`

If there are unexpected untracked files (temp data, compiled artifacts), check `.gitignore` before committing anything.

---

## Step 5 — Clear stale pending evolutions (if present)

Check if there are stuck pending evolutions:

```bash
cat evolutions/.pending-changes.json
```

If the `pending` array has items whose work is already merged into the repo (files already exist), clear them by resetting the file:

```bash
echo '{ "pending": [] }' > evolutions/.pending-changes.json
git add evolutions/.pending-changes.json
git commit -m "Clear stale pending evolutions on new machine setup"
```

---

## Step 6 — Boot test

Open Claude Code in the `my-os/` directory and run:

```
boot up
```

Confirm the morning briefing loads cleanly — Clay reminders, OmniFocus inbox, and live calendar all return data. If any MCP server fails, the error will identify which key in `mcp.json` needs fixing.

---

## Cloud Connectors (configured in Claude.ai UI, not mcp.json)

These don't go in `mcp.json` — configure them in Claude.ai Settings → Connectors:

| Connector | Used For |
|-----------|----------|
| Microsoft 365 | Outlook calendar, email, Teams |
| Mermaid Chart | Diagram rendering |

---

## Troubleshooting

**OmniFocus not responding** → OmniFocus must be running. MCP server connects to the running app.

**Obsidian tools failing** → Confirm iCloud has fully synced the vault. The MCP server reads directly from the local iCloud path.

**Clay returning empty results** → Check `mcp.json` — Clay's API key may have been rotated. Grab a fresh key from [clay.com](https://clay.com) → Settings → Integrations → MCP.

**Calendar not loading** → M365 connector is configured in the Claude.ai UI, not here. Re-authorize if the token expired.
