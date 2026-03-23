# Release Watch -- 2026-03-23

Sources checked: Claude Code GitHub (latest: v2.1.81), Claude Help Center (latest: March 17, 2026).
First run since 2026-03-07. Reporting changes from v2.1.76 through v2.1.81 and Cowork updates since March 7.

---

## Adopt

- **`--bare` flag for scripted `-p` calls** (v2.1.81): Skips hooks, LSP, plugin sync, and skill directory walks for clean headless execution. Recommendation: Use this in any automated/scripted IES invocations where boot overhead and hook interference are unwanted.

- **`effort` frontmatter for skills and slash commands** (v2.1.80): Skills can now declare their effort level in frontmatter, overriding the default. Recommendation: Add `effort:` to heavy skills (release-watch, quinn-weekly-review) to ensure they use full reasoning; add `effort: low` to lightweight ones for speed.

- **`PostCompact` hook** (v2.1.76): Fires after compaction completes. Recommendation: Hook this to re-inject persistent context (mission control, current rocks) that gets dropped during long-session compaction.

- **`StopFailure` hook event** (v2.1.78): Fires when a turn ends due to API error (rate limit, auth failure, etc.). Recommendation: Wire this into the error-log system to auto-capture API failures without manual reporting.

- **`source: 'settings'` plugin marketplace source** (v2.1.80): Declare plugin entries inline in settings.json rather than via marketplace. Recommendation: Cleaner way to pin IES plugins without marketplace dependency. Consider migrating current plugin declarations.

- **Plugin freshness: ref-tracked re-clone on every load** (v2.1.81): Ref-tracked plugins now re-clone on load to pick up upstream changes. Recommendation: If any IES plugins are ref-tracked, this ensures they stay current automatically. Verify plugin declarations use refs where appropriate.

- **`CLAUDE_CODE_PLUGIN_SEED_DIR` multi-directory support** (v2.1.79): Now accepts colon-separated list of seed directories. Recommendation: Useful if IES ever splits skills across directories. Low urgency but worth knowing.

- **Persistent Cowork thread for session management** (March 17, 2026 -- Pro/Max research preview): Persistent thread in Cowork for managing claude.ai sessions via Desktop and mobile. Recommendation: Worth enabling once out of research preview. Could provide a durable control surface for IES agent management from phone.

---

## Evaluate (Need Your Call)

- **`--channels` permission relay** (v2.1.81, research preview): Channel servers can forward tool approval prompts to your phone. Uncertainty: Could be useful for approving IES agent actions remotely, but it's research preview and channel server infrastructure isn't documented yet. Worth watching. Do you want to track this for when it ships?

- **MCP elicitation support + `Elicitation`/`ElicitationResult` hooks** (v2.1.76): MCP servers can request structured input mid-task via interactive dialog. Uncertainty: Could change how IES agents collect dynamic input mid-run. Need to know if any current MCP servers will start using this, which could interrupt automated flows. Should we add an ElicitationResult hook to control behavior?

- **`worktree.sparsePaths` setting** (v2.1.76): Sparse checkout for `--worktree` in large monorepos. Uncertainty: IES uses worktrees. If the repo grows, this could speed up worktree boots. Low urgency now -- worth adding to evolutions backlog?

- **Plugin marketplace + org admin controls** (Feb 24, 2026): Plugin marketplace live with Team/Enterprise org controls. Uncertainty: If Improving's org moves to managed settings, plugin installs may require admin approval. Does Improving have an Enterprise org? Could affect IES plugin installs.

- **Agent Skills open standard** (Dec 18, 2025): Anthropic published an open standard for agent skills; third-party skills directory launched. Uncertainty: Could mean the SKILL.md format gets updated or superseded by the standard. Worth reviewing whether IES skills comply. Should I pull the spec?

---

## Skipped

~40 changes with no IES relevance: voice mode fixes, Windows/WSL bugs, VS Code UI polish, CJK rendering, IDE-specific features, billing/plan management, Claude for Excel/PowerPoint, mobile health data, iTerm2/tmux rendering edge cases, interactive charts, LLM gateway integrations.

---

*Next run will report changes newer than 2026-03-23.*
