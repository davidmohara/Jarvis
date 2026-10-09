#!/usr/bin/env python3
"""Ground-truth verifier for dream-cycle/step-05-logging.

Log-and-finalize check. The step claims it appended a dream.log entry
(`dream_log_appended`), and committed/pushed (`git_commit`, `git_push`,
`git_commit_sha`). This verifier re-derives the claim from the real files
rather than trusting the frontmatter self-report:

  * memory/dream.log must exist and its most recent `## YYYY-MM-DD` header
    must match the run date (the date portion of this step's completed-at /
    started-at) - a claimed append that isn't in the log is a false report;
  * the last log entry must carry a `session_id:` line;
  * if `git_commit` is true, `git_commit_sha` must be recorded.

Verdict: retry on a missing/mismatched log entry; pass otherwise. `git_push`
false is recorded as a note, not a failure (the step's own rule: the run
completed even if the push is pending).
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

STEP_REL = Path("workflows") / "dream-cycle" / "steps" / "step-05-logging.md"
DATE_RE = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})", re.MULTILINE)


def extract_frontmatter(content: str) -> dict:
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    fm_lines = []
    in_fm = False
    for line in lines:
        if line.strip() == "---":
            in_fm = not in_fm
            if not in_fm:
                break
            continue
        if in_fm:
            fm_lines.append(line)
    try:
        return yaml.safe_load("\n".join(fm_lines)) or {}
    except Exception:
        return {}


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    step_path = ies_root / STEP_REL
    if yaml is None or not step_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "step-05-logging.md not found or YAML parser unavailable",
            "fields": {"log_verified": False},
            "validation_errors": ["step_file_missing"],
            "retry_instruction": "Confirm workflows/dream-cycle/steps/step-05-logging.md exists.",
        }))
        return

    fm = extract_frontmatter(step_path.read_text())
    outputs = fm.get("outputs") or {}
    if not isinstance(outputs, dict) or not outputs:
        print(json.dumps({
            "result": "retry",
            "reason": "step-05 outputs block is empty - no log/git results recorded",
            "fields": {"log_verified": False},
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Re-execute step-05 and record dream_log_appended/git_commit/git_commit_sha in the step frontmatter outputs.",
        }))
        return

    # Derive the run date from the step's own timestamps.
    run_date = None
    for key in ("completed-at", "started-at"):
        value = fm.get(key)
        if isinstance(value, str) and len(value) >= 10:
            run_date = value[:10]
            break

    log_path = ies_root / "memory" / "dream.log"
    last_log_date = None
    last_entry_has_session = False
    if log_path.is_file():
        text = log_path.read_text(encoding="utf-8", errors="replace")
        headers = DATE_RE.findall(text)
        if headers:
            last_log_date = headers[-1]
        # Inspect the tail block after the final header for a session_id line.
        idx = text.rfind("## ")
        if idx != -1:
            last_entry_has_session = "session_id:" in text[idx:]

    fields = {
        "run_date": run_date,
        "dream_log_exists": log_path.is_file(),
        "dream_log_last_date": last_log_date,
        "last_entry_has_session_id": last_entry_has_session,
        "dream_log_appended_reported": outputs.get("dream_log_appended"),
        "git_commit_reported": outputs.get("git_commit"),
        "git_push_reported": outputs.get("git_push"),
        "git_commit_sha": outputs.get("git_commit_sha"),
    }

    if not log_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "memory/dream.log does not exist - the mandatory log append is missing",
            "fields": fields,
            "validation_errors": ["dream_log_missing"],
            "retry_instruction": "Re-execute step-05; the dream log is the run's audit trail and must be written.",
        }))
        return

    if run_date and last_log_date and last_log_date != run_date:
        print(json.dumps({
            "result": "retry",
            "reason": f"dream.log's most recent entry is dated {last_log_date}, not the run date {run_date} - the claimed append is not present",
            "fields": fields,
            "validation_errors": ["log_date_mismatch"],
            "retry_instruction": "Re-execute step-05's dream.log append for the current run date.",
        }))
        return

    if not last_entry_has_session:
        print(json.dumps({
            "result": "retry",
            "reason": "the most recent dream.log entry has no session_id line - the entry is malformed",
            "fields": fields,
            "validation_errors": ["log_entry_malformed"],
            "retry_instruction": "Re-append the dream.log entry with all required fields including session_id.",
        }))
        return

    if outputs.get("git_commit") is True and not outputs.get("git_commit_sha"):
        print(json.dumps({
            "result": "retry",
            "reason": "git_commit is true but no git_commit_sha was recorded",
            "fields": fields,
            "validation_errors": ["commit_sha_missing"],
            "retry_instruction": "Record the commit sha in step-05 outputs, or correct git_commit to false.",
        }))
        return

    note = "" if outputs.get("git_push") is True else " (note: push not confirmed)"
    print(json.dumps({
        "result": "pass",
        "reason": f"step-05 log entry verified for {run_date}; session_id present{note}",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()
