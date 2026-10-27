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
from datetime import datetime, timedelta, timezone
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

# Status gate, in true execution order.
PRIOR_STEPS = [
    "step-01-load-context",
    "step-01.5-unified-calendar-pull",
    "step-01.2-unified-data-pull",
    "step-02-gather-data",
    "step-03-verify-phase2",
    "step-04-gather-meeting-context",
    "step-05-synthesize-briefing",
    "step-06-scan-workflows",
]

# Timestamp-integrity gate, in true execution order.
STAMP_STEPS = [
    "step-01-load-context",
    "step-01.5-unified-calendar-pull",
    "step-01.2-unified-data-pull",
    "step-02-gather-data",
    "step-03-verify-phase2",
    "step-04-gather-meeting-context",
    "step-05-synthesize-briefing",
    "step-06-scan-workflows",
]

# A correctly stamped step writes completed-at at the same moment as the final
# Edit that produced it, so the stamp and the file mtime agree within seconds.
# 120s absorbs filesystem/clock jitter without admitting a fabricated stamp.
STAMP_TOLERANCE_SECONDS = 120

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


def step_started_at(step_name):
    p = STEPS / f"{step_name}.md"
    if not p.exists():
        return None
    text = p.read_text()
    if not text.startswith("---"):
        return None
    fm = text.split("---", 2)[1]
    m = re.search(r"^started-at:\s*(.+)$", fm, re.MULTILINE)
    return m.group(1).strip().strip("'\"") if m else None


def _parse_ts(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None


def check_step_stamps(current_time, record_completed=None):
    """Hard-fail fabricated step timestamps.

    The eval harness derives per-step attribution windows from step frontmatter;
    on the 2026-10-26 boot the later steps were stamped 23-27 minutes after the
    files were actually written, which collapsed per-step attribution and nulled
    steps 05-08. A stamp that is ahead of the write that
    produced it (the file mtime) cannot be real. Also rejects a stamp in the
    verifier's future and, when supplied, one later than the boot record's own
    completed timestamp.
    """
    anomalies = []
    for name in STAMP_STEPS:
        p = STEPS / f"{name}.md"
        if not p.exists():
            continue
        status, completed = step_status(name)
        if status != "complete":
            continue
        started = step_started_at(name)
        started_dt = _parse_ts(started)
        completed_dt = _parse_ts(completed)
        if completed_dt is None:
            anomalies.append(f"{name}: status complete but completed-at missing/unparseable")
            continue
        if started_dt is not None and completed_dt < started_dt:
            anomalies.append(
                f"{name}: completed-at {completed} is before started-at {started}")
        if completed_dt.hour == 0 and completed_dt.minute == 0 and completed_dt.second == 0:
            anomalies.append(
                f"{name}: completed-at {completed} is an exact-midnight placeholder, "
                f"not a real clock reading")
        if completed_dt > current_time + timedelta(seconds=STAMP_TOLERANCE_SECONDS):
            anomalies.append(
                f"{name}: completed-at {completed} is later than the verifier clock "
                f"({current_time.strftime('%Y-%m-%dT%H:%M:%SZ')}) — fabricated future stamp")
        mtime = datetime.fromtimestamp(p.stat().st_mtime, timezone.utc)
        if completed_dt > mtime + timedelta(seconds=STAMP_TOLERANCE_SECONDS):
            delta = int((completed_dt - mtime).total_seconds())
            anomalies.append(
                f"{name}: completed-at {completed} is {delta}s later than the file was "
                f"actually written ({mtime.strftime('%Y-%m-%dT%H:%M:%SZ')}) — fabricated stamp")
        if record_completed is not None and completed_dt > record_completed + timedelta(
                seconds=STAMP_TOLERANCE_SECONDS):
            anomalies.append(
                f"{name}: completed-at {completed} is later than the boot record's "
                f"completed {record_completed.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    return anomalies


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


def cmd_completion(record_completed=None):
    anomalies = []
    # freshness + briefing currency (old 06.5 mechanics)
    anomalies += check_pull_files()
    # timestamp integrity (2026-10-26 fix): fabricated stamps collapse
    # per-step attribution, so they are a hard error, not a warning.
    anomalies += check_step_stamps(now(), record_completed)
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
    import argparse
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["phase2", "completion"])
    ap.add_argument(
        "--record-completed", default=None,
        help="ISO-8601 completion timestamp of the boot record. Any step stamped "
             "later than this (beyond 120s) is a hard error. Optional; the mtime "
             "check already catches fabricated future stamps.")
    args = ap.parse_args()
    record_completed = _parse_ts(args.record_completed)
    if args.command == "phase2":
        sys.exit(cmd_phase2())
    sys.exit(cmd_completion(record_completed))
