# GrafX2 for AROS

Port of [GrafX2](https://grafx2.gitlab.io/grafX2/) — a 256-colour indexed
bitmap paint program inspired by Deluxe Paint and Brilliance — to AROS
x86_64. The first target is AROS One / ABIv11; mainline v1 stays in scope
and unverified until it is actually built and run.

This is a refresh of an existing AROS port (historical i386 build 2.3.1781,
2011), not a new native UI. The program already has SDL2, `PROGDIR:` paths,
and Amiga/AROS volume handling.

## Start here

- [Current state](docs/current-state/overview.md): how the project works now.
- [Backlog](docs/backlog/README.md): proposed and ongoing work.
- [Development](docs/development.md): setup, build, run, and verification.
- [Directory map](docs/directory-map.md): where materials live and who owns them.
- [Patching guide](docs/patching.md): how upstream sources are managed.
- [Documentation](docs/README.md): the documentation entry point.

## Layout

```text
docs/                 maintained documentation and next steps
  current-state/      broad descriptions of implemented behavior
  backlog/            proposed and ongoing changes; done/ holds history
  attachments/        selected supporting images and logs
  references/         our research and source index
tests/                host-side workflow checks (added as they exist)
references/           external study material, separate from our notes
scripts/              workflow entry commands
packaging/            embedded arospkg manifest copied into the LHA
patches/grafx2/       versioned changes to upstream GrafX2
upstream/grafx2/      pinned clean checkout (ignored)
work/grafx2/          editable copy with patches applied (ignored)
build/                generated outputs per target (ignored)
```

Optional roles (`src/`, `assets/`, `content/`, `data/`, `tools/`,
`experiments/`) are unused until they gain real content.

## Project boundaries

One repository (this one) holds project documentation, scripts, patches, and
tests. Upstream GrafX2 is not forked: a pinned clean checkout lives in
`upstream/grafx2/` and all our source changes live in `patches/grafx2/`
(see `upstreams.json`).

## Where the code is

Upstream GrafX2 is not copied into this repository. `upstreams.json` pins
it to one commit and `patches/grafx2/` holds every change this port makes,
as numbered diffs with a header describing the problem, the fix and how
it was verified. `scripts/bootstrap.sh` clones the pinned commit and
applies the series, which gives the exact tree that was built in
`work/grafx2/`. Each GitHub release also carries
`GrafX2-<ver>-full-source.zip`, that patched tree ready to read or build,
as the corresponding source of the binary.

## Targets

Primary: AROS x86_64 ABIv11 (AROS One 1.3). Secondary: mainline AROS
x86_64 (ABIv1), retained and unverified; its SDK has SDL2 but no
SDL2_image. Releases are on the GitHub Releases page: an LHA with an
embedded `.arospkg` manifest, a source zip, and SHA256SUMS.

## Licence

GrafX2 is GPL-2.0; this port, its patches and scripts are distributed
under the same licence ([LICENSE](LICENSE)). Upstream's `COPYRIGHT.txt`
and the licence text ship inside the package drawer.
