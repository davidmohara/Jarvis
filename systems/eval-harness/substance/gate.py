#!/usr/bin/env python3
"""Substance elevation gate + append-only human decision log.

The coordinator may not auto-approve past this gate. When the substance
assessment trips the elevation rule (any toy, two or more peripheral, or any
unconfirmed classification), final disposition is blocked until a human
records a Continue/Reject decision. The decision log is append-only by
construction: this script offers no overwrite, edit, or delete path, and
every entry carries the reviewer's identity, role, and a UTC timestamp.

Usage:
  gate.py check [--assessment PATH] [--log PATH]
      Prints the gate state as JSON:
        { "elevation_required": bool, "reason": [...],
          "decision_covered": bool, "decision": {...} | null }
      Exit 0 when disposition may proceed (no elevation, or a covering
      Continue decision exists). Exit 3 when elevation is required and
      uncovered, or the last decision is Reject.

  gate.py record --reviewer NAME --role ROLE --decision continue|reject \
      [--note TEXT] [--assessment PATH] [--log PATH]
      Appends the human decision to the log (never rewrites prior entries).
      Exit 0 on append; 2 on misuse.

  gate.py confirm [--assessment PATH] [--log PATH]
      Marks every workflow's classification `confirmed: true` in the
      assessment, but ONLY when the most recent log decision is a Continue
      whose workflows_ruled_on matches the current classifications exactly.
      If the classifications changed since the decision, the gate refuses
      (exit 3): the human ruled on a different state; record a new decision.
      This is the only sanctioned way to confirm — hand-editing assessment
      classifications bypasses the decision log and is detectable by it.

  gate.py log [--log PATH]
      Prints the decision log verbatim.

The system's own report is never rewritten by a decision: the caller
snapshots the report path in --note (or the entry's report_path) and the
verbatim report stays wherever it was produced.
"""

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

IES_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ASSESSMENT = Path(__file__).resolve().parent / "assessment.json"
DEFAULT_LOG = Path(__file__).resolve().parent / "elevation-log.jsonl"

VALID_CLASSIFICATIONS = {"core", "peripheral", "toy"}
VALID_DECISIONS = {"continue", "reject"}


def load_assessment(path: Path) -> dict:
    data = json.loads(path.read_text())
    workflows = data.get("workflows")
    if not isinstance(workflows, dict) or not workflows:
        raise SystemExit(f"misconfigured assessment: no workflows in {path}")
    for name, row in workflows.items():
        if row.get("classification") not in VALID_CLASSIFICATIONS:
            raise SystemExit(
                f"misconfigured assessment: {name} classification "
                f"'{row.get('classification')}' not in {sorted(VALID_CLASSIFICATIONS)}")
    return data


def gate_reasons(assessment: dict) -> list[str]:
    """Why elevation is required (empty list = no elevation needed)."""
    reasons = []
    wfs = assessment["workflows"]
    toys = [n for n, r in wfs.items() if r["classification"] == "toy"]
    peripherals = [n for n, r in wfs.items() if r["classification"] == "peripheral"]
    unconfirmed = [n for n, r in wfs.items() if not r.get("confirmed")]
    if toys:
        reasons.append(f"toy-classified workflows present: {', '.join(sorted(toys))}")
    if len(peripherals) >= 2:
        reasons.append(f"two or more peripheral workflows: {', '.join(sorted(peripherals))}")
    if unconfirmed:
        reasons.append(f"classifications not yet confirmed by a human: {', '.join(sorted(unconfirmed))}")
    return reasons


def read_log(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    entries = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            entries.append(json.loads(line))
    return entries


def covering_decision(entries: list[dict]) -> dict | None:
    """The most recent decision that covers the current gate state.

    A Continue covers only the gate as it stood when it was recorded: a
    decision recorded against a different elevation-reason set does NOT
    cover the current state (classification changes re-open the gate).
    """
    if not entries:
        return None
    last = entries[-1]
    if last.get("decision") == "reject":
        return last  # surfaced as blocking by the caller
    return last if last.get("decision") == "continue" else None


def main() -> None:
    ap = argparse.ArgumentParser(description="Substance elevation gate")
    ap.add_argument("action", choices=["check", "record", "log", "confirm"])
    ap.add_argument("--reviewer")
    ap.add_argument("--role")
    ap.add_argument("--decision", choices=sorted(VALID_DECISIONS))
    ap.add_argument("--note", default="")
    ap.add_argument("--report-path", default=None,
                    help="path to the verbatim system report this decision rules on")
    ap.add_argument("--assessment", default=str(DEFAULT_ASSESSMENT))
    ap.add_argument("--log", default=str(DEFAULT_LOG))
    args = ap.parse_args()

    assessment_path = Path(args.assessment)
    log_path = Path(args.log)

    if args.action == "log":
        for entry in read_log(log_path):
            print(json.dumps(entry))
        return

    if args.action == "record":
        if not args.reviewer or not args.role or not args.decision:
            print("record requires --reviewer, --role, and --decision", file=sys.stderr)
            sys.exit(2)
        assessment = load_assessment(assessment_path)
        reasons = gate_reasons(assessment)
        entry = {
            "id": f"elev-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}-{uuid.uuid4().hex[:4].upper()}",
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "reviewer": args.reviewer,
            "reviewer_role": args.role,
            "decision": args.decision,
            "elevation_reasons": reasons,
            "workflows_ruled_on": {n: r["classification"]
                                   for n, r in assessment["workflows"].items()},
            "report_path": args.report_path,
            "note": args.note,
        }
        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        print(json.dumps(entry))
        return

    # confirm: flip confirmed=true only under a covering Continue decision
    if args.action == "confirm":
        assessment = load_assessment(assessment_path)
        entries = read_log(log_path)
        if not entries:
            print("no decision recorded yet; record a Continue first", file=sys.stderr)
            sys.exit(3)
        last = entries[-1]
        if last.get("decision") != "continue":
            print(f"most recent decision is '{last.get('decision')}', not continue", file=sys.stderr)
            sys.exit(3)
        current = {n: r["classification"] for n, r in assessment["workflows"].items()}
        if last.get("workflows_ruled_on") != current:
            print(
                "classifications changed since the human decision ruled on them "
                "(or the decision covered a different set); record a new decision",
                file=sys.stderr,
            )
            sys.exit(3)
        for row in assessment["workflows"].values():
            row["confirmed"] = True
        assessment_path.write_text(json.dumps(assessment, indent=2) + "\n")
        print(json.dumps({
            "confirmed": sorted(current),
            "by_decision": last["id"],
            "reviewer": last["reviewer"],
            "recorded_at": last["recorded_at"],
        }, indent=2))
        return

    # check
    assessment = load_assessment(assessment_path)
    reasons = gate_reasons(assessment)
    entries = read_log(log_path)
    decision = covering_decision(entries) if reasons else None

    if not reasons:
        print(json.dumps({
            "elevation_required": False,
            "reason": [],
            "decision_covered": True,
            "decision": None,
        }))
        return

    covered = bool(decision and decision.get("decision") == "continue")
    state = {
        "elevation_required": True,
        "reason": reasons,
        "decision_covered": covered,
        "decision": decision,
    }
    print(json.dumps(state, indent=2))
    if not covered:
        print(
            "ELEVATION REQUIRED AND UNCOVERED: a human must record a Continue/Reject "
            "decision before final disposition. The system may not self-approve.",
            file=sys.stderr,
        )
        sys.exit(3)


if __name__ == "__main__":
    main()
