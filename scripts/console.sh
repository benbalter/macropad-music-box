#!/usr/bin/env bash
# Open the Macropad's serial console (print output, tracebacks, REPL).
# Exit with Ctrl-A then K (screen's kill command).
set -euo pipefail
PORT="${1:-$(find /dev -maxdepth 1 -name "cu.usbmodem*" | sort | head -1)}"
exec screen "$PORT" 115200
