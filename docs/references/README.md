---
type: overview
updated: 2026-09-22
---

# Research references

| Topic | Canonical analysis | Sources and revision/date | Relevance |
|---|---|---|---|
| 2026-09-11 compile probe | [Compile probe report](../attachments/2026-09-11-compile-probe/REPORT.md) | GrafX2 `f84cb09d`; ABIv1 and ABIv11 object compile | Shows translation units, not a running program |
| SDL2 on AROS | SDK inspection | Degree 3 on both ABIs; SDL2_image only in ABIv11 SDK (2026-09-12, rechecked 2026-09-20) | First-milestone link libraries |
| PNG/zlib static link | SDK inspection (`nm` on the archives) | `-lpng_nostdio -lz.static`; SDK archives `libpng.a`/`libz.a` are stubs | Avoid depending on `png.library`/`z1.library` version |
| SDL2 mouse coordinates | Earlier SDL2 ports to AROS One | `ev.button.x/y` returned (0,0); poll `SDL_GetMouseState` | Verify GrafX2 motion events before patching |
| FAT32 POSIX overwrite | Earlier ports to AROS One | Silent empty file on rewrite (AROS One 1.3, 2026-09-17) | Saves must not target vvfat/FAT32 as durable storage |
