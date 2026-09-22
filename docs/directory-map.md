---
type: guide
updated: 2026-09-22
---

# Directory map

Actual starting layout. Unused optional roles are omitted rather than kept
as empty placeholders.

## Repositories and components

One Git repository: this project. Upstream GrafX2 is a nested
checkout in `upstream/grafx2/` with its own Git history; it is not part of
this repository's commits.

## Material ownership

| Role | Actual path | Source / preservation | Ships? |
|---|---|---|---|
| Current behavior | `docs/current-state/` | Versioned | Documentation only |
| Work queue | `docs/backlog/` (`done/` for history) | Versioned tasks | No |
| Test/run evidence | `docs/attachments/<run>/` | Selected logs and screenshots | No |
| Our research | `docs/references/` | Versioned analysis | Documentation only |
| Raw study material | `references/` | Index versioned; raw files local | No |
| Workflow commands | `scripts/` | Versioned entry points (`build.sh`, `stage.sh`, `package.sh`, `build-workbench-icons.py`, patch helpers) | No |
| Host regression tests | `tests/*.py` | Versioned; require materialized work sources and a host C compiler | No |
| Project patches | `patches/grafx2/` | Versioned series + patches | Source of GrafX2 modifications |
| Build upstream | `upstream/grafx2/` | Pinned clone from `upstreams.json`; ignored | No |
| Editable upstream copy | `work/grafx2/` | Pin + series; ignored | No |
| Generated output | `build/<target>/` | Ignored, reproducible | Build intermediates and local packages |
| Local compile-probe logs | `aros-assessment/` | Local; ignored; selected evidence copied to attachments | No |
| Embedded package manifest | `packaging/manifest.toml` | Versioned; copied into the LHA as `.arospkg/manifest.toml` | Yes, inside the archive |

Not applicable yet (create and record here when they gain content):
`src/` (no original support code yet), `assets/`, `content/`, `data/`,
`tools/`, `experiments/`, `tests/fixtures/`.

## Asset/content pipeline

Runtime skins, bitmap fonts, and `gfx2def.ini` are **upstream material** in
`work/grafx2/share/grafx2/`. Staging copies them into
`build/<target>/package/GrafX2/data/`. They are not authored here.
Workbench icons are generated at stage time from `data/gfx2.png` and written
as `GrafX2/GrafX2.info` (tool) and `package/GrafX2.info` (drawer).

## Shared resources

AROS toolchains, SDKs, and QEMU guests are located through
`scripts/env.sh` / `local.env`. Do not write into a running guest's vvfat
directory.
