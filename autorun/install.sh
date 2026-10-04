#!/usr/bin/env bash
# Shortcut: makes the bot run on every system boot.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "${SCRIPT_DIR}/autorun.sh" --install
