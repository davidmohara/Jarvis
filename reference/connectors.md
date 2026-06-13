# Connector System Reference

## What Is a Connector

A connector is an IES package that wires an external service into the agent capability system. When a connector is installed, it registers one or more **capabilities** — named slots that agents resolve at runtime to find the right MCP tool.

Connectors live in `contributions/` and are installed via `rigby-package-install`.

---

## Standardized Capability Names

When building a connector package, use these standardized capability names in the `capabilities` array of your package manifest. Agents resolve these names to find active connectors.

| Capability | What It Provides | Example Connectors |
|---|---|---|
| `calendar` | Meeting schedule, availability, event search | MS365, Google Calendar |
| `email` | Email read, search, send | MS365 Outlook, Gmail |
| `crm` | Deal pipeline, contact records, account data | Clay, Salesforce, HubSpot |
| `contact-management` | People records, relationship history, enrichment | Clay |
| `task-management` | Task inbox, project tracking, due dates | OmniFocus, Todoist |
| `file-storage` | Cloud file access, search, upload/download | SharePoint, Google Drive, Box |
| `knowledge-store` | Vault write target — notes, transcripts, structured docs | Obsidian MCP, IES on-disk |
| `communication` | Chat, messaging, team notifications | Slack, Teams |
| `scheduling` | Scheduled task creation and management | Cowork Scheduler |
| `health-data` | Biometrics, recovery scores, sleep, activity | WHOOP MCP |
| `transcription` | Audio-to-text, transcript staging, speaker ID | Plaud MCP |
| `analytics` | Usage data, metrics, dashboards | GA4 MCP |

---

## Connector Lifecycle

1. **Build** — Rigby creates the connector package using `rigby-package-create`
2. **Install** — Package deployed via `rigby-package-install`; capability registered in `INTEGRATIONS.md`
3. **Resolution** — Agents check `identity/INTEGRATIONS.md` for active connectors matching a capability name
4. **Fallback** — If no connector is active for a capability, agents report: "No [capability] connector active — install a connector for this capability."

---

## Adding a New Capability Name

If a new connector introduces a capability not in the table above, add it here when packaging. Capability names must be:
- Lowercase kebab-case
- Specific enough to be unambiguous
- Generic enough to apply to multiple potential connectors

Route the addition to Rigby via Master.
