#!/usr/bin/env bash
# Shortcut: removes the boot-time startup of the bot.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "${SCRIPT_DIR}/autorun.sh" --uninstall
