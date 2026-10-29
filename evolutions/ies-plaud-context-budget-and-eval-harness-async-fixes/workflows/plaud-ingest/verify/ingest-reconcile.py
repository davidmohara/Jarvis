#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Deterministic ingestion-accounting reconcile for plaud-ingest step-06.

Replaces the always-on LLM verification pass (Ralph reading state.yaml, the
vault, and the staging dir at 1-2.5M input tokens per ingest day) with the
deterministic diff that pass actually is: the discovered file_id set vs the
outcome sets, the vault on disk, and the staging dir. Mirrors how
workflows/boot/verify/boot-verify.py replaced LLM verification in boot.

Checks (the mechanical core of plaud-ingest-verification/steps/step-01-verify.md):
  1. Every discovered file_id (accumulated-context.new-recordings) is
     accounted for: present in the vault's file_id set, OR listed in
     pending-recordings / transcription-triggered / stale-staged-files, OR
     classified personal, OR carried in unresolved_speakers. A discovered
     file_id in NO set is a silent drop.
  2. Every accumulated-context.ingested-notes path exists in the vault on
     disk, and its frontmatter file_id (when present) is a discovered
     file_id.
  3. Staging: no top-level ~/Downloads/transcript-staging/plaud_* file
     remains that names a discovered file_id or a staged-files basename
     from this run.

Exit 0 = clean (all accounted, no anomalies) — record the pass, no Ralph.
Exit 1 = anomalies — the step spawns Ralph with the flagged items only.

Usage:
    uv run workflows/plaud-ingest/verify/ingest-reconcile.py [--json]
    python3 workflows/plaud-ingest/verify/ingest-reconcile.py [--json]
    (plain python3 works: PyYAML falls back to the eval-harness vendored copy)

Env overrides: IES_ROOT (repo root), IES_VAULT_ROOT (Obsidian vault root),
IES_PLAUD_STAGING (staging dir; default ~/Downloads/transcript-staging).
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("IES_ROOT", Path(__file__).resolve().parents[3]))
VAULT = Path(os.environ.get(
    "IES_VAULT_ROOT",
    os.path.expanduser("~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian")))
STATE = ROOT / "workflows" / "plaud-ingest" / "state.yaml"
STAGING = Path(os.environ.get(
    "IES_PLAUD_STAGING", os.path.expanduser("~/Downloads/transcript-staging")))

sys.path.insert(0, str(ROOT / "systems" / "eval-harness" / "vendor"))
try:
    import yaml  # uv/PEP 723 install, else the eval-harness vendored copy
except ImportError:
    print(json.dumps({"result": "error",
                      "reason": "PyYAML unavailable (run via `uv run` or keep the vendored copy at systems/eval-harness/vendor)"}))
    sys.exit(1)

FILE_ID_RE = re.compile(r"^file_id:\s*[\"']?([0-9a-f]{32})[\"']?\s*$", re.MULTILINE)


def load_state() -> dict:
    docs = [d for d in yaml.safe_load_all(STATE.read_text()) if d]
    return docs[0] if docs else {}


def file_ids_of(items) -> set:
    """Normalize a state list of file_id strings and/or {file_id: ...} dicts."""
    out = set()
    for it in items or []:
        if isinstance(it, str):
            out.add(it)
        elif isinstance(it, dict) and it.get("file_id"):
            out.add(str(it["file_id"]))
    return out


def vault_file_ids() -> dict:
    """file_id -> vault-relative path, from zzPlaud note frontmatter."""
    found = {}
    zplaud = VAULT / "zzPlaud"
    if not zplaud.is_dir():
        return found
    for md in zplaud.rglob("*.md"):
        try:
            head = md.read_text(errors="replace")[:4096]
        except Exception:
            continue
        if not head.startswith("---"):
            continue
        end = head.find("\n---", 3)
        block = head[3:end] if end != -1 else head[3:]
        m = FILE_ID_RE.search(block)
        if m:
            found.setdefault(m.group(1), str(md.relative_to(VAULT)))
    return found


def note_file_id(note_path: Path):
    try:
        head = note_path.read_text(errors="replace")[:4096]
    except Exception:
        return None
    if not head.startswith("---"):
        return None
    end = head.find("\n---", 3)
    block = head[3:end] if end != -1 else head[3:]
    m = FILE_ID_RE.search(block)
    return m.group(1) if m else None


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Deterministic ingestion-accounting reconcile for plaud-ingest step-06. "
                    "Exit 0 = every discovered recording accounted for (no Ralph needed); "
                    "exit 1 = anomalies (spawn Ralph on the flagged items).")
    ap.add_argument("--json", action="store_true", help="emit the verdict as JSON instead of a table")
    args = ap.parse_args()
    as_json = args.json
    anomalies = []
    rows = []

    if not STATE.is_file():
        print(json.dumps({"result": "error", "reason": f"state file missing: {STATE}"}))
        return 1

    ctx = (load_state() or {}).get("accumulated-context") or {}

    discovered = {}  # file_id -> name
    for rec in ctx.get("new-recordings") or []:
        if isinstance(rec, dict) and rec.get("file_id"):
            discovered[str(rec["file_id"])] = rec.get("name", "?")

    if not discovered:
        # A no-op run has an empty discovered set; reconciling nothing is clean.
        payload = {"result": "pass", "discovered": 0, "anomalies": [],
                   "note": "empty discovered set (no-op run)"}
        print(json.dumps(payload) if as_json else
              "No discovered recordings in state — nothing to reconcile (no-op run).")
        return 0

    classification = ctx.get("recording-classification") or {}
    deferred = (file_ids_of(ctx.get("pending-recordings"))
                | file_ids_of(ctx.get("transcription-triggered"))
                | file_ids_of(ctx.get("stale-staged-files")))
    personal = {str(k) for k, v in classification.items() if v == "personal"}
    unresolved = file_ids_of(ctx.get("unresolved_speakers"))
    ingested_notes = [p for p in (ctx.get("ingested-notes") or []) if isinstance(p, str)]
    staged_files = [p for p in (ctx.get("staged-files") or []) if isinstance(p, str)]

    vault_ids = vault_file_ids()
    if not vault_ids:
        anomalies.append(f"vault file_id scan found nothing under {VAULT}/zzPlaud — "
                         f"vault unreadable or path wrong; cannot confirm ingestion")

    # Check 2 first (it feeds per-recording verdicts): claimed notes on disk.
    note_on_disk = {}
    for rel in ingested_notes:
        p = VAULT / rel
        if not p.is_file():
            anomalies.append(f"ingested-notes path not on disk: {rel}")
            continue
        fid = note_file_id(p)
        note_on_disk[rel] = fid
        if fid and fid not in discovered:
            anomalies.append(f"vault note {rel} carries file_id {fid} which is not in "
                             f"this run's discovered set")

    for fid, name in sorted(discovered.items()):
        outcomes = []
        if fid in vault_ids:
            outcomes.append(f"note:{vault_ids[fid]}")
        if fid in deferred:
            outcomes.append("deferred")
        if fid in personal:
            outcomes.append("personal")
        if fid in unresolved:
            outcomes.append("unresolved-speakers")
        verdict = "OK" if outcomes else "SILENT DROP"
        if not outcomes:
            anomalies.append(f"silent drop: {fid} ({name}) — discovered but in no outcome set")
        rows.append((fid, name, ", ".join(outcomes) or "none", verdict))

    # Check 3: staging leftovers from THIS run.
    if STAGING.is_dir():
        staged_basenames = {Path(s).name for s in staged_files}
        for f in sorted(STAGING.glob("plaud_*")):
            if not f.is_file():
                continue
            if f.name in staged_basenames or any(fid in f.name for fid in discovered):
                anomalies.append(f"staging leftover from this run: {f.name}")

    clean = not anomalies

    if as_json:
        print(json.dumps({
            "result": "pass" if clean else "flag",
            "discovered": len(discovered),
            "ingested_notes": len(ingested_notes),
            "vault_file_ids": len(vault_ids),
            "anomalies": anomalies,
            "rows": [{"file_id": r[0], "name": r[1], "outcome": r[2], "verdict": r[3]}
                     for r in rows],
        }, indent=2))
    else:
        print("| Recording | Outcome | Verdict |")
        print("|-----------|---------|---------|")
        for fid, name, outcome, verdict in rows:
            print(f"| {name[:60]} ({fid[:8]}…) | {outcome} | {'✅' if verdict == 'OK' else '⚠️ ' + verdict} |")
        if clean:
            print(f"\nAll {len(discovered)} discovered recordings accounted for: zero silent drops. "
                  f"({len(ingested_notes)} note(s) verified on disk, staging clean.)")
        else:
            print(f"\nANOMALIES ({len(anomalies)}):")
            for a in anomalies:
                print(f"  - {a}")

    return 0 if clean else 1


if __name__ == "__main__":
    sys.exit(main())
