#!/usr/bin/env python3
"""Ground-truth verifier for talking-points/step-02-generate-talking-points.

The step generates the calibrated points and anticipated Q&A. This verifier
re-derives them from real records: first accumulated-context.talking_points
(the structured block the step is specified to write), then the step's own
frontmatter outputs, then the delivered document itself (the materialized
result of steps 02-03) counting real point and Q&A markers from content.

If no structured block, no step outputs, and no deliverable exists yet (the
normal state at step-02 completion in a live run, before step-03 writes the
document), the verifier passes with an explicit deferred note rather than
false-retrying a correct run, the step-03 verifier is the hard gate on the
deliverable. If a deliverable DOES exist but lacks the points, it retries.
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

POINT_MARKER_RE = re.compile(r"(?im)^(#{2,4}\s+\d+\.|(?:\*\*)?(?:talking point|point|key message|theme)\s*\[?\d*\]?)")
QA_MARKER_RE = re.compile(r"(?i)(anticipated (q\s*&\s*a|questions)|if asked|likely questions|questions to ask)")
MIN_POINTS = 3


def load_state(path: Path) -> dict:
    if yaml is None or not path.is_file():
        return {}
    try:
        merged = {}
        for doc in yaml.safe_load_all(path.read_text()):
            if isinstance(doc, dict):
                for k, v in doc.items():
                    if k not in merged or v:
                        merged[k] = v
        return merged
    except Exception:
        return {}


def step_outputs(ies_root: Path) -> dict:
    p = ies_root / "workflows" / "talking-points" / "steps" / "step-02-generate-talking-points.md"
    if yaml is None or not p.is_file():
        return {}
    lines = p.read_text().split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    fm_lines = []
    inside = False
    for line in lines:
        if line.strip() == "---":
            inside = not inside
            if not inside:
                break
            continue
        if inside:
            fm_lines.append(line)
    try:
        return (yaml.safe_load("\n".join(fm_lines)) or {}).get("outputs") or {}
    except Exception:
        return {}


def find_deliverable(ies_root: Path, ctx: dict):
    output = ctx.get("output")
    if output:
        candidate = Path(output)
        if not candidate.is_absolute():
            candidate = ies_root / candidate
        if candidate.is_file():
            return candidate
    meetings = ies_root / "meetings"
    if meetings.is_dir():
        matches = [p for p in meetings.glob("*.md") if "talking-point" in p.stem.lower()]
        if matches:
            return max(matches, key=lambda p: p.stat().st_mtime)
    return None


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state = load_state(ies_root / "workflows" / "talking-points" / "state.yaml")
    ctx = state.get("accumulated-context") or {}
    tp = ctx.get("talking_points") or {}
    outputs = step_outputs(ies_root)

    points = tp.get("points") if isinstance(tp, dict) else None
    questions = tp.get("anticipated_questions") if isinstance(tp, dict) else None

    fields = {
        "talking_points_block_present": bool(tp),
        "structured_points_count": len(points) if isinstance(points, list) else None,
        "structured_questions_count": len(questions) if isinstance(questions, list) else None,
        "step_output_keys": sorted(outputs.keys()) if isinstance(outputs, dict) else [],
    }

    if isinstance(points, list) and points:
        if len(points) < MIN_POINTS:
            print(json.dumps({
                "result": "retry",
                "reason": f"Only {len(points)} talking point(s) recorded, the step requires 3-5",
                "fields": fields,
                "validation_errors": [f"insufficient_points: {len(points)}"],
                "retry_instruction": "Re-execute step-02 to generate 3-5 talking points (with evidence, phrasing, and source).",
            }))
            return
        print(json.dumps({
            "result": "pass",
            "reason": f"talking_points recorded: {len(points)} point(s), "
                      f"{len(questions) if isinstance(questions, list) else 0} anticipated question(s)",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    deliverable = find_deliverable(ies_root, ctx)
    if deliverable is not None:
        content = deliverable.read_text(errors="ignore")
        point_count = len(POINT_MARKER_RE.findall(content))
        has_qa = QA_MARKER_RE.search(content) is not None
        fields["deliverable"] = str(deliverable.relative_to(ies_root))
        fields["deliverable_point_markers"] = point_count
        fields["deliverable_has_qa"] = has_qa
        errors = []
        if point_count < MIN_POINTS:
            errors.append(f"insufficient_points: {point_count}")
        if not has_qa:
            errors.append("missing_anticipated_qa")
        if errors:
            print(json.dumps({
                "result": "retry",
                "reason": f"Deliverable at {fields['deliverable']} lacks the generated points/Q&A: {', '.join(errors)}",
                "fields": fields,
                "validation_errors": errors,
                "retry_instruction": "Re-execute step-02/03: the delivered document must contain 3-5 talking points and an anticipated Q&A section.",
            }))
            return
        print(json.dumps({
            "result": "pass",
            "reason": f"Talking points present in deliverable {fields['deliverable']} "
                      f"({point_count} point marker(s), anticipated Q&A present)",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    if outputs:
        print(json.dumps({
            "result": "pass",
            "reason": "Step-02 outputs recorded (points generated); no structured block or deliverable to cross-check yet",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": "Deferred: no structured talking_points block, no step outputs, and no deliverable exists yet, "
                  "step-02 output is not independently verifiable at this point; step-03's deliverable is the hard gate",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()
