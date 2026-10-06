#!/usr/bin/env bash
# Copy the toy onto a Macropad mounted at CIRCUITPY (or $CIRCUITPY).
#
# macOS's user-space FAT driver delays metadata writes on small drives, which
# makes writes fail ("Bad address", "Input/output error") and can corrupt
# CIRCUITPY: https://github.com/adafruit/circuitpython/issues/8449
# So this script, rather than a bulk rsync:
#   - remounts the drive with synchronous writes on macOS (Adafruit's fix),
#   - copies only files whose contents changed (each write restarts the board,
#     and fewer writes means fewer chances to hit the bug),
#   - writes each file, syncs, and reads it back to verify, retrying once,
#   - removes package files that no longer exist here (scoped to music_box;
#     circup's libraries are left alone),
#   - stops at the first failure with a clear message instead of carrying on.
set -euo pipefail

DRIVE="${CIRCUITPY:-/Volumes/CIRCUITPY}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/circuitpy"

die() {
  echo "deploy: $*" >&2
  exit 1
}

[ -f "$DRIVE/boot_out.txt" ] || die "no CircuitPython drive at $DRIVE. Plug in the Macropad (or set CIRCUITPY=...)."
grep -q "CircuitPython 10\." "$DRIVE/boot_out.txt" ||
  die "expected CircuitPython 10.x on the board: $(head -1 "$DRIVE/boot_out.txt")"

# Adafruit's remount recipe (remount-CIRCUITPY.sh in their troubleshooting
# guide). Skip with NO_REMOUNT=1. Every write below is verified either way.
if [ "$(uname)" = "Darwin" ] && [ -z "${NO_REMOUNT:-}" ] &&
  ! mount | grep " on $DRIVE " | grep -q noasync; then
  echo "Remounting $DRIVE with synchronous writes (needs sudo)..."
  device="$(mount | awk -v d="$DRIVE" '$3 == d { print $1 }')"
  sudo umount "$DRIVE"
  sudo mkdir -p "$DRIVE"
  sleep 2
  sudo mount -o noasync -t msdos "$device" "$DRIVE"
  echo "  $(mount | grep " on $DRIVE ")"
fi

# stdin from /dev/null so circup can never sit waiting at a prompt.
uvx circup --path "$DRIVE" install neopixel < /dev/null

copy() {
  local rel="$1" src="$SRC/$1" dst="$DRIVE/$1"
  if [ -f "$dst" ] && cmp -s "$src" "$dst"; then
    return
  fi
  mkdir -p "$(dirname "$dst")"
  for _ in 1 2; do
    # Plain cp -X: no extended attributes, so no ._* files on the FAT drive.
    if cp -X "$src" "$dst" && sync && cmp -s "$src" "$dst"; then
      echo "  wrote $rel"
      return
    fi
    echo "  retrying $rel" >&2
    sleep 2
  done
  die "couldn't write $rel. If the drive won't mount or keeps failing, see 'Fixing a corrupted CIRCUITPY drive' in the README."
}

echo "Copying changed files..."
(cd "$SRC" && find . -type f ! -name '._*' ! -path '*/__pycache__/*' | sed 's|^\./||' | sort) |
  while read -r rel; do copy "$rel"; done

# Delete package files that were removed or renamed here.
if [ -d "$DRIVE/lib/music_box" ]; then
  (cd "$DRIVE/lib/music_box" && find . -type f ! -name '._*' | sed 's|^\./||') |
    while read -r rel; do
      if [ ! -f "$SRC/lib/music_box/$rel" ]; then
        rm "$DRIVE/lib/music_box/$rel"
        echo "  removed lib/music_box/$rel"
      fi
    done
fi

find "$DRIVE" -name '._*' -delete 2>/dev/null || true
sync
echo "Deployed to $DRIVE"
