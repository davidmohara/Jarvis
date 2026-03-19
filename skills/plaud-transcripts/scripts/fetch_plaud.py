#!/usr/bin/env python3
"""
Fetch Plaud recordings for a target date and save transcripts to staging.

Usage:
  python3 fetch_plaud.py                    # yesterday's recordings
  python3 fetch_plaud.py 2026-03-18         # specific date
  python3 fetch_plaud.py --all              # all recordings
  python3 fetch_plaud.py --login            # force re-login (ignore cached token)

Authentication:
  The script authenticates automatically. On first run it reads credentials from
  environment variables or prompts interactively, logs in via the Plaud API, and
  caches the token to ~/.config/plaud/token.json. Tokens last ~300 days and auto-
  refresh when within 30 days of expiry.

  Environment variables (optional — script will prompt if not set):
    PLAUD_EMAIL    — your Plaud account email
    PLAUD_PASSWORD — your Plaud account password
    PLAUD_REGION   — "us" (default) or "eu"

  If you use Google Sign-In on Plaud, set a password first via "Forgot Password"
  at web.plaud.ai.
"""

import requests
import json
import os
import sys
import base64
import getpass
import random
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


def prompt_credentials():
    """Interactively prompt for credentials."""
    print("Plaud login required.")
    print("  (If you use Google Sign-In, set a password first via 'Forgot Password' at web.plaud.ai)")
    email = input("  Email: ").strip()
    password = getpass.getpass("  Password: ")
    region = input("  Region (us/eu) [us]: ").strip().lower() or "us"

    if region not in ("us", "eu"):
        print(f"  Invalid region '{region}', defaulting to 'us'")
        region = "us"

    save_creds = input("  Save credentials for future runs? (y/n) [y]: ").strip().lower()
    if save_creds != "n":
        save_credentials(email, password, region)

    return {"email": email, "password": password, "region": region}


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

    # Need to authenticate
    creds = load_credentials()
    if not creds:
        creds = prompt_credentials()

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


def _format_segments(segments):
    """Format a list of transcript segments into readable text."""
    lines = []
    for seg in segments:
        speaker = seg.get("speaker", seg.get("spk", "Unknown"))
        text = seg.get("content", seg.get("text", seg.get("trans_text", "")))
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


def extract_transcript(detail):
    """Download and extract transcript text from a recording detail response.

    The actual transcript lives behind a presigned S3 URL in content_list
    where data_type == 'transaction'. The URL returns a JSON array of segments.
    """
    if not detail:
        return ""

    # Primary: download from content_list transaction link
    for item in detail.get("content_list", []):
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
                    print(f"  Warning: failed to download transcript: {e}")

    return ""


def extract_summary(detail):
    """Extract AI summary from a recording detail response.

    Summary is pre-embedded in pre_download_content_list as a JSON string
    in the data_content field of the auto_sum item.
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
                        return ai_content
                except Exception:
                    pass
            elif isinstance(data_content, dict):
                return data_content.get("ai_content", "")

    return ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def get_target_date():
    """Parse target date from CLI args. Default: yesterday."""
    for arg in sys.argv[1:]:
        if arg in ("--login", "--force-login"):
            continue
        if arg == "--all":
            return None
        try:
            datetime.strptime(arg, "%Y-%m-%d")
            return arg
        except ValueError:
            print(f"Invalid date format: {arg}. Use YYYY-MM-DD or --all")
            sys.exit(1)
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")


def main():
    force_login = "--login" in sys.argv or "--force-login" in sys.argv

    print("=" * 60)
    print("Plaud Transcript Fetcher")
    print("=" * 60)

    # Authenticate
    token = get_token(force_login=force_login)

    # Verify auth works
    if not verify_auth(token):
        print("Token appears invalid. Try --login to re-authenticate.")
        sys.exit(1)

    # Determine target date
    target_date = get_target_date()
    date_label = target_date or "all dates"
    os.makedirs(STAGING_DIR, exist_ok=True)

    print(f"\nFetching recordings for {date_label}...")
    recordings = list_recordings(token)
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

    # Fetch detail + transcript for each recording
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
        detail = get_recording_detail(token, file_id)

        transcript_text = extract_transcript(detail) if detail else ""
        summary_text = extract_summary(detail) if detail else ""

        if not transcript_text and has_trans:
            print("  Warning: is_trans=True but no transcript text extracted")

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

    print(f"\n{'=' * 60}")
    print(f"Done. {len(filtered)} transcripts saved to {STAGING_DIR}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
