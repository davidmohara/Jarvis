"""Shared loader for workflow step outputs.

Per the 2026-10-13 step-frontmatter convention change, run outputs live in
`state.yaml` `accumulated-context` only. Step-file frontmatter carries just
status/started-at/completed-at and is never a log.

Accumulated-context shapes vary by workflow (flat top-level keys, named
blocks, or dated `step-NN-YYYY-MM-DD` entries), so `load_step_outputs`
deep-searches the context tree and returns the dict that best matches the
caller's expected keys.
"""

from pathlib import Path


def _load_state(state_path: Path, yaml_module) -> dict:
    if yaml_module is None or not state_path.is_file():
        return {}
    try:
        merged = {}
        for doc in yaml_module.safe_load_all(state_path.read_text()):
            if isinstance(doc, dict):
                for k, v in doc.items():
                    if k not in merged or v:
                        merged[k] = v
        return merged
    except Exception:
        return {}


def load_step_outputs(ies_root: Path, workflow: str, expected_keys, yaml_module) -> dict:
    """Return the accumulated-context dict best matching expected_keys.

    Searches `workflows/{workflow}/state.yaml` -> `accumulated-context`
    depth-first; the dict containing the most expected keys wins. Returns {}
    when state.yaml is missing, has no context, or no key matches.
    """
    state = _load_state(Path(ies_root) / "workflows" / workflow / "state.yaml", yaml_module)
    ctx = state.get("accumulated-context")
    if not isinstance(ctx, dict):
        return {}
    expected = set(expected_keys)
    best, best_score = {}, 0
    stack = [ctx]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            score = len(expected & set(node.keys()))
            if score > best_score:
                best, best_score = node, score
            stack.extend(v for v in node.values() if isinstance(v, (dict, list)))
        elif isinstance(node, list):
            stack.extend(v for v in node if isinstance(v, (dict, list)))
    return best


def load_context(ies_root: Path, workflow: str, yaml_module) -> dict:
    """Return the raw accumulated-context dict (for presence checks)."""
    state = _load_state(Path(ies_root) / "workflows" / workflow / "state.yaml", yaml_module)
    ctx = state.get("accumulated-context")
    return ctx if isinstance(ctx, dict) else {}
