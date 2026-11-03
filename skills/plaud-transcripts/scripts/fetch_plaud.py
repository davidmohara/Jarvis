#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///
"""
Fetch Plaud recordings for a target date and save transcripts to staging.

Usage:
  python3 fetch_plaud.py                    # yesterday's recordings
  python3 fetch_plaud.py 2026-03-18         # specific date
  python3 fetch_plaud.py --all              # all recordings
  python3 fetch_plaud.py --login            # force re-login (ignore cached token)
  python3 fetch_plaud.py --read-source api  # legacy web API (rollback path)
                                            # Default is mcp: discovery and
                                            # transcripts via the official Plaud
                                            # MCP (local stdio). Requires
                                            # `npx -y @plaud-ai/mcp@0.3.14 login`.
                                            # An auth failure fails closed with
                                            # PLAUD_READ_STATUS=failed.

Authentication:
  The script authenticates automatically. It reads credentials from environment
  variables or ~/.config/plaud/credentials.json, logs in via the Plaud API, and
  caches the token to ~/.config/plaud/token.json. Tokens last ~300 days and auto-
  refresh when within 30 days of expiry.

  Non-interactive (required): if no cached token and no credentials are found,
  the script exits with code 2 and a helpful error on stderr — the calling agent
  handles the Chrome login flow to capture a token from web.plaud.ai.

  Environment variables:
    PLAUD_EMAIL    — your Plaud account email
    PLAUD_PASSWORD — your Plaud account password
    PLAUD_REGION   — "us" (default) or "eu"

  If you use Google Sign-In on Plaud, set a password first via "Forgot Password"
  at web.plaud.ai.
"""

import argparse
import requests
import json
import os
import sys
import time
import base64
import random
import re
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_BASES = {
    "us": "https://api.plaud.ai",
    "eu": "https://api-euc1.plaud.ai",
}

STAGING_DIR = os.path.expanduser("~/Downloads/transcript-staging")
CONFIG_DIR = os.path.expanduser("~/.config/plaud")
TOKEN_PATH = os.path.join(CONFIG_DIR, "token.json")
CREDS_PATH = os.path.join(CONFIG_DIR, "credentials.json")

TOKEN_REFRESH_BUFFER_DAYS = 30

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def save_credentials(email, password, region="us"):
    """Save credentials to config file with restrictive permissions."""
    os.makedirs(CONFIG_DIR, mode=0o700, exist_ok=True)
    data = {"email": email, "password": password, "region": region}
    with open(CREDS_PATH, "w") as f:
        json.dump(data, f)
    os.chmod(CREDS_PATH, 0o600)
    print(f"  Credentials saved to {CREDS_PATH}")


def load_credentials():
    """Load credentials from config file or environment."""
    # Environment variables take priority
    email = os.environ.get("PLAUD_EMAIL")
    password = os.environ.get("PLAUD_PASSWORD")
    region = os.environ.get("PLAUD_REGION", "us")

    if email and password:
        return {"email": email, "password": password, "region": region}

    # Fall back to saved credentials file
    if os.path.exists(CREDS_PATH):
        with open(CREDS_PATH) as f:
            return json.load(f)

    return None


def missing_credentials_error():
    """Non-interactive credential error: what went wrong, what was expected, what to try."""
    sys.stderr.write(
        "ERROR: no usable Plaud credentials.\n"
        "  Expected: a cached token at ~/.config/plaud/token.json, credentials at\n"
        "  ~/.config/plaud/credentials.json, or PLAUD_EMAIL + PLAUD_PASSWORD env vars\n"
        "  (PLAUD_REGION optional, 'us' or 'eu').\n"
        "  Try one of:\n"
        "    - export PLAUD_EMAIL=... PLAUD_PASSWORD=... and rerun\n"
        "    - write ~/.config/plaud/credentials.json ({\"email\": ..., \"password\": ..., \"region\": \"us\"})\n"
        "    - use the Chrome login flow to capture a token from web.plaud.ai\n"
        "  Note: if you use Google Sign-In on Plaud, set a password first via 'Forgot\n"
        "  Password' at web.plaud.ai — the API needs email/password.\n"
    )


def decode_jwt_expiry(token):
    """Extract iat and exp from a JWT without external dependencies."""
    parts = token.split(".")
    if len(parts) != 3:
        return None, None

    # JWT base64url decode (add padding)
    payload_b64 = parts[1]
    padding = 4 - len(payload_b64) % 4
    if padding != 4:
        payload_b64 += "=" * padding

    try:
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        return payload.get("iat", 0), payload.get("exp", 0)
    except Exception:
        return None, None


def load_cached_token():
    """Load cached token if it exists and isn't expiring soon."""
    if not os.path.exists(TOKEN_PATH):
        return None

    with open(TOKEN_PATH) as f:
        data = json.load(f)

    token = data.get("access_token")
    expires_at = data.get("expires_at", 0)

    # Check if token expires within the refresh buffer
    buffer_ms = TOKEN_REFRESH_BUFFER_DAYS * 24 * 60 * 60 * 1000
    now_ms = datetime.now().timestamp() * 1000

    if now_ms + buffer_ms > expires_at:
        print("  Cached token expiring soon, will re-authenticate")
        return None

    days_remaining = (expires_at - now_ms) / (24 * 60 * 60 * 1000)
    print(f"  Using cached token ({int(days_remaining)} days remaining)")
    return token


def save_token(access_token):
    """Cache the token with expiry metadata."""
    os.makedirs(CONFIG_DIR, mode=0o700, exist_ok=True)

    iat, exp = decode_jwt_expiry(access_token)
    data = {
        "access_token": access_token,
        "issued_at": (iat or 0) * 1000,
        "expires_at": (exp or 0) * 1000,
        "saved_at": datetime.now().isoformat(),
    }

    with open(TOKEN_PATH, "w") as f:
        json.dump(data, f, indent=2)
    os.chmod(TOKEN_PATH, 0o600)


def login(creds):
    """Authenticate with Plaud API and return a bearer token."""
    region = creds.get("region", "us")
    api_base = API_BASES.get(region, API_BASES["us"])

    print(f"  Logging in as {creds['email']} ({region} region)...")

    resp = requests.post(
        f"{api_base}/auth/access-token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": creds["email"],
            "password": creds["password"],
        },
    )

    if resp.status_code != 200:
        print(f"  Login request failed: HTTP {resp.status_code}")
        print(f"  Response: {resp.text[:500]}")
        return None

    data = resp.json()

    if data.get("status") != 0 or not data.get("access_token"):
        msg = data.get("msg", f"status={data.get('status')}")
        print(f"  Login failed: {msg}")
        return None

    token = data["access_token"]
    save_token(token)

    iat, exp = decode_jwt_expiry(token)
    if exp:
        days = (exp * 1000 - datetime.now().timestamp() * 1000) / (24 * 60 * 60 * 1000)
        print(f"  Login successful. Token valid for ~{int(days)} days.")

    return token


def get_token(force_login=False):
    """Get a valid bearer token — cached, refreshed, or fresh login."""
    if not force_login:
        cached = load_cached_token()
        if cached:
            return cached

    # Need to authenticate — try saved credentials first
    creds = load_credentials()

    # Non-interactive only: no credentials means exit code 2 so the calling
    # agent can trigger the Chrome login flow
    if not creds or not creds.get("password"):
        missing_credentials_error()
        sys.exit(2)

    token = login(creds)
    if not token:
        print("Authentication failed. Check your email/password.")
        print("  If you use Google Sign-In, set a password via 'Forgot Password' at web.plaud.ai")
        sys.exit(1)

    return token


# ---------------------------------------------------------------------------
# API calls — endpoints reverse-engineered from plaud-toolkit
#   List recordings:        GET /file/simple/web
#   Recording detail+trans: GET /file/detail/{id}
#   User info:              GET /user/me
# ---------------------------------------------------------------------------

def make_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Origin": "https://web.plaud.ai",
        "Referer": "https://web.plaud.ai/",
        "app-platform": "web",
        "edit-from": "web",
    }


def get_api_base():
    """Determine API base from saved credentials region."""
    creds = load_credentials()
    region = (creds or {}).get("region", "us")
    return API_BASES.get(region, API_BASES["us"])


def api_get(token, path, params=None):
    """Make an authenticated GET request, handling region redirects."""
    headers = make_headers(token)
    api_base = get_api_base()
    resp = requests.get(f"{api_base}{path}", headers=headers, params=params)

    # HTTP 302 redirect (wrong region)
    if resp.status_code == 302:
        location = resp.headers.get("Location", "")
        if location:
            resp = requests.get(location, headers=headers, params=params)
        return resp

    # Plaud API-level region redirect: status=-302 with correct domain in data
    if resp.status_code == 200:
        try:
            body = resp.json()
            if body.get("status") == -302:
                redirect_domain = (body.get("data") or {}).get("domains", {}).get("api", "")
                if redirect_domain:
                    new_url = f"https://{redirect_domain}{path}"
                    resp = requests.get(new_url, headers=headers, params=params)
        except Exception:
            pass

    return resp


def check_api_response(resp, context):
    """Validate an HTTP response and Plaud's in-band status.

    Plaud reports many failures with HTTP 200 and a non-zero `status` in the
    body (for example -1800907 "Please re-align version"), so an HTTP status
    check alone is not enough. Returns the parsed JSON body on success, or
    None on failure, logging both layers when they fail.
    """
    if resp.status_code != 200:
        print(f"  {context} failed: HTTP {resp.status_code}")
        print(f"  Response: {resp.text[:300]}")
        return None

    try:
        data = resp.json()
    except Exception:
        print(f"  {context} failed: response was not JSON")
        print(f"  Response: {resp.text[:300]}")
        return None

    status = data.get("status", 0)
    if status != 0:
        print(f"  {context} failed: status={status} msg={data.get('msg', '')}")
        return None

    return data


def verify_auth(token):
    """Verify the token works by hitting /user/me."""
    resp = api_get(token, "/user/me")
    if resp.status_code == 200:
        data = resp.json()
        # Response structure: { "data_user": { "nickname": "...", "email": "..." } }
        user = data.get("data_user", data.get("data", data))
        nickname = user.get("nickname", user.get("email", "unknown"))
        print(f"  Authenticated as: {nickname}")
        return True
    print(f"  Auth check failed: {resp.status_code} {resp.text[:200]}")
    return False


def list_recordings(token):
    """List all recordings via /file/simple/web with pagination."""
    all_recordings = []
    skip = 0
    limit = 50

    while True:
        params = {
            "skip": skip,
            "limit": limit,
            "is_trash": 0,
            "sort_by": "start_time",
            "is_desc": "true",
            "r": random.random(),
        }
        resp = api_get(token, "/file/simple/web", params=params)

        if resp.status_code != 200:
            print(f"  /file/simple/web failed: {resp.status_code}")
            print(f"  Response: {resp.text[:500]}")
            break

        data = resp.json()

        if data.get("status", 0) != 0:
            print(f"  API error: status={data.get('status')} msg={data.get('msg', '')}")
            break

        # Response key is "data_file_list"
        recordings = data.get("data_file_list", data.get("data", []))
        if isinstance(recordings, dict):
            recordings = recordings.get("items", recordings.get("list", []))

        if not recordings:
            break

        all_recordings.extend(recordings)

        if len(recordings) < limit:
            break  # last page

        skip += limit

    # Filter out trashed items (belt-and-suspenders)
    all_recordings = [r for r in all_recordings if not r.get("is_trash", False)]

    return all_recordings


def filter_by_date(recordings, target_date):
    """Filter recordings to those from the target date."""
    if target_date is None:
        return recordings

    filtered = []
    for rec in recordings:
        # The API uses start_time (epoch seconds or ms)
        start = rec.get("start_time", rec.get("created_at", rec.get("create_time", 0)))

        if isinstance(start, (int, float)):
            # Detect milliseconds vs seconds
            if start > 1e12:
                start = start / 1000
            dt = datetime.fromtimestamp(start)
            date_str = dt.strftime("%Y-%m-%d")
        elif isinstance(start, str):
            date_str = start[:10]
        else:
            continue

        if date_str == target_date:
            filtered.append(rec)

    return filtered


def get_recording_detail(token, file_id):
    """Get full recording detail including transcript via /file/detail/{id}."""
    resp = api_get(token, f"/file/detail/{file_id}")

    if resp.status_code != 200:
        print(f"  /file/detail/{file_id} failed: {resp.status_code}")
        return None

    data = resp.json()
    detail = data.get("data", data)
    return detail


def _repair_text_encoding(text):
    """Repair UTF-8 bytes that were decoded as Latin-1.

    The legacy S3 transcript layer occasionally double-encodes punctuation
    (an em dash arrives as the three characters a-circumflex, 0x80, 0x94).
    The MCP returns the correct text, so repairing here keeps the two read
    sources identical. The guard means correctly decoded text is untouched.
    """
    if not isinstance(text, str):
        return text
    if "â\u0080" not in text and "Ã" not in text:
        return text
    try:
        return text.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def _format_segments(segments):
    """Format a list of transcript segments into readable text."""
    lines = []
    for seg in segments:
        speaker = seg.get("speaker", seg.get("spk", "Unknown"))
        text = _repair_text_encoding(
            seg.get("content", seg.get("text", seg.get("trans_text", "")))
        )
        start_ms = seg.get("start_time", seg.get("st", 0))
        # start_time is in milliseconds
        start_s = start_ms / 1000 if start_ms > 1000 else start_ms
        minutes = int(start_s // 60)
        seconds = int(start_s % 60)
        if speaker and text:
            lines.append(f"[{minutes:02d}:{seconds:02d}] **{speaker}**: {text}")
        elif text:
            lines.append(text)
    return "\n\n".join(lines)


def get_transcript_status(detail):
    """Check the generation status of a recording's transcript.

    Returns one of:
      "ready"   — task_status == 1, transcript is available
      "pending" — task_status == 0, generation still in progress
      "missing" — no transaction content item exists at all
    """
    if not detail:
        return "missing"

    for item in detail.get("content_list", []):
        if item.get("data_type") == "transaction":
            status = item.get("task_status")
            if status == 1:
                return "ready"
            else:
                return "pending"

    return "missing"


def extract_transcript(detail):
    """Download and extract transcript text from a recording detail response.

    Plaud stores transcripts in two S3 layers inside content_list:
      - transaction_polish: the polished/formatted version rendered by the web UI
      - transaction: the raw diarization segments

    We prefer transaction_polish because it is what users see in the Plaud web UI,
    and it is what gets updated when is_reload=1 regeneration runs after a speaker
    rename. If transaction_polish is not available (e.g. during regeneration), we
    fall back to transaction.

    Both layers are presigned S3 URLs that expire after ~300 seconds — always
    fetch from a fresh /file/detail response, never cache the URL.
    """
    if not detail:
        return ""

    content_list = detail.get("content_list", [])

    # Prefer transaction_polish (web UI layer)
    for item in content_list:
        if item.get("data_type") == "transaction_polish" and item.get("task_status") == 1:
            url = item.get("data_link", "")
            if url:
                try:
                    resp = requests.get(url, timeout=30)
                    if resp.status_code == 200:
                        segments = resp.json()
                        if isinstance(segments, list) and segments:
                            return _format_segments(segments)
                except Exception as e:
                    print(f"  Warning: failed to download transaction_polish transcript: {e}")

    # Fall back to raw transaction layer
    for item in content_list:
        if item.get("data_type") == "transaction" and item.get("task_status") == 1:
            url = item.get("data_link", "")
            if url:
                try:
                    resp = requests.get(url, timeout=30)
                    if resp.status_code == 200:
                        segments = resp.json()
                        if isinstance(segments, list) and segments:
                            return _format_segments(segments)
                except Exception as e:
                    print(f"  Warning: failed to download transaction transcript: {e}")

    return ""


def share_recording(token, file_id, detail=None):
    """Share a recording publicly with transcript and summary enabled.

    Creates a public share link via POST /share/public/create.
    Returns the share URL string, or None on failure.
    """
    headers = make_headers(token)
    api_base = get_api_base()

    # Extract auto_sum note ID from file detail if available
    notes = []
    if detail:
        for item in detail.get("pre_download_content_list", []):
            data_id = item.get("data_id", "")
            if data_id.startswith("auto_sum:"):
                notes.append(data_id)
                break  # one summary note is enough

    payload = {
        "object_id": file_id,
        "object_type": "file",
        "content_config": {
            "audio": False,
            "transcript": True,
            "highlights": 0,
            "overview": False,
            "notes": notes,
        }
    }

    resp = requests.post(
        f"{api_base}/share/public/create",
        headers=headers,
        json=payload,
        timeout=30,
    )

    if resp.status_code != 200:
        print(f"  /share/public/create failed: {resp.status_code}")
        print(f"  Response: {resp.text[:300]}")
        return None

    data = resp.json()
    # Try common response shapes for the share URL
    share_data = data.get("data", {})
    url = (
        share_data.get("share_url") or
        share_data.get("url") or
        share_data.get("link") or
        (f"https://web.plaud.ai/share/{share_data.get('token')}" if share_data.get("token") else None) or
        (f"https://web.plaud.ai/share/{share_data.get('share_token')}" if share_data.get("share_token") else None)
    )

    if url:
        print(f"  Share link created: {url}")
    else:
        print(f"  Share created but URL not found in response: {json.dumps(share_data)[:200]}")

    return url


# ---------------------------------------------------------------------------
# Speaker management — reverse-engineered from arbuzmell/plaud-api
# ---------------------------------------------------------------------------

FILE_LIST_ENDPOINT = "/file/list"
SPEAKER_LIST_ENDPOINT = "/speaker/list"

# Rename verification reads the database copy of trans_result through
# POST /file/list. It never trusts the transaction_polish S3 layer, which the
# PATCH does not update. A write can also read back correctly and then be
# reverted by Plaud's async transcript rebuild, so success needs a confirming
# re-read after a short settle pause.
DB_VERIFY_ATTEMPTS = 2
DB_VERIFY_WAIT_SECONDS = 4
DB_VERIFY_SETTLE_SECONDS = 5


def list_speakers(token):
    """Get all known speakers from the Plaud account."""
    resp = api_get(token, SPEAKER_LIST_ENDPOINT)
    data = check_api_response(resp, SPEAKER_LIST_ENDPOINT)
    if data is None:
        return []
    # Response nests speakers under data.speakers (not data_speaker_list)
    speakers = data.get("data", {}).get("speakers", [])
    if not speakers:
        speakers = data.get("data_speaker_list", [])
    return speakers


def get_speaker_embeddings(token, file_id):
    """Get per-speaker voice embeddings from a recording's diarization.

    Calls POST /ai/transsumm/{file_id} which returns embeddings in
    data_others.embeddings keyed by original speaker label (e.g. "Speaker 1").
    These are 256-dimensional float vectors used for voice recognition.

    Returns dict of {"Speaker 1": [256 floats], "Speaker 2": [...], ...}
    """
    headers = make_headers(token)
    api_base = get_api_base()
    info_payload = json.dumps({
        "language": "en",
        "diarization": 1,
        "llm": "auto",
    })
    resp = requests.post(
        f"{api_base}/ai/transsumm/{file_id}",
        headers=headers,
        json={
            "is_reload": 0,
            "summ_type": "REASONING-NOTE",
            "summ_type_type": "system",
            "info": info_payload,
            "support_mul_summ": True,
            "r": random.random(),
        },
        timeout=120,
    )
    if resp.status_code != 200:
        print(f"  /ai/transsumm for embeddings failed: {resp.status_code}")
        return {}

    data = resp.json()
    return (data.get("data_others") or {}).get("embeddings", {})


def sync_speaker(token, speaker_name, embedding):
    """Register a speaker with their voice embedding for future auto-labeling.

    Calls POST /speaker/sync to create or update a speaker profile.
    Once synced, Plaud will auto-recognize this voice in future recordings.

    Args:
        token: Auth token
        speaker_name: Display name (e.g. "Todd Wynne")
        embedding: 256-float voice embedding vector
    """
    headers = make_headers(token)
    api_base = get_api_base()

    resp = requests.post(
        f"{api_base}/speaker/sync",
        headers=headers,
        json={
            "speakers": [{
                "speaker_id": uuid.uuid4().hex,
                "speaker_name": speaker_name,
                "speaker_type": 2,
                "embeddings": {"mark": embedding},
                "sample_counts": {"auto": 0, "mark": 1, "me": 0},
            }]
        },
        timeout=30,
    )

    data = check_api_response(resp, f"/speaker/sync for '{speaker_name}'")
    if data is None:
        return False

    results = (data.get("data") or {}).get("results") or []
    if not results:
        print(f"  /speaker/sync returned no results for '{speaker_name}': nothing was registered")
        return False

    result = results[0]
    merged = result.get("merged_speaker_id")
    if merged:
        print(f"  Registered '{speaker_name}' (merged with existing profile)")
    else:
        sid = result.get("speaker_id", "?")
        print(f"  Registered '{speaker_name}' (speaker_id: {sid[:12]}...)")
    return True


def get_recording_speakers(token, file_id):
    """Get unique speakers from a recording's transcript segments.

    Uses POST /file/list with [file_id] to get trans_result,
    then extracts unique speaker names with segment counts.
    Returns list of {"name": str, "segments_count": int, "sample_text": str}.
    """
    headers = make_headers(token)
    api_base = get_api_base()
    resp = requests.post(
        f"{api_base}{FILE_LIST_ENDPOINT}",
        headers=headers,
        json=[file_id],
        timeout=60,
    )
    data = check_api_response(resp, f"POST {FILE_LIST_ENDPOINT} for speakers")
    if data is None:
        return [], []

    files = data.get("data_file_list", [])
    if not files:
        return [], []

    trans_result = files[0].get("trans_result") or []

    # Build speaker stats with sample text
    stats = {}
    samples = {}
    for seg in trans_result:
        speaker = (seg.get("speaker") or "").strip()
        text = (seg.get("text") or seg.get("trans_text") or seg.get("content") or "").strip()
        if speaker:
            stats[speaker] = stats.get(speaker, 0) + 1
            if speaker not in samples and text:
                samples[speaker] = text[:120]

    speakers = [
        {
            "name": name,
            "segments_count": count,
            "sample_text": samples.get(name, ""),
        }
        for name, count in sorted(stats.items(), key=lambda x: -x[1])
    ]

    return speakers, trans_result


def rename_speakers(token, file_id, trans_result, mapping):
    """Rename several speakers in a recording's transcript with a single PATCH.

    Applies the whole mapping to trans_result in place, then PATCHes
    /file/{file_id} once with the full segment array. One PATCH per recording
    rather than one per speaker, which keeps the write atomic and gives the
    transcript pipeline nothing to interleave with.

    Returns (ok, counts), where counts is {old_name: segments_renamed}.
    """
    counts = {}
    for seg in trans_result:
        current = (seg.get("speaker") or "").strip()
        if current in mapping:
            new_name = mapping[current]
            if new_name and new_name != current:
                seg["speaker"] = new_name
            counts[current] = counts.get(current, 0) + 1

    if not counts:
        print(f"  None of the mapped speakers were found in the transcript")
        return False, counts

    headers = make_headers(token)
    api_base = get_api_base()
    resp = requests.patch(
        f"{api_base}/file/{file_id}",
        headers=headers,
        json={"trans_result": trans_result},
        timeout=60,
    )

    if check_api_response(resp, f"PATCH /file/{file_id}") is None:
        return False, counts

    for old_name, renamed in counts.items():
        print(f"  Renamed '{old_name}' → '{mapping[old_name]}' ({renamed} segments)")
    return True, counts


def trigger_transcription(token, file_id, language="en"):
    """Trigger transcription and analysis for a recording that hasn't been processed.

    Two-step process:
      1. PATCH /file/{file_id} with tranConfig to save the configuration
      2. POST /ai/transsumm/{file_id} to actually kick off the analysis pipeline

    Step 1 alone returns 200 but does NOT start transcription — step 2 is required.
    """
    headers = make_headers(token)
    api_base = get_api_base()

    # Step 1: Save transcription config
    resp = requests.patch(
        f"{api_base}/file/{file_id}",
        headers=headers,
        json={
            "extra_data": {
                "tranConfig": {
                    "language": language,
                    "type_type": "system",
                    "type": "REASONING-NOTE",
                    "diarization": 1,
                    "llm": "auto",
                }
            }
        },
        timeout=60,
    )

    if resp.status_code != 200:
        print(f"  Step 1 (config) failed: {resp.status_code}")
        print(f"  Response: {resp.text[:300]}")
        return False

    print(f"  Step 1: Config saved for {file_id}")

    # Step 2: Trigger the actual analysis pipeline
    info_payload = json.dumps({
        "language": language,
        "diarization": 1,
        "llm": "auto",
    })

    resp2 = requests.post(
        f"{api_base}/ai/transsumm/{file_id}",
        headers=headers,
        json={
            "is_reload": 0,
            "summ_type": "REASONING-NOTE",
            "summ_type_type": "system",
            "info": info_payload,
            "support_mul_summ": True,
            "r": random.random(),
        },
        timeout=60,
    )

    if resp2.status_code != 200:
        print(f"  Step 2 (trigger) failed: {resp2.status_code}")
        print(f"  Response: {resp2.text[:300]}")
        return False

    try:
        result = resp2.json()
        status = result.get("status", -1)
        msg = result.get("msg", "")
        print(f"  Step 2: Analysis triggered — status={status}, msg='{msg}'")
    except Exception:
        print(f"  Step 2: Analysis triggered (response not JSON)")

    print(f"  Transcription triggered for {file_id} — will be pending until Plaud finishes")
    return True


def check_generic_speakers(speakers):
    """Identify speakers that look like generic labels (Speaker 1, etc).

    Returns list of speaker names that need human identification.
    """
    generic_patterns = ["speaker", "spk", "unknown"]
    untagged = []
    for s in speakers:
        name_lower = s["name"].lower().strip()
        if any(p in name_lower for p in generic_patterns):
            untagged.append(s)
    return untagged


_SUMMARY_IMAGE_RE = re.compile(r"^\s*!\[[^\]]*\]\(permanent/[^)]*\)\s*$\n?", re.M)


def _clean_summary(text):
    """Drop the UI-only summary image reference and surrounding blank lines."""
    if not isinstance(text, str):
        return ""
    return _SUMMARY_IMAGE_RE.sub("", text).strip()


def extract_summary(detail):
    """Extract AI summary from a recording detail response.

    Summary is pre-embedded in pre_download_content_list as a JSON string
    in the data_content field of the auto_sum item. Newer recordings store
    raw markdown there instead of JSON, so both shapes are handled.
    """
    if not detail:
        return ""

    for item in detail.get("pre_download_content_list", []):
        data_id = item.get("data_id", "")
        if data_id.startswith("auto_sum:"):
            data_content = item.get("data_content", "")
            if isinstance(data_content, str):
                try:
                    parsed = json.loads(data_content)
                    ai_content = parsed.get("ai_content", "")
                    if ai_content:
                        return _clean_summary(ai_content)
                except Exception:
                    # Newer recordings store the summary as raw markdown in
                    # data_content rather than JSON with an ai_content field.
                    return _clean_summary(data_content)
            elif isinstance(data_content, dict):
                return _clean_summary(data_content.get("ai_content", ""))

    return ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _mcp_read():
    """Return the read-only MCP adapter module.

    The module imports cleanly without Node installed; only starting the MCP
    requires it.
    """
    import plaud_read
    return plaud_read


def read_failure_path():
    """Path of the fail-closed marker the workflow and eval record can read."""
    return os.path.join(STAGING_DIR, "plaud_read_failure.json")


def clear_read_failure():
    """Remove a stale failure marker after a successful read preflight."""
    path = read_failure_path()
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass


def report_read_failure(read_source, error_type, message, exit_code=2):
    """Fail loudly: console banner plus a machine-readable staging marker.

    The plaud-ingest step reads both. A 6am token failure should be obvious in
    the run output and leave one artifact explaining exactly what broke.
    """
    os.makedirs(STAGING_DIR, exist_ok=True)
    path = read_failure_path()
    try:
        with open(path, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "read_source": read_source,
                "status": "failed",
                "error_type": error_type,
                "message": str(message),
                "exit_code": exit_code,
                "action": (
                    "run `npx -y @plaud-ai/mcp@0.3.14 login` on the host, then re-run"
                    if error_type == "MCP_AUTH_REQUIRED"
                    else "inspect the message; the read path did not start"
                ),
            }, f, indent=2)
    except OSError as exc:
        path = f"(could not write marker: {exc})"

    bar = "!" * 72
    print(bar)
    print("PLAUD READ FAILED - INGEST CANNOT PROCEED")
    print(f"  read_source : {read_source}")
    print(f"  error       : {error_type}")
    print(f"  detail      : {message}")
    print(f"  marker      : {path}")
    if error_type == "MCP_AUTH_REQUIRED":
        print("  action      : run `npx -y @plaud-ai/mcp@0.3.14 login` on the host, then re-run")
    print("PLAUD_READ_STATUS=failed")
    print(bar)


def load_recordings(token, target_date, read_source):
    """Read the recording list from the selected source.

    The MCP branch returns recordings already normalized to the legacy shape
    (id, filename, start_time in epoch seconds, duration in milliseconds).
    """
    if read_source == "mcp":
        # List the whole library, then let main() apply the same date filter the
        # api path uses. This keeps plaud_all_recordings.json coverage identical
        # between sources instead of silently narrowing it to one date.
        return _mcp_read().list_recordings(None)
    return list_recordings(token)


def load_detail(token, file_id, read_source):
    """Read one recording's detail from the selected source."""
    if read_source == "mcp":
        return _mcp_read().get_detail(file_id)
    return get_recording_detail(token, file_id)


def load_transcript_text(token, file_id, detail, read_source):
    """Return the rendered transcript text for one recording.

    The MCP path renders the same segment shape through the same renderer, so
    the staging markdown stays identical between sources.
    """
    if read_source == "mcp":
        # Match the api path's layer preference: the polished render first,
        # then the raw transaction block.
        reader = _mcp_read()
        for block in ("transaction_polish", "transaction"):
            segments = reader.get_transcript_segments(file_id, block=block)
            if segments:
                return _format_segments(segments)
        return ""
    return extract_transcript(detail) if detail else ""


def load_summary_text(token, file_id, detail, read_source):
    """Return the AI summary text for one recording."""
    if read_source == "mcp":
        return _mcp_read().get_summary(file_id)
    return extract_summary(detail) if detail else ""


def get_target_date():
    """Parse target date from CLI args. Default: yesterday."""
    skip_next = False
    for arg in sys.argv[1:]:
        if skip_next:
            skip_next = False
            continue
        if arg in ("--login", "--force-login"):
            continue
        if arg == "--read-source":
            skip_next = True
            continue
        if arg == "--all":
            return None
        if arg.startswith("-"):
            continue
        try:
            datetime.strptime(arg, "%Y-%m-%d")
            return arg
        except ValueError:
            print(f"Invalid date format: {arg}. Use YYYY-MM-DD or --all")
            sys.exit(1)
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")


def main(read_source="mcp"):
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__.strip())
        print("""
Other modes:
  --check <file_id>       poll one recording's transcription status
  --share <file_id>      request share-token transcript for one recording
  --rename <file_id> <new_title>
                          rename a recording and refetch its transcript
""")
        sys.exit(0)

    force_login = "--login" in sys.argv or "--force-login" in sys.argv

    print("=" * 60)
    print("Plaud Transcript Fetcher")
    print("=" * 60)
    print(f"Read source: {read_source}")

    # Authenticate
    token = get_token(force_login=force_login)

    # Verify auth works
    if not verify_auth(token):
        print("Token appears invalid. Try --login to re-authenticate.")
        sys.exit(1)

    # When the MCP is the read source, prove its token before doing any work.
    # A failure here fails closed before anything is staged.
    if read_source == "mcp":
        print("  Verifying MCP authentication...")
        who = _mcp_read().preflight()
        print(f"  MCP authenticated as: {who}")
    clear_read_failure()

    # Determine target date
    target_date = get_target_date()
    date_label = target_date or "all dates"
    os.makedirs(STAGING_DIR, exist_ok=True)

    print(f"\nFetching recordings for {date_label}...")
    recordings = load_recordings(token, target_date, read_source)
    print(f"Total recordings found: {len(recordings)}")

    if not recordings:
        print("No recordings returned from /file/simple/web.")
        print("This could mean the account has no recordings, or the API shape changed.")
        sys.exit(1)

    # Save full recording list for debugging
    with open(f"{STAGING_DIR}/plaud_all_recordings.json", "w") as f:
        json.dump(recordings, f, indent=2, default=str)

    # Filter to target date
    filtered = filter_by_date(recordings, target_date)
    print(f"Recordings matching {date_label}: {len(filtered)}")

    if not filtered:
        print(f"No recordings found for {date_label}")
        print("Sample recordings:")
        for rec in recordings[:5]:
            start = rec.get("start_time", rec.get("created_at", 0))
            if isinstance(start, (int, float)):
                if start > 1e12:
                    start = start / 1000
                dt = datetime.fromtimestamp(start)
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            else:
                date_str = str(start)
            name = rec.get("filename", rec.get("fullname", rec.get("id", "unknown")))
            print(f"  {name}: {date_str}")
        sys.exit(0)

    # Re-check any previously pending recordings before processing new ones
    pending_path = os.path.join(STAGING_DIR, "plaud_pending.json")
    pending_registry = {}
    if os.path.exists(pending_path):
        with open(pending_path) as f:
            pending_registry = json.load(f)

    resolved_ids = []
    for pid, pinfo in list(pending_registry.items()):
        print(f"\nRe-checking pending: {pinfo.get('name', pid)} (ID: {pid})")
        detail = load_detail(token, pid, read_source)
        status = get_transcript_status(detail)

        if status == "ready":
            print(f"  Transcript now ready — will process")
            # Inject into filtered list so it gets processed below
            filtered.append(pinfo.get("recording", {"id": pid}))
            resolved_ids.append(pid)
        else:
            age_hours = (datetime.now().timestamp() - pinfo.get("first_seen", 0)) / 3600
            if age_hours > 24:
                print(f"  WARNING: Pending for {int(age_hours)}h — may have failed generation")
            else:
                print(f"  Still pending ({int(age_hours)}h old)")

    # Remove resolved entries
    for pid in resolved_ids:
        del pending_registry[pid]

    # Fetch detail + transcript for each recording
    processed_count = 0
    pending_count = 0

    for rec in filtered:
        file_id = rec.get("id", rec.get("file_id", ""))
        name = rec.get("filename", rec.get("fullname", file_id))
        has_trans = rec.get("is_trans", False)
        has_summary = rec.get("is_summary", False)
        duration = rec.get("duration", 0)
        clean_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in str(name))

        print(f"\nProcessing: {name} (ID: {file_id})")
        print(f"  Duration: {duration}s | Has transcript: {has_trans} | Has summary: {has_summary}")

        # Get full detail (includes transcript)
        detail = load_detail(token, file_id, read_source)

        # Check transcript generation status
        trans_status = get_transcript_status(detail)

        if trans_status == "missing":
            print(f"  No transcription exists — triggering Plaud to generate one")
            trigger_transcription(token, file_id)
            if file_id not in pending_registry:
                pending_registry[file_id] = {
                    "name": name,
                    "first_seen": datetime.now().timestamp(),
                    "recording": rec,
                    "triggered": True,
                }
            pending_count += 1

            with open(f"{STAGING_DIR}/plaud_{clean_name}_raw.json", "w") as f:
                json.dump(
                    {"recording": rec, "detail": detail},
                    f,
                    indent=2,
                    default=str,
                )
            continue

        if trans_status == "pending":
            print(f"  Transcript generation in progress — saving to pending queue")
            if file_id not in pending_registry:
                pending_registry[file_id] = {
                    "name": name,
                    "first_seen": datetime.now().timestamp(),
                    "recording": rec,
                }
            pending_count += 1

            with open(f"{STAGING_DIR}/plaud_{clean_name}_raw.json", "w") as f:
                json.dump(
                    {"recording": rec, "detail": detail},
                    f,
                    indent=2,
                    default=str,
                )
            continue

        transcript_text = load_transcript_text(token, file_id, detail, read_source)
        summary_text = load_summary_text(token, file_id, detail, read_source)

        if not transcript_text and has_trans:
            print("  Warning: is_trans=True but no transcript text extracted")

        # Check for generic/untagged speakers
        speakers, trans_result = get_recording_speakers(token, file_id)
        untagged = check_generic_speakers(speakers) if speakers else []

        if untagged:
            print(f"  Found {len(untagged)} untagged speaker(s):")
            for s in untagged:
                sample = f' — "{s["sample_text"]}"' if s["sample_text"] else ""
                print(f"    {s['name']} ({s['segments_count']} segments){sample}")

            # Write speaker mapping file for Knox to act on
            speaker_file = {
                "file_id": file_id,
                "recording_name": name,
                "all_speakers": speakers,
                "untagged_speakers": untagged,
                "known_speakers": list_speakers(token),
                "status": "needs_mapping",
            }
            speaker_path = f"{STAGING_DIR}/plaud_{clean_name}_speakers.json"
            with open(speaker_path, "w") as f:
                json.dump(speaker_file, f, indent=2, default=str)
            print(f"  Speaker mapping file: {speaker_path}")

        # Save raw JSON for debugging
        with open(f"{STAGING_DIR}/plaud_{clean_name}_raw.json", "w") as f:
            json.dump(
                {"recording": rec, "detail": detail},
                f,
                indent=2,
                default=str,
            )

        # Determine recording date from start_time
        start_ts = rec.get("start_time", 0)
        if isinstance(start_ts, (int, float)):
            if start_ts > 1e12:
                start_ts = start_ts / 1000
            rec_date = datetime.fromtimestamp(start_ts).strftime("%Y-%m-%d")
        else:
            rec_date = target_date or "unknown"

        # Save formatted transcript
        output = f"# {name}\n\n"
        output += f"**Date:** {rec_date}\n"
        output += f"**Duration:** {duration}s\n"
        output += f"**Source:** Plaud AI\n\n"

        if summary_text:
            output += f"## AI Summary\n\n{summary_text}\n\n"

        if transcript_text:
            output += f"## Transcript\n\n{transcript_text}\n"
        else:
            output += "## Transcript\n\n_No transcript available._\n"

        outpath = f"{STAGING_DIR}/plaud_{clean_name}.md"
        with open(outpath, "w") as f:
            f.write(output)

        print(f"  Saved: {outpath}")
        processed_count += 1

    # Write pending registry
    if pending_registry:
        with open(pending_path, "w") as f:
            json.dump(pending_registry, f, indent=2, default=str)
        print(f"\n  {len(pending_registry)} recording(s) in pending queue — will retry next run")
    elif os.path.exists(pending_path):
        os.remove(pending_path)

    print(f"\n{'=' * 60}")
    print(f"Done. {processed_count} transcripts saved, {pending_count} pending generation")
    if pending_registry:
        for pid, pinfo in pending_registry.items():
            age_hours = (datetime.now().timestamp() - pinfo.get("first_seen", 0)) / 3600
            flag = " ⚠ >24h" if age_hours > 24 else ""
            print(f"  Pending: {pinfo.get('name', pid)} ({int(age_hours)}h){flag}")
    print(f"{'=' * 60}")
    print("PLAUD_READ_STATUS=ok")


def verify_speaker_renames(token, file_id, original_to_new):
    """Assert the renamed speakers are stored in the recording's database record.

    Re-fetches through POST /file/list and checks every segment whose
    original_speaker label was mapped: the segment's `speaker` field must now
    carry the mapped name. original_speaker is the diarization label and is
    never rewritten, so it is the stable key across the rename.

    Returns (ok, problems), where problems is a list of readable mismatches.
    """
    if not original_to_new:
        return True, []

    _speakers, trans_result = get_recording_speakers(token, file_id)
    if not trans_result:
        return False, ["re-fetch returned no trans_result segments"]

    problems = []
    seen = set()
    for seg in trans_result:
        orig = (seg.get("original_speaker") or "").strip()
        expected = original_to_new.get(orig)
        if not expected:
            continue
        seen.add(orig)
        actual = (seg.get("speaker") or "").strip()
        if actual != expected:
            uid = seg.get("segment_uid", "?")
            problems.append(f"{uid}: original_speaker={orig} speaker={actual} expected={expected}")

    for orig in sorted(set(original_to_new) - seen):
        problems.append(
            f"original_speaker={orig} absent from trans_result (expected {original_to_new[orig]})"
        )

    return not problems, problems


def verify_speaker_renames_with_retry(token, file_id, original_to_new):
    """Verify renames with a bounded retry and one confirming re-read.

    Plaud rebuilds transcripts asynchronously, so a write can read back
    correctly and then be reverted a few seconds later. The confirming re-read
    after a settle pause catches that instead of reporting a false success.
    """
    ok = False
    problems = []
    for attempt in range(1, DB_VERIFY_ATTEMPTS + 1):
        ok, problems = verify_speaker_renames(token, file_id, original_to_new)
        if ok:
            time.sleep(DB_VERIFY_SETTLE_SECONDS)
            ok, problems = verify_speaker_renames(token, file_id, original_to_new)
            if ok:
                return True, []
        if attempt < DB_VERIFY_ATTEMPTS:
            print(f"  Verification attempt {attempt}/{DB_VERIFY_ATTEMPTS} failed, retrying in {DB_VERIFY_WAIT_SECONDS}s")
            time.sleep(DB_VERIFY_WAIT_SECONDS)

    return ok, problems


def trigger_transcript_regeneration(token, file_id):
    """Trigger regeneration of transcript output files after speaker changes.

    Uses POST /ai/transsumm with is_reload: 1 to regenerate without re-transcribing.
    """
    headers = make_headers(token)
    api_base = get_api_base()

    info_payload = json.dumps({
        "language": "en",
        "diarization": 1,
        "llm": "auto",
    })

    resp = requests.post(
        f"{api_base}/ai/transsumm/{file_id}",
        headers=headers,
        json={
            "is_reload": 1,  # Signal to regenerate outputs, don't re-transcribe
            "summ_type": "REASONING-NOTE",
            "summ_type_type": "system",
            "info": info_payload,
            "support_mul_summ": True,
            "r": random.random(),
        },
        timeout=120,
    )

    data = check_api_response(resp, f"Regeneration trigger for {file_id}")
    if data is None:
        return False

    print(f"  Regeneration accepted by Plaud (status=0, msg='{data.get('msg', '')}')")
    return True


def rename_and_refetch(file_id, mapping_json):
    """Rename speakers in a recording and re-fetch the updated transcript.

    Called by Knox after David provides a speaker mapping.

    Args:
        file_id: Plaud recording ID
        mapping_json: JSON string of {"old_name": "new_name", ...}

    Usage:
        python3 fetch_plaud.py --rename <file_id> '<json_mapping>'
    """
    mapping = json.loads(mapping_json)
    if not mapping:
        print("Empty mapping — nothing to rename")
        sys.exit(1)

    print("=" * 60)
    print("Plaud Speaker Rename + Re-fetch")
    print("=" * 60)

    token = get_token()
    if not verify_auth(token):
        print("Token invalid. Try --login to re-authenticate.")
        sys.exit(1)

    # Get current transcript segments
    speakers, trans_result = get_recording_speakers(token, file_id)
    if not trans_result:
        print(f"  Could not load transcript for {file_id}")
        sys.exit(1)

    # Get voice embeddings before renaming (keyed by original_speaker labels)
    print(f"\nExtracting voice embeddings...")
    embeddings = get_speaker_embeddings(token, file_id)
    if embeddings:
        print(f"  Got embeddings for {len(embeddings)} speaker(s)")
    else:
        print(f"  Warning: no embeddings returned — speakers won't be registered for auto-labeling")

    # Build original_speaker → new_name mapping before the PATCH.
    # trans_result has both "speaker" (current label, overwritten by the rename)
    # and "original_speaker" (diarization label, never overwritten), so
    # original_speaker is the stable key for verification and embedding sync.
    original_to_new = {}
    for old_name, new_name in mapping.items():
        matched = False
        for seg in trans_result:
            if (seg.get("speaker") or "").strip() == old_name:
                orig = (seg.get("original_speaker") or "").strip()
                if orig:
                    original_to_new[orig] = new_name
                matched = True
                break
        if not matched:
            print(f"  Warning: '{old_name}' is not in the transcript, nothing to rename for it")

    # Apply every rename in one pass, then send a single PATCH
    print(f"\nApplying {len(mapping)} rename(s) in a single PATCH...")
    patched, counts = rename_speakers(token, file_id, trans_result, mapping)

    # Register renamed speakers with voice embeddings for future auto-labeling
    if embeddings and original_to_new:
        print(f"\nRegistering speakers for auto-labeling...")
        existing = {s.get("speaker_name", ""): s for s in list_speakers(token)}
        for orig_label, new_name in original_to_new.items():
            if new_name in existing:
                print(f"  '{new_name}' already registered — skipping")
                continue
            emb = embeddings.get(orig_label)
            if emb:
                sync_speaker(token, new_name, emb)
            else:
                print(f"  No embedding for '{orig_label}' — can't register '{new_name}'")

    # Verify against the database copy of trans_result (POST /file/list).
    # The transaction_polish S3 layer is a rendered artifact that the PATCH does
    # not update, so it is not evidence that the write failed.
    verified = False
    if not patched:
        print(f"\n  ✗ Rename PATCH failed, speaker names are unchanged")
    elif not original_to_new:
        print(f"\n  Warning: no original_speaker labels resolved, skipping database verification")
    else:
        print(f"\nVerifying speaker updates in database...")
        verified, problems = verify_speaker_renames_with_retry(token, file_id, original_to_new)

        if verified:
            print(f"  ✓ Database holds the renamed speakers (confirmed after a settle re-read)")
        else:
            print(f"  ⚠ Speaker renames are not in the database record:")
            for problem in problems[:5]:
                print(f"    {problem}")

            # Regeneration is the last resort and only fires on a genuine
            # database verification failure, never because a rendered layer
            # looks stale.
            print(f"  Triggering transcript regeneration (is_reload=1) as the last resort...")
            confirmed = False
            if trigger_transcript_regeneration(token, file_id):
                # Regeneration rebuilds transcript outputs asynchronously and can
                # itself reset speaker labels, so re-verify and report honestly.
                REGEN_WAIT = 20  # seconds between checks
                MAX_RETRIES = 6  # up to 120s total
                for attempt in range(1, MAX_RETRIES + 1):
                    print(f"  Waiting {REGEN_WAIT}s for Plaud to regenerate (attempt {attempt}/{MAX_RETRIES})...")
                    time.sleep(REGEN_WAIT)
                    confirmed, problems = verify_speaker_renames(token, file_id, original_to_new)
                    if confirmed:
                        print(f"  ✓ Speaker renames confirmed in the database after regeneration")
                        break
                if not confirmed:
                    print(f"  ✗ Renames still not stored after {MAX_RETRIES} checks ({MAX_RETRIES * REGEN_WAIT}s)")
                    print(f"    Known Plaud 4.0 problem: the legacy PATCH writes a non-authoritative")
                    print(f"    store while the 4.0 pipeline rebuilds from its own copy. Regeneration")
                    print(f"    resets speaker labels, so re-running --rename may not help.")
                    print(f"    See reference/plaud-v4-rewrite-plan.md.")
            else:
                print(f"  ✗ Regeneration trigger failed, speaker names are unchanged")
            verified = confirmed

    # Re-fetch the updated recording detail and transcript
    print(f"\nRe-fetching updated transcript...")
    detail = get_recording_detail(token, file_id)
    summary_text = extract_summary(detail) if detail else ""
    transcript_text = ""

    if patched:
        # The renamed segments are authoritative in the recording record. The
        # transaction_polish layer is a separate render of the transcript that
        # the PATCH does not update, so use the database segments directly
        # whenever a rename was applied.
        _speakers_after, trans_result_after = get_recording_speakers(token, file_id)
        transcript_text = _format_segments(trans_result_after) if trans_result_after else ""
        if transcript_text:
            print(f"  Transcript rendered from the database trans_result segments")

    if not transcript_text:
        transcript_text = extract_transcript(detail) if detail else ""

    rec_name = detail.get("filename", detail.get("fullname", file_id)) if detail else file_id
    clean_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in str(rec_name))

    # Determine recording date
    start_ts = (detail or {}).get("start_time", 0)
    if isinstance(start_ts, (int, float)):
        if start_ts > 1e12:
            start_ts = start_ts / 1000
        rec_date = datetime.fromtimestamp(start_ts).strftime("%Y-%m-%d")
    else:
        rec_date = "unknown"

    # Overwrite the staged markdown with updated transcript
    os.makedirs(STAGING_DIR, exist_ok=True)
    output = f"# {rec_name}\n\n"
    output += f"**Date:** {rec_date}\n"
    output += f"**Duration:** {(detail or {}).get('duration', 0)}s\n"
    output += f"**Source:** Plaud AI\n\n"

    if summary_text:
        output += f"## AI Summary\n\n{summary_text}\n\n"

    if transcript_text:
        output += f"## Transcript\n\n{transcript_text}\n"
    else:
        output += "## Transcript\n\n_No transcript available._\n"

    outpath = f"{STAGING_DIR}/plaud_{clean_name}.md"
    with open(outpath, "w") as f:
        f.write(output)
    print(f"  Updated transcript saved: {outpath}")

    # Clean up the speaker mapping file
    speaker_path = f"{STAGING_DIR}/plaud_{clean_name}_speakers.json"
    if os.path.exists(speaker_path):
        os.remove(speaker_path)
        print(f"  Cleaned up speaker mapping file")

    print(f"\n{'=' * 60}")
    if verified:
        print(f"Done. Speakers renamed and verified in the database.")
    elif patched:
        print(f"Done with warnings. PATCH was accepted but the renames are NOT")
        print(f"stored in the database record, so the staged transcript still")
        print(f"carries the current speaker labels.")
    else:
        print(f"Done with errors. The rename PATCH failed, nothing was renamed.")
    print(f"RENAME_STATUS={'verified' if verified else ('unverified' if patched else 'failed')}")
    print(f"{'=' * 60}")


def check_single(file_id, read_source="mcp"):
    """Check a single recording's transcription status and process if ready.

    Called by the watcher scheduled task after a transcription was triggered.
    If the transcript is ready, fetches it and writes to staging.
    If still pending, exits with code 3 so the caller knows to retry.

    Usage:
        python3 fetch_plaud.py --check <file_id>
    """
    print("=" * 60)
    print("Plaud Transcription Watcher")
    print("=" * 60)

    token = get_token()
    if not verify_auth(token):
        print("Token invalid.")
        sys.exit(1)

    detail = load_detail(token, file_id, read_source)
    status = get_transcript_status(detail)

    rec_name = (detail or {}).get("filename", (detail or {}).get("fullname", file_id))
    print(f"\nRecording: {rec_name} (ID: {file_id})")
    print(f"  Status: {status}")

    if status == "pending" or status == "missing":
        # Check how long it's been pending from the registry
        pending_path = os.path.join(STAGING_DIR, "plaud_pending.json")
        if os.path.exists(pending_path):
            with open(pending_path) as f:
                pending_registry = json.load(f)
            pinfo = pending_registry.get(file_id, {})
            age_hours = (datetime.now().timestamp() - pinfo.get("first_seen", datetime.now().timestamp())) / 3600
            print(f"  Pending for {int(age_hours)}h")
            if age_hours > 24:
                print(f"  WARNING: >24h — may have failed. Check Plaud app.")

        print("  NOT_READY")
        sys.exit(3)

    if status == "ready":
        print("  Transcript is ready — fetching...")
        transcript_text = load_transcript_text(token, file_id, detail, read_source)
        summary_text = load_summary_text(token, file_id, detail, read_source)

        clean_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in str(rec_name))

        start_ts = (detail or {}).get("start_time", 0)
        if isinstance(start_ts, (int, float)):
            if start_ts > 1e12:
                start_ts = start_ts / 1000
            rec_date = datetime.fromtimestamp(start_ts).strftime("%Y-%m-%d")
        else:
            rec_date = "unknown"

        os.makedirs(STAGING_DIR, exist_ok=True)
        output = f"# {rec_name}\n\n"
        output += f"**Date:** {rec_date}\n"
        output += f"**Duration:** {(detail or {}).get('duration', 0)}s\n"
        output += f"**Source:** Plaud AI\n\n"

        if summary_text:
            output += f"## AI Summary\n\n{summary_text}\n\n"
        if transcript_text:
            output += f"## Transcript\n\n{transcript_text}\n"
        else:
            output += "## Transcript\n\n_No transcript available._\n"

        outpath = f"{STAGING_DIR}/plaud_{clean_name}.md"
        with open(outpath, "w") as f:
            f.write(output)
        print(f"  Saved: {outpath}")

        # Check for generic speakers
        speakers, trans_result = get_recording_speakers(token, file_id)
        untagged = check_generic_speakers(speakers) if speakers else []

        if untagged:
            speaker_file = {
                "file_id": file_id,
                "recording_name": rec_name,
                "all_speakers": speakers,
                "untagged_speakers": untagged,
                "known_speakers": list_speakers(token),
                "status": "needs_mapping",
            }
            speaker_path = f"{STAGING_DIR}/plaud_{clean_name}_speakers.json"
            with open(speaker_path, "w") as f:
                json.dump(speaker_file, f, indent=2, default=str)
            print(f"  {len(untagged)} untagged speaker(s) — mapping file written")

        # Remove from pending registry
        pending_path = os.path.join(STAGING_DIR, "plaud_pending.json")
        if os.path.exists(pending_path):
            with open(pending_path) as f:
                pending_registry = json.load(f)
            if file_id in pending_registry:
                del pending_registry[file_id]
                if pending_registry:
                    with open(pending_path, "w") as f:
                        json.dump(pending_registry, f, indent=2, default=str)
                else:
                    os.remove(pending_path)
                print(f"  Removed from pending queue")

        # Save raw JSON
        with open(f"{STAGING_DIR}/plaud_{clean_name}_raw.json", "w") as f:
            json.dump({"detail": detail}, f, indent=2, default=str)

        print(f"\n{'=' * 60}")
        print(f"READY — transcript fetched and staged for ingestion")
        print(f"{'=' * 60}")


if __name__ == "__main__":
    try:
        import plaud_read  # noqa: F401  (module used for MCP error types)
    except Exception:
        plaud_read = None

    ap = argparse.ArgumentParser(
        description="Fetch Plaud recordings and transcripts into the staging folder. "
                    "Default mode fetches a target date's recordings (default: yesterday).",
        epilog="Examples:\n"
               "  python3 fetch_plaud.py                        # yesterday's recordings\n"
               "  python3 fetch_plaud.py 2026-10-19             # specific date\n"
               "  python3 fetch_plaud.py --all                  # all recordings\n"
               "  python3 fetch_plaud.py --login                # force re-authentication\n"
               "  python3 fetch_plaud.py --check abc123         # poll one recording's transcription status\n"
               "  python3 fetch_plaud.py --share abc123         # request share-token transcript\n"
               "  python3 fetch_plaud.py --rename abc123 '{\"Speaker 1\": \"David O'Hara\"}'",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("date", nargs="?", default=None,
                    help="target date YYYY-MM-DD (default: yesterday); see also --all")
    ap.add_argument("--all", action="store_true", help="fetch recordings for all dates")
    ap.add_argument("--login", "--force-login", dest="force_login", action="store_true",
                    help="force re-authentication")
    ap.add_argument("--rename", nargs=2, metavar=("FILE_ID", "JSON_MAPPING"),
                    help="rename a recording's speakers and refetch its transcript")
    ap.add_argument("--check", metavar="FILE_ID",
                    help="poll one recording's transcription status")
    ap.add_argument("--share", metavar="FILE_ID",
                    help="request share-token transcript for one recording")
    ap.add_argument("--read-source", choices=["api", "mcp"], default="mcp",
                    help="read recordings and transcripts from the official Plaud "
                         "MCP over local stdio (default) or the legacy API "
                         "(rollback path)")
    args = ap.parse_args()

    try:
        if args.rename:
            # Speaker reads and the rename write stay on the legacy API in Phase 2.
            rename_and_refetch(args.rename[0], args.rename[1])
        elif args.check:
            check_single(args.check, read_source=args.read_source)
        elif args.share:
            _token = get_token()
            if not _token:
                print("NO_TOKEN")
                sys.exit(2)
            print(f"Sharing recording: {args.share}")
            _detail = get_recording_detail(_token, args.share)
            _url = share_recording(_token, args.share, detail=_detail)
            if _url:
                print(f"SHARE_URL={_url}")
                sys.exit(0)
            else:
                print("SHARE_FAILED")
                sys.exit(4)
        else:
            main(read_source=args.read_source)
    except Exception as exc:
        # Fail closed and loudly: banner, marker file, and a status line the
        # plaud-ingest step and eval record can key on. No traceback wall.
        if plaud_read is not None and isinstance(
            exc, (plaud_read.McpError, plaud_read.McpUnavailableError)
        ):
            error_type = (
                "MCP_AUTH_REQUIRED"
                if isinstance(exc, plaud_read.McpAuthError)
                else "MCP_READ_FAILED"
            )
            report_read_failure(args.read_source, error_type, exc, exit_code=2)
            sys.exit(2)
        raise
