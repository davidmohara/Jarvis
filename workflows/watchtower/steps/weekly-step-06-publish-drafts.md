---
status: complete
started-at: "2026-08-10T17:26:00Z"
completed-at: "2026-08-10T17:35:00Z"
outputs:
  drafts_sent:
    - Mind/Posts/_your-agents-have-keys-nobody-changed-the-locks.md
    - Mind/Posts/_the-service-line-is-not-the-delivery-model.md
  drafts_skipped: []
  channel: C0B160MA3EK
  step_skipped: false
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` to this file's frontmatter before doing anything else.
2. **Read `.claude/skills/master-slack/SKILL.md` before sending anything to Slack.** No exceptions. The No-Duplicate Rule, newline handling, and path-lookup pattern are all defined there and must be followed exactly.
3. **Never read vault files from filesystem paths.** Always use `mcp__obsidian-local__get_vault_file` to fetch draft content. This is mandatory — it catches any edits David has made since Knox created the files.
4. The Abbott/Texas draft is excluded from the default selection list. Identify it by checking whether its slug contains "abbott" or "texas". Present it in the exclusion note but do not pre-select it.
5. **No-Duplicate Rule is absolute.** After each send, wait at least 10 seconds, then read the channel via `read.py` to confirm delivery before proceeding. Only retry if `read.py` confirms the message is absent AND the original process returned an explicit error. One retry maximum per draft.
6. Multi-line messages must use actual newlines — never literal `\n`. Use single-quote wrapping (outer `'...'`) for the message string passed to `post.py`.
7. **Smart quote sanitization — mandatory before composing any message.** Draft content from Obsidian frequently contains curly/smart quotes that break shell quoting. Before building the message string, replace: `"` → `"`, `"` → `"`, `'` → `'`, `'` → `'`. Also replace em-dashes (`—`) with ` - ` and en-dashes (`–`) with `-`. The safest approach: pipe the message through a Python one-liner to do the substitution before passing to `post.py`:
   ```bash
   python3 -c "
   import sys
   msg = open('/tmp/draft_msg.txt').read()
   msg = msg.replace('“','\"').replace('”','\"').replace('‘',\"'\").replace('’',\"'\").replace('—',' - ').replace('–','-')
   sys.stdout.write(msg)
   " | python3 "$IES_ROOT/systems/slack-bot/post.py" C0B160MA3EK "$(cat)"
   ```
   Or write the sanitized message to a temp file and pass it as a shell variable. Either way — **sanitize before send, no exceptions.**
8. This step is **optional**. If David types "skip" at the selection prompt, set `status: skipped` and `outputs.step_skipped: true`. Do not send anything.
9. Write `status: complete` (or `skipped`), `completed-at`, and `outputs` when done.

---

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Knox |
| Model | sonnet |
| Input | Step-02 `outputs.draft_paths` (Obsidian paths); vault file content via Obsidian MCP; David's selection |
| Output | Draft posts sent to Slack `#content` (`C0B160MA3EK`); `drafts_sent` and `drafts_skipped` lists written to outputs |

---

## CONTEXT BOUNDARIES

- Scope: present draft selection, send approved drafts to `#content`, verify delivery.
- This step does NOT edit draft files, does NOT publish to any external platform, and does NOT alter `state.yaml` content beyond what is documented here.
- Channel `#content` (`C0B160MA3EK`) is the only authorized destination for this step.
- Knox executes this step directly. No sub-agent spawn.

---

## YOUR TASK

### 1. Read the skill

Read `.claude/skills/master-slack/SKILL.md` in full before proceeding. Internalize:
- Path-lookup pattern (find-based, not mdfind)
- No-Duplicate Rule and verification sequence
- Newline handling (`$'...'` ANSI-C quoting or real multi-line strings)
- Max 5000 chars per message

### 2. Collect draft paths

Read `draft_paths` from `workflows/watchtower/steps/weekly-step-02-draft-angles.md` frontmatter `outputs` section.

If `draft_paths` is empty or absent, surface: "[Knox]: No draft paths found in step-02 outputs. Nothing to send." Set `outputs.step_skipped: true`, set `status: complete`, and stop.

### 3. Read each draft from Obsidian

For each path in `draft_paths`, call `mcp__obsidian-local__get_vault_file` with the Obsidian path. Collect:
- File frontmatter: `channels`, `topic`
- Section content: `# <Post Title>`, `## Hook`, `## Story Angle`, `## Core Insight`, `## Challenge / CTA`

If a file cannot be read, log it to `drafts_skipped` with reason `vault_read_failed` and continue.

### 4. Present the selection prompt

Build a numbered list of available drafts. Apply the exclusion rule: if a draft's slug contains "abbott" or "texas", omit it from the numbered list and note it separately.

Present to David:

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

Wait for David's response.

If David types "skip": set `outputs.step_skipped: true`, write `status: skipped`, `completed-at`, and stop.

If David types "include-texas": add the excluded draft(s) back to the selection pool, re-present the full list, and wait again.

### 5. Send each selected draft to #content

For each selected draft, compose the Slack message using this exact format.

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
IES_ROOT="$(find ~ -name 'SYSTEM.md' -path '*/jarvis/SYSTEM.md' 2>/dev/null | head -1 | sed 's|/SYSTEM.md||')"
python3 "$IES_ROOT/systems/slack-bot/post.py" C0B160MA3EK $'<message with real newlines>'
```

Use `mcp__Desktop_Commander__start_process` for execution. Timeout: 15000ms.

### 6. Verify delivery — No-Duplicate Rule

After each send:

1. Wait at least 10 seconds.
2. Read `#content` via `read.py`:
   ```bash
   IES_ROOT="$(find ~ -name 'SYSTEM.md' -path '*/jarvis/SYSTEM.md' 2>/dev/null | head -1 | sed 's|/SYSTEM.md||')"
   python3 "$IES_ROOT/systems/slack-bot/read.py" channel C0B160MA3EK 0.1
   ```
3. If the message appears in the response — done. Add the draft to `drafts_sent`. Do NOT retry.
4. Only retry if `read.py` confirms the message is absent AND the original process returned an explicit error. One retry maximum.
5. If retry also fails, add the draft to `drafts_skipped` with reason `send_failed`, log the error, and surface the content in session output so David still has it.

Repeat for each selected draft. Send them sequentially — wait for verification before sending the next.

### 7. Write outputs

Write to this file's frontmatter:

```yaml
outputs:
  drafts_sent: []       # list of Obsidian paths successfully delivered
  drafts_skipped: []    # list of {path, reason} objects
  channel: C0B160MA3EK
  step_skipped: false   # true if David typed "skip"
```

---

## SUCCESS METRICS

- David was presented with a numbered draft list before anything was sent.
- Abbott/Texas draft excluded from default selection.
- Each selected draft delivered to `#content` and confirmed via `read.py` — confirmation is required; a send with no `read.py` verification does not count as delivered.
- No duplicate sends — No-Duplicate Rule honored for every draft.
- `drafts_sent` and `drafts_skipped` accurately reflect what happened.
- Step marked `skipped` cleanly if David opted out.
- Every message sent contains zero curly/smart quote characters (`"`, `"`, `'`, `'`) — verify by scanning the composed message string before calling `post.py`; if any are found, sanitize first.
- Vault path line in each message contains a valid `obsidian://open?vault=Obsidian&file=` URI — plain text paths are a failure.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `draft_paths` empty or absent in step-02 outputs | Surface note, set `step_skipped: true`, mark complete, stop |
| Vault read fails for a draft | Log to `drafts_skipped` with `vault_read_failed`; continue with remaining drafts |
| Desktop Commander unavailable | Log `send_failed` for all selected drafts; surface each draft's content in session output; mark complete |
| `read.py` confirms no delivery + original error | Retry once. If retry fails, log `send_failed`, surface content in session, continue |
| Message exceeds 5000 chars | Split into two sends: first send the header + Hook + Story Angle; second send Core Insight + CTA. Both are verified. |
| David selects no valid numbers | Prompt again once: "No valid selection — enter numbers, 'all', or 'skip'." |

---

## NEXT STEP

End of weekly run. This is the final optional step. Daily run resumes Tuesday.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
