# /// script
# requires-python = ">=3.11"
# dependencies = ["mpremote>=1.29", "circup"]
# ///
"""Copy the toy onto a Macropad over USB serial.

    uv run scripts/deploy.py [PORT]

The board hides its CIRCUITPY drive (see circuitpy/boot.py) and writes its
own files, so nothing here goes through the computer's FAT driver. Only
files whose SHA-256 differs from the board's copy are sent, each one is
hashed again after writing, and the first failure stops the deploy.

mpremote's serial transport handles the raw REPL. Its own `fs cp -r` and
`ls` need os.ilistdir, which CircuitPython doesn't have, so directory walks
here use os.listdir instead.
"""

import ast
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

from mpremote.transport_serial import SerialTransport
from serial.tools import list_ports

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "circuitpy"
LIBS = ["neopixel"]  # installed from the Adafruit bundle with circup
PACKAGE = "lib/music_box"  # stale files here are deleted; circup's libs are left alone
ADAFRUIT_VID = 0x239A

# Runs on the board: list every file under a directory.
WALK = """
import os
def _walk(d):
    for n in os.listdir(d):
        p = d + '/' + n
        if os.stat(p)[0] & 0x4000:
            yield from _walk(p)
        else:
            yield p
try:
    print(list(_walk({path!r})))
except OSError:
    print([])
"""


def die(message):
    sys.exit(f"deploy: {message}")


def find_port():
    if len(sys.argv) > 1:
        return sys.argv[1]
    # The console is the board's first serial interface.
    ports = sorted(p.device for p in list_ports.comports() if p.vid == ADAFRUIT_VID)
    if not ports:
        die("no CircuitPython board found over USB serial. Is the Macropad plugged in?")
    return ports[0]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def remote_hash(board, path):
    try:
        return board.fs_hashfile("/" + path, "sha256").hex()
    except Exception:  # missing file
        return None


def stage_libraries(board, staging):
    """Fetch the bundle libraries for the board's CircuitPython version."""
    (staging / "boot_out.txt").write_bytes(board.fs_readfile("/boot_out.txt"))
    (staging / "lib").mkdir()
    circup = Path(sys.executable).parent / "circup"
    subprocess.run(
        [circup, "--path", staging, "install", *LIBS], check=True, stdin=subprocess.DEVNULL
    )
    lib = staging / "lib"
    return {f"lib/{p.relative_to(lib)}": p for p in lib.rglob("*") if p.is_file()}


def local_files():
    return {
        str(p.relative_to(SRC)): p
        for p in SRC.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and not p.name.startswith("._")
    }


def ensure_dirs(board, path, made):
    parts = path.split("/")[:-1]
    for i in range(1, len(parts) + 1):
        d = "/" + "/".join(parts[:i])
        if d not in made:
            if not board.fs_exists(d):
                board.fs_mkdir(d)
            made.add(d)


def main():
    port = find_port()
    print(f"Connecting to {port}...")
    board = SerialTransport(port, baudrate=115200)
    board.enter_raw_repl(soft_reset=False)  # Ctrl-C stops code.py first

    version = board.eval("__import__('sys').implementation.version")
    if version[0] != 10:
        die(f"expected CircuitPython 10.x on the board, found {'.'.join(map(str, version))}")

    first_install = board.eval("__import__('storage').getmount('/').readonly")
    if first_install:
        die(
            "the board can't write its own files yet, because the CIRCUITPY drive is visible.\n"
            "  First time: copy circuitpy/boot.py to the CIRCUITPY drive, then unplug and\n"
            "  replug the Macropad. Already done that? Don't hold the top-left key while\n"
            "  plugging in; that shows the drive (see circuitpy/boot.py)."
        )

    with tempfile.TemporaryDirectory() as tmp:
        files = {**stage_libraries(board, Path(tmp)), **local_files()}

        changed = 0
        made = set()
        for rel, path in sorted(files.items()):
            data = path.read_bytes()
            if remote_hash(board, rel) == sha256(data):
                continue
            ensure_dirs(board, rel, made)
            for attempt in (1, 2):
                board.fs_writefile("/" + rel, data)
                if remote_hash(board, rel) == sha256(data):
                    break
                if attempt == 2:
                    die(f"{rel} didn't match after writing it twice")
            print(f"  wrote {rel}")
            changed += 1

    out = board.exec(WALK.format(path="/" + PACKAGE)).decode()
    for remote in ast.literal_eval(out.strip()):  # a list printed by the board
        rel = remote.lstrip("/")
        if rel not in files:
            board.fs_rmfile(remote)
            print(f"  removed {rel}")
            changed += 1

    print(f"{changed} file(s) changed. Restarting the board.")
    board.exec_raw_no_follow("import supervisor; supervisor.reload()")
    board.close()


if __name__ == "__main__":
    main()
