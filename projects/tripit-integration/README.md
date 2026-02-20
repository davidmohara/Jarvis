# TripIt Integration

**Status**: Planned — waiting on API app registration
**Spec**: [SPEC.md](./SPEC.md)

## What This Is

MCP server + Claude skill that pulls travel data from TripIt and generates pre-trip briefings with lounge recommendations, hotel/flight details, calendar integration, and David's preferences baked in.

## Components

1. `tripit-mcp/` — Node.js MCP server (OAuth 1.0a → TripIt API v1)
2. `travel-brief-skill/` — Claude skill for `/travel-brief` command

## Blockers

- [ ] **David**: Register TripIt API app (in OmniFocus inbox)
- [ ] Get consumer key + secret from registration
- [ ] Run OAuth authorization flow to get access token

## Related Files

- `reference/lounge-guide.md` — Airport lounge playbook (built 2026-02-19)
- `identity/MEMORY.md` — Travel preferences, loyalty numbers, airline/hotel prefs
