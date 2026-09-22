# Workflow scripts
#
#   scripts/bootstrap.sh              pin + work copy
#   scripts/bootstrap.sh --recreate   rebuild work/ after pin/series change
#   scripts/save-patch.sh             save staged work/ changes
#   scripts/check-reproduction.sh     apply series in isolation
#   scripts/build.sh                  cross-build GrafX2 for AROS_TARGET
#   scripts/stage.sh                  drawer with binary + data/
#   scripts/package.sh                LHA of the drawer + .arospkg (needs LHA_WRITER)
#   scripts/make-release.sh           release archives in dist/
#
# env.sh is the versioned loader. Copy local.env.example to ignored
# local.env for machine paths. Precedence: environment, local.env, defaults.
# Supported shell: bash. Documented in docs/development.md.
