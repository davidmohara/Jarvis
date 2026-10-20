<!-- personal:start -->
# SLACK INTEGRATION

> **CRITICAL — Desktop Commander MUST be loaded before any Slack operations:**
> - **ALWAYS load Desktop Commander tools at the start of any step that reads/writes Slack.** Use ToolSearch: `"select:mcp__Desktop_Commander__start_process,mcp__Desktop_Commander__read_file,mcp__Desktop_Commander__write_file"`.
> - **In a Cowork session:** the sandboxed `mcp__workspace__bash` tool does NOT have general outbound network access (small allowlist only) and WILL fail read.py/post.py with a tunnel/connection error. Do not use it for this step. Use `mcp__Desktop_Commander__start_process` instead — it executes on the actual Mac and has full network access.
> - **In native Jarvis (Claude Code) runtime:** `mcp__Desktop_Commander__start_process` is the only authorized path regardless — this was already the rule, restated here for emphasis.
> - If read.py/post.py fails with a network/connection error, do NOT conclude "no network access" and abort. First confirm which execution tool was used. If it was the Cowork sandbox bash tool, retry the identical command via `mcp__Desktop_Commander__start_process` before reporting any failure.
> - **Deferred-tool delay (Cowork):** Desktop Commander tools are deferred and may not appear in ToolSearch at the very start of a session. If ToolSearch returns no match for `mcp__Desktop_Commander__start_process`, do NOT abort the run or set `state.yaml` to `aborted`: wait a moment and retry ToolSearch, or attempt the tool call directly. A single failed ToolSearch is not evidence the tool is missing.

**Reading:** Use `systems/slack-bot/read.py` via Desktop Commander (mcp__Desktop_Commander__start_process)

```bash
# Read #content for URLs dropped in last 24 hours
python3 "$(mdfind -name 'read.py' | grep 'systems/slack-bot/read.py' | head -1)" channel C0B160MA3EK 24
```

Returns JSON: `{"ok": true, "messages": [...]}`. Each message object includes: `ts`, `user`, `text`, `thread_ts` (if part of a thread).

**GATE 1 (Source Integrity) validates this response before anything else happens — see step-01-discover.md.**

**Writing/Notifying:** Use `master-slack` skill — `systems/slack-bot/post.py` via Desktop Commander

```bash
python3 "$(mdfind -name 'post.py' | grep 'systems/slack-bot/post.py' | head -1)" C0B160MA3EK "<message>"
```

No Slack MCP connector is used. Both read and write go through the bot token in config/.env via these two scripts.
<!-- personal:end -->
