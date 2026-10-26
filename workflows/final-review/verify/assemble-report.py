#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Deterministic report assembly for the final-review workflow.

The harness, not the LLM, owns the report's headings and verdicts. A
findings file (deterministically produced per artifact) drives the
structure: a PASS artifact gets a PASS heading, a FAIL artifact gets a FAIL
heading, and the LLM-written prose is inserted verbatim underneath each
heading. Headings can never be wrong because they never pass through the
LLM.

Contract (stdin JSON, same shape as the verifier contract):
    {
      "workflow": "final-review",
      "step": "step-03-assemble-report.md",
      "ies_root": "<path>",
      "findings_path": "<path to findings JSON>",
      "prose_path": "<path to prose JSON>"
    }

findings JSON (deterministic, machine-checked):
    {
      "title": "...",
      "correlation_id": "corr-...",
      "artifacts": [
        {"artifact": "<name>", "verdict": "pass"|"fail", "summary_line": "..."}
      ]
    }

prose JSON (LLM-written, keyed by artifact name):
    { "<artifact name>": "prose paragraph(s), markdown" }

stdout (last line JSON, per the verifier contract):
    {"result": "pass"|"retry", "reason": "...", "fields": {"report_path": "..."}}

The assembled report is written to the output path given in
`report_path` (stdin), or next to the findings file as
<findings-stem>-report.md.
"""

import json
import sys
from pathlib import Path

IES_ROOT = Path(__file__).resolve().parents[3]
VALID_VERDICTS = {"pass", "fail"}


def main() -> None:
    try:
        payload = json.loads(sys.stdin.read())
    except Exception as e:
        print(json.dumps({"result": "retry",
                          "reason": f"stdin is not valid JSON: {e}"}))
        sys.exit(0)

    findings_path = Path(payload.get("findings_path", ""))
    prose_path = Path(payload.get("prose_path", ""))
    report_path = Path(payload["report_path"]) if payload.get("report_path") else \
        findings_path.with_name(findings_path.stem + "-report.md")

    problems = []
    if not findings_path.is_file():
        problems.append(f"findings file missing: {findings_path}")
    if not prose_path.is_file():
        problems.append(f"prose file missing: {prose_path}")
    if problems:
        print(json.dumps({"result": "retry",
                          "reason": "; ".join(problems),
                          "validation_errors": problems}))
        sys.exit(0)

    try:
        findings = json.loads(findings_path.read_text())
        prose = json.loads(prose_path.read_text())
    except Exception as e:
        print(json.dumps({"result": "retry",
                          "reason": f"findings/prose not valid JSON: {e}"}))
        sys.exit(0)

    artifacts = findings.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        print(json.dumps({"result": "retry",
                          "reason": "findings.artifacts missing or empty"}))
        sys.exit(0)
    for a in artifacts:
        if a.get("verdict") not in VALID_VERDICTS or not a.get("artifact"):
            print(json.dumps({"result": "retry",
                              "reason": f"malformed artifact entry: {json.dumps(a)[:200]}"})  # noqa: E501
              )
            sys.exit(0)

    # DETERMINISTIC ASSEMBLY — nothing below consults the LLM.
    lines = []
    title = findings.get("title", "Final Review")
    lines.append(f"# {title}")
    lines.append("")
    if findings.get("correlation_id"):
        lines.append(f"Correlation ID: {findings['correlation_id']}")
        lines.append("")
    overall = "PASS" if all(a["verdict"] == "pass" for a in artifacts) else "FAIL"
    lines.append(f"## Overall: {overall}")
    lines.append("")

    missing_prose = []
    for a in artifacts:
        verdict_heading = "PASS" if a["verdict"] == "pass" else "FAIL"
        lines.append(f"## [{verdict_heading}] {a['artifact']}")
        lines.append("")
        if a.get("summary_line"):
            lines.append(f"*{a['summary_line']}*")
            lines.append("")
        body = prose.get(a["artifact"])
        if body:
            lines.append(str(body).strip())
            lines.append("")
        else:
            missing_prose.append(a["artifact"])
            lines.append("_(no synthesis prose provided for this artifact)_")
            lines.append("")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines).rstrip() + "\n")

    if missing_prose:
        print(json.dumps({
            "result": "retry",
            "reason": f"report assembled but prose missing for: {', '.join(missing_prose)}",
            "validation_errors": [f"prose: {m}" for m in missing_prose],
            "fields": {"report_path": str(report_path)},
        }))
    else:
        print(json.dumps({
            "result": "pass",
            "reason": f"report assembled at {report_path} with deterministic headings",
            "fields": {"report_path": str(report_path)},
        }))


if __name__ == "__main__":
    main()
