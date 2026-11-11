Cut a release of the fork for Home Assistant.

Follow `docs/FORK_MAINTENANCE.md` section 5 "Cutting a release". Bump type (patch/minor/major/X.Y.Z): $ARGUMENTS. If none was given, choose one from the `[Unreleased]` entries using the semver rules in that section and say why. Run `python scripts/release.py check` before opening the PR. Only push the tag after the release PR is merged.
