# Tiling WM Setup — Installation Guide

## Prerequisites

- macOS with Homebrew installed
- ~30 minutes
- Willingness to grant Accessibility permissions to two apps

---

## Step 1: Install All Tools

```bash
brew install --cask aerospace
brew install --cask karabiner-elements
brew install --cask wezterm
brew install felixkratz/formulae/borders
brew install font-hack-nerd-font
```

---

## Step 2: Configure Karabiner-Elements (The Hyper Key)

Remaps Caps Lock to Ctrl+Alt — your universal modifier key that doesn't conflict with any standard macOS shortcuts.

Write to `~/.config/karabiner/karabiner.json`:

```json
{
    "profiles": [
        {
            "name": "Default profile",
            "selected": true,
            "simple_modifications": [
                {
                    "from": { "key_code": "caps_lock" },
                    "to": [{ "key_code": "left_option", "modifiers": ["left_control"] }]
                }
            ]
        }
    ]
}
```

Then open Karabiner-Elements from Applications. It will prompt for Accessibility permissions.

**Grant permissions**: System Settings → Privacy & Security → Accessibility → enable Karabiner-Elements.

---

## Step 3: Configure AeroSpace (Tiling Window Manager)

Write to `~/.aerospace.toml`:

```toml
# Start JankyBorders on launch for visual window focus feedback
after-startup-command = [
  'exec-and-forget borders active_color=0xffe1e3e4 inactive_color=0xff494d64 width=5.0'
]

start-at-login = false

# Normalization keeps the window tree clean
enable-normalization-flatten-containers = true
enable-normalization-opposite-orientation-for-nested-containers = true

accordion-padding = 30
default-root-container-layout = 'tiles'
default-root-container-orientation = 'auto'

# Mouse follows focus across monitors
on-focused-monitor-changed = ['move-mouse monitor-lazy-center']

# Prevent accidental cmd-h hiding apps
automatically-unhide-macos-hidden-apps = true

[key-mapping]
    preset = 'qwerty'

[gaps]
    inner.horizontal = 4
    inner.vertical =   4
    outer.left =       6
    outer.bottom =     6
    outer.top =        6
    outer.right =      6

# ──────────────────────────────────────────────
# MAIN BINDINGS — All use Ctrl+Alt (Caps Lock)
# ──────────────────────────────────────────────
[mode.main.binding]

    # Layout toggles
    ctrl-alt-slash = 'layout tiles horizontal vertical'
    ctrl-alt-comma = 'layout accordion horizontal vertical'

    # Vim-style focus (h/j/k/l)
    ctrl-alt-h = 'focus left'
    ctrl-alt-j = 'focus down'
    ctrl-alt-k = 'focus up'
    ctrl-alt-l = 'focus right'

    # Move windows (add Shift)
    ctrl-alt-shift-h = 'move left'
    ctrl-alt-shift-j = 'move down'
    ctrl-alt-shift-k = 'move up'
    ctrl-alt-shift-l = 'move right'

    # Resize
    ctrl-alt-minus = 'resize smart -50'
    ctrl-alt-equal = 'resize smart +50'

    # Numbered workspaces (1-9)
    ctrl-alt-1 = 'workspace 1'
    ctrl-alt-2 = 'workspace 2'
    ctrl-alt-3 = 'workspace 3'
    ctrl-alt-4 = 'workspace 4'
    ctrl-alt-5 = 'workspace 5'
    ctrl-alt-6 = 'workspace 6'
    ctrl-alt-7 = 'workspace 7'
    ctrl-alt-8 = 'workspace 8'
    ctrl-alt-9 = 'workspace 9'

    # Named workspaces — assign letters for quick access
    ctrl-alt-e = 'workspace e'   # Email
    ctrl-alt-m = 'workspace m'   # Messages
    ctrl-alt-c = 'workspace c'   # Calendar
    ctrl-alt-b = 'workspace b'   # Main project
    ctrl-alt-s = 'workspace s'   # Slack/Discord
    ctrl-alt-z = 'workspace z'   # Secondary project

    # Move window to workspace (add Shift)
    ctrl-alt-shift-1 = 'move-node-to-workspace 1'
    ctrl-alt-shift-2 = 'move-node-to-workspace 2'
    ctrl-alt-shift-3 = 'move-node-to-workspace 3'
    ctrl-alt-shift-4 = 'move-node-to-workspace 4'
    ctrl-alt-shift-5 = 'move-node-to-workspace 5'
    ctrl-alt-shift-6 = 'move-node-to-workspace 6'
    ctrl-alt-shift-7 = 'move-node-to-workspace 7'
    ctrl-alt-shift-8 = 'move-node-to-workspace 8'
    ctrl-alt-shift-9 = 'move-node-to-workspace 9'
    ctrl-alt-shift-e = 'move-node-to-workspace e'
    ctrl-alt-shift-m = 'move-node-to-workspace m'
    ctrl-alt-shift-c = 'move-node-to-workspace c'
    ctrl-alt-shift-b = 'move-node-to-workspace b'
    ctrl-alt-shift-s = 'move-node-to-workspace s'
    ctrl-alt-shift-z = 'move-node-to-workspace z'

    # Workspace navigation
    ctrl-alt-tab = 'workspace-back-and-forth'
    ctrl-alt-shift-tab = 'move-workspace-to-monitor --wrap-around next'

    # Window management
    ctrl-alt-f = 'fullscreen'
    ctrl-alt-w = 'close'
    ctrl-alt-enter = 'exec-and-forget open -na wezterm'

    # Disable macOS hide (conflicts with tiling)
    cmd-h = []
    cmd-alt-h = []

    # Join windows into containers
    ctrl-alt-cmd-h = 'join-with left'
    ctrl-alt-cmd-j = 'join-with down'
    ctrl-alt-cmd-k = 'join-with up'
    ctrl-alt-cmd-l = 'join-with right'

    # Config reload
    ctrl-alt-esc = [ 'reload-config', 'mode main' ]

    # Enter modal modes
    ctrl-alt-shift-semicolon = 'mode service'
    ctrl-alt-a = 'mode apps'

# ──────────────────────────────────────────
# SERVICE MODE — Layout resets, volume, etc.
# ──────────────────────────────────────────
[mode.service.binding]
    esc = ['reload-config', 'mode main']
    r = ['flatten-workspace-tree', 'mode main']        # Reset layout
    f = ['layout floating tiling', 'mode main']        # Toggle float
    down = 'volume down'
    up = 'volume up'
    shift-down = ['volume set 0', 'mode main']
    ctrl-alt-esc = [ 'reload-config', 'mode main' ]

# ──────────────────────────────────────────
# APPS MODE — Quick-launch apps
# ──────────────────────────────────────────
[mode.apps.binding]
    m = ['workspace m', 'exec-and-forget open -a "Messages"', 'mode main']
    w = ['workspace m', 'exec-and-forget open -a "WhatsApp"', 'mode main']
    s = ['workspace s', 'exec-and-forget open -a "Slack"', 'mode main']
    t = ['workspace m', 'exec-and-forget open -a "Telegram"', 'mode main']
    d = ['workspace s', 'exec-and-forget open -a "Discord"', 'mode main']
    c = ['workspace c', 'exec-and-forget open -a "Calendar"', 'mode main']
    ctrl-alt-esc = [ 'reload-config', 'mode main' ]
```

Open AeroSpace from Applications. Grant Accessibility permissions same as Karabiner.

---

## Step 4: Configure WezTerm (Terminal)

Write to `~/.wezterm.lua`:

```lua
local wezterm = require 'wezterm'
local config = wezterm.config_builder()

config.font = wezterm.font('Hack Nerd Font')
config.font_size = 11
config.color_scheme = 'Catppuccin Mocha'
config.window_background_opacity = 0.9
config.window_decorations = "RESIZE"

-- Visual bell instead of audio
config.visual_bell = {
  fade_in_function = 'EaseIn',
  fade_in_duration_ms = 150,
  fade_out_function = 'EaseOut',
  fade_out_duration_ms = 150,
}
config.colors = { visual_bell = '#202020' }

config.use_fancy_tab_bar = true
config.hide_mouse_cursor_when_typing = true
config.hide_tab_bar_if_only_one_tab = true

-- CSI-u and Kitty keyboard protocol for proper modifier detection
config.enable_csi_u_key_encoding = true
config.enable_kitty_keyboard = true

-- Make Shift+Enter send literal newline
config.keys = {
  { key = "Enter", mods = "SHIFT", action = wezterm.action.SendString("\n") },
}

return config
```

---

## Step 5: Test JankyBorders

AeroSpace launches it automatically via `after-startup-command`, but you can test manually:

```bash
borders active_color=0xffe1e3e4 inactive_color=0xff494d64 width=5.0
```

Light border on active window, subtle dark on inactive.

---

## Step 6: Verify

1. Press Caps Lock + Enter — should open a WezTerm window
2. Press Caps Lock + 2 — should switch to workspace 2
3. Press Caps Lock + h/j/k/l — should move focus between windows
4. Press Caps Lock + Shift + 1 — should move current window to workspace 1

---

## Post-Install: Customize Named Workspaces

Edit `~/.aerospace.toml` to map letters to your actual workflow. Suggested for David's setup:

```toml
ctrl-alt-w = 'workspace w'   # Windsurf (primary)
ctrl-alt-t = 'workspace t'   # Terminal / Claude Code CLI
ctrl-alt-e = 'workspace e'   # Email (Outlook)
ctrl-alt-m = 'workspace m'   # Teams
ctrl-alt-c = 'workspace c'   # Calendar
ctrl-alt-b = 'workspace b'   # Browser (Chrome)
ctrl-alt-o = 'workspace o'   # OmniFocus
```

---

## Start on Login (Optional)

Once you're confident in the setup:

1. AeroSpace: set `start-at-login = true` in `~/.aerospace.toml`
2. Karabiner: already starts at login by default after first run
3. WezTerm: Add to System Settings → General → Login Items if desired
