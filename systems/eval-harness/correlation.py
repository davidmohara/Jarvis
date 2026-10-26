#!/usr/bin/env python3
"""Correlation IDs for end-to-end audit tracing.

Every examination (workflow run) gets a correlation ID the first time a step
is recorded against it. The ID propagates to every step entry and every audit
export row, so a single identifier traces one execution across the full
multi-step, multi-agent structure — record, steps, and exports.

IDs are minted once per record and never recomputed: any writer that sees a
record without one mints it; any writer that sees one reuses it. The ID is
independent of the eval record's own `id` so it survives record renames and
can be carried into sub-records (e.g. a final-review run that consumed this
run's outputs) via `--correlation` style links.

Format: corr-<UTC compact timestamp>-<4 uppercase alphanumerics>
(e.g. corr-20261026T221900-K3QF).
"""

import json
import secrets
import string
from datetime import datetime, timezone
from pathlib import Path

_ALPHABET = string.ascii_uppercase + string.digits


def mint() -> str:
    """Mint a new correlation ID."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    rand = "".join(secrets.choice(_ALPHABET) for _ in range(4))
    return f"corr-{stamp}-{rand}"


def ensure_record_correlation(record: dict) -> str:
    """Return the record's correlation ID, minting and setting one if absent.

    Mutates `record` in place when minting. Never overwrites an existing ID.
    """
    existing = record.get("correlation_id")
    if isinstance(existing, str) and existing:
        return existing
    record["correlation_id"] = mint()
    return record["correlation_id"]


def attach_to_step(record: dict, step_entry: dict) -> str:
    """Ensure a step entry carries the parent record's correlation ID.

    Returns the correlation ID. Step-level IDs that disagree with the record's
    (from an earlier writer) are NOT overwritten at the step level — the
    record is authoritative and the mismatch is surfaced to the caller via
    the returned value so they can decide; normal flow never hits this.
    """
    cid = ensure_record_correlation(record)
    step_entry.setdefault("correlation_id", cid)
    return cid


def read_correlation(record_path: Path) -> str | None:
    """Read a record file's correlation ID without mutating it."""
    try:
        record = json.loads(Path(record_path).read_text())
    except Exception:
        return None
    cid = record.get("correlation_id")
    return cid if isinstance(cid, str) and cid else None
