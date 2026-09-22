#!/bin/bash
# Cross-build GrafX2 for AROS_TARGET (default one / ABIv11).
#
# Uses the upstream src/Makefile with PLATFORM=AROS so we do not take the
# Darwin/homebrew branch when building on macOS. CC, COPT, LOPT, BIN and
# OBJDIR are passed on the command line: the makefile's native AROS stanza
# still calls sdl-config and links SDL 1.2, which is wrong for this SDK.
#
# Flavour matches the first milestone: SDL2, no TTF, no Lua, no RECOIL,
# no TIFF. 6502 is fetched by the upstream 3rdparty makefile (needed by
# c64load.c even though C64 formats are not a first-run requirement).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=env.sh
source "$SCRIPT_DIR/env.sh"

SRC="$WORK_DIR/src"
[ -f "$SRC/Makefile" ] || { echo "build: no $SRC/Makefile — run scripts/bootstrap.sh first" >&2; exit 1; }
[ -x "$AROS_CC" ] || { echo "build: compiler not found: $AROS_CC" >&2; exit 1; }
[ -d "$AROS_SDK" ] || { echo "build: SDK not found: $AROS_SDK" >&2; exit 1; }

if [ "$AROS_TARGET" = "mainline" ]; then
  if [ ! -f "$AROS_SDK/include/SDL2/SDL_image.h" ] || [ ! -f "$AROS_SDK/lib/libSDL2_image.a" ]; then
    echo "build: mainline SDK has no SDL2_image (headers+lib). That target is unverified; aborting rather than inventing a stub." >&2
    exit 1
  fi
fi

mkdir -p "$BUILD_DIR"

# Host-side fetch of redcode/6502; the AROS compiler is not used here.
if [ ! -f "$WORK_DIR/3rdparty/6502/sources/6502.c" ]; then
  echo "build: fetching 6502 into work/3rdparty (host make)"
  make -C "$WORK_DIR/3rdparty" 6502
fi

# Probe flags plus the defines the makefile would add for this flavour.
# --sysroot is required so the cross compiler uses this SDK, not another.
# -I .../include/SDL2 is required because GrafX2 includes <SDL.h> / <SDL_image.h>.
COPT="-std=gnu99 -Wall -Wno-pointer-sign -O2 -g"
COPT="$COPT --sysroot=$AROS_SDK -I$AROS_SDK/include -I$AROS_SDK/include/SDL2"
COPT="$COPT -DUSE_SDL2 -DNOTTF=1 -DNORECOIL -D__no_tifflib__"

# SDL2_image on this SDK loads PNG via stb (no libpng/jpeg at link).
# GrafX2's own pngformat.c needs real png/zlib objects, not the SDK stubs.
# --sysroot and -L must be on the link line: COPT is not passed to the
# final gcc invocation, and collect-aros otherwise looks only in the
# toolchain (cannot find -lSDL2 / -lSDL2_image).
# -lGL is the SDK stub into gl.library (SDL2's AROS video path calls glA*).
# -liconv is required by libSDL2.a on this SDK.
LOPT="--sysroot=$AROS_SDK -L$AROS_SDK/lib -lSDL2_image -lSDL2 -lGL -liconv -lpng_nostdio -lz.static"

echo "build: target=$AROS_TARGET CC=$AROS_CC out=$BUILD_DIR/grafx2"
make -C "$SRC" \
  PLATFORM=AROS \
  API=sdl2 \
  NOTTF=1 \
  NOLUA=1 \
  NORECOIL=1 \
  CC="$AROS_CC" \
  COPT="$COPT" \
  LOPT="$LOPT" \
  BIN="$BUILD_DIR/grafx2" \
  OBJDIR="$BUILD_DIR/obj" \
  STRIP="true"

ls -l "$BUILD_DIR/grafx2"
