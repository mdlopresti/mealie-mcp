#!/usr/bin/env python3
"""
Single-source semantic versioning for Mealie MCP and its Home Assistant app.

The version lives in three places that must always agree:
  * CHANGELOG.md            - newest "## [X.Y.Z] - YYYY-MM-DD" section (Keep a Changelog)
  * mealie_mcp/config.yaml  - `version:` (what Home Assistant reads to offer updates)
  * src/__init__.py         - `__version__`
mealie_mcp/CHANGELOG.md is a generated copy of CHANGELOG.md that Home Assistant
shows in the app's update dialog.

Usage:
  python scripts/release.py bump patch|minor|major|X.Y.Z [--date YYYY-MM-DD]
      Move everything under [Unreleased] into a new release section and
      update all version files.
  python scripts/release.py check [--tag vX.Y.Z]
      Fail if the version files disagree (used by CI; --tag also checks the git tag).
  python scripts/release.py sync
      Regenerate mealie_mcp/CHANGELOG.md from CHANGELOG.md.
  python scripts/release.py version
      Print the current version.
"""

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHANGELOG = ROOT / "CHANGELOG.md"
APP_CHANGELOG = ROOT / "mealie_mcp" / "CHANGELOG.md"
APP_CONFIG = ROOT / "mealie_mcp" / "config.yaml"
PKG_INIT = ROOT / "src" / "__init__.py"
REPO_URL = "https://github.com/warinthestars/mealie-mcp"

SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:-[0-9A-Za-z.-]+)?$")
RELEASE_HEADING = re.compile(r"^## \[(\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?)\]", re.M)
UNRELEASED_HEADING = re.compile(r"^## \[Unreleased\][^\n]*\n", re.M)
CONFIG_VERSION = re.compile(r'^version:\s*"?([^"\s]+)"?\s*$', re.M)
INIT_VERSION = re.compile(r'^__version__\s*=\s*"([^"]+)"', re.M)

APP_CHANGELOG_HEADER = (
    "<!-- Generated from ../CHANGELOG.md by scripts/release.py - do not edit by hand. -->\n\n"
)


# --- file helpers (preserve each file's existing line endings) --------------

def read(path: Path) -> tuple[str, str]:
    raw = path.read_bytes().decode("utf-8")
    eol = "\r\n" if "\r\n" in raw else "\n"
    return raw.replace("\r\n", "\n"), eol


def write(path: Path, text: str, eol: str = "\n") -> None:
    path.write_bytes(text.replace("\n", eol).encode("utf-8"))


# --- version sources --------------------------------------------------------

def changelog_version() -> str:
    text, _ = read(CHANGELOG)
    m = RELEASE_HEADING.search(text)
    if not m:
        sys.exit("CHANGELOG.md has no released version section")
    return m.group(1)


def config_version() -> str:
    m = CONFIG_VERSION.search(read(APP_CONFIG)[0])
    if not m:
        sys.exit("mealie_mcp/config.yaml has no version field")
    return m.group(1)


def init_version() -> str | None:
    m = INIT_VERSION.search(read(PKG_INIT)[0])
    return m.group(1) if m else None


def set_versions(version: str) -> None:
    text, eol = read(APP_CONFIG)
    write(APP_CONFIG, CONFIG_VERSION.sub(f'version: "{version}"', text, count=1), eol)

    text, eol = read(PKG_INIT)
    if INIT_VERSION.search(text):
        text = INIT_VERSION.sub(f'__version__ = "{version}"', text, count=1)
    else:
        text = text.rstrip("\n") + f'\n\n__version__ = "{version}"\n'
    write(PKG_INIT, text, eol)


def app_changelog_text() -> str:
    text, _ = read(CHANGELOG)
    return APP_CHANGELOG_HEADER + text


def sync() -> None:
    write(APP_CHANGELOG, app_changelog_text())


# --- commands ---------------------------------------------------------------

def next_version(current: str, part: str) -> str:
    if SEMVER.match(part):
        return part
    m = SEMVER.match(current)
    major, minor, patch = (int(x) for x in m.groups()[:3])
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    sys.exit(f"Unknown bump '{part}' (use patch, minor, major or X.Y.Z)")


def cmd_bump(part: str, date: str | None) -> None:
    current = changelog_version()
    new = next_version(current, part)
    if [int(x) for x in SEMVER.match(new).groups()[:3]] <= [
        int(x) for x in SEMVER.match(current).groups()[:3]
    ]:
        sys.exit(f"New version {new} must be greater than current {current}")

    text, eol = read(CHANGELOG)
    m = UNRELEASED_HEADING.search(text)
    if not m:
        sys.exit("CHANGELOG.md has no '## [Unreleased]' section")
    body_start = m.end()
    nxt = RELEASE_HEADING.search(text, body_start)
    body_end = nxt.start() if nxt else len(text)
    body = text[body_start:body_end].strip("\n")
    if not re.search(r"^\s*[-*] ", body, re.M):
        sys.exit("Nothing under [Unreleased] - add changelog entries before releasing")

    date = date or dt.date.today().isoformat()
    new_section = (
        "## [Unreleased]\n\n"
        f"## [{new}] - {date}\n\n{body}\n\n"
    )
    text = text[: m.start()] + new_section + text[body_end:]

    link = f"[{new}]: {REPO_URL}/releases/tag/v{new}\n"
    first_link = re.search(r"^\[\d+\.\d+\.\d+[^\]]*\]: ", text, re.M)
    if first_link:
        text = text[: first_link.start()] + link + text[first_link.start():]
    else:
        text = text.rstrip("\n") + "\n\n" + link
    write(CHANGELOG, text, eol)

    set_versions(new)
    sync()
    print(f"Released {current} -> {new}\n")
    print("Next steps (feature branch + PR, per CLAUDE.md):")
    print(f"  git checkout -b release/v{new}")
    print(f'  git add -A && git commit -m "chore: release v{new}"')
    print(f"  git push origin release/v{new} && gh pr create --fill")
    print("  # after the PR is merged:")
    print(f"  git checkout main && git pull && git tag v{new} && git push origin v{new}")


def cmd_check(tag: str | None) -> None:
    versions = {
        "CHANGELOG.md": changelog_version(),
        "mealie_mcp/config.yaml": config_version(),
        "src/__init__.py": init_version(),
    }
    if tag:
        versions["git tag"] = tag.removeprefix("refs/tags/").removeprefix("v")
    problems = []
    if len(set(versions.values())) != 1:
        problems.append("version mismatch:\n" + "\n".join(
            f"    {k:<24} {v}" for k, v in versions.items()))
    if not SEMVER.match(versions["mealie_mcp/config.yaml"] or ""):
        problems.append(f"config.yaml version is not semver: {versions['mealie_mcp/config.yaml']}")
    if not APP_CHANGELOG.exists() or read(APP_CHANGELOG)[0] != app_changelog_text():
        problems.append("mealie_mcp/CHANGELOG.md is out of date - run: python scripts/release.py sync")
    if problems:
        print("Release check FAILED:\n  " + "\n  ".join(problems))
        sys.exit(1)
    print(f"Release check OK: version {versions['CHANGELOG.md']}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("bump")
    b.add_argument("part")
    b.add_argument("--date")
    c = sub.add_parser("check")
    c.add_argument("--tag")
    sub.add_parser("sync")
    sub.add_parser("version")
    args = ap.parse_args()

    if args.cmd == "bump":
        cmd_bump(args.part, args.date)
    elif args.cmd == "check":
        cmd_check(args.tag)
    elif args.cmd == "sync":
        sync()
        print("mealie_mcp/CHANGELOG.md regenerated")
    elif args.cmd == "version":
        print(changelog_version())


if __name__ == "__main__":
    main()
