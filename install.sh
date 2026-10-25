#!/usr/bin/env bash
#
# claude-kit installer for Claude Code. Re-runnable.
#
#   From a checkout:   ./install.sh
#   Remote:            curl -fsSL https://raw.githubusercontent.com/canotalois/claude-kit/main/install.sh | bash
#
# 1. Links CLAUDE.md as ~/.claude/CLAUDE.md, the instructions loaded in every project.
# 2. Links every skill into ~/.claude/skills.
# 3. Optionally merges the two hooks and the permission posture into
#    ~/.claude/settings.json, after asking (CLAUDE_KIT_MERGE=y or =n answers in advance).
# Anything replaced is moved to ~/.claude-kit-backups/<timestamp>/ first.
#
set -euo pipefail

REPO="${CLAUDE_KIT_REPO:-https://github.com/canotalois/claude-kit.git}"
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || true)"

for bin in git python3; do
  command -v "$bin" >/dev/null 2>&1 || { echo "claude-kit needs '$bin' on your PATH." >&2; exit 1; }
done

if [ -n "$SELF_DIR" ] && [ -f "$SELF_DIR/CLAUDE.md" ] && [ -d "$SELF_DIR/skills" ]; then
  KIT="$SELF_DIR"
else
  KIT="${CLAUDE_KIT_DIR:-$HOME/.claude-kit}"
  if [ -d "$KIT/.git" ]; then
    git -C "$KIT" pull --ff-only
  else
    git clone --depth 1 "$REPO" "$KIT"
  fi
fi

BACKUP="$HOME/.claude-kit-backups/$(date +%Y%m%d-%H%M%S)"

# Symlink $2 -> $1, moving any existing file or foreign link to the backup dir.
link() {
  local target="$1" link_path="$2"
  if [ -L "$link_path" ] && [ "$(readlink "$link_path")" = "$target" ]; then return; fi
  if [ -e "$link_path" ] || [ -L "$link_path" ]; then
    local dest="$BACKUP/${link_path#"$HOME"/}"
    mkdir -p "$(dirname "$dest")"
    mv "$link_path" "$dest"
    echo "  backed up $link_path"
  fi
  mkdir -p "$(dirname "$link_path")"
  ln -s "$target" "$link_path"
  echo "  linked $link_path"
}

echo "Conventions"
link "$KIT/CLAUDE.md" "$HOME/.claude/CLAUDE.md"

echo "Skills"
for skill in "$KIT"/skills/*/; do
  name="$(basename "$skill")"
  link "$KIT/skills/$name" "$HOME/.claude/skills/$name"
done

reply="${CLAUDE_KIT_MERGE:-}"
if [ -z "$reply" ] && { : </dev/tty; } 2>/dev/null; then
  read -r -p "Merge the hooks and the permission posture into ~/.claude/settings.json? [y/N] " reply </dev/tty || reply="n"
fi
if [[ ! "$reply" =~ ^[Yy]$ ]]; then
  echo "Skipped the settings merge. See settings/permissions.json to do it by hand."
  exit 0
fi

KIT="$KIT" BACKUP="$BACKUP" python3 - <<'PY'
import json, os, shutil

kit, backup = os.environ["KIT"], os.environ["BACKUP"]
home = os.path.expanduser("~")
path = os.path.join(home, ".claude", "settings.json")

settings = {}
if os.path.exists(path):
    with open(path, encoding="utf-8") as f:
        settings = json.load(f)
before = json.loads(json.dumps(settings))

with open(os.path.join(kit, "settings", "permissions.json"), encoding="utf-8") as f:
    posture = json.load(f)["permissions"]
perms = settings.setdefault("permissions", {})
for key in ("allow", "ask", "deny"):
    existing = perms.get(key, [])
    perms[key] = existing + [r for r in posture[key] if r not in existing]

hooks = (
    ("PreToolUse", "Bash", f"python3 '{kit}/hooks/gate-destructive.py'"),
    ("PostToolUse", "Edit|Write", f"python3 '{kit}/hooks/check-ai-tells.py'"),
)
for event, matcher, command in hooks:
    entries = settings.setdefault("hooks", {}).setdefault(event, [])
    if not any(h.get("command") == command for e in entries for h in e.get("hooks", [])):
        entries.append({"matcher": matcher, "hooks": [{"type": "command", "command": command}]})

if settings == before:
    print("  unchanged", path)
else:
    if os.path.exists(path):
        dest = os.path.join(backup, os.path.relpath(path, home))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(path, dest)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("  merged", path)
PY

echo "Restart Claude Code so the hooks load."
