#!/usr/bin/env python3
"""
Risk classifier for git commit paths (err-20261013T231457-A7IQVJ).

Deterministic, path-based classification of a changeset into:

  Class A (routine)   - session churn: memory/, data/, reviews/, meetings/,
                        decisions/, people/, delegations/, projects/, plus the
                        run-output carve-outs systems/eval-harness/runs/ and
                        systems/error-tracking/entries/ (run outputs, not
                        capability files), the tracked audit log
                        systems/eval-harness/git-ops.jsonl, and the session
                        index memory/sessions/index.json (via memory/).
                        Eligible for the `session-commit` fast lane.
  Class B (gated)     - workflows/, skills/, agents/, .claude/, and the rest
                        of systems/. Full ceremony: --ack-gated, standard
                        commit path, Ralph verification.
  Class C (push)      - remote operations; unchanged, full ceremony.

Structural rule: if ANY staged path is not Class A, the fast lane refuses.
Gated content cannot reach the fast lane.

Also implements the pre-flight pattern blocker for the fast lane: forbidden
artifact patterns and the media-deletion rule (never stage a deletion of
image/media files from Class A content folders).
"""

import re

# Class A content directories (session churn).
CLASS_A_PREFIXES = (
    "memory/",
    "data/",
    "reviews/",
    "meetings/",
    "decisions/",
    "people/",
    "delegations/",
    "projects/",
)

# systems/ is gated, EXCEPT these run-output paths, which are routine churn.
# The carve-out is checked BEFORE the gated list, so order in classify_path
# is load-bearing.
CLASS_A_SYSTEM_CARVEOUTS = (
    "systems/eval-harness/runs/",
    "systems/error-tracking/entries/",
)

# The tracked git-ops audit log is folded into the tree by `add`; it is
# routine churn even though it lives under a gated dir.
CLASS_A_EXACT = frozenset({
    "systems/eval-harness/git-ops.jsonl",
})

# Gated directories (Class B). systems/ minus the carve-outs above.
GATED_PREFIXES = (
    "workflows/",
    "skills/",
    "agents/",
    ".claude/",
    "systems/",
)

# Pre-flight forbidden patterns. Each entry: (compiled regex, human reason).
# Regexes match against the repo-relative path.
def _base(pat):
    return re.compile(r"(?:^|/)" + pat)

FORBIDDEN_PATTERNS = [
    (re.compile(r"^meetings/.*\.html$"), "meetings/**/*.html temp PDF build artifact"),
    (_base(re.escape(".DS_Store") + r"$"), ".DS_Store"),
    (_base(r"\.fuse_hidden"), "FUSE mount artifact (.fuse_hidden*)"),
    (_base(r"\.~lock\..*#$"), "Office lock file (.~lock.*#)"),
    (re.compile(r"^[^/]+\.(?:js|py|sh)$"), "stray temp script in repo root"),
    (re.compile(r"^meetings/.*\.(?:js|py|sh)$"), "stray temp script under meetings/"),
    (_base(r"__pycache__(?:/|$)"), "__pycache__ directory"),
]

# Media extensions covered by the screenshot/media rule: a staged DELETION
# of one of these from a Class A content folder is blocked and surfaced
# (feedback_dont_delete_screenshots).
MEDIA_EXTENSIONS = frozenset({
    ".png", ".jpg", ".jpeg", ".gif", ".heic", ".heif", ".webp",
    ".tiff", ".tif", ".bmp", ".svg",
    ".mp4", ".mov", ".m4v", ".avi",
    ".mp3", ".m4a", ".wav", ".aiff",
})


def classify_path(path):
    """Return "A", "B", or "other" for one repo-relative path."""
    if path in CLASS_A_EXACT:
        return "A"
    if path.startswith(CLASS_A_SYSTEM_CARVEOUTS):
        return "A"
    if path.startswith(CLASS_A_PREFIXES):
        return "A"
    if path.startswith(GATED_PREFIXES):
        return "B"
    return "other"


def classify_changeset(paths):
    """Return ("A", []) if every path is Class A, else ("refused", offenders)
    where offenders is a list of (path, class) for non-A paths. Any non-A
    path poisons the whole changeset for the fast lane."""
    offenders = [(p, classify_path(p)) for p in paths]
    bad = [(p, c) for p, c in offenders if c != "A"]
    if bad:
        return ("refused", bad)
    return ("A", [])


def preflight_blocks(paths):
    """Return a list of (path, reason) for candidate paths matching a
    forbidden artifact pattern. Empty list means clean."""
    hits = []
    for p in paths:
        for pat, reason in FORBIDDEN_PATTERNS:
            if pat.search(p):
                hits.append((p, reason))
                break
    return hits


def media_deletions(status_paths):
    """Given [(status, path), ...] (porcelain name-status letters), return
    deleted paths (status D) that are media files under Class A content
    folders. Those deletions are never staged by the fast lane."""
    out = []
    for status, p in status_paths:
        if status != "D":
            continue
        lower = p.lower()
        ext = "." + lower.rsplit(".", 1)[-1] if "." in lower else ""
        if ext in MEDIA_EXTENSIONS and classify_path(p) == "A":
            out.append(p)
    return out
