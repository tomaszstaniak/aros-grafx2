# Single place for machine-local paths and upstream pins. Override with
# environment variables; optional ignored local.env; scripts must not
# hardcode paths elsewhere.
#
# Precedence: existing environment, then local.env, then the defaults below.
# Relative values in local.env resolve against the directory that contains it.

# --- project root and local.env --------------------------------------------
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -f "$PROJECT_ROOT/local.env" ]; then
  eval "$(python3 - "$PROJECT_ROOT/local.env" <<'PY'
import os, shlex, sys
from pathlib import Path
path = Path(sys.argv[1])
base = path.parent
for raw in path.read_text().splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    key, val = line.split("=", 1)
    key = key.strip()
    val = val.strip()
    if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
        val = val[1:-1]
    if not key or key in os.environ:
        continue
    candidate = Path(val)
    if val and not candidate.is_absolute():
        val = str((base / candidate).resolve())
    print(f"export {key}={shlex.quote(val)}")
PY
)"
fi

# --- AROS target selection -------------------------------------------------
# one | mainline. Default is ABIv11 / AROS One (project decision 2026-09-20).
AROS_TARGET="${AROS_TARGET:-one}"

case "$AROS_TARGET" in
  mainline)
    # No portable default: point local.env at a mainline AROS build.
    AROS_GCC_ROOT="${AROS_GCC_ROOT:?set AROS_GCC_ROOT for the mainline target}"
    AROS_SDK="${AROS_SDK:?set AROS_SDK for the mainline target}"
    AROS_SHARED="${AROS_SHARED:-$HOME/Work/AROS/shared-main}"
    ;;
  one)
    AROS_GCC_ROOT="${AROS_GCC_ROOT:-$HOME/Work/AROS/toolchain}"
    AROS_SDK="${AROS_SDK:-$HOME/Work/AROS/sdk}"
    AROS_SHARED="${AROS_SHARED:-$HOME/Work/AROS/shared}"
    ;;
  *)
    echo "scripts/env.sh: unknown AROS_TARGET '$AROS_TARGET' (mainline|one)" >&2
    return 1 2>/dev/null || exit 1
    ;;
esac

AROS_CC="${AROS_CC:-$AROS_GCC_ROOT/x86_64-aros-gcc}"
AROS_AR="${AROS_AR:-$AROS_GCC_ROOT/x86_64-aros-ar}"
AROS_STRIP="${AROS_STRIP:-$AROS_GCC_ROOT/x86_64-aros-strip}"

# Cross-linking needs the volume with the toolchain's linker mounted
# (collect-aros has the linker path hardcoded).
AROS_BUILD_VOLUME="${AROS_BUILD_VOLUME:-}"

# --- Upstream pin ----------------------------------------------------------
REPO_ID="${REPO_ID:-grafx2}"
UPSTREAM_URL="${UPSTREAM_URL:-https://gitlab.com/GrafX2/grafX2.git}"

# --- Project layout --------------------------------------------------------
UPSTREAM_DIR="$PROJECT_ROOT/upstream/$REPO_ID"
WORK_DIR="$PROJECT_ROOT/work/$REPO_ID"
PATCHES_DIR="$PROJECT_ROOT/patches/$REPO_ID"
BUILD_DIR="$PROJECT_ROOT/build/$AROS_TARGET"

# Classic create-capable lha (not Homebrew Lhasa). No portable default;
# scripts/package.sh requires LHA_WRITER from the environment or local.env.
