#!/usr/bin/env python3
"""Ground-truth verifier for shutdown-cleanup/step-04-commit.

Re-derives the commit claim from the record instead of trusting the step's
self-report: the claimed commit sha must exist, its file list must contain
no temp-artifact patterns, and the wrapper's audit log
(systems/eval-harness/git-ops.jsonl) must show the commit ran through the
authorized path. Read-only git (`git show`); `git status` is never used.
"""

import json
import subprocess
import sys
from pathlib import Path

STEP = Path(__file__).resolve().parents[1] / "steps" / "step-04-commit.md"
AUDIT_LOG = Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "git-ops.jsonl"

TEMP_NAME_MARKERS = (".DS_Store", ".fuse_hidden", "__pycache__", ".tmp", ".pyc")


def main():
    validation_errors = []
    fields = {}

    # claimed sha from step frontmatter outputs
    import re
    fm = STEP.read_text()
    m = re.search(r'commit_sha:\s*"?([0-9a-f]{7,40})"?', fm)
    sha = m.group(1) if m else None
    fields["claimed_commit_sha"] = sha

    if not sha:
        print(json.dumps({
            "result": "retry",
            "reason": "step-04 frontmatter records no commit_sha: the commit step must complete and record its sha",
            "fields": fields,
            "validation_errors": ["commit_sha_not_recorded"],
            "retry_instruction": "Complete step-04 through the ies-git wrapper and record the resulting sha in the step frontmatter outputs.",
        }))
        return

    show = subprocess.run(["git", "show", "--name-only", "--pretty=format:", sha],
                         capture_output=True, text=True)
    if show.returncode != 0:
        print(json.dumps({
            "result": "retry",
            "reason": f"claimed commit sha {sha} does not resolve: {show.stderr.strip()[:200]}",
            "fields": fields,
            "validation_errors": ["commit_sha_unresolvable"],
            "retry_instruction": "Re-run the commit through the wrapper and record the actual sha.",
        }))
        return

    files = [l.strip() for l in show.stdout.splitlines() if l.strip()]
    temp_in_commit = [f for f in files if any(mk in f for mk in TEMP_NAME_MARKERS)]
    fields["files_in_commit"] = len(files)
    fields["temp_artifacts_in_commit"] = temp_in_commit

    # audit trail: the commit must have a wrapper entry (executed, not refused)
    # within the step's own execution window. Any-executed-entry matching is too
    # loose: a stale sha would ride an unrelated session's audit entry.
    from datetime import datetime, timedelta
    import re as _re

    def _fm_time(key):
        m = _re.search(rf'^{key}:\s*"?([^"\n~]+)"?', fm, _re.M)
        if not m:
            return None
        try:
            return datetime.fromisoformat(m.group(1).strip().replace("Z", "+00:00"))
        except ValueError:
            return None

    win_start = _fm_time("started-at")
    win_end = _fm_time("completed-at")
    if win_end is not None:
        win_end = win_end + timedelta(seconds=600)  # audit appends land seconds after git
    audited = False
    if AUDIT_LOG.exists():
        for line in AUDIT_LOG.read_text().splitlines():
            try:
                e = json.loads(line)
            except Exception:
                continue
            if e.get("verb") != "commit" or e.get("refused") or str(e.get("exit_code")) != "0":
                continue
            ts = None
            try:
                ts = datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00"))
            except Exception:
                pass
            in_window = True
            if win_start is not None and ts is not None and ts < win_start:
                in_window = False
            if win_end is not None and ts is not None and ts > win_end:
                in_window = False  # a stale step cannot ride a later session's audit entry
            if in_window:
                audited = True
                break
    fields["commit_audited_via_wrapper"] = audited
    fields["audit_window"] = f"{win_start} .. {win_end}" if win_start else None

    if temp_in_commit:
        validation_errors.append("temp_artifacts_committed")
    if not audited:
        validation_errors.append("commit_not_audited_via_wrapper")

    if validation_errors:
        reasons = []
        if temp_in_commit:
            reasons.append(f"{len(temp_in_commit)} temp artifact(s) committed")
        if not audited:
            reasons.append("no executed commit entry in git-ops.jsonl (the commit bypassed the wrapper or the audit log is missing)")
        print(json.dumps({
            "result": "retry",
            "reason": "; ".join(reasons),
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Fix per the validation errors: unstage temp artifacts, commit through python3 skills/git/scripts/ies-git, and surface audit gaps to the controller.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"commit {sha[:7]} verified: {len(files)} file(s), no temp artifacts, executed through the wrapper per git-ops.jsonl",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()
