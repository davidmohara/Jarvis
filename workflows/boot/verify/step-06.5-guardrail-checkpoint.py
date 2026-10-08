#!/usr/bin/env python3
"""Ground-truth verifier for boot/step-06.5-guardrail-checkpoint.

Stage 5 Phase 4A: this checkpoint used to be a manual review whose result was
only self-reported. It is now machine-checked. The verifier re-derives, from
files on disk (never from the step's own summary):

  * stale_sources        - data/*.json older than STALE_THRESHOLD_HOURS
  * briefing_current     - workflows/morning-briefing/state.yaml exists and its
                           last-run date matches the run date (catches a briefing
                           synthesized on top of a wrong-day/stale briefing state)
  * checkpoint_recorded  - a "pre-completion-review" entry exists in this run's
                           boot eval record guardrails array, proving
                           guardrail-checkpoint.py actually ran (not just claimed)
  * leakage_hits         - credential-shaped strings in the session index or the
                           briefing content

Verdict:
  * retry  - this run's boot eval record exists but the checkpoint was NOT
             recorded (guardrail-checkpoint.py did not run or did not attach).
             The checkpoint must execute; that is the machine enforcement.
  * pass   - otherwise. Stale sources, a briefing-state date mismatch, and
             leakage-shaped strings are surfaced in the fields and in `reason`
             but do not by themselves force a retry: a stale source is fixed by
             re-running the upstream pull step, not by re-running step-06.5, so
             blocking here would be the wrong lever.

This keeps the checkpoint's outcome deterministic and inspectable via the eval
record's guardrails[].computed_fields, which is what the Stage 4 evidence bundle
reads.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

STALE_THRESHOLD_HOURS = 24

# Credential-shaped strings. Deliberately conservative to avoid false positives
# on ordinary prose: only high-signal prefixes, plus long base64-ish blobs.
LEAKAGE_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{16,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]


def parse_iso(value):
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None


def find_run_boot_eval_record(ies_root, ref_time):
    """Return (record_dict, record_path, started) for the boot eval record whose
    `started` is nearest to and not after ref_time, or (None, None, None)."""
    runs_dir = ies_root / "systems" / "eval-harness" / "runs"
    if not runs_dir.exists():
        return None, None, None
    best = None
    for f in runs_dir.glob("eval-*.json"):
        try:
            data = json.loads(f.read_text())
        except Exception:
            continue
        if data.get("name") != "boot":
            continue
        started = parse_iso(data.get("started"))
        if started is None:
            continue
        if ref_time and started > ref_time:
            continue
        if best is None or started > best[0]:
            best = (started, data, f)
    if best is None:
        return None, None, None
    return best[1], best[2], best[0]


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))
    step_completed = payload.get("step_completed")

    ref_time = parse_iso(step_completed) or datetime.now(timezone.utc)
    run_date = ref_time.date().isoformat()

    # 1. Data freshness (unchanged behaviour, still machine-derived).
    data_dir = ies_root / "data"
    stale_sources = []
    fresh_sources = []
    if data_dir.is_dir():
        for f in sorted(data_dir.glob("*.json")):
            mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
            age_hours = (ref_time - mtime).total_seconds() / 3600
            entry = {"file": f.name, "age_hours": round(age_hours, 1)}
            (stale_sources if age_hours > STALE_THRESHOLD_HOURS else fresh_sources).append(entry)

    # 2. Briefing state currency: the synthesized briefing must not be built on a
    #    briefing state from a different day.
    briefing_current = None
    briefing_last_run_date = None
    briefing_state_path = ies_root / "workflows" / "morning-briefing" / "state.yaml"
    if briefing_state_path.is_file():
        text = briefing_state_path.read_text(errors="replace")
        m = re.search(r"(?:last-run|last_run|session-started)[^\n]*?(\d{4}-\d{2}-\d{2})", text)
        if m:
            briefing_last_run_date = m.group(1)
            briefing_current = briefing_last_run_date == run_date
        else:
            briefing_current = None  # present but undated, informational only
    else:
        briefing_current = None  # no briefing state, informational only

    # 3. Checkpoint actually recorded: machine proof that guardrail-checkpoint.py ran.
    #    Only enforce this against THIS run's record. A stale prior boot record
    #    (e.g. an old aborted one) must not trigger a false retry, so the record
    #    counts as "this run's" only if it started within RECENT_WINDOW_HOURS of
    #    the step's completion.
    RECENT_WINDOW_HOURS = 12
    record, record_path, record_started = find_run_boot_eval_record(ies_root, ref_time)
    record_is_current = bool(
        record is not None and record_started is not None
        and (ref_time - record_started).total_seconds() <= RECENT_WINDOW_HOURS * 3600
    )
    checkpoint_recorded = False
    recorded_result = None
    if record is not None:
        for g in record.get("guardrails", []) or []:
            if g.get("name") == "pre-completion-review":
                checkpoint_recorded = True
                recorded_result = g.get("result")
                break

    # 4. Leakage scan over the two artifacts step-06.5 reviews.
    leakage_hits = []
    for rel in ("memory/sessions/index.json",):
        p = ies_root / rel
        if p.is_file():
            text = p.read_text(errors="replace")
            for pat in LEAKAGE_PATTERNS:
                if pat.search(text):
                    leakage_hits.append({"file": rel, "pattern": pat.pattern})
    wm_dir = ies_root / "memory" / "working"
    if wm_dir.is_dir():
        for f in sorted(wm_dir.glob("morning-briefing-*.md")):
            text = f.read_text(errors="replace")
            for pat in LEAKAGE_PATTERNS:
                if pat.search(text):
                    leakage_hits.append({"file": str(f.relative_to(ies_root)), "pattern": pat.pattern})

    fields = {
        "stale_sources": stale_sources,
        "fresh_sources": fresh_sources,
        "stale_threshold_hours": STALE_THRESHOLD_HOURS,
        "briefing_current": briefing_current,
        "briefing_last_run_date": briefing_last_run_date,
        "run_date": run_date,
        "checkpoint_recorded": checkpoint_recorded,
        "recorded_checkpoint_result": recorded_result,
        "boot_eval_record": record_path.name if record_path else None,
        "boot_eval_record_is_current": record_is_current,
        "leakage_hits": leakage_hits,
        "data_freshness_report": (
            "pass" if not stale_sources else f"{len(stale_sources)} stale source(s) found"
        ),
    }

    # Decision: enforce that the checkpoint was actually recorded this run.
    if record_is_current and not checkpoint_recorded:
        print(json.dumps({
            "result": "retry",
            "reason": "pre-completion-review checkpoint was not recorded in this run's boot eval record "
                      "(guardrail-checkpoint.py did not run or did not attach). The checkpoint must execute.",
            "fields": fields,
            "validation_errors": ["checkpoint_not_recorded"],
            "retry_instruction": "Run: python3 systems/eval-harness/guardrail-checkpoint.py boot "
                                 "pre-completion-review step-06-scan-workflows <pass|flag|escalate> \"<reason>\" "
                                 "before proceeding to step-07.",
        }))
        return

    reason = "All data sources fresh" if not stale_sources else (
        f"{len(stale_sources)} stale source(s): {', '.join(s['file'] for s in stale_sources)}")
    if briefing_current is False:
        reason += f"; briefing state date {briefing_last_run_date} != run date {run_date}"
    if leakage_hits:
        reason += f"; {len(leakage_hits)} leakage-shaped string(s) found"
    if recorded_result:
        reason += f" (checkpoint recorded: {recorded_result})"

    print(json.dumps({
        "result": "pass",
        "reason": reason,
        "fields": fields,
        "validation_errors": (
            [f"stale_source: {s['file']}" for s in stale_sources]
            + [f"leakage_shape: {h['file']}" for h in leakage_hits]
        ),
    }))


if __name__ == "__main__":
    main()
