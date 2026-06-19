---
id: git
name: Git Operations
owning_agent: rigby
model: haiku
context: inline
trigger_keywords:
  - git
  - commit
  - push
  - pull
  - branch
  - merge
  - rebase
  - stage
  - stash
  - checkout
  - cherry-pick
  - PR
  - pull request
  - diff
  - status
  - log
  - reset
  - amend
  - origin
  - remote
---

<!-- system:start -->
# Git Operations Skill

**This skill is the only authorized path for all git operations in Jarvis.** Read it before executing any git command — commit, push, branch, merge, or PR creation. No exceptions.
<!-- system:end -->

<!-- personal:start -->
## Jurisdiction

This skill governs all git operations in the repository. It applies to every agent. When any agent needs to touch git, it uses this skill.
<!-- personal:end -->

---

## Pre-Flight Gate

Before any git operation, answer these questions:

1. **Are there files in gated directories?** (`workflows/`, `skills/`, `agents/`, `systems/`, `.claude/skills/`)  
   → If yes and Rigby did NOT build them: **STOP. Do not commit. Route to Rigby.**  
   → If Rigby built them this session: proceed.

2. **Are there credentials, API keys, or secrets in any staged file?**  
   → If yes: **STOP. Do not commit. Surface to David immediately.**

3. **Are there intermediate/temp artifacts that should be purged first?**  
   → See SYSTEM.md Shutdown Cleanup Protocol. Purge before staging.

---

## Atomic Command Rule

**Every git command is a separate, individual tool call. No exceptions.**

Never use `&&`, `||`, `;`, pipes, or multi-line bash scripts to chain git commands. Chaining prevents git from releasing its lock files between operations, which produces `index.lock` and `HEAD.lock` errors that block all further git use until manually cleared.

✅ Correct — one command per call:
```
Call 1: git status
Call 2: git add -A
Call 3: git commit -m "feat(rigby): add git skill"
Call 4: git push origin main
```

❌ Wrong — chained in one call:
```bash
git add -A && git commit -m "feat(rigby): add git skill" && git push origin main
```

Wait for each call to return a result before issuing the next.

---

## Commit Convention: Conventional Commits

All commits use the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

| Type | When to Use |
|------|-------------|
| `feat` | New skill, workflow, agent, capability, or identity file addition |
| `fix` | Correcting broken behavior, wrong data, bad logic in an existing file |
| `chore` | Routine maintenance — manifest updates, purging temp files, gitignore |
| `docs` | Pure documentation changes (no logic change) |
| `refactor` | Restructuring without changing behavior |
| `perf` | Performance improvement to a skill or workflow |
| `test` | Adding or updating eval records, assertion files |
| `revert` | Reverting a previous commit |

### Scope (optional but recommended)

Use the agent or subsystem name: `master`, `chief`, `chase`, `quinn`, `shep`, `harper`, `rigby`, `knox`, `sterling`, `galen`, `memory`, `identity`, `system`, `eval`.

### Examples

```
feat(rigby): add git operations skill with Conventional Commits enforcement
fix(chief): correct UTC-to-CT conversion in morning briefing
chore: purge temp HTML artifacts and update gitignore
docs(identity): update GOALS_AND_DREAMS with Q3 rocks
refactor(chase): consolidate call-prep and meeting-prep into single skill
```

### Rules

- **Description**: imperative mood, lowercase, no period at end. "add skill" not "Added skill" or "Adds skill."
- **Scope**: lowercase, no spaces.
- **Body**: use when the why isn't obvious from the subject. Wrap at 72 characters.
- **Breaking changes**: add `BREAKING CHANGE:` footer or `!` after type: `feat!(master): restructure agent routing`.
- **Multi-topic commits**: if changes span unrelated concerns, split into separate commits.
- **Session-end commits**: when committing the shutdown cleanup batch, use `chore: session cleanup — purge artifacts, organize deliverables` as the default message. Adjust if meaningful work is included.

---

## Staging Rules

### Stage these
- All new and modified files that belong to the session's work
- `.gitignore` updates
- Files moved/renamed as part of cleanup

### Never stage these
- `**/*.html` inside `meetings/` (temp PDF build artifacts)
- `**/.DS_Store`
- `**/.fuse_hidden*`
- Root-level one-off scripts (`*.py`, `*.js`, `*.sh`) created during session
- Any file containing credentials, tokens, or secrets

### How to stage

**Run each command as a separate, atomic call. Never chain commands with `&&`, `|`, `;`, or multi-line scripts.** Chaining causes `index.lock` and `HEAD.lock` files that block subsequent operations and require manual cleanup.

```bash
# Step 1 — check status (separate call)
git status

# Step 2 — stage specific files (preferred for precision; separate call per file or group)
git add path/to/file

# OR stage all tracked changes (separate call)
git add -A

# Step 3 — review staged changes (separate call)
git diff --staged
```

Wait for each command to return before issuing the next.

---

## Push & Remote Operations

### Rules

- **Never force push to `main`** under any circumstances.
- Force push (`--force-with-lease`) is allowed on personal feature branches only, and only when David explicitly requests it.
- Always verify the current branch before pushing: `git branch --show-current`.
- Default remote is `origin`. Confirm with `git remote -v` if uncertain.

### Standard push

Issue as a single atomic command — no chaining:

```bash
git push origin <branch>
```

### Push new branch

```bash
git push -u origin <branch>
```

---

## Branch Management

### Naming convention

```
<type>/<scope>-<short-description>
```

Examples:
- `feat/rigby-git-skill`
- `fix/chief-utc-conversion`
- `chore/session-cleanup-2026-06-19`

### Rules

- Branch from `main` unless continuing in-progress work.
- Delete merged branches after PR close: `git branch -d <branch>`.
- Never work directly on `main` for capability builds — always branch.
- For session-end cleanup commits: committing directly to `main` is acceptable since these are maintenance operations, not capability changes.

---

## Merge & Rebase

### Merging

- Merge PRs via GitHub (not local merge) whenever possible — preserves history.
- Local merge allowed for: pulling `main` into a feature branch to resolve conflicts.
- Always use `--no-ff` for feature merges if doing locally: `git merge --no-ff <branch>`.
- **Never merge directly to `main` locally** without David's explicit instruction.

### Rebasing

- Rebase is allowed for cleaning up local commits before pushing.
- **Never rebase commits that have been pushed to a shared remote.**
- Interactive rebase (`git rebase -i`) is allowed for squashing WIP commits before a PR.

---

## Pull Request Creation

Use the GitHub MCP (`mcp__51a62735-b1fd-4e98-ac1e-92e5535bf997__create_pr`) for PR creation.

### PR title format

Follow Conventional Commits: `feat(scope): description`

### PR body template

```markdown
## What

[What this PR does — one paragraph]

## Why

[Why this change was needed]

## Changes

- file/path — what changed and why
- file/path — what changed and why

## Testing

[How this was verified, or "N/A — documentation only"]
```

### PR rules

- One logical concern per PR.
- Link to relevant decision files or workflow docs in the body if applicable.
- Assign to David unless he instructs otherwise.
- Do not merge your own PR without David's approval.

---

## Session-End Commit Protocol

**Every command is a separate, atomic call. Do not chain. Wait for each to return before issuing the next.**

```
Call 1:  git status
         → review output; identify what to stage and what to purge

Call 2:  [delete temp artifacts individually via Desktop Commander]
         → meetings/**/*.html, .DS_Store, .fuse_hidden*, root scripts

Call 3:  git add -A
         → stage all remaining files

Call 4:  git diff --staged
         → verify staged content looks correct before committing

Call 5:  git commit -m "chore: session cleanup — <brief summary of session work>"
         → commits staged files

Call 6:  git push origin main
         → pushes to remote
```

If the session produced meaningful capability work, use a descriptive type in Call 5:

```
git commit -m "feat(rigby): <what was built>"
```

or for mixed sessions:

```
git commit -m "feat(rigby): add git skill

Includes session cleanup."
```

---

## Error Handling

| Situation | Response |
|-----------|----------|
| Merge conflict | Surface to David. Do not auto-resolve. Show the conflicting sections. |
| Push rejected (non-fast-forward) | Pull first (`git pull --rebase origin main`), resolve conflicts, then push. |
| Accidentally staged a secret | `git reset HEAD <file>` immediately. Add to `.gitignore`. Report to David. |
| Wrong commit message | `git commit --amend` if not yet pushed. If pushed, leave it and note the error. |
| Detached HEAD | `git checkout main` or create a branch: `git checkout -b <branch>`. |
