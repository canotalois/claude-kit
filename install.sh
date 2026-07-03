#!/usr/bin/env bash
set -euo pipefail

KIT="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$HOME/.claude"
ln -sf "$KIT/CLAUDE.md" "$HOME/.claude/CLAUDE.md"
echo "Linked ~/.claude/CLAUDE.md -> $KIT/CLAUDE.md"
echo
echo "Add this to ~/.claude/settings.json (merge into the hooks key):"
echo
cat <<JSON
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          { "type": "command", "command": "python3 '$KIT/hooks/check-ai-tells.py'" }
        ]
      }
    ]
  }
}
JSON
