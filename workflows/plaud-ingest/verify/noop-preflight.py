#!/usr/bin/env python3
"""Single-turn no-op preflight for plaud-ingest.

Why this exists: on an ordinary day the Plaud discovery finds nothing new, but
the full run still pays for the Knox persona load, the whole workflow read, a
full API pagination, and a complete Obsidian vault walk before it can say so.
The 2026-10-26 boot spent 1.65M input tokens and ~24 turns to report "No new
Plaud recordings found".

This preflight answers the only question that matters — has anything new
appeared since the last full enumeration? — in one API call, before any persona
or vault work:

    NOOP     nothing new since the last full run; take the no-op exit now
    NEW      something new; proceed to the full step-01 discovery
    UNKNOWN  cannot prove no-op (missing marker/ledger, auth, network); proceed
    RESUME   state.yaml is in-progress; follow the normal STATE CHECK

It never aborts and never gates on a token file. Any doubt resolves to NEW/
UNKNOWN, which falls through to the existing full run. That preserves the
load-bearing TOKEN PRE-CHECK PROHIBITION (err-20260730T143152-S0TRMO): the
Chrome login flow still belongs to the discovery skill, not to a pre-check.

The signal is data/.plaud-last-seen.json, written by step-01 after every
successful full enumeration. One cheap /file/simple/web call returns the newest
50 recordings; if the newest id matches the marker and every returned id is in
the dedup ledger, no recording has been added since that enumeration.

Usage:  python3 workflows/plaud-ingest/verify/noop-preflight.py
Exit:   always 0. Read the first token of stdout.
"""
import contextlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STATE = ROOT / "workflows" / "plaud-ingest" / "state.yaml"
MARKER = ROOT / "data" / ".plaud-last-seen.json"
LEDGER = ROOT / "systems" / "eval-harness" / "skill-runs" / "plaud-discover-ledger-latest.json"
FETCH_SCRIPT = ROOT / "skills" / "plaud-transcripts" / "scripts" / "fetch_plaud.py"

PEEK_LIMIT = 50


def emit(verdict, detail):
    print(f"{verdict} {detail}".strip())
    sys.exit(0)


def state_status():
    try:
        text = STATE.read_text()
    except Exception:
        return None
    m = re.search(r"^status:\s*(\S+)", text, re.MULTILINE)
    return m.group(1).strip("'\"") if m else None


def load_json(path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def known_ids():
    """Every id/title the dedup ledger has already accounted for, or None."""
    entries = load_json(LEDGER)
    if not isinstance(entries, list):
        return None
    known = set()
    for e in entries:
        if not isinstance(e, dict):
            continue
        for key in ("id_or_title", "name", "file_id"):
            v = e.get(key)
            if v:
                known.add(str(v))
    return known


def recording_id(rec):
    return str(rec.get("file_id") or rec.get("id") or "")


def main():
    if state_status() == "in-progress":
        emit("RESUME", "plaud-ingest state.yaml is in-progress; follow STATE CHECK")

    marker = load_json(MARKER)
    if not isinstance(marker, dict) or not marker.get("newest_file_id"):
        emit("UNKNOWN", "no data/.plaud-last-seen.json marker; run full discovery")

    # Import the fetch script's auth/API helpers. Import failures resolve to
    # UNKNOWN (proceed), never to an abort.
    sys.path.insert(0, str(FETCH_SCRIPT.parent))
    try:
        import fetch_plaud  # noqa: E402
    except Exception as e:
        emit("UNKNOWN", f"fetch_plaud import failed ({e}); run full discovery")

    try:
        # get_token() prints progress; keep stdout clean for the verdict.
        with contextlib.redirect_stdout(sys.stderr):
            token = fetch_plaud.get_token()
    except SystemExit:
        emit("UNKNOWN", "no cached token/credentials; let the full run handle auth")
    except Exception as e:
        emit("UNKNOWN", f"token acquisition failed ({e}); run full discovery")

    try:
        params = {
            "skip": 0,
            "limit": PEEK_LIMIT,
            "is_trash": 0,
            "sort_by": "start_time",
            "is_desc": "true",
        }
        resp = fetch_plaud.api_get(token, "/file/simple/web", params=params)
        if resp.status_code != 200:
            emit("UNKNOWN", f"API HTTP {resp.status_code}; run full discovery")
        body = resp.json()
        recs = body.get("data_file_list", body.get("data", []))
        if isinstance(recs, dict):
            recs = recs.get("items", recs.get("list", []))
        if not isinstance(recs, list) or not recs:
            emit("UNKNOWN", "API returned no records; run full discovery")
    except Exception as e:
        emit("UNKNOWN", f"API peek failed ({e}); run full discovery")

    ids = [recording_id(r) for r in recs if recording_id(r)]
    newest_id = ids[0] if ids else ""
    if not newest_id:
        emit("UNKNOWN", "could not read a recording id; run full discovery")

    if newest_id != str(marker.get("newest_file_id")):
        emit("NEW", f"newest id {newest_id} != marker {marker.get('newest_file_id')}")

    known = known_ids()
    if known is not None:
        unknown = [i for i in ids if i not in known]
        if unknown:
            emit("NEW", f"{len(unknown)} recording(s) not in the dedup ledger")

    # Nothing new: refresh the marker's liveness fields and take the no-op exit.
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    try:
        marker["checked_at"] = now
        marker["last_noop_at"] = now
        MARKER.write_text(json.dumps(marker, indent=2) + "\n")
    except Exception:
        pass
    emit("NOOP", f"newest recording unchanged ({newest_id}); nothing to do")


if __name__ == "__main__":
    main()
