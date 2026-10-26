#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""
Sub-Agent Output Schema Validation (delegation boundary, Layer 0)

Validates a sub-agent's structured output against a declared schema BEFORE
the coordinator sees the result. The coordinator never receives garbage: an
invalid output produces a structured error the coordinator can reason over
(retry the step, or proceed without it), not a silent pass.

Contract (stdin JSON, mirroring the verifier contract):
    {
      "workflow": "<workflow dir name>",
      "step": "<step filename>",
      "ies_root": "<path>",            # optional, defaults to repo root
      "output": {...}                  # optional; when absent the validator
                                       # reads workflows/<wf>/state.yaml
                                       # accumulated-context itself
    }

stdout JSON (last line):
    {
      "result": "pass" | "retry",
      "reason": "...",
      "validation_errors": ["<field>: <problem>", ...]
    }

Schema convention: workflows/<workflow>/schemas/<step>.schema.json — colocated
with the workflow's verify/ scripts. A step with no schema file PASSES with
reason "no schema declared" (schemas are opt-in per step, added as outputs
stabilize).

Supported schema subset (deliberately small, no external deps):
    {
      "type": "object",
      "required": ["field", ...],
      "properties": {
        "field": {"type": "string|number|boolean|list|object",
                  "minLength": n, "minItems": n, "enum": [...]}
      }
    }

Exit code is always 0 when the contract itself is honored (validation
verdicts travel in stdout); nonzero only on harness-side misuse so callers
can distinguish "invalid output" from "broken invocation".
"""

import json
import sys
from pathlib import Path

IES_ROOT = Path(__file__).resolve().parents[2]

VALID_TYPES = {"string", "number", "boolean", "list", "object"}
PY_TYPE_MAP = {
    "string": str,
    "number": (int, float),
    "boolean": bool,
    "list": list,
    "object": dict,
}


def fail_usage(msg: str) -> None:
    print(json.dumps({"result": "retry", "reason": f"validator misuse: {msg}",
                      "validation_errors": []}))
    sys.exit(2)


def find_schema(ies_root: Path, workflow: str, step: str) -> Path | None:
    # Step names arrive both with and without their .md extension; accept
    # "step-01.md" -> step-01.md.schema.json or step-01.schema.json, and the
    # bare stem as canonical.
    candidates = []
    if step.endswith(".md"):
        candidates.append(ies_root / "workflows" / workflow / "schemas" / f"{step}.schema.json")
        candidates.append(ies_root / "workflows" / workflow / "schemas" / f"{step[:-3]}.schema.json")
    else:
        candidates.append(ies_root / "workflows" / workflow / "schemas" / f"{step}.schema.json")
        candidates.append(ies_root / "workflows" / workflow / "schemas" / f"{step}.md.schema.json")
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def load_output(ies_root: Path, workflow: str, payload: dict) -> dict:
    if isinstance(payload.get("output"), dict):
        return payload["output"]
    state = ies_root / "workflows" / workflow / "state.yaml"
    if not state.is_file():
        return {}
    try:
        sys.path.insert(0, str(IES_ROOT / "systems" / "eval-harness" / "vendor"))
        import yaml  # vendored
        data = yaml.safe_load(state.read_text()) or {}
    except Exception:
        return {}
    ctx = data.get("accumulated-context")
    return ctx if isinstance(ctx, dict) else {}


def validate(output: dict, schema: dict) -> list[str]:
    errors: list[str] = []
    props = schema.get("properties", {}) or {}

    for field in schema.get("required", []) or []:
        if field not in output:
            errors.append(f"{field}: required field missing")

    for field, spec in props.items():
        if field not in output:
            continue  # absence of an optional field is not an error
        value = output[field]
        want = spec.get("type")
        if want in VALID_TYPES:
            got_type = PY_TYPE_MAP[want]
            if want == "number" and isinstance(value, bool):
                errors.append(f"{field}: expected number, got boolean")
            elif not isinstance(value, got_type):
                errors.append(f"{field}: expected {want}, got {type(value).__name__}")
                continue
        if "minLength" in spec and isinstance(value, str) and len(value) < spec["minLength"]:
            errors.append(f"{field}: shorter than minLength {spec['minLength']}")
        if "minItems" in spec and isinstance(value, list) and len(value) < spec["minItems"]:
            errors.append(f"{field}: fewer than minItems {spec['minItems']}")
        if "enum" in spec and value not in spec["enum"]:
            errors.append(f"{field}: not in enum {spec['enum']}")
    return errors


def main() -> None:
    try:
        payload = json.loads(sys.stdin.read())
    except Exception as e:
        fail_usage(f"stdin is not valid JSON: {e}")

    workflow = payload.get("workflow")
    step = payload.get("step")
    if not workflow or not step:
        fail_usage("payload needs 'workflow' and 'step'")

    ies_root = Path(payload.get("ies_root") or IES_ROOT)

    schema_path = find_schema(ies_root, workflow, step)
    if schema_path is None:
        print(json.dumps({"result": "pass", "reason": "no schema declared",
                          "validation_errors": []}))
        return

    try:
        schema = json.loads(schema_path.read_text())
    except Exception as e:
        fail_usage(f"schema file unreadable: {schema_path}: {e}")

    output = load_output(ies_root, workflow, payload)
    if not output:
        print(json.dumps({
            "result": "retry",
            "reason": f"no structured output available to validate for {step} "
                      f"(state.yaml accumulated-context empty and no payload output)",
            "validation_errors": ["output: empty"],
        }))
        return

    errors = validate(output, schema)
    if errors:
        print(json.dumps({
            "result": "retry",
            "reason": f"sub-agent output failed schema validation ({len(errors)} errors); "
                      "re-run the step and repopulate the declared fields",
            "validation_errors": errors,
        }))
    else:
        print(json.dumps({"result": "pass",
                          "reason": f"output conforms to {schema_path.name}",
                          "validation_errors": []}))


if __name__ == "__main__":
    main()
