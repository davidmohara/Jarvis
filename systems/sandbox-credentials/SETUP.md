# Sandbox Git Credentials Setup

**Problem:** The Cowork sandbox cannot push to GitHub because there are no credentials available inside the VM. Every scheduled dream cycle commits successfully (the git commit runs locally against the mounted repo) but the push fails with `fatal: could not read Username for 'https://github.com'`. David has to manually run `git push origin main` from his Mac after every run.

**Fix:** Fine-scoped GitHub Personal Access Token (PAT), stored in 1Password, written to a credentials file inside the repo (gitignored), resolved at runtime by a committed shell script. The `.git/config` credential.helper path contains no session ID — it resolves via `git rev-parse --show-toplevel` at runtime and survives session rotation automatically.

**Repo confirmed:** `https://github.com/davidmohara/Jarvis.git` (verified via `git remote -v` in the sandbox).

---

## How the credential flow works

The sandbox mounts `~/develop/jarvis` at `/sessions/<session-id>/mnt/jarvis/`. The session ID in that path rotates whenever Cowork rebuilds the sandbox — confirmed behavior. This means any credential.helper path hardcoding the session ID breaks on rotation.

**Rotation-proof design:** A shell script committed at `systems/sandbox-credentials/git-credential-helper.sh` resolves its own directory at runtime via `$(dirname "$0")`, then reads `.git-credentials` from that same directory. Git is configured with:

```
credential.helper = !$(git rev-parse --show-toplevel)/systems/sandbox-credentials/git-credential-helper.sh
```

The `!` prefix tells git to run the value as a shell command. `git rev-parse --show-toplevel` returns the repo root regardless of session ID. The script and credentials file are both inside the mounted Mac filesystem, so they're always reachable.

**Why a script over `credential.helper store`:** The `store` helper requires an absolute path in `.git/config`. Any absolute path containing the session ID breaks on rotation. The script approach defers path resolution to runtime, eliminating the session ID dependency entirely.

**Security:** `.git-credentials` is plaintext with 600 permissions and is gitignored. The helper script contains no token — it only reads from the credentials file.

**Empirically verified:** Tested in sandbox session `sleepy-blissful-meitner`. The stored `.git/config` value contains no session ID. `git credential fill` returns the correct username and password from the credentials file. See test evidence at bottom of this document.

---

## Step 1: Generate the PAT in GitHub

1. Go to https://github.com/settings/tokens (classic tokens).
2. Click **Generate new token (classic)**.
3. Name: `jarvis-sandbox-push`
4. Expiration: **90 days** (set a calendar reminder — see Step 6).
5. Scopes: check **`repo`** only.
6. Click **Generate token**.
7. **Copy the token immediately** — GitHub shows it only once.

> **Fine-grained token note:** Fine-grained tokens work but require additional configuration. Stick with classic for simplicity.

---

## Step 2: Store in 1Password

1. Open 1Password. Go to your **Personal** vault.
2. Create a new **Login** item:
   - Title: `GitHub PAT — jarvis-sandbox-push`
   - Username: `davidmohara`
   - Password: `<paste-token-here>`
   - Website: `https://github.com`
   - Notes: `Scope: repo (classic). Expiry: <set date>. Rotate every 90 days. Used by Cowork sandbox to push davidmohara/Jarvis.`
3. Save.

---

## Step 3: Write the credentials file on the Mac

Run these commands in your Mac terminal (not in the sandbox):

```bash
# Create the credentials file (gitignored, 600 permissions)
touch ~/develop/jarvis/systems/sandbox-credentials/.git-credentials
chmod 600 ~/develop/jarvis/systems/sandbox-credentials/.git-credentials

# Write the token — replace <token from 1Password> with the actual value
echo "https://davidmohara:<token from 1Password>@github.com" \
  > ~/develop/jarvis/systems/sandbox-credentials/.git-credentials
```

Verify it's gitignored (the `.gitignore` rule should already be present — add it if not):

```bash
grep "sandbox-credentials/.git-credentials" ~/develop/jarvis/.gitignore \
  || echo "systems/sandbox-credentials/.git-credentials" >> ~/develop/jarvis/.gitignore
```

Verify the file is excluded from tracking:

```bash
git -C ~/develop/jarvis status systems/sandbox-credentials/.git-credentials
# Expected: nothing (untracked but ignored)
```

---

## Step 4: Configure git (one-time, already done)

This step was performed during the credential flow design session. Verify it's still in place:

```bash
git -C ~/develop/jarvis config --local credential.helper
# Expected: !$(git rev-parse --show-toplevel)/systems/sandbox-credentials/git-credential-helper.sh
```

If it's missing (e.g., after a git config reset), restore it:

```bash
git -C ~/develop/jarvis config --local credential.helper \
  '!$(git rev-parse --show-toplevel)/systems/sandbox-credentials/git-credential-helper.sh'
```

This command can be run from either the Mac terminal or the sandbox — both write to the same `.git/config` on the mounted filesystem.

---

## Step 5: Verify the helper script is executable

The script at `systems/sandbox-credentials/git-credential-helper.sh` must be executable. Check it:

```bash
ls -la ~/develop/jarvis/systems/sandbox-credentials/git-credential-helper.sh
# Expected: -rwx------ (or similar with x bit set)
```

If not executable:

```bash
chmod +x ~/develop/jarvis/systems/sandbox-credentials/git-credential-helper.sh
```

---

## Step 6: Test end-to-end

From inside the sandbox (via workspace bash tool or scheduled task):

```bash
# Verify git resolves credentials correctly
echo -e "protocol=https\nhost=github.com" | git -C /sessions/*/mnt/jarvis credential fill
# Expected: username=davidmohara / password=<your token>

# Dry-run push
git -C /sessions/*/mnt/jarvis push --dry-run origin main
# Expected: Everything up-to-date (or a dry-run push summary)
```

Then do a real push to confirm end-to-end:

```bash
git -C /sessions/*/mnt/jarvis push origin main
```

---

## Step 7: Rotation procedure (90-day cadence)

1. **Calendar reminder:** Set a recurring 90-day reminder titled "Rotate jarvis-sandbox-push PAT".
2. When it fires:
   a. Generate a new PAT in GitHub with the same scope (Step 1).
   b. Update the 1Password entry with the new token.
   c. Overwrite the credentials file: `echo "https://davidmohara:<new token>@github.com" > ~/develop/jarvis/systems/sandbox-credentials/.git-credentials`
   d. No sandbox or git config changes needed — the mounted file updates automatically.
3. Revoke the old PAT at https://github.com/settings/tokens after confirming the new one works.

---

## Security notes

- `.git-credentials` is plaintext. The 600 permissions and `.gitignore` exclusion are the controls. Do not share or commit this file.
- The PAT has `repo` scope. If you want tighter scope in the future, create a fine-grained token scoped to `davidmohara/Jarvis` with `Contents: Read and write` — the helper script approach is already compatible.
- The helper script is committed to the repo. It contains no token — only path resolution logic.
- Session ID rotation has no effect on this design. The credential.helper value in `.git/config` contains no session ID. Verified empirically.

---

## Test evidence (captured 2026-05-31)

```
# Stored credential.helper value — no session ID:
$ git -C /sessions/sleepy-blissful-meitner/mnt/jarvis config --local credential.helper
!$(git rev-parse --show-toplevel)/systems/sandbox-credentials/git-credential-helper.sh

# git credential fill resolves correctly:
$ echo -e "protocol=https\nhost=github.com" | git credential fill
protocol=https
host=github.com
username=testuser
password=testtoken123
```

The test used a dummy credentials file with `testuser:testtoken123`. David replaces this with the real PAT in Step 3.
