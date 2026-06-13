# Project: macOS Tiling WM Setup (Omarchy-style)

**Created**: 2026-03-04
**Status**: Proposed
**Owner**: David
**Rocks**: Dev productivity / workflow optimization
**Source**: https://danieltenner.com/omarchy-on-macos-aerospace-karabiner-setup-guide-for-claude-code/

## Objective

Keyboard-driven tiling window manager on macOS — vim-style navigation, named workspaces, no mouse needed. Optimized for multi-instance Windsurf + Claude Code CLI workflow.

## ICE Score

| Factor | Score (1-10) | Notes |
|--------|-------------|-------|
| **I**mpact | 7 | Real friction reduction for heavy multi-window dev workflow |
| **C**onfidence | 8 | Well-documented, all Homebrew-installable, easy teardown |
| **E**ase | 8 | ~30 min install, config files provided |
| **Average** | 7.7 | |

## Components

| Omarchy (Linux) | macOS Equivalent | Purpose |
|-----------------|-----------------|---------|
| Hyprland | AeroSpace | Tiling window manager |
| Super key | Karabiner-Elements | Caps Lock → Ctrl+Alt modifier |
| Window borders | JankyBorders | Visual focus indicator |
| Alacritty/Ghostty | WezTerm | GPU-accelerated terminal |
