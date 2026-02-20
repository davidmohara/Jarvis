# TripIt Integration

**Status**: Shelved (2026-02-20) — TripIt denied API access request
**Spec**: [SPEC.md](./SPEC.md)

## What This Is

MCP server + Claude skill that pulls travel data from TripIt and generates pre-trip briefings with lounge recommendations, hotel/flight details, calendar integration, and David's preferences baked in.

## Components

1. `tripit-mcp/` — Node.js MCP server (scaffolded, not implemented)
2. `travel-brief-skill/` — Claude skill for `/travel-brief` command

## Why Shelved

TripIt denied the request to enable API access. Without official API access, the remaining options (undocumented web API with browser cookies, iCal feed parsing, or pulling travel data from Outlook instead) weren't worth pursuing right now.

## Related Files

- `reference/lounge-guide.md` — Airport lounge playbook (built 2026-02-19)
- `identity/MEMORY.md` — Travel preferences, loyalty numbers, airline/hotel prefs
