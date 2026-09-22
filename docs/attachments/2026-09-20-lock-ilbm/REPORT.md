---
type: report
updated: 2026-09-20
---

# Exclusive lock and IFF ILBM, 2026-09-20

AROS One x86_64 under QEMU. Built against the AROS One 1.3 SDK with
`x86_64-aros-gcc` 10.5.0. Binary
`build/one/grafx2` (9,950,048 bytes, unstripped). Series through
`0007-aros-renderer-no-sticky-hint`. `__stack` is the 8-byte integer
0x00800000 (8,388,608) in `.data`; nm shows the symbol at `.data+0x158`,
not that value.

This run is not an archives-ready package test. It checks the exclusive
instance lock on `SYS:` and an IFF ILBM (`lbm`) roundtrip.

## What ran

The guest was stopped, `build/one/package/GrafX2/` was restaged into
the vvfat directory, and the guest was started.
Guest copy of the new binary and icons onto the existing SYS: drawer:

```
Copy "Qemu Vvfat:GrafX2/GrafX2" SYS:GrafX2/GrafX2
Copy "Qemu Vvfat:GrafX2.info" SYS:GrafX2.info
Copy "Qemu Vvfat:GrafX2/GrafX2.info" SYS:GrafX2/GrafX2.info
```

`List SYS:GrafX2` showed `GrafX2` 9950048 and leftover empty `gfx2.lck`
(dated 03:33:07). All launches were `Run SYS:GrafX2/GrafX2` from Shell
so `PROGDIR:` was `SYS:GrafX2`.

### Exclusive lock (A / B / C / D)

- **A** opened GrafX2 2.9 with the About splash (lock acquired, backups
  on). `Status` listed `Process 9 Loaded as command: SYS:GrafX2/GrafX2`.
- **B** (A still running) showed the existing Warning: "Safety backups
  (every minute) are disabled because Grafx2 is running from a
  read-only device, or other instances are running." `Q` then quit B;
  `Status` no longer listed a second GrafX2.
- **C** (B gone, A still holding the lock) showed the same Warning.
  Right-Amiga+Q opened `Quit ?`; Discard quit C.
- Right-Amiga+Q / Discard quit **A**. `List SYS:GrafX2/gfx2.lck` still
  showed the empty sentinel (not deleted).
- **D** then opened with the About splash: lock acquired despite the
  leftover `gfx2.lck`.

### IFF ILBM

In D, F3 loaded `SYS:GrafX2/data/gfx2.png` (48×48 8bpp). F2, Format
dropdown item `lbm` (not `pbm`), saved `gfx2.iff`. F3 selected that
file: `Image: lbm 48x 48 3bpp (1062)` with the logo preview. Return
loaded it on the canvas. After quit, `List SYS:GrafX2/data/gfx2.iff`
showed 1062 bytes at 08:35:40.

`Save_IFF` for `FORMAT_LBM` writes a `FORM`/`ILBM` interleaved bitmap
and uses the minimum bit depth (here 3 planes). `FORMAT_PBM` would be
chunky 8bpp.

The guest was stopped after the run.

## Evidence

- `sys-list.png` — new 9950048 binary on SYS:
- `instance-a.png` — A About splash (lock held)
- `instance-b.png` — B Warning, backups off
- `instance-c.png` — C Warning after B quit
- `gfx2-lck-after-a.png` — sentinel still present after A quit
- `instance-d.png` — D About splash despite leftover `gfx2.lck`
- `format-is-lbm.png` / `fmt-cont-415.png` — Format `lbm`
- `iff-ilbm-selected.png` — `Image: lbm … 3bpp (1062)`
- `iff-ilbm-loaded.png` — canvas after load
- `list-gfx2-iff.png` — `gfx2.iff` 1062 bytes on SYS:

## What this did not show

- Killing A instead of a clean quit (dos.library still auto-UnLocks on
  process death; that path was not exercised here).
- Two instances writing backups at once (the Warning path disables
  them; we did not inspect backup files).
- Guest unzip of `GrafX2-x86_64-aros-abiv11.zip`.
- License audit of statically linked dependencies.
- The accelerated SDL renderer fallback (software create succeeded).
- mainline v1 runtime.
- Upload to archives.arosworld.org.
