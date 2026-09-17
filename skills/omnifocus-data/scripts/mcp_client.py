#!/usr/bin/env python3
"""Minimal MCP stdio client for the OmniFocus server.

WHY THIS EXISTS
---------------
`omnifocus_data.py` talks to OmniFocus two ways. AppleScript (osascript) is the
unattended path: it has no session dependency, which is why the canonical pull
uses it. The MCP path exists for the reads the MCP models better — it speaks
OmniFocus's *effective* status, so it excludes archived work that `completed is
false` silently counts.

The MCP is normally reached by an agent through its session connection. A
standalone python3 process has no such connection, so this module spawns the
same launcher the agent's client spawns (`run-server.sh`, which execs
`dist/server.js`) and speaks newline-delimited JSON-RPC over its stdin/stdout.
That is exactly the MCP stdio transport, so the script reaches the same 12 tools
and 46 resources an agent does.

TWO THINGS THE CALLER MUST KNOW
-------------------------------
1. `tools/call query_omnifocus` returns *prose*, not JSON — a human-formatted
   bullet list (see `formatQueryResults` in the server). It is fine for counts
   (`summary: true` returns a parseable "Found N ...") and unsuitable for
   structured extraction: it drops `note` entirely and cannot be parsed reliably
   when a task name contains brackets.
   `resources/read` is the structured path: those return JSON with real fields.

2. Spawning the server costs a node process (a few hundred ms warm, up to ~10s
   cold). Callers should treat a failure here as "fall back to AppleScript",
   never as "OmniFocus is unreachable".
"""

from __future__ import annotations

import json
import os
import select
import subprocess
import time
from pathlib import Path

DEFAULT_SERVER = Path.home() / "develop" / "omnifocus-mcp" / "run-server.sh"
PROTOCOL_VERSION = "2024-11-05"
CLIENT_NAME = "ies-omnifocus-data"
CLIENT_VERSION = "1.0.0"


class McpError(RuntimeError):
    """The MCP server could not be reached, or returned an error."""


def resolve_server() -> Path | None:
    """Locate the launcher. Returns None when it is not installed."""
    override = os.environ.get("OMNIFOCUS_MCP_SERVER")
    if override:
        p = Path(override).expanduser()
        return p if p.is_file() else None
    return DEFAULT_SERVER if DEFAULT_SERVER.is_file() else None


class McpClient:
    """Speaks MCP over a spawned server's stdio. Use as a context manager."""

    def __init__(self, server: Path | None = None, timeout: float = 120.0):
        self.server = server or resolve_server()
        self.timeout = timeout
        self.proc: subprocess.Popen | None = None
        self._next_id = 1

    # -- lifecycle ---------------------------------------------------------

    def __enter__(self) -> "McpClient":
        self.start()
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def start(self) -> None:
        if self.server is None:
            raise McpError("omnifocus-mcp launcher not found")
        try:
            self.proc = subprocess.Popen(
                [str(self.server)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
        except OSError as exc:
            raise McpError(f"could not spawn {self.server}: {exc}") from exc

        try:
            self._request("initialize", {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": CLIENT_NAME, "version": CLIENT_VERSION},
            })
            self._notify("notifications/initialized")
        except Exception:
            # An initialize that never completes leaves a live node process
            # holding OmniFocus; reap it before propagating.
            self.close()
            raise

    def close(self) -> None:
        if self.proc is None:
            return
        try:
            if self.proc.stdin and not self.proc.stdin.closed:
                self.proc.stdin.close()
            self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()
        finally:
            self.proc = None

    # -- transport ---------------------------------------------------------

    def _send(self, payload: dict) -> None:
        if self.proc is None or self.proc.stdin is None:
            raise McpError("client not started")
        try:
            self.proc.stdin.write(json.dumps(payload) + "\n")
            self.proc.stdin.flush()
        except (BrokenPipeError, ValueError) as exc:
            raise McpError(f"server closed the connection: {exc}") from exc

    def _notify(self, method: str, params: dict | None = None) -> None:
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        self._send(msg)

    def _stderr_tail(self) -> str:
        """Best-effort read of whatever the server wrote to stderr."""
        if self.proc is None or self.proc.stderr is None:
            return ""
        try:
            ready, _, _ = select.select([self.proc.stderr], [], [], 0)
            if not ready:
                return ""
            return (self.proc.stderr.readline() or "").strip()
        except Exception:
            return ""

    def _request(self, method: str, params: dict | None = None) -> dict:
        req_id = self._next_id
        self._next_id += 1
        msg = {"jsonrpc": "2.0", "id": req_id, "method": method}
        if params is not None:
            msg["params"] = params
        self._send(msg)

        if self.proc is None or self.proc.stdout is None:
            raise McpError("client not started")

        deadline = time.monotonic() + self.timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                self.close()
                raise McpError(f"{method} timed out after {self.timeout:.0f}s")

            ready, _, _ = select.select([self.proc.stdout], [], [], remaining)
            if not ready:
                self.close()
                raise McpError(f"{method} timed out after {self.timeout:.0f}s")

            line = self.proc.stdout.readline()
            if not line:
                detail = self._stderr_tail()
                self.close()
                raise McpError(f"server exited during {method}{': ' + detail if detail else ''}")

            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                # A non-JSON line on stdout would be a transport violation, but
                # skipping it beats dying on a stray log line.
                continue

            # Ignore unrelated traffic (notifications, server-initiated requests
            # we never make). Match on our own id.
            if obj.get("id") != req_id:
                continue
            if "error" in obj:
                raise McpError(f"{method}: {obj['error'].get('message', obj['error'])}")
            return obj.get("result", {})

    # -- high-level API ----------------------------------------------------

    def call_tool(self, name: str, arguments: dict) -> str:
        """Return the tool's text content. Raises McpError on isError."""
        result = self._request("tools/call", {"name": name, "arguments": arguments})
        if result.get("isError"):
            raise McpError(f"{name} returned an error: {self._text_of(result)}")
        return self._text_of(result)

    def read_resource(self, uri: str) -> str:
        """Return a resource's text. Raises McpError on failure."""
        result = self._request("resources/read", {"uri": uri})
        contents = result.get("contents") or []
        if not contents:
            raise McpError(f"resource {uri} returned no contents")
        return contents[0].get("text", "")

    @staticmethod
    def _text_of(result: dict) -> str:
        parts = [
            c.get("text", "")
            for c in (result.get("content") or [])
            if c.get("type") == "text"
        ]
        return "\n".join(parts)

    # -- OmniFocus conveniences -------------------------------------------

    def query_count(self, **params) -> int:
        """Run a summary query and parse the count out of the prose reply.

        `summary: true` makes the server return exactly "Found N <entity>
        matching your criteria." — the one prose reply that is safe to parse.
        """
        params["summary"] = True
        text = self.call_tool("query_omnifocus", params)
        return _parse_found_count(text)


def _parse_found_count(text: str) -> int:
    marker = "Found "
    if not text.startswith(marker):
        raise McpError(f"unparseable summary reply: {text!r}")
    rest = text[len(marker):]
    digits = rest.split(" ", 1)[0]
    if not digits.isdigit():
        raise McpError(f"unparseable summary reply: {text!r}")
    return int(digits)


def available() -> bool:
    """True when the launcher exists on this machine."""
    return resolve_server() is not None
