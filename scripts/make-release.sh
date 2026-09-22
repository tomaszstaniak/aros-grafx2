#!/bin/bash
# Stage the release archives in dist/.
# Nothing here is uploaded: publication is a separate, explicit step
# (git tag + gh release create with these files as assets). GitHub Actions
# are not used; the archives are built here and attached by hand.
#
#   LHA_WRITER=/path/to/lha scripts/make-release.sh
#       -> dist/GrafX2-<ver>.x86_64-aros-v11.lha   (the AROS package)
#          dist/GrafX2-<ver>-source.zip            (this repository at HEAD)
#          dist/SHA256SUMS
#
# <ver> is "<upstream version>-r<AROS package revision>" from
# packaging/manifest.toml, for example 2.9-r3.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=env.sh
source "$SCRIPT_DIR/env.sh"

MANIFEST="$PROJECT_ROOT/packaging/manifest.toml"
UPSTREAM_VER="$(sed -n 's/^version *= *"\(.*\)"/\1/p' "$MANIFEST")"
REVISION="$(sed -n 's/^revision *= *\([0-9]*\).*/\1/p' "$MANIFEST")"
[ -n "$UPSTREAM_VER" ] && [ -n "$REVISION" ] || { echo "make-release: version/revision not found in $MANIFEST" >&2; exit 1; }
VER="$UPSTREAM_VER-r$REVISION"

# The AROS package: scripts/package.sh checks LHA_WRITER and the target.
bash "$SCRIPT_DIR/package.sh" >/dev/null

OUT="$PROJECT_ROOT/dist"
mkdir -p "$OUT"
NAME="GrafX2-$VER.x86_64-aros-v11"
cp "$BUILD_DIR/grafx2.x86_64-aros-v11.lha" "$OUT/$NAME.lha"

# Source: this repository at HEAD. It pins GrafX2 by commit in upstreams.json
# and carries the patches, so scripts/bootstrap.sh reconstructs the exact
# tree that was built; the upstream sources are not duplicated here.
SRC="GrafX2-$VER-source"
rm -rf "$OUT/$SRC" "$OUT/$SRC.zip"; mkdir -p "$OUT/$SRC"
git -C "$PROJECT_ROOT" archive --format=tar HEAD | tar -x -C "$OUT/$SRC"
# Screen captures under docs/attachments are evidence, not source, and
# weigh tens of megabytes; they stay in the repository, not in this zip.
rm -rf "$OUT/$SRC/docs/attachments"
( cd "$OUT" && zip -q -r "$SRC.zip" "$SRC" && rm -rf "$SRC" )

( cd "$OUT" && shasum -a 256 "$NAME.lha" "$SRC.zip" > SHA256SUMS )

echo "archives:"; ( cd "$OUT" && ls -l "$NAME.lha" "$SRC.zip" && cat SHA256SUMS )
echo; echo "publish with:"
echo "  git tag -a v$VER -m 'GrafX2 $UPSTREAM_VER, AROS package revision $REVISION' && git push origin main v$VER"
echo "  gh release create v$VER dist/$NAME.lha dist/$SRC.zip dist/SHA256SUMS --title 'GrafX2 $UPSTREAM_VER, AROS package revision $REVISION' --notes-file <notes>"
