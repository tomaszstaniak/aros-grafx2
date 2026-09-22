---
type: report
updated: 2026-09-20
---

# Save-dialog filename input, 2026-09-20

AROS One x86_64 under QEMU.
Binary: `build/one/grafx2` (9,940,064 bytes, unstripped), staged to
`Qemu Vvfat:GrafX2` with `data/`. Patch
`0003-aros-sdl2-filename-input` on top of the software renderer.

## What ran

From a Shell, `stack 8000000`, `cd "Qemu Vvfat:GrafX2"`, `GrafX2`.
Esc dismissed About. F2 opened **Save picture**. A click in the filename
field, then the keys `hello`, changed the field from `NO_NAME.GIF` to
`NO_NAME.helloGIF`. Esc restored `NO_NAME.GIF`. The program kept taking
mouse and keyboard; it did not lock.

Evidence: `grafx2-launch.png`, `save-dialog.png`, `filename-click2.png`,
`filename-typed2.png`, `after-esc-filename.png`.

## What this did not show

Completing Save (writing a file), PNG or IFF round-trip, a run from
`SYS:`, or mainline v1. The Save-picture dialog was left open.
