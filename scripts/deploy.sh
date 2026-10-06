#!/usr/bin/env bash
# Copy the toy onto a Macropad mounted at CIRCUITPY (or $CIRCUITPY).
# Installs the one library it needs (neopixel) with circup, then syncs
# circuitpy/ onto the drive. The board restarts by itself when files change.
set -euo pipefail

DRIVE="${CIRCUITPY:-/Volumes/CIRCUITPY}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ ! -f "$DRIVE/boot_out.txt" ]; then
  echo "No CircuitPython drive at $DRIVE. Plug in the Macropad (or set CIRCUITPY=...)." >&2
  exit 1
fi

# stdin from /dev/null so circup can never sit waiting at a prompt.
uvx circup --path "$DRIVE" install neopixel < /dev/null

# COPYFILE_DISABLE and the ._* exclude keep macOS from adding resource-fork
# files to the FAT drive. --checksum avoids rewriting unchanged files, since
# every write restarts the board.
COPYFILE_DISABLE=1 rsync -r --checksum --exclude '._*' --exclude '__pycache__' \
  "$ROOT/circuitpy/" "$DRIVE/"
# macOS writes ._* files anyway on some versions; remove them.
find "$DRIVE" -name "._*" -delete
sync
echo "Deployed to $DRIVE"
