#!/usr/bin/env python3
"""Ground-truth verifier for shutdown-cleanup/step-01-purge-artifacts.

Re-scans the actual filesystem for the known temp-artifact patterns the
step is supposed to have deleted, and re-runs the IES root-check against
the canonical allowlist, instead of trusting the model's purge_results
self-report.
"""

import json
import sys
from pathlib import Path

CANONICAL_ROOT_ENTRIES = {
    "CLAUDE.md", "SETUP.md", "SYSTEM.md", "evolution.manifest.json",
    "accounts", "agents", "archive", "briefs", "config", "contacts",
    "context", "contributions", "data", "decisions", "delegations",
    "evolutions", "hooks", "identity", "logs", "meetings", "memory",
    "people", "podcast", "presentations", "projects", "proposals",
    "reference", "reports", "reviews", "scripts", "skills", "specs",
    "systems", "tasks", "Talks", "training", "workflows", "Remarkable",
    "YPO", "content",
}

# Hidden/tool-cache entries that are expected but not part of the
# canonical allowlist (git internals, editor/tool caches).
EXPECTED_HIDDEN = {".git", ".claude", ".playwright-mcp", ".gitignore", ".DS_Store"}

TEMP_GLOBS = [
    "**/.DS_Store",
    "**/.fuse_hidden*",
    "**/__pycache__",
    "**/*.tmp",
    "meetings/**/*.html",
]


def find_temp_artifacts(ies_root: Path) -> list:
    found = []
    for pattern in TEMP_GLOBS:
        for p in ies_root.glob(pattern):
            if ".git" in p.parts:
                continue
            found.append(str(p.relative_to(ies_root)))
    return found


def find_root_scripts(ies_root: Path) -> list:
    found = []
    for ext in ("*.js", "*.py", "*.sh"):
        for p in ies_root.glob(ext):
            found.append(p.name)
    return found


def find_noncanonical_root_entries(ies_root: Path) -> list:
    flagged = []
    for entry in ies_root.iterdir():
        name = entry.name
        if name in CANONICAL_ROOT_ENTRIES:
            continue
        if name.startswith(".") and name in EXPECTED_HIDDEN:
            continue
        if name.startswith(".") and name not in EXPECTED_HIDDEN:
            # Unknown hidden entry — still flag it, root-check is strict.
            flagged.append(name)
            continue
        flagged.append(name)
    return sorted(flagged)


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    if not ies_root.is_dir():
        print(json.dumps({
            "result": "retry",
            "reason": f"ies_root does not exist: {ies_root}",
            "fields": {},
            "validation_errors": ["ies_root_missing"],
            "retry_instruction": "Confirm the IES root path resolves correctly before re-running purge.",
        }))
        return

    temp_artifacts = find_temp_artifacts(ies_root)
    root_scripts = find_root_scripts(ies_root)
    noncanonical = find_noncanonical_root_entries(ies_root)

    validation_errors = []
    if temp_artifacts:
        validation_errors.append(f"temp_artifacts_remaining: {len(temp_artifacts)}")
    if root_scripts:
        validation_errors.append(f"root_scripts_remaining: {len(root_scripts)}")
    if noncanonical:
        validation_errors.append(f"noncanonical_root_entries: {noncanonical}")

    fields = {
        "temp_artifacts_remaining": temp_artifacts[:20],
        "temp_artifacts_count": len(temp_artifacts),
        "root_scripts_remaining": root_scripts,
        "noncanonical_root_entries": noncanonical,
    }

    if temp_artifacts or root_scripts or noncanonical:
        print(json.dumps({
            "result": "retry",
            "reason": f"Purge incomplete: {len(temp_artifacts)} temp artifact(s), {len(root_scripts)} root script(s), {len(noncanonical)} non-canonical root entr(y/ies) remain",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Delete the remaining temp artifacts and root-level scripts listed in fields, and move or delete any non-canonical root entries before proceeding.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": "No temp artifacts, root scripts, or non-canonical root entries found — workspace is clean",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()
