#!/usr/bin/env bash
# One line to start:  curl -fsSL https://raw.githubusercontent.com/yyakowvw/readme-studio/main/install.sh | bash
set -e
DIR="${README_STUDIO_DIR:-$HOME/readme-studio}"
if [ -d "$DIR/.git" ]; then
  git -C "$DIR" pull --quiet --ff-only || true
elif command -v git >/dev/null 2>&1; then
  git clone --quiet --depth 1 https://github.com/yyakowvw/readme-studio "$DIR"
else
  mkdir -p "$DIR" && curl -fsSL https://github.com/yyakowvw/readme-studio/archive/refs/heads/main.tar.gz | tar -xz -C "$DIR" --strip-components 1
fi
exec bash "$DIR/setup.sh" "$@" < /dev/tty
