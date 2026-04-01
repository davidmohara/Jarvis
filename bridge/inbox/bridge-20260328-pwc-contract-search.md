---
id: bridge-20260328-pwc-contract-search
from: code
to: desktop
created: 2026-03-28T00:00:00Z
status: pending
type: file-search
priority: high
---

## Request

Search OneDrive for a client contract for **PwC** (may be labeled "Pricewaterhouse Cooper" or "PricewaterhouseCoopers" or "PWC").

**Where to look:**
- `~/Library/CloudStorage/OneDrive-Improving/` — search for a Dallas contracts folder
- Try paths like: `Contracts/Dallas/`, `Dallas/Contracts/`, `Clients/Dallas/`, or similar
- Search filenames and folder names for: `PWC`, `PwC`, `Pricewaterhouse`, `PricewaterhouseCoopers`

**What David needs:**
- The contract file(s) for PwC under the Dallas folder
- Report back with the full file path(s) so he can access them

**Search commands to try:**
```bash
find ~/Library/CloudStorage/OneDrive-Improving/ -maxdepth 5 -iname "*dallas*" -type d
find ~/Library/CloudStorage/OneDrive-Improving/ -maxdepth 5 -iname "*pwc*" -o -iname "*pricewaterhouse*"
find ~/Library/CloudStorage/OneDrive-Improving/ -maxdepth 5 -iname "*contract*" -type d
```
