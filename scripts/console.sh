#!/usr/bin/env bash
# Open the Macropad's serial console (print output, tracebacks, REPL).
# Exit with Ctrl-A then K (screen's kill command).
set -euo pipefail
PORT="${1:-$(ls /dev/cu.usbmodem* | head -1)}"
exec screen "$PORT" 115200
