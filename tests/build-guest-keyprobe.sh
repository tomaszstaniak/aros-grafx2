#!/bin/bash
# Build tests/guest-keyprobe.c twice for the AROS target: against the
# current work/grafx2/src/keyboard.c and against the keyboard.c of a given
# work-tree commit, e.g. the one named after 0011-aros-keymap-text-fallback.
# Usage: tests/build-guest-keyprobe.sh <outdir> <old-commit>
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")/../scripts" && pwd)"
# shellcheck source=../scripts/env.sh
source "$SCRIPT_DIR/env.sh"
OUT="$1"; OLD="$2"
mkdir -p "$OUT/old-src"
SRC="$WORK_DIR/src"
git -C "$WORK_DIR" show "$OLD:src/keyboard.c" > "$OUT/old-src/keyboard.c"
CFLAGS="-O2 -g -w --sysroot=$AROS_SDK -I$AROS_SDK/include -I$AROS_SDK/include/SDL2 -DUSE_SDL2 -I$SRC"
LIBS="--sysroot=$AROS_SDK -L$AROS_SDK/lib -lSDL2 -lGL -liconv"
PROBE="$(cd "$(dirname "$0")" && pwd)/guest-keyprobe.c"
"$AROS_CC" $CFLAGS -o "$OUT/keyprobe-new" "$PROBE" "$SRC/keyboard.c" $LIBS
"$AROS_CC" $CFLAGS -o "$OUT/keyprobe-old" "$PROBE" "$OUT/old-src/keyboard.c" $LIBS
rm -rf "$OUT/old-src"
