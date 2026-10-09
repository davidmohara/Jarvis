#!/usr/bin/env python3
"""Ground-truth verifier for talking-points/step-03-format-and-deliver.

Locates the delivered talking-points document on disk (accumulated-context.
output, then a glob of meetings/*talking-point*.md) rather than trusting a
self-reported path, and checks the delivery directly from content: the file
exists, is substantive, contains the generated points, and includes the
anticipated Q&A the step is required to carry into every format.
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
MIN_BYTES = 500


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
    event_type = ctx.get("event_type") or (ctx.get("event_context") or {}).get("event_type")

    deliverable = find_deliverable(ies_root, ctx)
    if deliverable is None:
        print(json.dumps({
            "result": "retry",
            "reason": "No delivered talking-points document found (accumulated-context.output missing and no "
                      "matching file under meetings/)",
            "fields": {"file_found": False, "event_type": event_type},
            "validation_errors": ["file_not_found"],
            "retry_instruction": "Re-execute step-03: format and save the talking points, then record the path in "
                                 "accumulated-context.output.",
        }))
        return

    content = deliverable.read_text(errors="ignore")
    size = deliverable.stat().st_size
    point_count = len(POINT_MARKER_RE.findall(content))
    has_qa = QA_MARKER_RE.search(content) is not None

    fields = {
        "file_found": True,
        "file_path": str(deliverable.relative_to(ies_root)),
        "file_size_bytes": size,
        "event_type": event_type,
        "point_markers": point_count,
        "has_anticipated_qa": has_qa,
    }

    errors = []
    if size < MIN_BYTES:
        errors.append(f"content_too_thin: {size} bytes (need >= {MIN_BYTES})")
    if point_count < MIN_POINTS:
        errors.append(f"insufficient_points: {point_count}")
    if not has_qa:
        errors.append("missing_anticipated_qa")

    if errors:
        print(json.dumps({
            "result": "retry",
            "reason": f"Delivered document at {fields['file_path']} failed delivery checks: {', '.join(errors)}",
            "fields": fields,
            "validation_errors": errors,
            "retry_instruction": "Re-execute step-03: deliver 3-5 formatted points with the anticipated Q&A section included.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"Talking points delivered at {fields['file_path']} ({point_count} point(s), anticipated Q&A present, "
                  f"{size} bytes)",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()
