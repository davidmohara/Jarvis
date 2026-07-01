#!/usr/bin/env python3
"""
Boot Workflow Instrumentation
Measures context window usage, data pull sizes, and identifies bloat sources.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

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
        json_str = json.dumps(obj, default=str)
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
            field_name = f"{prefix}.{key}" if prefix else key

            # Skip deeply nested objects
            if isinstance(value, (dict, list)) and len(json.dumps(value)) > 10000:
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
                "total_size_bytes": len(json.dumps(accumulated).encode('utf-8')),
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
    if len(sys.argv) < 2:
        print("Usage: measure.py <command> [args]")
        print("Commands:")
        print("  measure-state <path/to/state.yaml>  — Measure a single boot state")
        print("  compare <before-state> <after-state> — Compare two boot runs")
        sys.exit(1)

    project_root = os.getenv("IES_ROOT", "/Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES")
    instrument = BootInstrument(project_root)

    command = sys.argv[1]

    if command == "measure-state" and len(sys.argv) > 2:
        state_path = Path(sys.argv[2])
        measurement = instrument.measure_boot_state(state_path)
        instrument.write_measurement("state", measurement)
        print(json.dumps(measurement, indent=2))

    elif command == "compare" and len(sys.argv) > 3:
        before = Path(sys.argv[2])
        after = Path(sys.argv[3])
        comparison = instrument.measure_workflow_comparison(before, after)
        instrument.write_measurement("comparison", comparison)
        print(json.dumps(comparison, indent=2))

    else:
        print("Invalid command or missing arguments")
        sys.exit(1)


if __name__ == "__main__":
    main()
