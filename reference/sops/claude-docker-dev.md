# Claude Code Docker Dev Environment

## Purpose
Run Claude Code with `--dangerously-skip-permissions` inside a Docker container so it can't touch anything outside the mounted project tree.

## Location
Files live in `~/develop/improving/devbox/`:
- `Dockerfile-claude` — Image definition (node:20-slim, pnpm, Claude CLI)
- `Makefile-claude` — Build/run/shell/claude commands

## Architecture
```
~/develop/improving/          ← mounted as /workspace
├── devbox/                   ← WORKDIR (Claude starts here)
├── ies/                      ← accessible via ../ies
└── (other improving projects)
```

## Quick Start
```bash
cd ~/develop/improving/devbox
export ANTHROPIC_API_KEY=sk-ant-...
make -f Makefile-claude build
make -f Makefile-claude run
make -f Makefile-claude claude    # launches Claude in dangerous mode
```

## Commands
| Command | What it does |
|---------|-------------|
| `make build` | Build the Docker image |
| `make run` | Start container (detached) |
| `make claude` | Launch Claude Code in dangerous mode |
| `make shell` | Bash shell into container |
| `make stop` | Stop and remove container |
| `make restart` | Stop + run |
| `make clean` | Remove container and image |
| `make status` | Show container status |

## Volume Mounts
- `~/develop/improving` → `/workspace` (project files)
- `~/.claude` → `/root/.claude` (settings, session history, API config)

## Security
- Blast radius limited to `~/develop/improving` — rest of system is untouched
- All git-tracked, so destructive changes are recoverable
- No `.env` secrets mounted (API key passed as env var)

## Source
Based on: https://www.ksred.com/claude-code-dangerously-skip-permissions-when-to-use-it-and-when-you-absolutely-shouldnt/

## Created
2026-02-27
