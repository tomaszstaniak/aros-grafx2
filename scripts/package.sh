#!/bin/bash
# AROS Archives LHA of the staged Workbench drawer. Publication/upload is
# a separate, explicit user action. Not a public source distribution.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=env.sh
source "$SCRIPT_DIR/env.sh"

[ "$AROS_TARGET" = one ] || {
  echo "package: only the runtime-verified AROS One ABIv11 target may be packaged" >&2
  exit 1
}

LHA_WRITER="${LHA_WRITER:?set LHA_WRITER to a create-capable classic lha executable}"
[ -x "$LHA_WRITER" ] || {
  echo "package: LHA_WRITER is not executable: $LHA_WRITER" >&2
  exit 1
}
"$LHA_WRITER" --help 2>&1 | grep -q 'a   Add' || {
  echo "package: $LHA_WRITER cannot create archives (Homebrew Lhasa is read-only)" >&2
  exit 1
}

TEMP="$(mktemp -d "${TMPDIR:-/tmp}/aros-grafx2-package.XXXXXX")"
trap 'rm -rf "$TEMP"' EXIT
GRAFX2_STAGE_DIR="$TEMP/GrafX2" bash "$SCRIPT_DIR/stage.sh"

MANIFEST="$PROJECT_ROOT/packaging/manifest.toml"
[ -f "$MANIFEST" ] || { echo "package: missing $MANIFEST" >&2; exit 1; }
mkdir -p "$TEMP/.arospkg"
cp "$MANIFEST" "$TEMP/.arospkg/manifest.toml"

# Site name is lowercase; version lives in the Archives form, not the filename.
DEST="$BUILD_DIR/grafx2.x86_64-aros-v11.lha"
mkdir -p "$BUILD_DIR"
rm -f "$DEST" "$BUILD_DIR/GrafX2-x86_64-aros-abiv11.zip"
# aq2o51: add, quiet, lh5, header level 1. Generic headers dropped the
# executable protection bit after AROS Lha extract.
# .arospkg stays at the archive root, not inside the drawer, so install
# does not copy it to SYS:Packages/grafx2/.arospkg/.
(
  cd "$TEMP"
  "$LHA_WRITER" aq2o51 "$DEST" GrafX2 GrafX2.info .arospkg
)
ls -l "$DEST"
echo "package: $DEST"
