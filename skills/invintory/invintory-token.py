#!/usr/bin/env python3
"""
invintory-token.py
Reads config/.env, refreshes INVINTORY_ACCESS_TOKEN if within 5 minutes of
expiry or already expired, writes updated values back to .env.
Prints the valid access token to stdout.

Used by Sterling and any agent needing Invintory MCP access outside Cowork.
Run via Desktop Commander (host process), not sandbox bash.

Usage:
    python3 skills/invintory-token.py
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = REPO_ROOT / "config" / ".env"
TOKEN_URL_DEFAULT = "https://api.invintory.com/oauth/token"
REFRESH_BUFFER_SECONDS = 300  # refresh if within 5 min of expiry


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


def write_env_key(key: str, value: str) -> None:
    lines = ENV_PATH.read_text().splitlines()
    updated = False
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"{key}=") and not stripped.startswith("#"):
            new_lines.append(f"{key}={value}")
            updated = True
        else:
            new_lines.append(line)
    if not updated:
        new_lines.append(f"{key}={value}")
    ENV_PATH.write_text("\n".join(new_lines) + "\n")


def refresh_access_token(env: dict[str, str]) -> str:
    required = ["INVINTORY_REFRESH_TOKEN", "INVINTORY_CLIENT_ID", "INVINTORY_CLIENT_SECRET"]
    missing = [k for k in required if not env.get(k)]
    if missing:
        print(
            f"ERROR: Missing required .env keys for token refresh: {', '.join(missing)}\n"
            "Re-authorize via: claude mcp add invintory https://api.invintory.com/mcp",
            file=sys.stderr,
        )
        sys.exit(1)

    payload = json.dumps({
        "grant_type": "refresh_token",
        "refresh_token": env["INVINTORY_REFRESH_TOKEN"],
        "client_id": env["INVINTORY_CLIENT_ID"],
        "client_secret": env["INVINTORY_CLIENT_SECRET"],
    }).encode()

    url = env.get("INVINTORY_TOKEN_URL", TOKEN_URL_DEFAULT)
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        print(
            f"ERROR: Token refresh failed — HTTP {e.code}: {body}\n"
            "If 401/403: re-authorize via: claude mcp add invintory https://api.invintory.com/mcp",
            file=sys.stderr,
        )
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Network error during token refresh: {e.reason}", file=sys.stderr)
        sys.exit(1)

    new_token = result["access_token"]
    expires_in = result.get("expires_in", 3600)
    expires_at = int(time.time()) + int(expires_in)

    write_env_key("INVINTORY_ACCESS_TOKEN", new_token)
    write_env_key("INVINTORY_TOKEN_EXPIRES", str(expires_at))
    if "refresh_token" in result:
        write_env_key("INVINTORY_REFRESH_TOKEN", result["refresh_token"])

    return new_token


def get_valid_token() -> str:
    env = load_env()
    expires = int(env.get("INVINTORY_TOKEN_EXPIRES", "0"))
    if time.time() > expires - REFRESH_BUFFER_SECONDS:
        return refresh_access_token(env)
    token = env.get("INVINTORY_ACCESS_TOKEN", "")
    if not token:
        print("ERROR: INVINTORY_ACCESS_TOKEN missing from config/.env", file=sys.stderr)
        sys.exit(1)
    return token


if __name__ == "__main__":
    print(get_valid_token())
