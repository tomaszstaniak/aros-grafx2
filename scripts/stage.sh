#!/bin/bash
# Stage a PROGDIR: drawer: binary + data/ (skins, fonts, default ini),
# Workbench icons, ReadMe, and licenses. Local runnable tree, not a
# published source distribution.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=env.sh
source "$SCRIPT_DIR/env.sh"

BIN="$BUILD_DIR/grafx2"
[ -f "$BIN" ] || { echo "stage: no $BIN — run scripts/build.sh first" >&2; exit 1; }
[ -d "$WORK_DIR/share/grafx2" ] || { echo "stage: missing $WORK_DIR/share/grafx2" >&2; exit 1; }
[ -f "$WORK_DIR/share/grafx2/gfx2.png" ] || { echo "stage: missing gfx2.png" >&2; exit 1; }

STAGE="${GRAFX2_STAGE_DIR:-$BUILD_DIR/package/GrafX2}"
rm -rf "$STAGE"
mkdir -p "$STAGE/data" "$STAGE/Licenses"

cp "$BIN" "$STAGE/GrafX2"
chmod +x "$STAGE/GrafX2"
cp -R "$WORK_DIR/share/grafx2/." "$STAGE/data/"
python3 "$SCRIPT_DIR/build-workbench-icons.py" "$STAGE" "$WORK_DIR/share/grafx2/gfx2.png"

cp "$WORK_DIR/COPYRIGHT.txt" "$STAGE/Licenses/COPYRIGHT.txt"
cp "$WORK_DIR/doc/gpl-2.0.txt" "$STAGE/Licenses/gpl-2.0.txt"

cat > "$STAGE/ReadMe.txt" <<'README'
GrafX2 for AROS x86_64 (ABIv11 / AROS One)
Version 2.9, AROS package revision 3 (2026-09-22)
GPL-2. See Licenses/. Upstream: https://grafx2.gitlab.io/grafX2/

Revision 3
  Shift, Ctrl, Alt, Amiga, Caps Lock, the function keys and the keypad
  operators no longer insert stray characters into text fields such as
  the Save filename. Keypad + - * / . type their characters.

Revision 2
  Fix a Load/Save file-selector crash when scrolling after a failed
  directory change or an empty filename selection. Fix parent-directory
  navigation on AROS.

Install
  Copy the entire GrafX2 drawer AND GrafX2.info (next to the drawer) onto
  an installed writable disk such as SYS:. Do not run from RAM: or from
  Qemu Vvfat: if you intend to save pictures.

Launch
  Open the drawer and double-click the GrafX2 icon (8 MiB stack).
  From a Shell:  stack 8388608
                 cd SYS:GrafX2
                 GrafX2

Use
  F2 save as, F3 load. PNG and IFF ILBM are in the Format list.
  Save pictures on the installed disk, not on Qemu Vvfat.

This build is SDL2, no TrueType, no Lua, no TIFF, no RECOIL.
README

echo "stage: $STAGE"
find "$STAGE" -maxdepth 2 | head -40
