Sync this fork with upstream mdlopresti/mealie-mcp.

Follow `docs/FORK_MAINTENANCE.md` section 3 exactly: fetch upstream (no tags), stop if `main..upstream/main` is empty, merge on a `sync/upstream-YYYYMMDD` branch, resolve conflicts with the hotspot table in section 2, fold upstream changelog entries into `## [Unreleased]`, run the section 6 checks, then push and open a PR. Report what upstream changed, any conflicts and how you resolved them, and which semver bump (patch/minor/major) the release should use. Don't tag or release unless asked: $ARGUMENTS
