## Release Watch — 2026-03-07

### Adopt

- **`/loop` command for recurring prompts**: Cron-based recurring prompts within sessions (e.g., `/loop 5m check the deploy`). Recommendation: Integrate into Chief's boot cycle for repeating monitor tasks, health checks, and delegation nudges. Pair with scheduled-tasks for background execution.

- **Cron scheduling tools for recurring prompts**: Native cron scheduling within Claude Code sessions. Recommendation: Use for recurring Shep nudge cycles, Harper content calendar beats, and Quinn initiative polling without external orchestration.

- **`InstructionsLoaded` hook event**: New hook triggered when instructions load. Recommendation: Wire into Master's agent dispatch on boot to validate all 8 agents' SYSTEM.md files and skill manifests load correctly. Add safety checkpoint before sub-agent launch.

- **HTTP hooks that POST JSON to URLs**: Hooks can now fire POST requests to external endpoints. Recommendation: Route OmniFocus completion events (via osascript) and Clay CRM updates to external logging/audit system. Enable async notification chains between agents.

- **`${CLAUDE_SKILL_DIR}` variable for skills**: New variable for accessing skill directory path. Recommendation: Update all skill references in Master boot sequence to use this var instead of relative paths. Improves portability across machines.

- **Auto-memory**: Claude automatically saves useful context (manage with `/memory`). Recommendation: Enable for all agents to reduce per-session context rebuilding. Use `/memory` in Harper and Chase for persistent account/campaign state across conversations.

- **Scheduled Tasks in Cowork** (Feb 25): Create and schedule both recurring and on-demand tasks. Recommendation: Use for Quinn's rock review cycle and Harper's content calendar beats. Offload timing logic from Master to Cowork scheduling engine.

- **Plugin reload without restart** (`/reload-plugins`): Activate pending plugin changes without restarting Claude Code. Recommendation: Use during IES evolution deployments to test new MCP servers and skill registrations live.

### Evaluate (Need Your Call)

- **Opus 4.6 now defaults to medium effort; "ultrathink" keyword for high effort**: Default model behavior changed. Master currently dispatches agents without explicit effort declaration. Uncertainty: Should each agent have explicit effort tuning? Should strategy (Quinn), analysis (Knox), and prep (Chief) tasks use `ultrathink` for deeper work? Or is medium effort sufficient for agent tasks?

- **`sandbox.enableWeakerNetworkIsolation` for macOS**: Allows Go programs (gh, gcloud, terraform) with custom MITM proxy. Uncertainty: Does IES need this for CI/CD integration or cloud CLI calls? Is this a security trade-off worth evaluating for your Improving infrastructure integration?

- **`oauth.authServerMetadataUrl` config option for MCP servers**: Custom OAuth metadata server support. Uncertainty: If Improving uses proprietary/custom OAuth servers for Clay CRM or M365, this could unlock those integrations. Need to verify Improving's auth infrastructure.

- **`pathPattern` regex matching for `strictKnownMarketplaces`**: Plugin source validation via regex. Uncertainty: Is this needed for IES's internal skill/workflow distribution, or is it only relevant for team/org marketplace vetting?

- **Plugin source type `git-subdir`**: Plugins can now come from git subdirectories. Uncertainty: Does IES benefit from splitting agents/skills into separate git repos with subdir registration? Or is monorepo cleaner for your workflow?

- **Memory for Free Users** (Mar 2): Memory features now available to all Claude users. Uncertainty: Does this change IES's approach to persistent agent state? Should auto-memory replace some custom Obsidian vault logic?

### Skipped

18 changes with no IES relevance:
- Voice STT language expansion (10 new languages)
- Clipboard corruption fixes (Windows/WSL)
- Bridge reconnection improvements
- Numeric keypad support for interviews
- Non-ASCII text handling (Windows/WSL)
- Effort level display in logo/spinner
- Plugin deduplication improvements
- Startup performance deferring image processor loading
- Bash auto-approval allowlist expansion (fmt, comm, cmp, numfmt, expr, test, printf, getconf, seq, tsort, pr)
- MCP OAuth token refresh race condition fix
- Config file corruption fixes
- Prompt cache handling improvements
- Claude Sonnet 4.6 launch (already captured in Opus 4.6 relevance)
- PowerPoint/Excel add-in integrations
- Enterprise Analytics API
- Self-serve Enterprise plans
- VSCode activity bar spark icon
- VSCode markdown document view for plans

---

## Summary

**10 items to adopt immediately.** Focus: `/loop` + cron for recurring cycles, hooks for boot validation, HTTP post for async chains, auto-memory for agent state persistence, Cowork scheduling for quarterly cycles.

**4 items need your call.** Model effort tuning and OAuth infrastructure are the heavyweight decisions.

**18 items skipped.** Mostly UI polish, language support, and enterprise features outside IES scope.
