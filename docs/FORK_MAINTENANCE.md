# Fork Maintenance Guide (for LLM agents)

This repository is **warinthestars/mealie-mcp**, a fork of
**mdlopresti/mealie-mcp** ("upstream"). The fork adds a Home Assistant app
(add-on) that runs the server over streamable HTTP. This file tells an agent
how to (1) pull in upstream changes, (2) keep the container base image and
dependencies current, (3) add the owner's own changes, and (4) ship a release
that Home Assistant will pick up.

**Precedence:** `CLAUDE.md` came from upstream. For anything about git remotes,
versions, releases, images or deployment, **this file wins**. CLAUDE.md is still
correct for code structure and the endpoint implementation pattern.

---

## 1. Ground rules

| Thing | Value |
| --- | --- |
| `origin` | `https://github.com/warinthestars/mealie-mcp` (push here) |
| `upstream` | `https://github.com/mdlopresti/mealie-mcp` (read only, never push) |
| Default branch | `main` (protected by convention: change via PRs) |
| App image | `ghcr.io/warinthestars/mealie-mcp-addon:<X.Y.Z>` (built only from `vX.Y.Z` tags) |
| Version source of truth | `CHANGELOG.md`, kept in sync by `scripts/release.py` |
| Upstream tags | **Not fetched** (`remote.upstream.tagOpt = --no-tags`). Fork tags and upstream tags share the `v*` namespace and would clash. |

- **Never hand-edit version numbers** in `mealie_mcp/config.yaml`,
  `src/__init__.py` or `mealie_mcp/CHANGELOG.md`. Use `scripts/release.py`.
- **Never push to `upstream`**, never force-push `main`, never delete or move
  an existing `v*` tag (Home Assistant users may already be on that image).
- **Merge, don't rebase**, when syncing upstream. `main` is already published.
- Work on a branch, open a PR, let CI pass, then merge (see CLAUDE.md "Git Workflow").
- If `git fetch upstream` fails here, still check for `.git/*.lock` files
  before rerunning; a leftover lock makes later git commands fail with "File exists".

Ignore these upstream-specific details in CLAUDE.md: `recipe.vilo.network` (use
the owner's `MEALIE_URL` from `.env`), `kubectl` debugging, and
`ghcr.io/mdlopresti/...` image names.

## 2. What the fork owns

Keep fork-specific work in **fork-owned files** wherever possible. Upstream
never touches these, so syncs merge cleanly.

**Fork-owned (upstream does not have them):**
- `repository.yaml` - Home Assistant app repository manifest
- `mealie_mcp/` - the app: `config.yaml`, `Dockerfile`, `run.py`, `DOCS.md`,
  `README.md`, `translations/`, and generated `CHANGELOG.md`
- `src/http_transport.py` - streamable HTTP transport + bearer-token middleware
- `scripts/release.py` - semver release tool
- `.github/workflows/ha-addon.yml` - version check on PRs, image build on tags
- `docs/FORK_MAINTENANCE.md` (this file), `AGENTS.md`, `.claude/commands/sync-upstream.md`

**Fork patches to upstream files (conflict hotspots). Lines are marked `FORK:`
where the file format allows comments:**

| File | Fork change | When resolving conflicts |
| --- | --- | --- |
| `src/server.py` | Bottom entry point is `def main()` choosing stdio vs HTTP via `MCP_TRANSPORT`; `if __name__ == "__main__": main()` | Take upstream's tools/resources, then re-apply `main()` exactly. `mealie_mcp/run.py` calls `server.main()`; it must exist. |
| `requirements.txt` | `fastmcp>=2.3.2`, `uvicorn>=0.30.0` | Keep the higher of upstream's and the fork's minimums. Never drop `uvicorn`. |
| `src/__init__.py` | `__version__ = "X.Y.Z"` | Always keep the **fork's** value. |
| `CHANGELOG.md` | Fork release sections (1.9.0+), fork link refs | See section 3, step 4. |
| `README.md` | "Home Assistant App" section at the end | Keep the section, take upstream's other edits. |
| `CLAUDE.md` | Pointer to this file at top; "Version Management" rewritten | Keep both fork blocks, take upstream's other edits. |
| `.github/dependabot.yml` | Extra docker entry for `/mealie_mcp` | Keep it. |

If upstream renames or restructures something the fork depends on (for example
`mcp = FastMCP(...)` in `server.py`, or the `MEALIE_URL` / `MEALIE_API_TOKEN`
env vars read in `src/client.py`), update `src/http_transport.py` /
`mealie_mcp/run.py` to match. Don't reintroduce the old upstream code.

## 3. Syncing with upstream

```bash
git checkout main && git pull origin main
git fetch upstream                      # tags are not fetched (by design)
git log --oneline main..upstream/main   # what's new upstream; stop if empty
git checkout -b sync/upstream-$(date +%Y%m%d)
git merge upstream/main --no-ff -m "chore: merge upstream mdlopresti/mealie-mcp"
```

1. **Resolve conflicts** using the hotspot table above. Default rule: take
   upstream's version of anything upstream owns; re-apply only the fork's marked changes.
2. **Line endings:** this checkout is on Windows and files may show as
   modified purely from CRLF. Judge real changes with
   `git diff --ignore-cr-at-eol`. Don't commit whole-file line-ending churn.
3. **Find the upstream version you merged:** look at upstream's newest
   `## [X.Y.Z]` heading in its CHANGELOG (`git show upstream/main:CHANGELOG.md | grep -m3 '^## \['`)
   or `git ls-remote --tags upstream`.
4. **CHANGELOG.md:**
   - Upstream's new entries go under the fork's `## [Unreleased]`, in the matching
     `### Added / Changed / Fixed / Removed` groups.
   - **Do not** keep upstream's `## [X.Y.Z]` release headings for versions the fork
     hasn't released. The fork has its own version line.
   - Add: `- Merged upstream mdlopresti/mealie-mcp vX.Y.Z (<short-sha>)` under `### Changed`.
   - Leave the fork's existing release sections and link refs untouched.
5. **Verify** (section 6), commit, push the branch, and open a PR titled
   `chore: sync upstream vX.Y.Z`.
6. After merge, cut a release (section 5) so Home Assistant gets the new code.
   Bump **minor** if upstream added tools/features, **patch** for fixes only,
   **major** if upstream made breaking changes (removed/renamed tools or env vars).

## 4. Keeping the image and dependencies current

The app image is `python:3.12-slim` (`mealie_mcp/Dockerfile`) plus
`requirements.txt`. Images are immutable per version, so **a base-image or
dependency update only reaches Home Assistant through a new release.**

- Dependabot opens weekly PRs for `pip` (`/`), `docker` (`/` and `/mealie_mcp`)
  and GitHub Actions. For each one: let CI pass, then add a line under
  `## [Unreleased]` → `### Changed` (e.g. `- Updated base image to python:3.12.x-slim`),
  merge, and cut a **patch** release.
- With no Dependabot activity, do a monthly security refresh: a patch release
  that only rebuilds picks up the latest `python:3.12-slim` and dependency
  patch versions (`requirements.txt` uses `>=` minimums). Log it as
  `- Rebuilt on latest python:3.12-slim base image and dependencies`.
- Moving to a new Python minor (e.g. 3.13): change `FROM` in **both**
  `Dockerfile` (root, stdio image) and `mealie_mcp/Dockerfile`, plus
  `python-version` in `.github/workflows/*.yml`. That's a minor release.
- FastMCP majors have changed APIs before. After any FastMCP bump, run the
  HTTP smoke test in section 6. `src/http_transport.py` relies on
  `mcp.http_app(path=..., middleware=[...])`.

## 5. Adding the owner's own changes

1. `git checkout main && git pull origin main && git checkout -b feat/<short-name>`
2. Implement it:
   - **New Mealie tools:** follow CLAUDE.md "Implementation Pattern"
     (client method → `tools/*.py` → `@mcp.tool()` in `server.py`). Name new
     tool modules distinctively (e.g. `src/tools/fork_<area>.py`) so upstream
     additions don't collide.
   - **App behaviour / options:** edit `mealie_mcp/config.yaml` (`options` +
     `schema`), map the option to an env var in `mealie_mcp/run.py`, document it
     in `mealie_mcp/DOCS.md` and `mealie_mcp/translations/en.yaml`.
   - **Transport/auth:** `src/http_transport.py`.
   - Prefer new files over edits to upstream files. When you must edit an
     upstream file, keep the edit small and mark it with a `# FORK:` comment.
3. Add entries under `## [Unreleased]` in `CHANGELOG.md` (Keep a Changelog
   groups). Write them for a Home Assistant user. The app's update dialog shows them.
4. Verify (section 6), commit with a conventional message (`feat:`, `fix:`,
   `chore:`, `docs:`), push, `gh pr create --fill`, wait for CI, then `gh pr merge --squash`.
5. Release (below) when the user wants it in Home Assistant.

### Cutting a release

```bash
git checkout main && git pull origin main
python scripts/release.py bump patch    # or minor / major / X.Y.Z / X.Y.Z-rc.1
git checkout -b release/vX.Y.Z
git add -A && git commit -m "chore: release vX.Y.Z"
git push origin release/vX.Y.Z && gh pr create --fill
# after CI passes and the PR is merged:
git checkout main && git pull origin main
git tag vX.Y.Z && git push origin vX.Y.Z
gh run watch    # "Home Assistant App" workflow builds and pushes the image
```

`release.py bump` refuses to run with an empty `[Unreleased]` section, and the
workflow refuses to overwrite an image tag that already exists. If a release
went out broken, **don't retag**: fix forward with the next patch version.

Semver for this project:
- **major:** removed/renamed MCP tools, changed or removed app options/env vars,
  changed default port or `/mcp` path.
- **minor:** new tools, new app options, upstream feature merges, Python minor upgrade.
- **patch:** bug fixes, dependency/base-image refreshes, docs.

The GHCR package `mealie-mcp-addon` must be **public**, or Home Assistant can't pull it.

## 6. Verification checklist

Run before every PR:

```bash
python scripts/release.py check                       # versions + app changelog in sync
find src mealie_mcp -name '*.py' -exec python -m py_compile {} +
python -m pytest tests/ -q -m "not e2e and not docker" # needs Python 3.12
```

HTTP smoke test (no real Mealie needed; checks transport, auth, tool listing):

```bash
MEALIE_URL=http://127.0.0.1:1 MEALIE_API_TOKEN=x MCP_AUTH_TOKEN=t MCP_PORT=18099 \
  PYTHONPATH=src python mealie_mcp/run.py & PID=$!; sleep 8
A='Accept: application/json, text/event-stream'; C='Content-Type: application/json'
INIT='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"t","version":"1"}}}'
curl -s -o /dev/null -w '%{http_code}\n' -X POST localhost:18099/mcp -H "$C" -H "$A" -d "$INIT"   # expect 401
curl -s -X POST localhost:18099/mcp -H 'Authorization: Bearer t' -H "$C" -H "$A" -d "$INIT" | head -c 120  # expect "result"
kill $PID
```

Optional full image check (needs Docker):
`docker build -f mealie_mcp/Dockerfile --build-arg BUILD_VERSION=test -t mealie-mcp-addon:test .`
