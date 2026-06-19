## Release Watch -- 2026-06-19

Last checked: 2026-03-23 (v2.1.81). Latest: v2.1.158. Covering ~3 months of releases.

---

### Adopt

- **Skills auto-load from `.claude/skills/`** (v2.1.157): Plugins in `.claude/skills` are now loaded automatically without marketplace registration. IES already stores skills there -- verify nothing breaks on next boot. Also check if any skills were previously marketplace-registered and are now double-loading.

- **`agent` field in `settings.json` honored for dispatched sessions** (v2.1.154): The `agent` field is now respected when Claude dispatches subagents, `--agent <name>` overrides it. Directly affects how IES routes agent calls. Review `settings.json` to confirm the right default agent is set.

- **`SessionStart` hook can return `reloadSkills: true`** (v2.1.152): Hook can trigger a skill re-scan without restarting. The boot workflow could install or update skills during startup and have them available in the same session.

- **`SessionStart` hook can set session title** (v2.1.152): `hookSpecificOutput.sessionTitle` sets the session name on startup and resume. Useful for labeling Jarvis boot sessions in `claude agents`.

- **`disallowed-tools` in skill frontmatter** (v2.1.152): Skills can now remove specific tools from the model while active. Useful for constraining sensitive skills -- e.g., the git skill could disallow raw bash.

- **Stdio MCP servers receive `CLAUDE_CODE_SESSION_ID`** (v2.1.154): MCP server subprocesses get the session ID in their environment. Useful if IES MCP servers need to correlate logs by session.

- **Background sessions get correct date after sleep/wake** (v2.1.154): Bug fix for stale date context in background sessions. Already shipped. Explains any past stale-date behavior in IES background agents.

---

### Evaluate (Need Your Call)

- **Dynamic workflows** (v2.1.154): `/workflows` command lets Claude orchestrate tens-to-hundreds of agents in the background for large tasks. Uncertainty: could overlap with or complement IES dispatch architecture. Worth running `/workflows` to inspect before deciding whether to integrate or ignore.

- **Opus 4.8 now default** (v2.1.154): Opus 4.8 is new default; fast mode at 2x rate for 2.5x speed. Uncertainty: IES agents may have model pins in frontmatter, but any that don't will silently upgrade. Check `agents/*.md` for unpinned models. Cost/behavior change may or may not be acceptable.

- **`MessageDisplay` hook** (v2.1.152): New hook type that transforms or suppresses assistant message text before display. Uncertainty: no clear IES use case right now, but this is a meaningful hook system extension. Worth noting for future instrumentation or output filtering.

- **`tool_decision` telemetry with `tool_parameters`** (v2.1.157): When `OTEL_LOG_TOOL_DETAILS=1`, telemetry events include bash commands and MCP/skill names. Uncertainty: IES eval harness doesn't use OpenTelemetry. Could be a path to richer skill-run data, but requires wiring in OTEL. Decide if worth pursuing.

- **`claude plugin init <name>` scaffolding** (v2.1.157): Scaffolds a new skill in `.claude/skills`. Uncertainty: IES has its own SKILL.md conventions. Check if generated scaffold matches IES format or conflicts.

- **Claude Compliance API integrations** (May 21, 2026): IT/security teams can govern Claude via compliance API. Uncertainty: if Improving IT has deployed this, it could restrict which tools or MCP servers IES can use. Worth asking Global IT Services.

- **Subagent MCP servers now honor managed-settings allow/deny** (v2.1.153): Previously, subagent MCP servers bypassed managed settings. Now enforced. Uncertainty: if Improving has managed settings deployed, this could silently restrict IES subagent MCP access. Verify no IES subagents are affected.

---

### Skipped

12 changes with no IES relevance (bug fixes for unused features, WSL/Windows-specific, IDE-specific, cosmetic UI, Bedrock/Vertex/Foundry-specific, suspended model access, billing/plan management).

---

*Next run will report changes newer than 2026-06-19.*
