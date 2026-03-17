# Plaud MCP Integration

**Status**: Planned (2026-03-16)
**Spec**: [SPEC.md](./SPEC.md)
**Plan**: [PLAN.md](./PLAN.md)

## What This Is

MCP server that gives Jarvis native access to Plaud transcripts, summaries, and recording metadata — replacing the current browser-based scraping workflow via Knox.

## Approach

**Adopt and extend** — an existing community MCP (`sergivalverde/plaud-toolkit`) already implements the core functionality. Evaluate for adoption, fork if needed, extend with IES-specific features.

## Components

1. `plaud-mcp/` — MCP server (adopt or build)
2. IES integration — auto-ingest transcripts into Obsidian, meeting prep, post-meeting capture

## Why This Matters

Current workflow requires Chrome automation to pull Plaud transcripts. That's fragile, slow, and blocks Jarvis from using transcripts in real-time during conversations. A native MCP means:

- Instant transcript access during any conversation
- Auto-routing of meeting notes to Obsidian vault
- Post-meeting action item extraction without manual steps
- Steve Hall deployment can reuse the same connector

## Related Files

- `agents/knox.md` — Knox currently handles Plaud via browser automation
- `projects/steve-hall/Steve-Hall-Implementation-Guide.md` — Steve's IES uses Plaud for Zoom/Teams capture
- `identity/INTEGRATIONS.md` — Current tool inventory
