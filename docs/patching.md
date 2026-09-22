---
type: guide
updated: 2026-09-22
---

# Project patch workflow

Profiles `aros` and `upstream-patches` are selected in `project.json`.
This document records this project's repository and actual tools.

## Sources

`upstreams.json` pins the single modified external repository:

| ID | URL | Pinned commit |
|---|---|---|
| `grafx2` | `https://gitlab.com/GrafX2/grafX2.git` | `f84cb09dc59d706d6e7b28778b01ba911f52298c` |

The same ID is used in `upstream/grafx2/`, `work/grafx2/`, and
`patches/grafx2/`. `upstreams.example.json` is the unfilled template.

The 2026-09-11 checkout of `tests/pic-samples` is sparse on this Mac: one
filename under `amiga_icons/16colors/FreshIcons/` is rejected by the host
filesystem. That does not affect the editor sources. A complete copy of
that submodule is the local tarball `aros-assessment/pic-samples-complete.tar`.

## Commands

| Operation | Project command | Required result |
|---|---|---|
| Bootstrap | `scripts/bootstrap.sh` | Clean pinned upstream plus editable patched work copy; verifies work **by content** against the reconstructed pin+series tree **and the recorded base** against the manifest pin; in-sync runs are no-ops |
| Rebuild after change | `scripts/bootstrap.sh --recreate` | Refuses a dirty tree; otherwise moves the previous work copy aside (full `.git`) and rebuilds |
| Save patch | `scripts/save-patch.sh <NNNN-name> --problem … --solution … --scope …` | Staged changes saved with header and series entry before the local baseline advances |
| Check reproduction | `scripts/check-reproduction.sh` | Complete series applies to the pinned base in isolation |
| Build / verify | `scripts/build.sh` | Recorded results for the selected target and scope |

## Patch semantics

- `Base-Commit` is the **manifest pin**, not the local work HEAD.
- `Requires` is the preceding patch from the series (`none` for the first).
- "In sync" is recorded base **and** content, reconstructed from
  `upstream/`'s object database.
- Saving order: patch file and `series` entry are written before the local
  baseline advances; failure rolls both back.

## Patch history

`patches/grafx2/series` lists applied patches. New patches are
`NNNN-description.patch` with the header the existing patches use. Do not edit `upstream/`
sources. As of 2026-09-20 the series is 0001 (PNG stdio callbacks), 0002
(software renderer), 0003 (filename input), 0004 (8 MiB stack / nostdiowin),
0005 (Amiga-Q #elif/KEY_q), 0006 (exclusive dos.library Lock), 0007 (no
sticky software renderer hint). On 2026-09-21, 0008 (NULL-safe file selection)
and 0009 (AROS absolute parent directory) were validated and packaged in
revision 2; see [the regression report](attachments/2026-09-21-fileselector/REPORT.md).
On 2026-09-22, 0010 (SDL2 `Keysym_to_ANSI` returns no character for keys
that have none) fixed stray characters from modifier, function and keypad
keys in text fields; validated on AROS One and packaged in revision
3; see [the keyboard report](attachments/2026-09-22-keyboard-modifiers/REPORT.md).

## Tool verification record

Treat bootstrap/save-patch/check-reproduction as operational only after
they have been run on this repository.

| Scenario | Command/report | Result |
|---|---|---|
| Initial pin with empty series | `scripts/bootstrap.sh` | Not recorded until run |
| Isolated reconstruction | `scripts/check-reproduction.sh` | 2026-09-20 PASS, series of 7 patches on pin `f84cb09` |

## Updating the base

Not performed yet. When it happens: keep the existing series in Git
history, drop patches that landed upstream, adapt the rest, run
`scripts/check-reproduction.sh`, rebuild, and record results.
