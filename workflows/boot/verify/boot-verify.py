#!/usr/bin/env python3
"""Consolidated boot verification: measurement + mechanical checks in one script.

Replaces the LLM-driven mechanics of the old step-02.5 (measure), step-03
(Ralph manifest verification), step-06.5 (guardrail review), and step-07
(completion gate). LLM judgment is now only needed when this script reports
anomalies; on a clean run boot pays zero model tokens for verification.

Subcommands:
    phase2      measure state size + verify phase-2 pull files exist, are
                fresh (<24h), non-empty, and carry a parseable status field
    completion  freshness + leakage scan + briefing currency + step frontmatter
                gate (the old 06.5 + 07 mechanics)

Exit code 0 = clean (proceed, no Ralph needed). Exit 1 = anomalies; the step
doc decides whether to spawn Ralph for judgment.

Usage:
    python3 workflows/boot/verify/boot-verify.py phase2
    python3 workflows/boot/verify/boot-verify.py completion
"""
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data"
STATE = ROOT / "workflows" / "boot" / "state.yaml"
STEPS = ROOT / "workflows" / "boot" / "steps"
MEASURE = ROOT / "systems" / "boot-instrumentation" / "measure.py"

PULL_FILES = [
    "email-unified.json",
    "omnifocus-unified.json",
    "clay-reminders-unified.json",
    "jarvis-inbox-unified.json",
    "ynab-unified.json",
    "calendar-unified.json",
]

PRIOR_STEPS = [
    "step-01-load-context",
    "step-01.2-unified-data-pull",
    "step-01.5-unified-calendar-pull",
    "step-02-gather-data",
    "step-03-verify-phase2",
    "step-04-gather-meeting-context",
    "step-05-synthesize-briefing",
    "step-06-scan-workflows",
]

CREDENTIAL_RE = re.compile(
    r"(sk-ant-[a-z0-9-]{20,}|fw_[A-Za-z0-9]{20,}|xox[bap]-[0-9A-Za-z-]{10,}|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----|password\s*[:=]\s*\S+)",
    re.IGNORECASE,
)


def now():
    return datetime.now(timezone.utc)


def file_age_hours(p):
    return (now().timestamp() - p.stat().st_mtime) / 3600


def check_pull_files():
    anomalies = []
    for name in PULL_FILES:
        p = DATA / name
        if not p.exists():
            anomalies.append(f"{name}: missing")
            continue
        if p.stat().st_size < 10:
            anomalies.append(f"{name}: effectively empty ({p.stat().st_size} bytes)")
            continue
        age = file_age_hours(p)
        if age > 24:
            anomalies.append(f"{name}: stale ({age:.0f}h old)")
        try:
            d = json.loads(p.read_text())
            if isinstance(d, dict) and "status" in d and d["status"] == "failed":
                anomalies.append(f"{name}: pull reported status=failed ({d.get('reason', 'no reason')})")
        except Exception as e:
            anomalies.append(f"{name}: unparseable JSON ({e})")
    return anomalies


def step_status(step_name):
    p = STEPS / f"{step_name}.md"
    if not p.exists():
        return None, None
    text = p.read_text()
    if not text.startswith("---"):
        return "no-frontmatter", None
    fm = text.split("---", 2)[1]
    status = re.search(r"^status:\s*(.+)$", fm, re.MULTILINE)
    completed = re.search(r"^completed-at:\s*(.+)$", fm, re.MULTILINE)
    return (status.group(1).strip().strip("'\"") if status else "missing",
            completed.group(1).strip().strip("'\"") if completed else None)


def cmd_phase2():
    anomalies = []
    # measurement (best-effort; old step-02.5)
    if MEASURE.exists():
        r = subprocess.run(
            ["python3", str(MEASURE), "measure-state", str(STATE)],
            capture_output=True, text=True, cwd=ROOT)
        out = (r.stdout or "").strip()
        if r.returncode == 0 and out:
            for line in out.splitlines()[:12]:
                print(f"  [measure] {line}")
        else:
            print(f"  [measure] failed (non-fatal): {(r.stderr or r.stdout)[:200]}")
    # manifest check (old step-03 mechanics)
    anomalies += check_pull_files()
    if anomalies:
        print("\nPHASE2 FLAGS:")
        for a in anomalies:
            print(f"  - {a}")
        print("\nAnomalies present: spawn Ralph for judgment on degraded sources.")
        return 1
    print("\nPHASE2 PASS: all pulls fresh, parseable, non-empty. Ralph not needed.")
    return 0


def cmd_completion():
    anomalies = []
    # freshness + briefing currency (old 06.5 mechanics)
    anomalies += check_pull_files()
    briefing_state = ROOT / "workflows" / "morning-briefing" / "state.yaml"
    if briefing_state.exists():
        txt = briefing_state.read_text()
        today = now().strftime("%Y-%m-%d")
        if today not in txt:
            anomalies.append("morning-briefing state.yaml has no entry dated today")
    # leakage scan (old 06.5)
    for p in [ROOT / "memory" / "sessions" / "index.json"]:
        if p.exists():
            m = CREDENTIAL_RE.search(p.read_text())
            if m:
                anomalies.append(f"credential-shaped string in {p.name}")
    # frontmatter gate (old 07)
    print(f"{'step':<40} {'status':<14} completed-at")
    failed = []
    for s in PRIOR_STEPS:
        status, completed = step_status(s)
        ok = status == "complete"
        if not ok:
            failed.append(s)
        print(f"{s:<40} {str(status):<14} {completed or ''}")
    if failed:
        anomalies.append("steps not complete: " + ", ".join(failed))
    if anomalies:
        print("\nCOMPLETION FLAGS:")
        for a in anomalies:
            print(f"  - {a}")
        return 1
    print("\nCOMPLETION PASS.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("phase2", "completion"):
        print(__doc__)
        sys.exit(2)
    sys.exit(cmd_phase2() if sys.argv[1] == "phase2" else cmd_completion())
