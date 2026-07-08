#!/usr/bin/env bash
set -euo pipefail

KIT="$(cd "$(dirname "$0")" && pwd)"
SETTINGS="$HOME/.claude/settings.json"

mkdir -p "$HOME/.claude"

# 1. Universal conventions, loaded in every project.
ln -sf "$KIT/CLAUDE.md" "$HOME/.claude/CLAUDE.md"
echo "Linked ~/.claude/CLAUDE.md -> $KIT/CLAUDE.md"

# 2. Merge the balanced autopilot permissions and the two hooks into user
#    settings, keeping a timestamped backup. Opt-in.
echo
# Read from the terminal even when this script arrives over a pipe (curl | bash);
# with no usable terminal (CI), default to not touching the user's settings.
reply="n"
if { : </dev/tty; } 2>/dev/null; then
  read -r -p "Merge autopilot permissions + hooks into ~/.claude/settings.json? [y/N] " reply </dev/tty || reply="n"
fi
if [[ "$reply" =~ ^[Yy]$ ]]; then
  KIT="$KIT" SETTINGS="$SETTINGS" python3 - <<'PY'
import json, os, shutil, time

kit = os.environ["KIT"]
path = os.environ["SETTINGS"]

settings = {}
if os.path.exists(path):
    with open(path, encoding="utf-8") as f:
        settings = json.load(f)
    backup = f"{path}.bak.{int(time.time())}"
    shutil.copy2(path, backup)
    print(f"Backed up existing settings to {backup}")

# Union each permission list, dedup, keep order.
with open(os.path.join(kit, "settings", "autopilot.json"), encoding="utf-8") as f:
    autopilot = json.load(f)["permissions"]
perms = settings.setdefault("permissions", {})
for key in ("allow", "ask", "deny"):
    existing = perms.get(key, [])
    merged = existing + [r for r in autopilot.get(key, []) if r not in existing]
    perms[key] = merged

# Append the two hooks with absolute paths (for a non-plugin install), skipping
# any already registered.
def add_hook(event, matcher, command):
    hooks = settings.setdefault("hooks", {}).setdefault(event, [])
    for entry in hooks:
        for h in entry.get("hooks", []):
            if h.get("command") == command:
                return
    hooks.append({"matcher": matcher, "hooks": [{"type": "command", "command": command}]})

add_hook("PreToolUse", "Bash", f"python3 '{kit}/hooks/gate-destructive.py'")
add_hook("PostToolUse", "Write|Edit|MultiEdit", f"python3 '{kit}/hooks/check-ai-tells.py'")

with open(path, "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)
    f.write("\n")
print("Merged permissions and hooks into", path)
PY
  echo "Review the result, then restart Claude Code so the hooks reload."
else
  echo "Skipped. See settings/README.md to merge by hand, or install as a plugin"
  echo "for the hooks (the plugin cannot ship permissions; those stay manual)."
fi
