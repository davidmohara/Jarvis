#!/usr/bin/env python3
"""
Regression suite for the ies-git wrapper's policy layer (skills/git/scripts/ies-git).
Plain asserts, runnable directly: `python3 test_ies_git.py`.

Runs against a THROWAWAY git repo in a temp directory with the audit log
redirected: nothing in the real repo is read, staged, or committed, and no
real git-ops.jsonl entries are written by the tests.

Policies under test (each is a skill rule the wrapper mechanizes):
  - `git status` refused with lock-free alternatives
  - commit requires -m and passes Conventional Commits lint
  - commit refuses gated-directory changes without --ack-gated
  - add/commit refuse credential-shaped staged content
  - force push to main refused unconditionally; force push elsewhere needs
    --allow-destructive; reset/clean need --allow-destructive
  - every invocation appends an audit line
"""

import importlib.util
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
    mod.AUDIT_SPOOL = tmp_root / "git-ops-spool-test.jsonl"  # and out of the real .git/ spool
    return mod


def run_wrapper(mod, argv):
    mod.sys.argv = ["ies-git", *argv]
    try:
        mod.main()
        return 0
    except SystemExit as e:
        return e.code or 0


def main():
    tmp = Path(tempfile.mkdtemp(prefix="ies-git-test-"))
    repo = tmp / "repo"
    repo.mkdir()
    os.chdir(repo)
    subprocess.run(["git", "init", "-q"], check=True)
    subprocess.run(["git", "config", "user.email", "test@test"], check=True)
    subprocess.run(["git", "config", "user.name", "Test"], check=True)

    mod = load_module(tmp)
    # Isolate the allowlist so refusal tests exercise real refusals; the
    # allowlist-pass case below writes its own temp allowlist entry.
    mod.ALLOWLIST_PATH = tmp / "allowlist.txt"
    (tmp / "allowlist.txt").write_text("")

    # status refusal
    code = run_wrapper(mod, ["status"])
    assert code == 1, code

    # commit requires -m
    (repo / "a.txt").write_text("hello")
    subprocess.run(["git", "add", "a.txt"], check=True)
    code = run_wrapper(mod, ["commit"])
    assert code == 1, code

    # commit lint: capitalized, past-tense, trailing period all rejected
    for bad in ["Added stuff", "add stuff.", "feat: Adds stuff"]:
        code = run_wrapper(mod, ["commit", "-m", bad])
        assert code == 1, f"lint should reject {bad!r}, got exit {code}"

    # gated dirs: staged workflow file without --ack-gated -> exit 4, nothing committed
    (repo / "workflows").mkdir()
    (repo / "workflows" / "w.md").write_text("gate test")
    subprocess.run(["git", "add", "workflows/w.md"], check=True)
    code = run_wrapper(mod, ["commit", "-m", "feat(rigby): test gated refusal"])
    assert code == 4, code
    log = subprocess.run(["git", "log", "--oneline"], capture_output=True, text=True).stdout
    assert log.strip() == "", "refused commit must not have created a commit"

    # gated dirs with --ack-gated and a clean message -> commit proceeds
    code = run_wrapper(mod, ["--ack-gated", "--ack-root-files", "commit", "-m", "feat(rigby): test gated ack"])
    assert code == 0, code
    log = subprocess.run(["git", "log", "--oneline"], capture_output=True, text=True).stdout
    assert "test gated ack" in log, log

    # secrets in staged content -> exit 5, refused
    (repo / "secret.txt").write_text('aws_key = "AKIAIOSFODNN7EXAMPLE"')
    subprocess.run(["git", "add", "secret.txt"], check=True)
    code = run_wrapper(mod, ["--ack-gated", "commit", "-m", "feat(rigby): test secrets refusal"])
    assert code == 5, code
    subprocess.run(["git", "reset", "-q", "HEAD", "secret.txt"], check=False)

    # secrets in the diff being staged (add path) -> exit 5
    (repo / "secret2.txt").write_text("token = 'abcdef1234567890'")
    code = run_wrapper(mod, ["add", "secret2.txt"])
    assert code == 5, code

    # allowlisted literal passes (exact-literal subtraction, David-approved
    # fake-by-construction strings only; anything else still refuses)
    (tmp / "allowlist.txt").write_text("AKIAIOSFODNN7EXAMPLE\n")
    (repo / "fixture.txt").write_text('aws_key = "AKIAIOSFODNN7EXAMPLE"')
    code = run_wrapper(mod, ["add", "fixture.txt"])
    assert code == 0, f"allowlisted fixture must pass the add scan, got {code}"
    code = run_wrapper(mod, ["--ack-gated", "--ack-root-files", "commit", "-m", "feat(rigby): test allowlisted fixture passes"])
    assert code == 0, f"allowlisted fixture must pass the commit scan, got {code}"
    (repo / "realsecret.txt").write_text('aws_key = "AKIAIOSFODNN7EXAMPLX"')  # NOT allowlisted
    code = run_wrapper(mod, ["add", "realsecret.txt"])
    assert code == 5, f"non-allowlisted secret must still refuse, got {code}"

    # Office lock file staged -> refused outright (err-20261008T225136-RWH7B6 hardening)
    (repo / ".~lock.Test.xlsx#").write_text("office lock artifact")
    subprocess.run(["git", "add", ".~lock.Test.xlsx#"], check=True)
    code = run_wrapper(mod, ["--ack-gated", "--ack-root-files", "commit", "-m", "feat(rigby): lock refusal test"])
    assert code == 6, f"Office lock file must be refused even with all ack flags, got {code}"
    subprocess.run(["git", "reset", "-q", "HEAD", ".~lock.Test.xlsx#"], check=False)

    # Non-canonical root-level file staged -> needs --ack-root-files
    (repo / "loose-deliverable.xlsx").write_text("misplaced deliverable")
    subprocess.run(["git", "add", "loose-deliverable.xlsx"], check=True)
    code = run_wrapper(mod, ["--ack-gated", "commit", "-m", "feat(rigby): root entry refusal test"])
    assert code == 7, f"non-canonical root file must be refused without --ack-root-files, got {code}"
    code = run_wrapper(mod, ["--ack-gated", "--ack-root-files", "commit", "-m", "feat(rigby): root entry ack test"])
    assert code == 0, f"--ack-root-files must let a conscious root-file commit proceed, got {code}"

    # force push to main refused unconditionally (even with --allow-destructive)
    for argv in [["push", "--force", "origin", "main"], ["--allow-destructive", "push", "--force", "origin", "main"]]:
        code = run_wrapper(mod, argv)
        assert code == 3, f"force to main must refuse, got {code}: {argv}"

    # force push elsewhere requires --allow-destructive
    code = run_wrapper(mod, ["push", "--force-with-lease", "origin", "feat/x"])
    assert code == 3, code

    # reset --hard requires --allow-destructive
    code = run_wrapper(mod, ["reset", "--hard"])
    assert code == 3, code

    # audit log: every execution AND every policy refusal recorded.
    # The reset refusal above ran last, so its line is still in the spool;
    # real runs harvest at the next `add` — fold it here deterministically.
    mod.harvest_audit()
    assert not mod.AUDIT_SPOOL.exists() or not mod.AUDIT_SPOOL.read_text().strip(), \
        "harvest must empty the spool"
    entries = [json.loads(l) for l in (tmp / "git-ops-test.jsonl").read_text().splitlines() if l.strip()]
    verbs = {e["verb"] for e in entries}
    assert "commit" in verbs and "add" in verbs, verbs
    ack = [e for e in entries if e["verb"] == "commit" and e["ack_gated"] and not e["refused"]]
    assert ack, "the --ack-gated commit must be visible in the audit log"
    reasons = {e.get("reason") for e in entries if e.get("refused")}
    for expected in ("commit-lint", "gated-dirs-unacked", "secrets-staged", "secrets-add", "force-push-to-main", "destructive-reset"):
        assert expected in reasons, f"refusal reason {expected!r} missing from audit log: {sorted(reasons)}"
    refused_all = [e for e in entries if e["refused"] is True]
    assert refused_all and all(e["exit_code"] != 0 for e in refused_all), "every audited refusal must carry its exit code"

    # spool behavior: a new op appends ONLY to the spool, never the tracked
    # log, so the tracked log is never dirty by construction
    before = mod.AUDIT_LOG.read_text() if mod.AUDIT_LOG.exists() else ""
    run_wrapper(mod, ["status"])  # refused op, audited
    assert mod.AUDIT_SPOOL.exists() and mod.AUDIT_SPOOL.read_text().strip(), \
        "a new op must append to the spool"
    assert (mod.AUDIT_LOG.read_text() if mod.AUDIT_LOG.exists() else "") == before, \
        "a new op must not touch the tracked log"

    print("test_ies_git: all cases passed")


if __name__ == "__main__":
    main()
