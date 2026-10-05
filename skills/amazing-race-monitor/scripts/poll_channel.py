#!/usr/bin/env python3
"""Amazing Race channel poller.

Deterministic Graph poll for the 2026 Amazing Race Photos channel.
No model tokens burned unless there is new media to review.

Auth: Microsoft Graph device-code flow (delegated). Token cache in
data/amazing-race/auth.json. Config in data/amazing-race/config.json.

Usage:
  poll_channel.py --setup                 # device-code login (writes auth.json)
  poll_channel.py --list-teams            # list joined teams (id + display name)
  poll_channel.py --list-channels TEAM_ID # list channels of a team
  poll_channel.py --poll                  # fetch new messages + download media
  poll_channel.py --status                # show watermark + counts

Exit codes (--poll): 0 = ran clean (stdout JSON has new_post/new_media counts);
non-zero only on hard failure (config/auth/network unrecoverable).

Stdlib only. Python 3.9+.
"""

import argparse
import html as html_mod
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import apply_ruling  # roster lookup_team — correlate posts to teams when the number is missing

IES_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DATA_DIR = os.path.join(IES_ROOT, "data", "amazing-race")
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")
AUTH_PATH = os.path.join(DATA_DIR, "auth.json")
STATE_PATH = os.path.join(DATA_DIR, "state.json")
POSTS_PATH = os.path.join(DATA_DIR, "posts.jsonl")
NEW_ITEMS_PATH = os.path.join(DATA_DIR, "new-items.json")
MEDIA_DIR = os.path.join(DATA_DIR, "media")
FRAMES_DIR = os.path.join(MEDIA_DIR, "frames")

GRAPH = "https://graph.microsoft.com/v1.0"
SCOPES = ["ChannelMessage.Read.All", "Files.Read.All", "Team.ReadBasic.All", "User.Read", "offline_access"]

HTTP_TIMEOUT = 60  # seconds; no urlopen call may hang forever

SLACK_POST = os.path.join(IES_ROOT, "systems", "slack-bot", "post.py")


def slack_dm(text):
    """Best-effort DM to David (event-night re-auth without being at the Mac)."""
    try:
        cfg = load_json(CONFIG_PATH) or {}
        channel = cfg.get("slack_dm_channel", "U0ANHV5UXEW")
        subprocess.run(["python3", SLACK_POST, channel, text],
                       capture_output=True, timeout=20)
    except Exception:
        pass  # offline/rehearsal — the console print already covers it

VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".m4v"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".bmp"}

# full words plus T#/Q# shorthand (real event posts use "T#7 Q#1", "t12", "Q3")
TEAM_RE = re.compile(r"\b(?:team|t)\s*#?\s*(\d{1,2})\b", re.IGNORECASE)
QUEST_RE = re.compile(r"\b(?:quest|q)\s*#?\s*(\d{1,2})\b", re.IGNORECASE)
IMG_SRC_RE = re.compile(r"<img[^>]+src=[\"']([^\"']+)[\"']", re.IGNORECASE)


def die(msg, code=1):
    print(json.dumps({"ok": False, "error": msg}), file=sys.stderr)
    sys.exit(code)


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return json.load(f)


def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def load_config():
    cfg = load_json(CONFIG_PATH)
    if not cfg or not cfg.get("tenant_id") or not cfg.get("client_id"):
        die("config missing or incomplete at %s — fill in tenant_id and client_id "
            "(see skills/amazing-race-monitor/references/config.example.json)" % CONFIG_PATH)
    return cfg


def device_login(cfg):
    tenant = cfg["tenant_id"]
    body = urllib.parse.urlencode({
        "client_id": cfg["client_id"],
        "scope": " ".join(SCOPES),
    }).encode()
    req = urllib.request.Request(
        "https://login.microsoftonline.com/%s/oauth2/v2.0/devicecode" % tenant,
        data=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
        dev = json.load(r)
    print("To sign in, use a web browser to open %s" % dev["verification_uri"], flush=True)
    print("Enter code: %s" % dev["user_code"], flush=True)
    slack_dm("Amazing Race Monitor needs re-authentication.\nOpen %s and enter code: %s" %
             (dev["verification_uri"], dev["user_code"]))
    token_body = urllib.parse.urlencode({
        "client_id": cfg["client_id"],
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "device_code": dev["device_code"],
    }).encode()
    interval = dev.get("interval", 5)
    expires = time.time() + dev.get("expires_in", 900)
    while time.time() < expires:
        time.sleep(interval)
        treq = urllib.request.Request(
            "https://login.microsoftonline.com/%s/oauth2/v2.0/token" % tenant,
            data=token_body, headers={"Content-Type": "application/x-www-form-urlencoded"})
        try:
            with urllib.request.urlopen(treq, timeout=HTTP_TIMEOUT) as r:
                tok = json.load(r)
            tok["obtained_at"] = time.time()
            save_json(AUTH_PATH, tok)
            print("Authenticated. Token cached at %s" % AUTH_PATH, flush=True)
            print("refresh_token present: %s" % bool(tok.get("refresh_token")), flush=True)
            return
        except urllib.error.HTTPError as e:
            err = json.load(e)
            code = err.get("error")
            if code == "authorization_pending":
                continue
            die("device-code login failed: %s" % err.get("error_description", code))
    die("device-code login timed out")


def get_access_token(cfg, force_refresh=False):
    auth = load_json(AUTH_PATH)
    if not auth:
        device_login(cfg)
        auth = load_json(AUTH_PATH)
    if not force_refresh and auth.get("access_token") and \
            time.time() < auth.get("obtained_at", 0) + auth.get("expires_in", 3600) - 120:
        return auth["access_token"]
    refresh = {
        "client_id": cfg["client_id"],
        "grant_type": "refresh_token",
        "refresh_token": auth.get("refresh_token"),
        "scope": " ".join(SCOPES),
    }
    body = urllib.parse.urlencode(refresh).encode()
    req = urllib.request.Request(
        "https://login.microsoftonline.com/%s/oauth2/v2.0/token" % cfg["tenant_id"],
        data=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
            tok = json.load(r)
        tok["obtained_at"] = time.time()
        save_json(AUTH_PATH, tok)
        return tok["access_token"]
    except urllib.error.HTTPError:
        # refresh token expired — interactive re-login
        device_login(cfg)
        auth = load_json(AUTH_PATH)
        return auth["access_token"]


def graph_get(cfg, url, binary=False, retry=True):
    token = get_access_token(cfg)
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token})
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
            return r.read() if binary else json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 401 and retry:
            return graph_get(cfg, url, binary=binary, retry=False)
        raise


# ---------------------------------------------------------------------------
# Message parsing
# ---------------------------------------------------------------------------

def strip_html(raw):
    if not raw:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", raw, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    return html_mod.unescape(text).strip()


def parse_team(text):
    m = TEAM_RE.search(text or "")
    return int(m.group(1)) if m else None


def parse_quest(text):
    m = QUEST_RE.search(text or "")
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------------------
# Media download
# ---------------------------------------------------------------------------

def fetch_hosted_contents(cfg, team_id, channel_id, message_id):
    """Inline images in a channel message. Returns list of (id, bytes)."""
    out = []
    url = "%s/teams/%s/channels/%s/messages/%s/hostedContents" % (GRAPH, team_id, channel_id, message_id)
    try:
        data = graph_get(cfg, url)
    except urllib.error.HTTPError as e:
        print(json.dumps({"warn": "hostedContents list failed for %s: HTTP %s" % (message_id, e.code)}),
              file=sys.stderr)
        return out
    for item in data.get("value", []):
        try:
            blob = graph_get(cfg, url + "/%s/$value" % item["id"], binary=True)
            out.append((item["id"], blob))
        except urllib.error.HTTPError as e:
            print(json.dumps({"warn": "hostedContent %s download failed: HTTP %s" % (item["id"], e.code)}),
                  file=sys.stderr)
    return out


def guess_ext(name, content_type, blob):
    name = (name or "").lower()
    _, ext = os.path.splitext(name)
    if ext:
        return ext.lower()
    ct = (content_type or "").lower()
    for e in IMAGE_EXTS | VIDEO_EXTS:
        if e.strip(".") in ct:
            return e
    if blob[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if blob[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    return ".bin"


def extract_frames(path, message_id, idx):
    """Pull ~4 evenly spaced frames from a video with ffmpeg. Returns frame paths."""
    stem = "%s_%02d" % (message_id, idx)
    outdir = os.path.join(FRAMES_DIR, stem)
    os.makedirs(outdir, exist_ok=True)
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", path,
           "-vf", "fps=0.4", "-frames:v", "6", "-q:v", "3",
           os.path.join(outdir, "frame_%02d.jpg")]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=120)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(json.dumps({"warn": "ffmpeg frame extraction failed for %s: %s" % (path, e)}),
              file=sys.stderr)
        return []
    return sorted(os.path.join(outdir, f) for f in os.listdir(outdir))

def download_sharepoint_file(cfg, url):
    """Download a file posted to a team's SharePoint via the Graph sites/drive API.

    contentUrl shape: https://<tenant>.sharepoint.com/sites/<site>/Shared Documents/<file>
    A bearer-token GET on the raw SharePoint URL is rejected (401) — resolve the
    site, then the driveItem by path, then fetch its pre-authenticated downloadUrl.
    Returns bytes.
    """
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc
    path = urllib.parse.unquote(parsed.path)
    m = re.match(r"^/sites/([^/]+)/(.+)$", path)
    if not m:
        raise ValueError("not a /sites/<site>/ SharePoint URL: %s" % url)
    site_name, file_path = m.group(1), m.group(2)
    site = graph_get(cfg, "%s/sites/%s:/sites/%s" % (GRAPH, host, site_name))
    # "Shared Documents" in the URL is the library display name, not part of the
    # drive path — a team-channel file at "Shared Documents/x.mov" is addressed
    # as drive root child "x.mov". Try both forms.
    candidates = [file_path]
    segs = file_path.split("/")
    if segs[0] in ("Shared Documents", "Documents"):
        candidates.append("/".join(segs[1:]))
    item = None
    for candidate in candidates:
        try:
            item = graph_get(cfg, "%s/sites/%s/drive/root:/%s" % (
                GRAPH, site["id"], urllib.parse.quote(candidate)))
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue
            raise
    if item is None:
        raise ValueError("driveItem not found for %s" % url)
    dl = item.get("@microsoft.graph.downloadUrl")
    if not dl:
        raise ValueError("driveItem has no downloadUrl: %s" % url)
    with urllib.request.urlopen(dl, timeout=HTTP_TIMEOUT) as r:
        return r.read()


def download_attachments(cfg, msg, media_log, warn_log):
    """Download inline images + reference attachments for one message. Mutates media_log."""
    import hashlib
    team_id, channel_id, message_id = cfg["team_id"], cfg["channel_id"], msg["id"]
    seen = 0
    blob_hashes = set()  # same image arrives as both hostedContent and inline <img>

    def record(blob, ext, name=""):
        nonlocal seen
        h = hashlib.sha256(blob).hexdigest()
        if h in blob_hashes:
            return  # identical bytes already captured for this post
        blob_hashes.add(h)
        rel = os.path.join("media", "%s_%02d%s" % (message_id, seen, ext))
        with open(os.path.join(DATA_DIR, rel), "wb") as f:
            f.write(blob)
        entry = {"type": "image" if ext in IMAGE_EXTS else "video" if ext in VIDEO_EXTS else "other",
                 "path": rel}
        if entry["type"] == "video":
            entry["frames"] = extract_frames(os.path.join(DATA_DIR, rel), message_id, seen)
        if name:
            entry["name"] = name
        media_log.append(entry)
        seen += 1

    for hc_id, blob in fetch_hosted_contents(cfg, team_id, channel_id, message_id):
        record(blob, guess_ext("", "image", blob))
    raw_body = (msg.get("body") or {}).get("content", "") or ""
    for src in IMG_SRC_RE.findall(raw_body or ""):
        if src.startswith("data:"):
            continue
        try:
            if "graph.microsoft.com" in src:
                blob = graph_get(cfg, src, binary=True)
            else:
                with urllib.request.urlopen(src, timeout=HTTP_TIMEOUT) as r:
                    blob = r.read()
            record(blob, guess_ext(src, "image", blob))
        except (urllib.error.HTTPError, urllib.error.URLError, ValueError) as e:
            warn_log.append("inline image skipped (%s): %s" % (e, src[:120]))
    for att in msg.get("attachments", []):
        content_url = att.get("contentUrl") or ""
        name = att.get("name") or ""
        if not content_url:
            continue
        try:
            if "sharepoint.com" in urllib.parse.urlparse(content_url).netloc:
                blob = download_sharepoint_file(cfg, content_url)
            else:
                blob = graph_get(cfg, content_url, binary=True)
            record(blob, guess_ext(name, att.get("contentType"), blob), name=name)
        except (urllib.error.HTTPError, urllib.error.URLError, ValueError) as e:
            warn_log.append("attachment %r skipped (%s): %s" % (name, e, content_url))


# ---------------------------------------------------------------------------
# Poll
# ---------------------------------------------------------------------------

def known_post_ids():
    ids = set()
    if os.path.exists(POSTS_PATH):
        with open(POSTS_PATH) as f:
            for line in f:
                try:
                    ids.add(json.loads(line)["id"])
                except (json.JSONDecodeError, KeyError):
                    continue
    return ids


def cmd_poll(cfg):
    url = "%s/teams/%s/channels/%s/messages?$top=50" % (
        GRAPH, cfg["team_id"], cfg["channel_id"])
    try:
        data = graph_get(cfg, url)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:500]
        die("channel messages fetch failed: HTTP %s — %s" % (e.code, body))
    known = known_post_ids()
    new_posts = []
    warn_log = []
    for msg in data.get("value", []):
        if msg["id"] in known:
            continue
        if msg.get("messageType") != "message":
            # system/unknownFutureValue events (member added, etc.) — not posts
            continue
        text = strip_html((msg.get("body") or {}).get("content"))
        author = ((msg.get("from") or {}).get("user") or {}).get("displayName")
        team = parse_team(text)
        team_source = "text" if team is not None else None
        if team is None:
            team = apply_ruling.lookup_team(author)  # roster correlation
            team_source = "roster" if team is not None else None
        post = {
            "id": msg["id"],
            "createdDateTime": msg.get("createdDateTime"),
            "author": author,
            "text": text,
            "team": team,
            "team_source": team_source,
            "quest": parse_quest(text),
            "dawn_tagged": bool(re.search(r"dawn", text or "", re.IGNORECASE)),
            "attachments": [],
            "first_seen": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
        }
        download_attachments(cfg, msg, post["attachments"], warn_log)
        # append immediately — a poll killed mid-run (timeout, network) must not
        # lose already-processed posts; the next poll skips known ids from here
        with open(POSTS_PATH, "a") as f:
            f.write(json.dumps(post) + "\n")
        new_posts.append(post)

    if new_posts:
        # new-items.json: what the vision sub-agent should look at this sweep
        reviewable = [p for p in new_posts
                      if p["attachments"] or p["team"] is None or p["quest"] is None]
        save_json(NEW_ITEMS_PATH, {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                   "posts": reviewable})
    elif os.path.exists(NEW_ITEMS_PATH):
        os.remove(NEW_ITEMS_PATH)

    state = load_json(STATE_PATH, {})
    state["last_poll"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    state["last_new_posts"] = len(new_posts)
    save_json(STATE_PATH, state)

    print(json.dumps({
        "ok": True,
        "new_posts": len(new_posts),
        "reviewable": len([p for p in new_posts if p.get("attachments")]),
        "unidentified": len([p for p in new_posts if p["team"] is None or p["quest"] is None]),
        "warnings": warn_log,
    }))


def cmd_setup(cfg):
    device_login(cfg)
    me = graph_get(cfg, GRAPH + "/me")
    print("Signed in as %s <%s>" % (me.get("displayName"), me.get("userPrincipalName")))


def cmd_list_teams(cfg):
    data = graph_get(cfg, GRAPH + "/me/joinedTeams")
    for t in data.get("value", []):
        print("%s\t%s" % (t["id"], t.get("displayName", "")))


def cmd_list_channels(cfg, team_id):
    try:
        data = graph_get(cfg, "%s/teams/%s/channels" % (GRAPH, team_id))
    except urllib.error.HTTPError as e:
        die("channel list failed: HTTP %s — listing channels needs Channel.ReadBasic.All, "
            "which this app does not have. Instead copy a link to the channel in Teams "
            "(right-click the channel → Copy link) and run: "
            "poll_channel.py --channel-link '<pasted link>'" % e.code)
    for c in data.get("value", []):
        print("%s\t%s" % (c["id"], c.get("displayName", "")))


def cmd_channel_link(cfg, link):
    """Extract team/channel IDs from a Teams web link and write them to config.json.

    Link shape: https://teams.microsoft.com/l/channel/<channelId>/<name>?groupId=<teamId>[...]
    Handles URL-encoded and base64-prefixed channel ids (19:xxx@thread.tacv2).
    """
    import base64
    m = re.search(r"teams\.microsoft\.com/l/channel/([^/?#]+)/[^?]*(?:\?[^#]*)?", link)
    if not m:
        die("could not parse a Teams channel link out of: %s" % link)
    channel_id = urllib.parse.unquote(m.group(1))
    team_id = urllib.parse.parse_qs(urllib.parse.urlparse(link).query).get("groupId", [None])[0]
    if channel_id.startswith("19%3A") or channel_id.startswith("19:"):
        pass  # already the real channel id (19:...@thread.tacv2)
    else:
        # some links base64-encode the 19:... form
        try:
            dec = base64.b64decode(channel_id + "===").decode("utf-8", "replace")
            if dec.startswith("19:"):
                channel_id = dec
        except Exception:
            pass
    if not (channel_id.startswith("19:") and "@thread" in channel_id):
        die("channel id did not resolve to a 19:...@thread.tacv2 form: %r" % channel_id)
    if not team_id or not re.match(r"^[0-9a-f-]{36}$", team_id):
        die("groupId (team id) missing or not a GUID in link: %s" % link)
    cfg["channel_id"] = channel_id
    cfg["team_id"] = team_id
    save_json(CONFIG_PATH, cfg)
    print(json.dumps({"ok": True, "team_id": team_id, "channel_id": channel_id,
                      "saved_to": CONFIG_PATH}, indent=2))


def cmd_status(cfg):
    state = load_json(STATE_PATH, {})
    posts = 0
    if os.path.exists(POSTS_PATH):
        with open(POSTS_PATH) as f:
            posts = sum(1 for _ in f)
    print(json.dumps({
        "config_ok": all(cfg.get(k) for k in ("tenant_id", "client_id", "team_id", "channel_id")),
        "auth_cached": os.path.exists(AUTH_PATH),
        "last_poll": state.get("last_poll"),
        "last_new_posts": state.get("last_new_posts"),
        "total_posts_tracked": posts,
    }, indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--setup", action="store_true", help="device-code login + verify /me")
    ap.add_argument("--list-teams", action="store_true")
    ap.add_argument("--list-channels", metavar="TEAM_ID")
    ap.add_argument("--channel-link", metavar="URL",
                    help="extract team/channel IDs from a copied Teams channel link and save to config")
    ap.add_argument("--poll", action="store_true")
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()
    os.makedirs(MEDIA_DIR, exist_ok=True)
    os.makedirs(FRAMES_DIR, exist_ok=True)

    needs_cfg = any([args.setup, args.list_teams, args.list_channels, args.poll])
    if needs_cfg:
        cfg = load_config()
    else:
        # status works even before config exists
        cfg = load_json(CONFIG_PATH) or {}
    if args.setup:
        cmd_setup(cfg)
    elif args.list_teams:
        cmd_list_teams(cfg)
    elif args.list_channels:
        cmd_list_channels(cfg, args.list_channels)
    elif args.channel_link:
        cmd_channel_link(cfg, args.channel_link)
    elif args.poll:
        if not cfg.get("team_id") or not cfg.get("channel_id"):
            die("team_id/channel_id not set in config.json")
        cmd_poll(cfg)
    else:
        cmd_status(cfg)


if __name__ == "__main__":
    main()
