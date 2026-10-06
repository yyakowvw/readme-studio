#!/usr/bin/env bash
# readme-studio setup: prepares Python once, then asks you about your profile.
set -e
cd "$(dirname "$0")"
PY=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; sys.exit(sys.version_info < (3, 9))' 2>/dev/null; then
    PY="$candidate"; break
  fi
done
if [ -z "$PY" ]; then
  echo "Python 3.9+ is needed. On macOS run: xcode-select --install   ·   Linux: sudo apt install python3 python3-venv"
  exit 1
fi
if [ ! -x .venv/bin/python ]; then
  echo "Preparing readme-studio (first run only)…"
  "$PY" -m venv .venv
  .venv/bin/python -m pip install --quiet --disable-pip-version-check -r requirements.txt
fi
exec .venv/bin/python -m studio init "$@"
