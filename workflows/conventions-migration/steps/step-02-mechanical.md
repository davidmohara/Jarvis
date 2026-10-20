---
status: complete
started-at: 2026-10-18
completed-at: 2026-10-18
---

<!-- system:start -->
# Step 02: Mechanical Fixes

Apply only the `mechanical` bucket, only these fix shapes:

| Finding | Fix |
|---|---|
| `skill.frontmatter` / `step.frontmatter` missing | Add well-formed frontmatter following a sibling file's pattern (fields: name, description for skills; status, started-at, completed-at for steps) |
| `skill.description` missing | Write one imperative sentence stating intent; surface to David only if intent is genuinely unclear |
| `skill.manifest_registration` | Append the entry to `skills/_manifest.jsonl` following the existing line shape; verify with `python3 skills/rigby-skill-audit/scripts/audit.py` section 2 |
| `script.interactive_input` | Replace `input()` with a required flag or env var, preserving behavior; if the interactivity is load-bearing, move the finding to `judgment` and flag it |
| `script.pep723_dependencies` | Add the PEP 723 block (`# /// script` + `dependencies = [...]`) naming the actual imports; verify with `uv run <script> --help` |
| `skill.evolution_blocks` / `agent.evolution_blocks` | Wrap existing content in `<!-- system:start -->` ... `<!-- system:end -->` without moving any text |

Rules: read each file before editing; one finding, one edit; re-lint the single file after each fix (`--target <path>`) and confirm the finding cleared. Batch related files, but never batch a fix shape you have not done before in this run.

Any finding that does not fit a fix shape exactly: move it to `judgment`. No improvisation in the mechanical pass.
<!-- system:end -->
