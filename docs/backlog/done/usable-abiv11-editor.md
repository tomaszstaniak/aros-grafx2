---
type: backlog
stage: done
created: 2026-09-20
updated: 2026-09-20
truth-targets:
  - current-state/overview.md
---

# Establish a usable ABIv11 editor

## Goal

Run GrafX2 on AROS One (x86_64, ABIv11) as a usable indexed-colour editor:
window with skins, painting, mouse drag, load/save PNG, load/save IFF ILBM.
Then package a Workbench drawer. Mainline v1 stays in
scope and unmarked until actually tested.

## Current-state reference

[Current overview](../../current-state/overview.md). Object compile from
2026-09-11 is not a link or a run.

## Findings and decisions

- SDL2 backend, not SDL 1.2 and not a native Intuition rewrite.
- Layout follows the AROS-port template; upstream is read-only.
- Optional Lua/TTF/TIFF/RECOIL stay off for this task.
- Renderer fallback and mouse `SDL_GetMouseState` only if the first run
  shows they are needed. The save-filename freeze showed they are: patch
  0003 polls buttons and skips CaptureMouse on AROS.
- Saves go to an installed writable disk, not vvfat.
- Workbench stack is 8 MiB (`__stack` plus icon tag 0x80001009).

## Next steps

- [x] Convert the directory to the AROS-port template.
- [x] Bootstrap `work/grafx2` from the pin.
- [x] Cross-build and link ABIv11 SDL2.
- [x] Stage `PROGDIR:` + `data/` and package a zip.
- [x] Window on AROS One; save-dialog filename typing after 0003.
- [x] LMB drag paints (host-driven stroke, 2026-09-20).
- [x] PNG/IFF on a writable disk (`SYS:`, not vvfat); Workbench `.info`.
- [x] Record remaining evidence and update current state.

## Verification

Observable on AROS One under QEMU, built against the ABIv11 SDK:

1. Window opens and skins/fonts load.
2. LMB paints; drag tracks the pointer.
3. Load and save a PNG; load and save an IFF/ILBM.
4. Package is a drawer that can be copied to a writable disk.

Environment: AROS One 1.3 under QEMU, screenshots in
`docs/attachments/<run>/`. A "what this did not show" section is required.

## Result

Done for ABIv11 on AROS One, 2026-09-20. Guest evidence is series
0001–0007 staged on SYS: (binary 9,950,048 bytes; `__stack` 0x00800000 in
`.data`). SYS: install, PNG load/save, IFF ILBM save/load (Format `lbm`,
`gfx2.iff` 1062 bytes 3bpp), Workbench double-click of the PNG tool icon.
Exclusive `Lock(EXCLUSIVE_LOCK)` on `gfx2.lck` (A holds; B and C warn;
leftover sentinel; D acquires). 8 MiB stack is `8 * 1024 * 1024`.
Evidence: [2026-09-20 lock and ILBM](../../attachments/2026-09-20-lock-ilbm/REPORT.md).

The local ZIP `build/one/GrafX2-x86_64-aros-abiv11.zip` was rebuilt
2026-09-20 09:18 with `scripts/package.sh` from that 0007 binary (ZIP
4,161,090 bytes; same 9,950,048-byte executable; both icons stack tag
0x00800000). It is not the artefact exercised by the earlier smoke test.
That report is a historical record of the then-0004 ZIP (02:32, binary
9,939,840, `__stack` 8,000,000):
[2026-09-20 ABIv11 package smoke test](../../attachments/2026-09-20-archives/REPORT.md).
`package.sh` later stopped writing ZIP and writes
`grafx2.x86_64-aros-v11.lha` instead (same drawer and `.info` payload).

Not shown: mainline v1 runtime, guest extract of the LHA, license
audit of static dependencies, archives upload, killing A instead of a
clean quit.
