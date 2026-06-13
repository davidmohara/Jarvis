# Tiling WM Setup — Teardown Guide

Complete removal. Restores macOS to its previous state.

---

## Step 1: Quit Running Apps

```bash
osascript -e 'quit app "AeroSpace"'
osascript -e 'quit app "Karabiner-Elements"'
killall borders 2>/dev/null
```

---

## Step 2: Remove Config Files

```bash
rm -f ~/.aerospace.toml
rm -f ~/.wezterm.lua
rm -rf ~/.config/karabiner
```

---

## Step 3: Uninstall via Homebrew

```bash
brew uninstall --cask aerospace
brew uninstall --cask karabiner-elements
brew uninstall --cask wezterm
brew uninstall felixkratz/formulae/borders
brew uninstall font-hack-nerd-font
```

---

## Step 4: Revoke Accessibility Permissions

System Settings → Privacy & Security → Accessibility

Remove entries for:
- AeroSpace
- Karabiner-Elements
- karabiner_grabber
- karabiner_observer

---

## Step 5: Verify

- Caps Lock should function as Caps Lock again
- Windows should float freely (normal macOS behavior)
- No border outlines around windows

---

## Notes

- No system files are modified by this setup. Everything is user-level config.
- SIP is never disabled. Nothing to re-enable.
- If Karabiner's virtual keyboard driver persists, run: `sudo '/Library/Application Support/org.pqrs/Karabiner-DriverKit-VirtualHIDDevice/Applications/Karabiner-VirtualHIDDevice-Daemon.app/Contents/MacOS/Karabiner-VirtualHIDDevice-Daemon' uninstall`
