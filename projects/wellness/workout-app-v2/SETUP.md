# Workout App Setup

## Step 1 — Create GitHub repos

1. Go to github.com and sign in
2. Create a **public** repo called `workout` (this hosts the app)
3. Create a **private** repo called `workout-data` (this stores your data)

## Step 2 — Deploy to GitHub Pages

1. In the `workout` repo, upload `index.html` and `manifest.json` from this folder
2. Go to Settings → Pages → Source: Deploy from branch → branch: main → folder: / (root)
3. Save. Your app URL will be: `https://YOUR_USERNAME.github.io/workout`

## Step 3 — Create a Personal Access Token

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Name: "Workout App"
4. Expiration: No expiration (or 1 year)
5. Scopes: check **repo** only
6. Generate and copy the token (you only see it once)

## Step 4 — First launch

1. Open `https://YOUR_USERNAME.github.io/workout` in Safari on your iPhone
2. The app will show a setup screen
3. Enter your GitHub username, `workout-data` as the repo name, and your PAT
4. Tap Connect

## Step 5 — Add to home screen

1. In Safari, tap the Share button
2. Tap "Add to Home Screen"
3. Name it "Workout" → Add
4. Open from your home screen — it runs fullscreen like a native app

## How data works

- Every completed session saves to `workout-log.json` in your private `workout-data` repo
- History tab reads from localStorage (fast) — pull from GitHub anytime to sync across devices
- The JSON file is human-readable and importable to Excel

## Auto-lock

Go to Settings → Display & Brightness → Auto-Lock → set to Never while at the gym.
Or set it back to 5 min when done — the app will keep requesting wake lock but iOS may override.
