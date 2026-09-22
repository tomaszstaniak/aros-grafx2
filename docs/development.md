---
type: guide
updated: 2026-09-22
---

# Development

## Environment and targets

Targets, in priority order:

1. **AROS x86_64, ABIv11 (AROS One)** — primary. User-facing editor; first
   useful outcome is paint + mouse + PNG/IFF load/save, then a Workbench
   package.
2. **mainline v1** — secondary, retained. Unverified. The mainline SDK has
   SDL2 but not SDL2_image.
3. **aarch64** — in platform scope, not examined.

Toolchains and SDKs are located through `scripts/env.sh`, overridable in
`local.env` or the environment; `AROS_TARGET` defaults to `one`:

| | `AROS_TARGET=one` (default) | `AROS_TARGET=mainline` |
|---|---|---|
| Toolchain | `AROS_GCC_ROOT`: x86_64-aros GCC 10.5.0 built for ABIv11 | `AROS_GCC_ROOT`: GCC 10.5.0 from a mainline AROS build |
| SDK | `AROS_SDK`: the AROS One 1.3 SDK (`include/`, `lib/`) | `AROS_SDK`: mainline `Developer/` |
| Guest | AROS One 1.3 in QEMU, `AROS_SHARED` as its vvfat directory | mainline AROS in QEMU |

The cross tools sit in the toolchain root, not in `bin/`. The toolchain,
SDK, and guest must be the same AROS build.

First flavour: `API=sdl2 NOTTF=1 NOLUA=1 NORECOIL=1`, no TIFF. Link
`-lSDL2_image -lSDL2 -lpng_nostdio -lz.static` on ABIv11. Do not full-strip;
use `x86_64-aros-strip --strip-unneeded --remove-section .comment` if
stripping at all.

## Commands

| Operation | Command | Expected result |
|---|---|---|
| Bootstrap | `scripts/bootstrap.sh` | Clean pin in `upstream/grafx2/`, work copy in `work/grafx2/`; in-sync is a no-op |
| Rebuild after pin/series change | `scripts/bootstrap.sh --recreate` | Previous work copy moved aside, never deleted by the script |
| Save patch | `scripts/save-patch.sh <NNNN-name> --problem … --solution … --scope …` | Staged `work/` changes written as patch + series entry |
| Check reproduction | `scripts/check-reproduction.sh` | Series applies to the pin in an isolated temp directory |
| Build (AROS) | `scripts/build.sh` | `build/<target>/grafx2` (unstripped unless the script strips safely) |
| Stage drawer | `scripts/stage.sh` | `build/<target>/package/GrafX2/` (binary, `data/`, icons, ReadMe, Licenses) plus sibling `GrafX2.info` |
| Package | `LHA_WRITER=<create-capable-lha> scripts/package.sh` | `build/one/grafx2.x86_64-aros-v11.lha` containing `GrafX2/`, sibling `GrafX2.info`, and `.arospkg/manifest.toml`. ABIv11 only. Homebrew Lhasa cannot create archives. |
| Run on guest | see deploy notes below | Window, skins, paint, PNG/IFF — evidence in attachments |
| Release archives | `LHA_WRITER=<create-capable-lha> scripts/make-release.sh` | `dist/GrafX2-<ver>.x86_64-aros-v11.lha`, `dist/GrafX2-<ver>-source.zip` (HEAD without `docs/attachments/`), `dist/GrafX2-<ver>-full-source.zip` (patched `work/grafx2` tree), `dist/SHA256SUMS`; `<ver>` is `<upstream>-r<revision>` from the manifest |

### Publishing a release

The archives are generated locally, not by GitHub Actions, and attached
to a GitHub Release by hand. `dist/` is
ignored by git; the release assets are the durable copy.

1. Commit the revision (manifest, ReadMe text in `scripts/stage.sh`,
   patches, evidence), then `scripts/make-release.sh`.
2. `git tag -a v<ver>` and push `main` and the tag.
3. `gh release create v<ver> dist/GrafX2-<ver>.x86_64-aros-v11.lha
   dist/GrafX2-<ver>-source.zip dist/GrafX2-<ver>-full-source.zip
   dist/SHA256SUMS --title … --notes …`.
   The script prints the exact commands.

### Deploy notes (AROS One under QEMU)

1. Stage into the guest's vvfat directory (`AROS_SHARED`) only while the
   guest is stopped: vvfat is built at QEMU start, later host copies are
   invisible until restart, and a host write under a running guest can
   corrupt the volume.
2. Copy the **entire** `GrafX2/` drawer **and** `GrafX2.info` (next to the
   drawer) to a writable installed disk (for example `SYS:GrafX2/` plus
   `SYS:GrafX2.info`), not RAM: and not the vvfat volume, before saving
   pictures. POSIX rewrite on FAT32 has silently emptied files.
3. Launch from the drawer icon (8 MiB stack) or `cd SYS:GrafX2` then
   `GrafX2` (`__stack` is 8 MiB; a prior `stack` command is not required).
4. Results come from screenshots; guest writes onto the vvfat volume are
   not a reliable host-side file. Do not save pictures onto `Qemu Vvfat:`.

## Local resources

- `scripts/env.sh` plus ignored `local.env` (copy `local.env.example`).
  Precedence: environment, then `local.env`, then portable defaults.
  Packaging needs `LHA_WRITER` in that file or the environment.
- Pin: `upstreams.json`.

## Reproduction and preservation

- `upstream/` is reproducible from the manifest. Git-ignored. Never edit it.
- `work/` is reproducible from pin + series **only for the saved part**.
  Unsaved edits are unique. `bootstrap.sh` refuses a dirty work tree.
  `--recreate` moves the previous copy aside. Git-ignored is not "safe to
  delete".
- `scripts/check-reproduction.sh` clones from local `upstream/`; it does
  not re-prove the GitLab URL is fetchable.

## File-selector regression

Run `python3 tests/test-parent-directory.py` for the native-path contract
check (host C compiler required, production function from `work/grafx2`).
Guest reproduction steps and evidence are in the
[revision 2 report](attachments/2026-09-21-fileselector/REPORT.md).

## Text-field keyboard regression

Run `python3 tests/test-keysym-to-ansi.py` for the SDL2 `Keysym_to_ANSI`
character contract (host C compiler and Homebrew SDL2 headers required,
production `keyboard.c` from `work/grafx2`). Guest reproduction steps and
evidence are in the
[revision 3 report](attachments/2026-09-22-keyboard-modifiers/REPORT.md).
