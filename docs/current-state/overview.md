---
type: reference
updated: 2026-09-22
---

# Current project state

## Scope and coverage

GrafX2 for AROS x86_64. Intended coverage is ABIv11 (AROS One) first and
mainline v1 second. This document describes what exists in *this* project
tree, not what the 2011 i386 binary used to do.

## How it works now

The directory is an AROS port project. Upstream GrafX2 is pinned at
`f84cb09dc59d706d6e7b28778b01ba911f52298c` in `upstreams.json`. The clean
checkout lives in `upstream/grafx2/` (moved in place from the previous
GitLab clone). Editable work copies, patches, and binaries are produced by
the scripts in `scripts/`.

GrafX2 itself is a C pixel editor with an SDL2 backend (`src/sdlscreen.c`).
On AROS it already:

- uses `PROGDIR:` as the program and config directory (`src/setup.c`)
- looks for read-only data in `PROGDIR:data/`
- handles Amiga/AROS volumes in the file selector (`src/filesel.c`)
- implements IFF ILBM/PBM/ACBM in `src/ifformat.c` and PNG in
  `src/pngformat.c`
- sets `__stack = 8 * 1024 * 1024` (8,388,608) and `__nostdiowin = 1`
  (`src/osdep.c`, patch 0004) so a Workbench or CLI launch has an 8 MiB
  stack and no extra console
- ships PNG Workbench icons (drawer kind 2, tool kind 3, stack 8 MiB)
  produced by `scripts/build-workbench-icons.py` from `data/gfx2.png`

The staged drawer is `GrafX2/` plus a sibling `GrafX2.info`.
`scripts/package.sh` writes an AROS Archives LHA
(`grafx2.x86_64-aros-v11.lha`) of the drawer, the drawer icon, and
`.arospkg/manifest.toml` (`packaging/manifest.toml`: id `grafx2`,
upstream `version = "2.9"`, this port's `revision = 3`,
`[install].icon = "GrafX2.info"` at the archive root). The tool icon
`GrafX2/GrafX2.info` is a different file and stays inside the drawer.
`[source]` is omitted until there is a corresponding-source archive to
hash; its absence does not block install. The script needs `LHA_WRITER`
pointing at classic jca02266 LHa (`a` Add); Homebrew Lhasa is read-only.
Flags are `aq2o51` (lh5, header level 1) so AROS `Lha` keeps the
executable protection bit. ZIP is no longer produced. Host extract
2026-09-20 15:03: archive 4,202,483 bytes; `GrafX2.info` at the root,
`GrafX2/GrafX2.info` inside the drawer, `.arospkg/manifest.toml` at the
root, binary mode 0755. Nothing has been uploaded to
archives.arosworld.org. Guest `Lha` extract is not done.

The upstream `PLATFORM=AROS` Makefile stanza is a native i386 SDL 1.2
recipe (`sdl-config`, `-lSDL_image`). It is not a ready x86_64 SDL2
cross-build. This project uses `API=sdl2 NOTTF=1 NOLUA=1 NORECOIL=1`.

## Constraints and verification

**Compile probe, 2026-09-11** (objects only, no link, no QEMU): 70/71
listed translation units compiled on ABIv11 with
`-std=gnu99 -O0 -Wall -DUSE_SDL2 -DNOTTF=1 -DNORECOIL -D__no_tifflib__`.
The failure was `c64load.c` (missing `6502.h`). ABIv1 compiled 64/71;
failures were SDL_image.h and the same 6502 gap. `version.c` is generated
by the Makefile. Evidence:
[2026-09-11 compile probe](../attachments/2026-09-11-compile-probe/REPORT.md).

**Launch, 2026-09-20, AROS One under QEMU:** the first unstripped ABIv11 binary
(accelerated SDL2 renderer) starts and dies on the first screen flush:
`Flush_update` → `GFX2_UpdateRect` → `stdlib.library memremove`.
Evidence: [ABIv11 launch](../attachments/2026-09-20-abiv11-launch/REPORT.md),
including the full More… backtrace (`more-backtrace-full.png`).

**Software-renderer retry:** patch
`0002-sdl2-software-renderer-aros` prefers `SDL_RENDERER_SOFTWARE` on AROS.
After stop / restage on vvfat / start (no extra ISO), GrafX2 2.9 opens with
skins, toolbar, palette and the About splash. No requester.
Evidence: `retry-software.png`.

**Save filename freeze, 2026-09-20:** after the software
renderer, the editor painted, but clicking the Save-picture filename field
locked input (no keys, cursor stuck). Cause: GrafX2's SDL2 Readline inserts
printables from `SDL_TEXTINPUT` only, and `Wait_end_of_click` needs
`MOUSEBUTTONUP`; AROS SDL2 may emit neither TEXTINPUT nor a captured
BUTTONUP. Patch `0003-aros-sdl2-filename-input` skips `SDL_CaptureMouse` on
AROS, polls `SDL_GetMouseState` for buttons, starts text input in Readline,
and inserts KEYDOWN characters when `Key_Text` is empty.

**Retry, restaged binary:** F2 opened Save picture; a click
in the filename field then `hello` produced `NO_NAME.helloGIF`. Esc restored
`NO_NAME.GIF`. No freeze. Evidence:
[2026-09-20 filename input](../attachments/2026-09-20-filename-input/REPORT.md).

**Paint, same run:** a host-driven drag on the canvas drew a stroke that
followed the pointer (image coords, not 0,0). Evidence:
`attachments/2026-09-20-remaining/after-paint.png`.

**SYS: install, PNG/IFF PBM, Workbench, 2026-09-20:** the
then-0004 binary (9,939,840 bytes, `__stack` still 8,000,000) was copied
from vvfat to `SYS:GrafX2`. CLI launch without `stack` opened the editor.
F3 loaded `data/gfx2.png`; F2 wrote `roundtrip.png` (1433 bytes) and
`roundtrip.iff` (2436 bytes, Format `pbm`) on SYS:; F3 loaded the IFF.
`WBRun SYS:GrafX2` showed the PNG tool icon; a QMP double-click launched
GrafX2 2.9 with no extra console. Evidence:
[2026-09-20 ABIv11 package smoke test](../attachments/2026-09-20-archives/REPORT.md).
That report is not an archives-ready claim: no guest unzip, no ILBM
label, no exclusive lock, no license audit.

**Exclusive lock and IFF ILBM, 2026-09-20:** series
0001–0007, binary 9,950,048 bytes. `__stack` is the 8-byte integer
0x00800000 in `.data` (nm only shows the symbol at `.data+0x158`). On
SYS: (not vvfat), instance A acquired `Lock(gfx2.lck, EXCLUSIVE_LOCK)`;
B and then C (after B quit) got the existing “other instances are
running” Warning and backups off; after A quit the sentinel file
remained and D acquired the lock. Same run: F2 Format `lbm` saved
`data/gfx2.iff` (1062 bytes, 3bpp ILBM); F3 loaded it
(`Image: lbm 48x 48 3bpp`). Right-Amiga+Q opened Quit.
`scripts/check-reproduction.sh` applied patches 0001–0007 to the pin.
Evidence:
[2026-09-20 lock and ILBM](../attachments/2026-09-20-lock-ilbm/REPORT.md).
The guest tree was the 08:06 staging, not an archive extract. A ZIP of that
tree was built the same morning (`scripts/package.sh`, 09:18) and later
replaced: `package.sh` now writes `grafx2.x86_64-aros-v11.lha` instead.

Do not save pictures onto `Qemu Vvfat:`. A `NO_NAME.GIF` that appeared in
the host vvfat directory is 1753 bytes of non-GIF data. Copy the drawer
to `SYS:` first.

Instance lock on AROS is dos.library `Lock(EXCLUSIVE_LOCK)` on a
persistent empty `gfx2.lck`. posixc has no `lockf`; `fcntl F_SETLK`
returns `EINVAL`; `LockRecord` is filesystem-dependent. The sentinel is
not deleted on exit.

Mouse motion uses `event->x/y`; button *state* is polled on AROS.

## Revision 2 file-selector fix (2026-09-21)

The previous archive reproduced `Scroll_fileselector` calling `strdup(NULL)`
after a failed parent-directory change, causing error 0x80000003 in strlen.
Patch 0008 protects NULL filenames and restores selection after failed chdir.
Its initial `chdir("..")` parent mapping still failed on ABIv11; patch 0009
replaces it with the native absolute parent from getcwd, with volume roots
remaining unchanged. The final parent mapping is AROS-only.

Revision 2 was built with the ABIv11 SDK and GCC 10.5.0, then its host-extracted
executable ran on AROS One 1.3 x86_64 under QEMU. Verified: root
parent plus scroll, return from a child directory, and Save filename editing
cancel plus scroll. The old archive crashed in the root-parent test; the new
one did not. Host LHA extraction verified binary equality, executable mode,
icons and manifest revision. No new image-I/O or guest archive-extraction
claim. Details, hashes and scope:
[revision 2 regression report](../attachments/2026-09-21-fileselector/REPORT.md).

## Reference for changes

Read this document before designing changes. Capture proposals in the
[backlog](../backlog/README.md), then consolidate implemented behavior here.

## Revision 3 keyboard fix (2026-09-22)

Modifier, function and keypad keys inserted stray characters into text
fields because the SDL2 `Keysym_to_ANSI` returned a keycode for keysyms
without a character and AROS SDL2 never emits `SDL_TEXTINPUT`. Patch 0010
returns the keypad character or 0. Verified on AROS One 1.3 under QEMU;
host contract test `tests/test-keysym-to-ansi.py`. Details:
[revision 3 report](../attachments/2026-09-22-keyboard-modifiers/REPORT.md).
