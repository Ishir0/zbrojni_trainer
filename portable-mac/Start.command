#!/bin/sh
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required to start this local app."
  echo "Install Python 3, then double-click Start.command again."
  printf "Press Return to close this window. "
  read -r _ || true
  exit 1
fi
exec python3 server.py
