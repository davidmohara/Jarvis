#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Read-only Plaud adapter over the official Plaud MCP server (stdio transport).

Why this exists
---------------
The fetch pipeline historically scraped Plaud's private web routes
(api.plaud.ai /file/simple/web and /file/detail). Those routes move whenever
Plaud changes its web client. The official MCP rides a documented partner API
instead, and it is read-only, which is all this module does.

The rename write and the speaker read for verification stay on the legacy
API inside fetch_plaud.py. See reference/plaud-v4-rewrite-plan.md.

Transport constraint
--------------------
This module spawns the MCP server locally over stdio (newline-delimited
JSON-RPC 2.0). Recording data never passes through Plaud's hosted MCP server.
Do NOT replace this with a hosted/connector form for this account: the
recordings include client work.

Auth
----
OAuth, tokens at ~/.plaud/tokens-mcp.json, separate from the legacy JWT at
~/.config/plaud/token.json. A missing or expired token surfaces as
McpAuthError. Sign in once with:

    npx -y @plaud-ai/mcp@0.3.14 login

The login tool opens a browser and blocks for the callback, so it is a
supervised step, not something an unattended run can complete.

CLI for diagnostics
-------------------
    python3 plaud_read.py status
    python3 plaud_read.py list 2026-11-03
    python3 plaud_read.py transcript <file_id>
    python3 plaud_read.py summary <file_id>
"""

import argparse
import atexit
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
from contextlib import contextmanager
from datetime import datetime, date, timezone

# Pin the tested MCP version. Upgrade deliberately, not with @latest.
MCP_PACKAGE = "@plaud-ai/mcp@0.3.14"
DEFAULT_MCP_CMD = ["npx", "-y", MCP_PACKAGE]

MCP_START_TIMEOUT = 120      # npx may need to download the package on first use
MCP_CALL_TIMEOUT = 180
TRANSCRIPT_PAGE_LIMIT = 500  # server maximum

# The partner API prefixes object ids with "of_" (for example
# "of_900d3853c0a06d570942db021be3853d"). The rest of the pipeline, the
# staging filenames, and the vault frontmatter all use the bare legacy id, so
# the adapter strips the prefix on the way out and adds it on the way in.
MCP_ID_PREFIX = "of_"
_LEGACY_ID_RE = re.compile(r"^[0-9a-f]{32}$")


def _to_mcp_id(file_id):
    """Add the partner API's object-id prefix when given a bare legacy id."""
    fid = str(file_id or "")
    if fid.startswith(MCP_ID_PREFIX):
        return fid
    if _LEGACY_ID_RE.match(fid):
        return MCP_ID_PREFIX + fid
    return fid


def _to_legacy_id(file_id):
    """Strip the partner API prefix so downstream code sees the legacy id."""
    fid = str(file_id or "")
    return fid[len(MCP_ID_PREFIX):] if fid.startswith(MCP_ID_PREFIX) else fid

# The server names the block in a prose preamble first, then opens the real
# block with a source attribute. Requiring the attribute avoids matching the
# mention in the preamble.
_UNTRUSTED_RE = re.compile(
    r'<untrusted-user-data-[0-9a-f]+\s+source="[^"]*">\n?(.*?)\n?</untrusted-user-data-[0-9a-f]+>',
    re.S,
)

# The partner API prepends a rendered summary-card reference that the legacy
# api path never returns. Strip it so both read sources stage the same text.
_SUMMARY_CARD_RE = re.compile(
    r"^\s*\[\]\(plaud://image\?type=summaryCard[^)]*\)\s*$\n?",
    re.M,
)
_SUMMARY_IMAGE_RE = re.compile(r"^\s*!\[[^\]]*\]\(permanent/[^)]*\)\s*$\n?", re.M)


class McpError(RuntimeError):
    """Any failure talking to the MCP server or reading its result."""


class McpAuthError(McpError):
    """The MCP has no usable OAuth token."""


class McpUnavailableError(McpError):
    """Node/npx or the MCP package is not available on this machine."""


def _strip_untrusted(text):
    """The MCP wraps user data in a random untrusted-data tag. Return the payload."""
    if not isinstance(text, str):
        return text
    match = _UNTRUSTED_RE.search(text)
    return match.group(1) if match else text


def _is_auth_error(text):
    """Classify an MCP response as an auth failure.

    Never scan a data payload: a transcript that mentions "401(k)" would
    otherwise be misread as a 401. Data payloads are wrapped in the
    untrusted-data tag, and a bare 401 only counts in a short message.
    """
    raw = text or ""
    if "<untrusted-user-data-" in raw:
        return False
    lowered = raw.lower()
    if (
        "not authenticated" in lowered
        or "auth_failed" in lowered
        or "token invalid or expired" in lowered
    ):
        return True
    return len(lowered) < 400 and "401" in lowered


def mcp_command():
    """Resolve the MCP launch command.

    PLAUD_MCP_CMD (shell-like string) overrides the default. It is split on
    whitespace, which is enough for the documented node invocations.
    """
    override = os.environ.get("PLAUD_MCP_CMD", "").strip()
    if override:
        return override.split()
    return list(DEFAULT_MCP_CMD)


def mcp_available():
    """True when the configured MCP command can be launched."""
    cmd = mcp_command()
    return bool(cmd) and shutil.which(cmd[0]) is not None


class PlaudMcp:
    """Minimal MCP stdio client: initialize, then tools/call."""

    def __init__(self, cmd=None, call_timeout=MCP_CALL_TIMEOUT):
        self.cmd = cmd or mcp_command()
        self.call_timeout = call_timeout
        self._proc = None
        self._next_id = 0
        self._lines = queue.Queue()
        self._stderr = []
        self._threads = []

    # -- lifecycle ---------------------------------------------------------

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    def start(self):
        if shutil.which(self.cmd[0]) is None:
            raise McpUnavailableError(
                f"MCP launcher not found: {self.cmd[0]}. Node/npx is required for "
                f"the stdio MCP read path."
            )

        try:
            self._proc = subprocess.Popen(
                self.cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env={**os.environ, "NO_COLOR": "1"},
            )
        except OSError as exc:
            raise McpUnavailableError(f"Could not start the Plaud MCP: {exc}") from exc

        self._threads = [
            threading.Thread(target=self._pump_stdout, daemon=True),
            threading.Thread(target=self._pump_stderr, daemon=True),
        ]
        for thread in self._threads:
            thread.start()

        response = self._rpc(
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "ies-plaud-read", "version": "1.0"},
            },
            timeout=MCP_START_TIMEOUT,
        )
        if "error" in response:
            raise McpError(f"MCP initialize failed: {response['error']}")

        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def close(self):
        proc = self._proc
        self._proc = None
        if proc is None:
            return
        try:
            if proc.stdin:
                proc.stdin.close()
        except Exception:
            pass
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    # -- io ----------------------------------------------------------------

    def _pump_stdout(self):
        proc = self._proc
        if proc is None or proc.stdout is None:
            return
        for line in proc.stdout:
            line = line.strip()
            if line:
                self._lines.put(line)

    def _pump_stderr(self):
        proc = self._proc
        if proc is None or proc.stderr is None:
            return
        for line in proc.stderr:
            self._stderr.append(line.rstrip())
            if len(self._stderr) > 80:
                del self._stderr[:-80]

    def _send(self, message):
        if self._proc is None or self._proc.stdin is None:
            raise McpError("MCP process is not running")
        self._proc.stdin.write(json.dumps(message) + "\n")
        self._proc.stdin.flush()

    def _rpc(self, method, params=None, timeout=MCP_CALL_TIMEOUT):
        self._next_id += 1
        request_id = self._next_id
        message = {"jsonrpc": "2.0", "id": request_id, "method": method}
        if params is not None:
            message["params"] = params
        self._send(message)

        deadline = datetime.now().timestamp() + timeout
        while True:
            remaining = deadline - datetime.now().timestamp()
            if remaining <= 0:
                tail = "\n".join(self._stderr[-5:])
                raise McpError(
                    f"MCP call '{method}' timed out after {timeout}s"
                    + (f"\nserver stderr tail:\n{tail}" if tail else "")
                )
            try:
                line = self._lines.get(timeout=remaining)
            except queue.Empty:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if payload.get("id") != request_id:
                continue  # notification or a response to something else
            return payload

    # -- tools -------------------------------------------------------------

    def call_tool(self, name, arguments=None, _retry=True):
        response = self._rpc("tools/call", {"name": name, "arguments": arguments or {}})
        if "error" in response:
            raise McpError(f"MCP tool '{name}' failed: {response['error']}")

        result = response.get("result") or {}
        content = result.get("content") or []
        text = ""
        for item in content:
            if item.get("type") == "text":
                text = item.get("text", "")
                break

        auth_error = False
        if result.get("isError"):
            if _is_auth_error(text):
                auth_error = True
            else:
                raise McpError(f"MCP tool '{name}' returned an error: {text[:400]}")
        elif _is_auth_error(text) and not text.lstrip().startswith(("{", "[", "<")):
            auth_error = True

        if auth_error:
            # A 401 can be a transient refresh race. Retry once inside the same
            # server process before declaring the token dead.
            if _retry:
                time.sleep(2)
                return self.call_tool(name, arguments, _retry=False)
            raise McpAuthError(
                "Plaud MCP is not authenticated. Run "
                f"`npx -y {MCP_PACKAGE} login` and complete the browser flow, "
                "then retry."
            )

        return _strip_untrusted(text)

    def call_json(self, name, arguments=None):
        text = self.call_tool(name, arguments)
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise McpError(
                f"MCP tool '{name}' did not return JSON: {text[:300]}"
            ) from exc


# One long-lived server process per client process. Spawning a fresh MCP
# process per call caused refresh-token races: concurrent processes read and
# rotate the same token file, and later calls came back 401. Reusing one
# process lets the server own its refresh loop.
_shared_client = None


def _client():
    """Return the shared MCP client, restarting it if the process died."""
    global _shared_client
    if (
        _shared_client is None
        or _shared_client._proc is None
        or _shared_client._proc.poll() is not None
    ):
        if _shared_client is not None:
            try:
                _shared_client.close()
            except Exception:
                pass
        client = PlaudMcp()
        client.start()
        _shared_client = client
    return _shared_client


def close():
    """Close the shared MCP client. Also runs at interpreter exit."""
    global _shared_client
    if _shared_client is not None:
        try:
            _shared_client.close()
        finally:
            _shared_client = None


atexit.register(close)


@contextmanager
def _session():
    """Yield the shared client without closing it on block exit."""
    yield _client()


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

def _epoch_seconds(value):
    """Normalize an API timestamp (ISO string, epoch s, or epoch ms) to seconds."""
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return value / 1000 if value > 1e12 else value
    text = str(value).strip()
    if not text:
        return 0
    if text.isdigit():
        number = int(text)
        return number / 1000 if number > 1e12 else number
    try:
        # Partner API timestamps are naive UTC strings ("2026-11-02T20:01:38").
        # Treat a missing offset as UTC so the epoch matches the legacy
        # start_time instead of shifting by the local offset.
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.timestamp()
    except ValueError:
        return 0


def _duration_ms(value):
    """Duration is milliseconds in both the legacy list and the MCP."""
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _file_items(payload):
    """Pull the item list out of whatever wrapper the partner API returned."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("data", "items", "list", "recordings", "files"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    return []


def normalize_recording(item):
    """Map an MCP file summary onto the legacy recording shape fetch_plaud uses."""
    raw_id = item.get("id") or item.get("file_id") or item.get("object_id") or ""
    file_id = _to_legacy_id(raw_id)
    name = item.get("name") or item.get("filename") or item.get("fullname") or file_id
    # start_at is the recording start; created_at is the ingest time and can be
    # hours later. Prefer the real start so date filtering matches the api path.
    start = (
        item.get("start_at")
        or item.get("start_time")
        or item.get("created_at")
        or item.get("created_at_show")
        or item.get("create_time")
        or 0
    )
    return {
        "id": file_id,
        "file_id": file_id,
        "mcp_id": raw_id,
        "filename": name,
        "fullname": name,
        "start_time": _epoch_seconds(start),
        "duration": _duration_ms(item.get("duration")),
        "is_trans": item.get("is_trans"),
        "is_summary": item.get("is_summary"),
        "is_trash": bool(item.get("is_trash", False)),
        "_read_source": "mcp",
    }


# ---------------------------------------------------------------------------
# Public read API
# ---------------------------------------------------------------------------

def list_recordings(target_date=None, page_size=100, max_pages=200):
    """List recordings, optionally for one local date, normalized to the legacy shape.

    The MCP applies date_from/date_to server-side, so a filtered result is exact
    and can be paged safely. No query term is used here.
    """
    recordings = []
    with _session() as mcp:
        page = 1
        while page <= max_pages:
            arguments = {"page": page, "page_size": page_size}
            if target_date:
                arguments["date_from"] = target_date
                arguments["date_to"] = target_date
            payload = mcp.call_json("list_files", arguments)
            items = _file_items(payload)
            if not items:
                break
            recordings.extend(normalize_recording(item) for item in items)
            if len(items) < page_size:
                break
            page += 1

    if target_date:
        wanted = str(target_date)[:10]
        recordings = [
            rec for rec in recordings
            if datetime.fromtimestamp(rec["start_time"]).strftime("%Y-%m-%d") == wanted
            or not rec["start_time"]
        ]
    return [rec for rec in recordings if not rec.get("is_trash")]


def preflight():
    """Verify MCP authentication before a run does any work.

    Raises McpAuthError (or McpError) on failure so the caller can fail closed
    before staging anything. Returns a short identity string on success.
    """
    with _session() as mcp:
        text = mcp.call_tool("get_current_user")
    try:
        user = json.loads(text)
    except json.JSONDecodeError:
        return "unknown"
    return (
        user.get("email")
        or user.get("nickname")
        or user.get("id")
        or "unknown"
    )


def get_file(file_id):
    """Return the raw MCP file record (source_list, note_list, presigned_url)."""
    with _session() as mcp:
        return mcp.call_json("get_file", {"file_id": _to_mcp_id(file_id)})


def get_detail(file_id):
    """Return a legacy-shaped detail dict so existing status/summary parsing works."""
    record = get_file(file_id)
    source_list = record.get("source_list") or []
    note_list = record.get("note_list") or []

    content_list = []
    for block in source_list:
        data_type = block.get("data_type")
        if not data_type:
            continue
        content_list.append({
            "data_type": data_type,
            "task_status": 1 if (block.get("data_content") or block.get("data_link")) else 0,
            "data_link": block.get("data_link", ""),
        })

    pre_download = []
    for note in note_list:
        data_type = note.get("data_type") or ""
        if data_type != "auto_sum_note":
            continue
        text = _note_text(note)
        if text:
            pre_download.append({
                "data_id": f"auto_sum:{note.get('data_id', '')}",
                "data_content": {"ai_content": text},
            })

    name = record.get("name") or record.get("filename") or file_id
    start = (
        record.get("start_at")
        or record.get("start_time")
        or record.get("created_at")
        or record.get("created_at_show")
        or 0
    )
    return {
        "filename": name,
        "fullname": name,
        "start_time": _epoch_seconds(start),
        "duration": _duration_ms(record.get("duration")),
        "content_list": content_list,
        "pre_download_content_list": pre_download,
        "_read_source": "mcp",
        "_raw": record,
    }


def get_transcript_segments(file_id, block="transaction"):
    """Fetch every page of transcript segments for one recording.

    Returns a list of segment dicts in the API's own shape. The caller decides
    how to render them, which keeps the staging markdown format stable.
    """
    segments = []
    cursor = None
    mcp_file_id = _to_mcp_id(file_id)
    with _session() as mcp:
        while True:
            arguments = {
                "file_id": mcp_file_id,
                "block": block,
                "limit": TRANSCRIPT_PAGE_LIMIT,
            }
            if cursor:
                arguments["cursor"] = cursor
            text = mcp.call_tool("get_transcript", arguments)
            if text.lstrip().startswith("Block "):
                return []  # block not available for this recording
            try:
                payload = json.loads(text)
            except json.JSONDecodeError as exc:
                raise McpError(
                    f"get_transcript returned non-JSON for {file_id}: {text[:300]}"
                ) from exc

            if isinstance(payload, list):
                segments.extend(payload)
                break
            segments.extend(payload.get("segments") or payload.get("items") or [])
            cursor = payload.get("next_cursor")
            if not cursor:
                break
    return segments


def _note_text(note):
    """Extract readable markdown from one note item."""
    if isinstance(note, str):
        return note.strip()
    for key in ("data_content", "content", "markdown", "text", "ai_content"):
        value = note.get(key)
        if isinstance(value, str) and value.strip():
            stripped = value.strip()
            if stripped.startswith("{"):
                try:
                    parsed = json.loads(stripped)
                    if isinstance(parsed, dict):
                        inner = parsed.get("ai_content") or parsed.get("content")
                        if isinstance(inner, str) and inner.strip():
                            return inner.strip()
                except json.JSONDecodeError:
                    pass
            return stripped
    return ""


def get_summary(file_id):
    """Return the AI summary markdown for one recording, or '' when absent."""
    payload = None
    with _session() as mcp:
        text = mcp.call_tool("get_note", {"file_id": _to_mcp_id(file_id)})
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return text.strip()

    notes = payload if isinstance(payload, list) else [payload]
    parts = []
    for note in notes:
        if isinstance(note, dict) and note.get("data_type") not in (None, "", "auto_sum_note"):
            continue
        text_part = _note_text(note)
        if text_part:
            parts.append(text_part)
    combined = "\n\n".join(parts)
    combined = _SUMMARY_IMAGE_RE.sub("", combined)
    combined = _SUMMARY_CARD_RE.sub("", combined)
    return combined.strip()


def format_segments(segments):
    """Render segments exactly like fetch_plaud._format_segments does.

    Kept here so the adapter can be used on its own for diagnostics. The
    fetch pipeline keeps using its own renderer to hold the staging contract.
    """
    lines = []
    for seg in segments:
        speaker = seg.get("speaker", seg.get("spk", "Unknown"))
        text = seg.get("content", seg.get("text", seg.get("trans_text", "")))
        start_ms = seg.get("start_time", seg.get("st", 0))
        start_s = start_ms / 1000 if start_ms > 1000 else start_ms
        minutes = int(start_s // 60)
        seconds = int(start_s % 60)
        if speaker and text:
            lines.append(f"[{minutes:02d}:{seconds:02d}] **{speaker}**: {text}")
        elif text:
            lines.append(text)
    return "\n\n".join(lines)


# ---------------------------------------------------------------------------
# Diagnostic CLI
# ---------------------------------------------------------------------------

def _cmd_status():
    with _session() as mcp:
        return mcp.call_tool("get_current_user")


def _cmd_list(target_date):
    recordings = list_recordings(target_date)
    print(json.dumps(recordings, indent=2))
    return f"{len(recordings)} recording(s)"


def _cmd_transcript(file_id):
    segments = get_transcript_segments(file_id)
    print(format_segments(segments))
    return f"{len(segments)} segment(s)"


def _cmd_summary(file_id):
    print(get_summary(file_id))
    return "summary printed"


def main():
    parser = argparse.ArgumentParser(description="Read-only Plaud MCP adapter")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="show the authenticated Plaud user")
    list_parser = sub.add_parser("list", help="list recordings for a date (YYYY-MM-DD)")
    list_parser.add_argument("date", nargs="?", default=None)
    transcript_parser = sub.add_parser("transcript", help="print one transcript")
    transcript_parser.add_argument("file_id")
    summary_parser = sub.add_parser("summary", help="print one AI summary")
    summary_parser.add_argument("file_id")
    args = parser.parse_args()

    try:
        if args.command == "status":
            print(_cmd_status())
        elif args.command == "list":
            print(_cmd_list(args.date))
        elif args.command == "transcript":
            print(_cmd_transcript(args.file_id))
        elif args.command == "summary":
            print(_cmd_summary(args.file_id))
    except McpAuthError as exc:
        sys.stderr.write(f"AUTH: {exc}\n")
        sys.exit(2)
    except (McpError, McpUnavailableError) as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
