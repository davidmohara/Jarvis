# Jarvis Bridge Protocol

Two Jarvis instances collaborate through this file-based message queue. Both sides read this file on boot.

## Instances

| Instance | Environment | Capabilities |
|----------|-------------|-------------|
| **Code** | Claude Code (terminal) | Bash, osascript, OmniFocus, git, Obsidian MCP, file creation, Mac Mail drafts |
| **Desktop** | Claude Desktop | M365 MCP (email, calendar, Teams), filesystem MCP |

## Message Format

**Filename**: `YYYYMMDD-HHMMSS-{from}-{slug}.md`

Example: `20260211-143022-code-email-search-forbes.md`

**Template**: See `_template.md` for the full structure. Every message includes:
- Frontmatter: `from`, `to`, `priority`, `status`, `category`, `created`
- Sections: Request, Context, Response

## Lifecycle

```
1. Sender creates message in bridge/inbox/
2. Receiver picks it up on /bridge-check or boot
3. Receiver fills ## Response, sets status: done
4. Receiver moves file from inbox/ to done/
5. Sender reads result on next check
```

If a request can't be fulfilled, the receiver sets `status: failed` and explains in Response.

## Capability Routing

When a request falls outside your capability, create a bridge message - no need for David to say `/bridge-send`. Just confirm: "I can't access [X] directly. I've queued this for [Desktop/Code]."

| Need | Routes To | Category |
|------|-----------|----------|
| Search/read email | Desktop | `email` |
| Search/read calendar | Desktop | `calendar` |
| Search Teams messages | Desktop | `teams` |
| Create OmniFocus tasks | Code | `omnifocus` |
| Run osascript / Mac Mail | Code | `osascript` |
| Git operations | Code | `git` |
| Complex file creation | Code | `file-ops` |
| Obsidian vault ops | Code | `obsidian` |

## Priority

- **normal**: Next time the receiver checks inbox
- **urgent**: Receiver should process immediately on boot before other work

## Stale Messages

Any message sitting in `inbox/` for more than 24 hours is flagged as stale by `/bridge-status`. Either the receiving instance hasn't been opened, or the message was missed.

## Automation

The Code instance can submit prompts directly to Claude Desktop using:

```bash
bridge/send-to-desktop.sh "Your prompt here"
bridge/send-to-desktop.sh --file /path/to/prompt.txt
```

This opens a new Cowork task in Claude Desktop with the my-os folder, pastes the prompt, and submits it. Requires the `swift` runtime to have accessibility permissions (System Settings > Privacy & Security > Accessibility).

## Rules

1. One request per message. Keep it atomic.
2. Include enough context for the receiver to act without follow-up questions.
3. Never send messages, modify CRM, or make commitments - same rules as AUTOMATION.md.
4. Both instances share the same identity: Jarvis. Same voice, same rules, same loyalty.
