#!/usr/bin/env bash
#
# claude-kit bootstrap. Clones the kit and installs the universal conventions,
# the two hooks, and the balanced permissions. Re-runnable (updates in place).
#
# Read before running:  curl -fsSL <url>/bootstrap.sh | less
# Then install:          curl -fsSL <url>/bootstrap.sh | bash
#
set -euo pipefail

REPO="${CLAUDE_KIT_REPO:-https://github.com/canotalois/claude-kit.git}"
DIR="${CLAUDE_KIT_DIR:-$HOME/.claude-kit}"

for bin in git python3; do
  command -v "$bin" >/dev/null 2>&1 || {
    echo "claude-kit needs '$bin' on your PATH. Install it and re-run." >&2
    exit 1
  }
done

if [ -d "$DIR/.git" ]; then
  echo "Updating claude-kit in $DIR"
  git -C "$DIR" pull --ff-only
else
  echo "Cloning claude-kit into $DIR"
  git clone --depth 1 "$REPO" "$DIR"
fi

bash "$DIR/install.sh"

echo
echo "claude-kit is installed. Start a project with:  /kickoff <stack>"
echo "Stacks available: $(ls "$DIR/stacks" | tr '\n' ' ')"
