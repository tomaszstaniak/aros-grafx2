---
type: report
updated: 2026-09-21
---

# GrafX2 revision 2: file-selector crash

## Environment

Verified 2026-09-21: AROS One 1.3 x86_64 ABIv11 under QEMU, 1024x768
desktop, SDL2 software renderer. GCC 10.5.0, AROS One 1.3 SDK. Build flags and link command: `build-final.log`;
recipe `AROS_TARGET=one scripts/build.sh` (unchanged flags).
Upstream pin `f84cb09dc59d706d6e7b28778b01ba911f52298c`, patches 0001–0009.

## Reproduction and correction

The reported screenshot `guru2_1.jpg` shows error 0x80000003 in `strlen`, argument RDI=0,
with `strdup` called by `Scroll_fileselector` in `Button_Load_or_Save`.
The previous local release archive was preserved as
`build/one/grafx2-revision1-preserved.lha` and extracted on the host.
Its binary SHA-256 is
`61232c36cae089ab1675d725b06a8248b0668f628f1074b8ca30ac782a9b43ab`.

Runtime reproduction with that extracted binary:

1. Launch `"Qemu Vvfat:GrafX2-r1-test/GrafX2"` from a Shell at `AROS:`.
2. Dismiss the splash, press F3. Parent directory is selected.
3. Enter fails to change directory to `/`.
4. Down crashes in `stdlib.library strlen`, error 0x80000003.

Evidence: `revision1-crash.ppm`. A failed directory change steals a NULL
save buffer into `Selector->filename`; scrolling then calls `strdup(NULL)`.

Patch 0008 existed locally, uncommitted and marked untested. Its NULL checks prevented this crash: repeating the four
steps selected Burntime without a requester (`revision2-no-crash.ppm`, an
**intermediate eight-patch build**, not the final revision 2 binary).
However, its replacement `chdir("..")` still failed even inside
`AROS:Burntime` (`intermediate-parent-still-fails.ppm`). The original patch
was therefore incomplete; neither its previous header nor a successful
build established correct parent navigation.

Patch 0009 resolves `/` to the absolute parent of the native `getcwd`
path before calling `chdir`. Volume roots remain at the same root. The
change is AROS-only; it removes 0008's unverified parent-path mapping for
other Amiga-family platforms. The CRT retains ownership of directory locks.

## Final runtime checks

The final archive was extracted on the host. Its executable compared equal
to the build with `cmp`, then replaced the test executable while the guest
was stopped. After a restart, the exact extracted executable ran from
`Qemu Vvfat:GrafX2-r2-test/GrafX2` with the same upstream data files.

- F3, Enter on Parent at `AROS:`, Down: selects Burntime, no error flash
  and no crash (`final-root-scroll.ppm`).
- Enter Burntime, Enter Parent: returns from `AROS:Burntime` to `AROS:`
  and selects Burntime (`final-parent.ppm`).
- Cancel Load, F2, select Burntime, click filename (becomes blank), Esc,
  Down: selects C and remains responsive (`final-save-name-scroll.ppm`).

The screenshots are raw QEMU P6 PPM. Files ending `.ppm.png` are labelled
presentation conversions of those originals, not independent evidence.
The crashed old process was suspended; the guest was restarted for the
final binary. No automated test results were written to the guest console.
The warnings behind the intermediate screenshots were the editor's own output.

## Host checks and artifact

- `python3 tests/test-parent-directory.py`: failed before patch 0009
  (`parent-test-before.log`), passed afterwards (`parent-test-after.log`).
  It compiles the actual production function with host replacements only
  at the getcwd/chdir boundary. Covers native root, one-level and nested
  parents, spaces, getcwd failure, NULL and ordinary paths. This does not
  prove the guest CRT; the runtime checks above do.
- `scripts/check-reproduction.sh`: nine patches apply cleanly to the pin
  (`reproduction.log`).
- Build/link succeeded (`build-final.log`). The intermediate build logged
  an existing `strncpy` bound warning in the filename editor (`build.log`).
- LHA created with classic LHa, `aq2o51` (`package.log`). Host extraction
  (`extract.log`) retained executable permission, both Workbench icons,
  data, licenses and `.arospkg/manifest.toml` with revision 2.

Artifact: `build/one/grafx2.x86_64-aros-v11.lha`, 4,203,804 bytes.
SHA-256: `a2f696acb23ddc8a903a3dca1068347e9822cbc239010e4559749202fb4db5e8`.
Executable SHA-256:
`78ef4e6c03ee9685e54c85bc4de702be2039c68531be7afe47f8642ca6fa2d30`.
The companion `.lha.sha256` records the archive checksum. No upload performed.

## What this test did NOT show

No guest Lha extraction, fresh installation, image save/load roundtrip,
new lock test, real hardware test, mainline v1, other architectures,
MorphOS or AmigaOS testing. The filename test cancelled editing; it did
not save a picture. No pictures were written onto vvfat. Earlier image-I/O
and lock results remain scoped to their own reports.
