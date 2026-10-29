#!/usr/bin/env python3
"""
Boot Workflow Instrumentation
Measures context window usage, data pull sizes, and identifies bloat sources.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def _jsonable(obj: Any) -> Any:
    """Recursively coerce a YAML-loaded structure into something json.dumps
    always accepts.

    The 2026-10-23 `default=str` fix covers non-string VALUES. It does not
    cover non-string KEYS: YAML 1.1 parses an unquoted date-like key (e.g.
    `2026-10-29:` under boot state.yaml's task-g-72hr-lookahead block) into a
    datetime.date KEY, and json.dumps rejects those outright ("keys must be
    str, int, float, bool or None, not datetime.date") — the 2026-10-28
    measurement snapshot contains only that error. Stringify mapping keys
    here, recursively, before any dumps."""
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    return obj


def _dumps(obj: Any, **kwargs) -> str:
    """json.dumps with key-sanitizing always applied. `default=str` still
    handles non-string leaf values (dates, datetimes) that _jsonable passes
    through."""
    kwargs.setdefault("default", str)
    return json.dumps(_jsonable(obj), **kwargs)


class BootInstrument:
    """Instruments boot workflow to measure context bloat."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.measurements = {
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": None,
            "measurements": []
        }

    def measure_object_size(self, obj: Any, name: str) -> Dict[str, Any]:
        """Measure size of a Python object in tokens (approximate) and bytes."""
        # Approximate token count: ~4 chars per token
        json_str = _dumps(obj)
        size_bytes = len(json_str.encode('utf-8'))
        estimated_tokens = len(json_str) // 4

        return {
            "name": name,
            "size_bytes": size_bytes,
            "size_kb": round(size_bytes / 1024, 2),
            "estimated_tokens": estimated_tokens,
            "type": type(obj).__name__
        }

    def measure_dict_fields(self, data: dict, prefix: str = "") -> List[Dict[str, Any]]:
        """Recursively measure each field in a dict."""
        results = []
        for key, value in data.items():
            field_name = f"{prefix}.{key}" if prefix else str(key)

            # Skip deeply nested objects
            if isinstance(value, (dict, list)) and len(_dumps(value)) > 10000:
                measurement = self.measure_object_size(value, field_name)
                results.append(measurement)
            elif isinstance(value, dict):
                # Recurse into nested dicts
                results.extend(self.measure_dict_fields(value, field_name))
            elif isinstance(value, list):
                measurement = self.measure_object_size(value, field_name)
                results.append(measurement)
            else:
                results.append({
                    "name": field_name,
                    "size_bytes": len(str(value).encode('utf-8')),
                    "size_kb": 0,
                    "estimated_tokens": len(str(value)) // 4,
                    "type": type(value).__name__
                })

        return sorted(results, key=lambda x: x["size_bytes"], reverse=True)

    def measure_boot_state(self, state_file: Path) -> Dict[str, Any]:
        """Load and measure a boot state.yaml file."""
        if not state_file.exists():
            return {"error": "state.yaml not found"}

        try:
            import yaml
            with open(state_file) as f:
                state = yaml.safe_load(f)

            accumulated = state.get("accumulated-context", {})

            measurement = {
                "workflow": "boot",
                "total_size_bytes": len(_dumps(accumulated).encode('utf-8')),
                "accumulated_context": self.measure_object_size(accumulated, "accumulated-context"),
                "field_breakdown": self.measure_dict_fields(accumulated)
            }

            return measurement
        except Exception as e:
            return {"error": str(e)}

    def measure_workflow_comparison(self, before_state: Path, after_state: Path) -> Dict[str, Any]:
        """Compare before/after boot runs."""
        before = self.measure_boot_state(before_state)
        after = self.measure_boot_state(after_state)

        if "error" in before or "error" in after:
            return {"error": "Unable to load one or both state files"}

        before_bytes = before["total_size_bytes"]
        after_bytes = after["total_size_bytes"]
        reduction = before_bytes - after_bytes
        reduction_pct = (reduction / before_bytes * 100) if before_bytes > 0 else 0

        return {
            "before_bytes": before_bytes,
            "before_kb": round(before_bytes / 1024, 2),
            "before_tokens": round(before_bytes / 4),
            "after_bytes": after_bytes,
            "after_kb": round(after_bytes / 1024, 2),
            "after_tokens": round(after_bytes / 4),
            "reduction_bytes": reduction,
            "reduction_kb": round(reduction / 1024, 2),
            "reduction_tokens": round(reduction / 4),
            "reduction_pct": round(reduction_pct, 1),
            "before_breakdown": before["field_breakdown"][:10],
            "after_breakdown": after["field_breakdown"][:10]
        }

    def write_measurement(self, name: str, measurement: Dict[str, Any]):
        """Write a measurement to disk."""
        output_dir = self.project_root / "systems" / "boot-instrumentation" / "measurements"
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        filename = f"measurement-{name}-{timestamp}.json"
        filepath = output_dir / filename

        with open(filepath, "w") as f:
            json.dump(measurement, f, indent=2)

        print(f"Measurement saved: {filepath}")
        return filepath


def main():
    """CLI for boot instrumentation."""
    ap = argparse.ArgumentParser(
        description="Boot instrumentation: measure boot state token usage and compare boot runs.",
        epilog="Examples:\n"
               "  python3 systems/boot-instrumentation/measure.py measure-state workflows/boot/state.yaml\n"
               "  python3 systems/boot-instrumentation/measure.py compare before.json after.json",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    p_state = sub.add_parser("measure-state", help="measure a single boot state")
    p_state.add_argument("state_path", help="path to state.yaml")
    p_cmp = sub.add_parser("compare", help="compare two boot runs")
    p_cmp.add_argument("before", help="before-state JSON")
    p_cmp.add_argument("after", help="after-state JSON")
    args = ap.parse_args()

    project_root = os.getenv("IES_ROOT", "/Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES")
    instrument = BootInstrument(project_root)

    if args.command == "measure-state":
        state_path = Path(args.state_path)
        measurement = instrument.measure_boot_state(state_path)
        instrument.write_measurement("state", measurement)
        print(json.dumps(measurement, indent=2))

    elif args.command == "compare":
        before = Path(args.before)
        after = Path(args.after)
        comparison = instrument.measure_workflow_comparison(before, after)
        instrument.write_measurement("comparison", comparison)
        print(json.dumps(comparison, indent=2))


if __name__ == "__main__":
    main()
