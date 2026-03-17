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

## Unblock Options

1. **Re-request API access** — TripIt may have changed policy since Feb 2026
2. **iCal feed parsing** — TripIt exposes calendar feeds; limited data but no auth needed
3. **Outlook-based travel extraction** — Parse confirmation emails directly via M365 MCP (no TripIt dependency)
4. **Concur/SAP integration** — If Improving uses Concur, that may be a better source

## See Also

- `projects/plaud-mcp/` — Sister MCP project (planned, 2026-03-16). Similar pattern, different API. Plaud is unblocked and ready to build.

## Related Files

- `reference/lounge-guide.md` — Airport lounge playbook (built 2026-02-19)
- `identity/MEMORY.md` — Travel preferences, loyalty numbers, airline/hotel prefs
