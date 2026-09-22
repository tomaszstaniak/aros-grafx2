---
type: report
updated: 2026-09-20
---

# ABIv11 launch, 2026-09-20

AROS One x86_64 under QEMU.
Binary: `build/one/grafx2` (9,935,256 bytes, unstripped), staged to
`Qemu Vvfat:GrafX2` with `data/`. Flavour: SDL2, no TTF/Lua/RECOIL/TIFF,
`-lSDL2_image -lSDL2 -lGL -liconv -lpng_nostdio -lz.static`.

## What ran

From a Shell, `stack 8000000`, `cd "Qemu Vvfat:GrafX2"`, `GrafX2`.
An Intuition window titled GrafX2 opened, then a Software Failure
requester. No editor canvas.

```
Error: Illegal address access
Module: stdlib.library  Function: memremove
Stack: memremove +0x1F
       GFX2_UpdateRect +0x106   (src/sdlscreen.c, SDL2)
       Flush_update +0x56
```

Evidence: `window.png`, `crash.png`, `more-backtrace.png`, `more-backtrace-full.png`.

`nm` on the binary shows `GLBase` (SDL2 GL stubs), `SDL_Init`, no
`PNGBase`/`Z1Base`.

The ABIv11 `x86_64-aros-gcc` links through `collect-aros`, which invokes
a linker from a separate toolchain build. Whether that mix caused the
crash is unproven; the stack is in SDL2 texture update, not in png.

## What this did not show

Paint, mouse coordinates, PNG or IFF load/save, a run from `SYS:`,
mainline v1, or a software-renderer build. The requester was left up;
the guest was not rebooted for this report.
