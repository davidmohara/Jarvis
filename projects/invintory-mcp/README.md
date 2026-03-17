# Invintory MCP Integration

**Status**: Planned (2026-03-17) — API discovered, auth mechanism pending
**Spec**: [SPEC.md](./SPEC.md)
**Plan**: [PLAN.md](./PLAN.md)

## What This Is

MCP server that gives Jarvis native access to David's wine collection in Invintory — cellar inventory, tasting notes, market valuations, drinking windows, and collection analytics.

## Approach

**Reverse-engineer the web app API.** Invintory has no public API, but the web app at `app.invintory.com` is a SolidStart SSR app that proxies calls to `api.invintorywines.com/v3/`. We've mapped the API surface and identified Firebase Auth as the likely auth mechanism (based on profile UID format). Same playbook as Plaud.

**Gating issue**: Auth discovery (Phase 0 in PLAN.md). Once we can authenticate directly against the API, build is straightforward.

## Why

- "What wines do I have that are ready to drink?" — answered instantly
- Meeting prep: "We're hosting a dinner for 8 — what should I pull from the cellar?"
- Collection health: "How's my cellar value trending? Any wines past their window?"
- Purchase decisions: "Do I already own this producer/vintage?"
- Event pairing: Wisdom dinners, entertaining — Jarvis can suggest pairings and check stock

## Components

1. `invintory-mcp/` — MCP server (to be built after API discovery)
2. IES integration — collection queries, dinner planning, purchase tracking

## Related Files

- `identity/MEMORY.md` — David's preferences (if wine prefs are documented)
- `projects/plaud-mcp/` — Sister MCP project, similar reverse-engineering approach
