---
type: report
updated: 2026-09-20
---

# ABIv11 package smoke test, 2026-09-20

AROS One x86_64 under QEMU. Built against the AROS One 1.3 SDK with
`x86_64-aros-gcc` 10.5.0. Binary
`build/one/grafx2` (9,939,840 bytes, unstripped). Series through
`0004-aros-wb-stack-lock-quit`. Zip
`build/one/GrafX2-x86_64-aros-abiv11.zip` (4,159,051 bytes).

This is a local pre-release drawer, not an upload to
archives.arosworld.org. Follow-up:
[exclusive lock and IFF ILBM](../2026-09-20-lock-ilbm/REPORT.md)
(series 0001–0007, `__stack` 8,388,608, Format `lbm`).

## What ran

With the guest stopped, the staged drawer plus sibling `GrafX2.info` were
copied into the vvfat directory, then the guest was started.
Guest copy:

```
Copy "Qemu Vvfat:GrafX2" SYS:GrafX2 ALL
Copy "Qemu Vvfat:GrafX2.info" SYS:GrafX2.info
```

`List SYS:GrafX2` showed `GrafX2` 9939840, `data/`, `Licenses/`,
`ReadMe.txt`, tool `GrafX2.info` 1757. `List SYS:GrafX2.info` showed
the drawer icon 1757.

CLI launch from `SYS:GrafX2` without a prior `stack` command opened
GrafX2 2.9 (About splash). `__stack = 8000000` is in the binary
(`nm`: `D __stack`, `D __nostdiowin`).

F3 loaded `SYS:GrafX2/data/gfx2.png` (48×48 8bpp). F2 saved
`roundtrip.png` (1433 bytes) in that same directory. Format was
switched to `pbm` and F2 saved `roundtrip.iff` (2436 bytes) via
`Save_IFF`. F3 loaded `roundtrip.iff`; preview and canvas showed the
same logo. `List SYS:GrafX2/data/roundtrip#?` listed both files on
SYS:.

`Q` quit. `WBRun SYS:GrafX2` opened a Wanderer drawer with the PNG
tool icon. A QMP `dclick` on that icon launched GrafX2 2.9 with the
About splash and no extra console. `Q` quit again.

Host checks: `scripts/check-reproduction.sh` applied patches 0001–0004
to the pin. Drawer icon is two concatenated PNGs, kind 2, stack
8000000; tool icon kind 3, same stack. The zip contains `GrafX2/` and
sibling `GrafX2.info`.

## Evidence

- `sys-list.png` — SYS: install
- `sys-launch.png` — CLI from SYS: without `stack`
- `png-loaded.png` — loaded `gfx2.png`
- `png-saved.png` / `list-roundtrip.png` — `roundtrip.png` on SYS:
- `iff-saved.png` / `iff-loaded.png` / `reload-iff-sel2.png` — IFF PBM
- `wbrun-drawer.png` — Wanderer drawer and tool icon
- `wb-dclick.png` — Workbench double-click launch
- `wb-after-quit.png` — selected-state icon after quit

## What this did not show

- The Format list item was `pbm`, not `lbm`. Follow-up selected `lbm`:
  [2026-09-20-lock-ilbm](../2026-09-20-lock-ilbm/REPORT.md).
- Reload of `roundtrip.png` after the IFF load (original PNG load and
  the save are on record).
- Opening the outer `SYS:GrafX2.info` as a drawer icon on the SYS:
  volume window (the file is there; WBRun opened the drawer).
- Native unzip of the zip on the guest (host-built tree was copied).
- Right-Amiga+Q (plain `Q` quit from CLI and Workbench). Follow-up
  used Right-Amiga+Q.
- Exclusive instance lock: this binary only `open()`ed `gfx2.lck`.
  Follow-up uses `Lock(EXCLUSIVE_LOCK)` and does not delete the sentinel.
- mainline v1 runtime.
- Upload to archives.arosworld.org.
- License audit of statically linked dependencies.
