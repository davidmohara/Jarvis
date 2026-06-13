---
name: peekaboo
owning_agent: rigby
description: "macOS screenshots, UI inspection, clicks, typing, and app/window automation via the Peekaboo CLI."
model: sonnet
trigger_keywords: [screenshot, screen capture, UI inspect, click, type, window automation, peekaboo]
trigger_agents: [rigby, chief]
---

<!-- system:start -->
## Trigger Phrases

- "take a screenshot", "capture the screen", "screenshot of", "peekaboo"
- "inspect the UI", "click on", "automate the window", "what's on screen"
- Invoked when any agent needs visual confirmation of on-screen state or GUI automation

## Binary

Use `peekaboo` from PATH directly. Confirm availability before proceeding:

```bash
peekaboo --version
```

If not found, report the missing install — do not proceed.

## Safety

- Check permissions before any capture or automation: `peekaboo permissions status --json`
- Screenshot requires Screen Recording permission; clicks, typing, and window control require Accessibility.
- On remote Macs, Screen Recording may be blocked while Accessibility still works — fall back to clicks or DOM automation when the target is otherwise knowable.
- Prefer `--json` for machine parsing and `--no-remote` when testing local TCC.
- Do not click, type, or destructively automate unless David explicitly requested it or the target is a controlled test environment.

## Common Commands

```bash
peekaboo permissions status --json
peekaboo list screens --json
peekaboo list apps --json
peekaboo list windows --app Safari --json
peekaboo image --mode screen --screen-index 0 --path /tmp/screen.png --json --no-remote
peekaboo see --app frontmost --path /tmp/frontmost.png --json --annotate
peekaboo tools --json
peekaboo learn
peekaboo click --coords 100,100 --json
peekaboo type "text" --json
```

## Workflow

1. Confirm `peekaboo` is available via `peekaboo --version`.
2. Run `permissions status --json`. If TCC grants are missing, report the exact missing permission — do not attempt the blocked operation.
3. For screenshots, use `image`; include `--path`, `--json`, and `--no-remote`.
4. For element targeting, run `see --json --annotate`, then click by element ID or snapshot reference.
5. For long-running or change-aware capture, use `capture live`; for video frame sampling, use `capture video`.
6. Use `tools --json` for command and tool discovery; use `learn` when the full agent guide is needed.
7. Verify output files with `sips -g pixelWidth -g pixelHeight <path>` or render the image inline.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
