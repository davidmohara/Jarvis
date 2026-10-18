#!/usr/bin/env python3
"""
Regression suite for the ies-git wrapper's credential scanner (scan_secrets,
skills/git/scripts/ies-git). Plain asserts, runnable directly:
`python3 test_secret_scanner.py`.

Encodes the false-positive incident of err-20261018T223936 / commit afd1f16f:
deletion lines and bare identifiers are not leaks, while literal secret values
still refuse. The scanner is exercised pure (no git operations, no repo
writes) plus two wrapper-level exit-code checks so the add-path wiring is
covered, not just the function.

Guarantees under test:
  - diff deletion lines and context lines never produce a refusal
  - deletion lines carrying literal secret values warn on stderr, don't block
  - bare identifiers (access_token, save_token) pass; digit-bearing literal
    values assigned to secret-shaped names refuse
  - raw file text (deletions_exempt=False) scans every line as an addition,
    so '- bullet' and '---' frontmatter are content, not diff markers
  - all six known-prefix literal patterns still refuse on added lines
"""

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
from importlib.machinery import SourceFileLoader
from pathlib import Path

WRAPPER_PATH = Path(__file__).resolve().parents[3] / "skills/git/scripts/ies-git"


def load_module(tmp_root):
    # extensionless file: an explicit SourceFileLoader is required
    spec = importlib.util.spec_from_loader("ies_git", SourceFileLoader("ies_git", str(WRAPPER_PATH)))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.AUDIT_LOG = tmp_root / "git-ops-test.jsonl"  # keep test writes out of the real log
    mod.AUDIT_SPOOL = tmp_root / "git-ops-spool-test.jsonl"
    mod.ALLOWLIST_PATH = tmp_root / "allowlist.txt"  # isolate: empty allowlist
    (tmp_root / "allowlist.txt").write_text("")
    return mod


def scan(mod, text, **kwargs):
    """Run scan_secrets with stderr captured so warn-not-refuse is observable."""
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        hits = mod.scan_secrets(text, **kwargs)
    return hits, err.getvalue()


def main():
    tmp = Path(tempfile.mkdtemp(prefix="scanner-test-"))
    mod = load_module(tmp)

    # --- 1. PASS: deletion lines with token identifiers (today's incident) ---
    hits, warns = scan(mod, '-    token = data.get("access_token")\n'
                             '-def save_token(access_token):\n'
                             '-    "access_token": access_token,')
    assert hits == [] and warns == "", (hits, warns)

    # --- 2. PASS: added lines with bare identifiers only ---
    hits, warns = scan(mod, '+def save_token(access_token):\n'
                             '+    token = data["access_token"]\n'
                             '+    token = data.get("access_token")')
    assert hits == [] and warns == "", (hits, warns)

    # --- 3. PASS: context lines with token words ---
    hits, warns = scan(mod, ' token = data.get("access_token")\n'
                             ' def save_token(access_token):')
    assert hits == [] and warns == "", (hits, warns)

    # --- 4. PASS: raw text with markdown bullets / frontmatter, no literals ---
    hits, warns = scan(mod, "---\nname: thing\ntoken: <placeholder>\n---\n"
                             "- token = data.get(\"access_token\")\n"
                             "- item with the word password in prose",
                       deletions_exempt=False)
    assert hits == [] and warns == "", (hits, warns)

    # --- 5. REFUSE: added ghp_ literal ---
    hits, _ = scan(mod, '+GITHUB_TOKEN = "ghp_' + "a" * 36 + '"')
    assert hits and hits[0].startswith("ghp_"), hits

    # --- 6. REFUSE: digit-bearing password literal ---
    hits, _ = scan(mod, '+password = "abc123def456ghi789"')
    assert hits, hits

    # --- 7. REFUSE: raw untracked text with sk- literal (deletions_exempt=False) ---
    hits, _ = scan(mod, "api_key: sk-" + "b" * 24, deletions_exempt=False)
    assert hits and hits[0].startswith("sk-"), hits

    # --- 8. WARN, not refuse: deletion line carrying an AKIA literal ---
    hits, warns = scan(mod, '-aws_key = "AKIAIOSFODNN7EXAMPLE"')
    assert hits == [], hits
    assert "warn:" in warns and "AKIA" in warns, warns

    # --- 9. All six known-prefix patterns refuse on added lines ---
    literals = [
        "AKIAIOSFODNN7EXAMPLX",                                 # AKIA + 16 [0-9A-Z]
        "sk-" + "c" * 24,                                        # sk-
        "ghp_" + "d" * 33,                                       # ghp_
        "github_pat_" + "e" * 34,                                # github_pat_
        "xoxb-" + "f" * 24,                                      # xox[baprs]-
        "-----BEGIN RSA PRIVATE KEY-----",                       # private key block
    ]
    for lit in literals:
        hits, _ = scan(mod, f'+key = "{lit}"')
        assert hits, f"known-prefix literal must refuse: {lit[:20]}"

    # --- 10. The incident composite: deletion of credential-handling code plus
    # addition of a missing-credentials error function passes cleanly ---
    composite = (
        '-    token = data.get("access_token")\n'
        '-def save_token(access_token):\n'
        '-    iat, exp = decode_jwt_expiry(access_token)\n'
        '-        "access_token": access_token,\n'
        '-    if data.get("status") != 0 or not data.get("access_token"):\n'
        '-    token = data["access_token"]\n'
        '+def missing_credentials_error():\n'
        '+    print("missing credentials: set PLAUD_EMAIL/PLAUD_PASSWORD", file=sys.stderr)\n'
        '+    sys.exit(2)\n'
        '+    # token.json or credentials.json expected, none found\n'
    )
    hits, warns = scan(mod, composite)
    assert hits == [] and warns == "", (hits, warns)

    # --- wrapper-level: the add path wires scan_secrets (exit 5 on a real
    # staged literal, exit 0 on the incident composite) ---
    repo = tmp / "repo"
    repo.mkdir()
    os.chdir(repo)
    subprocess.run(["git", "init", "-q"], check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "config", "user.name", "T"], check=True)

    def run_wrapper(argv):
        mod.sys.argv = ["ies-git", *argv]
        try:
            mod.main()
            return 0
        except SystemExit as e:
            return e.code or 0

    (repo / "bad.txt").write_text('token = "' + "a1b2c3d4e5f6g7h" + '"')
    assert run_wrapper(["add", "bad.txt"]) == 5, "add must exit 5 on a raw literal"

    (repo / "clean.txt").write_text(
        'def save_token(access_token):\n'
        '    token = data.get("access_token")\n'
        '    # handles the Plaud token; no literals here\n'
    )
    assert run_wrapper(["add", "clean.txt"]) == 0, "add must pass bare identifier code"

    print("test_secret_scanner: all cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
