<!-- system:start -->
# Draft Publishing Formats (watchtower weekly-step-06)

Used by tasks 4-5 when presenting and sending Watchtower drafts.

## Selection prompt format (task 4)

```
[Knox]: Watchtower drafts ready to send to #content. Select which to post:

1. <Post Title> — <channels joined by comma>
2. <Post Title> — <channels joined by comma>
3. <Post Title> — <channels joined by comma>

Options:
  • Type numbers separated by commas (e.g., 1,3) to select specific drafts
  • Type "all" to send all listed drafts
  • Type "skip" to skip this step

Excluded by default (contains Abbott/Texas content — type "include-texas" to add it back):
  • <Post Title>
```

## Message format and send (task 5)

**Obsidian link construction:** The vault path line uses Slack's `<url|label>` link syntax. Build the URL as:
`obsidian://open?vault=Obsidian&file=<url-encoded path>`
where the path is the Obsidian-relative path (e.g. `Mind/Posts/_my-draft.md`) with spaces encoded as `%20` and no leading slash. Example:
`obsidian://open?vault=Obsidian&file=Mind%2FPosts%2F_my-draft.md`
Slack renders `<url|label>` as a clickable hyperlink. Use the raw path string as the label.

```
*Draft: [Post Title]*
_<obsidian://open?vault=Obsidian&file=[url-encoded obsidian_path]|[obsidian_path]> — [channels joined by comma]_

*Hook*
[hook text]

*Story Angle*
[story angle text]

*Core Insight*
[core insight text]

*Challenge / CTA*
[cta text]
```

Omit the `*Challenge / CTA*` block entirely if that section is empty or absent in the draft.

Locate `post.py` using the find-based path lookup:

```bash
IES_ROOT="$(find ~ -name 'SYSTEM.md' -path '*/IES/SYSTEM.md' 2>/dev/null | head -1 | sed 's|/SYSTEM.md||')"
python3 "$IES_ROOT/systems/slack-bot/post.py" C0B160MA3EK $'<message with real newlines>'
```

Use `mcp__Desktop_Commander__start_process` for execution. Timeout: 15000ms.
<!-- system:end -->
