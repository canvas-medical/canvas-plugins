"""Resolving a plugin's dependencies for ``canvas deploy``, and its lock file.

A manifest's ``dependencies`` name plugins by an exact version or a PEP 440
specifier set. Each resolves among the versions Canvas Platform holds and, for a
dependency with a ``source`` that one of the person's organizations publishes,
the release tags of that git repository. A version only the repository holds is
cloned, so that ``canvas deploy`` can validate it and push it to platform, and
the cloned plugin's own dependencies are resolved the same way, depth first.

``CANVAS_LOCK.json`` beside the manifest records what each dependency resolved
to. A later deploy installs exactly that, until ``canvas deploy --update``
resolves again or the manifest asks for a version the lock does not satisfy.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import typer
from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

from canvas_cli.apps.platform import git
from canvas_cli.apps.platform.client import PlatformClient

MANIFEST_FILE = "CANVAS_MANIFEST.json"
LOCK_FILE = "CANVAS_LOCK.json"
LOCK_VERSION = 1

# Release tag names tried when a source names no ``tag``, most specific first.
DEFAULT_TAGS = ("{name}-v{version}", "v{version}")


def _version(text: object) -> Version | None:
    try:
        return Version(str(text))
    except InvalidVersion:
        return None


def satisfies(version: object, specifier: str) -> bool:
    """Whether ``version`` meets ``specifier``, an exact version or a PEP 440 specifier set.

    A prerelease meets only an exact version naming it.
    """
    candidate = _version(version)
    if candidate is None:
        return False
    pinned = _version(specifier)
    if pinned is not None:
        return candidate == pinned
    return SpecifierSet(specifier).contains(candidate, prereleases=False)


def _require_specifier(name: str, specifier: str, requirer: str) -> None:
    if _version(specifier) is not None:
        return
    try:
        SpecifierSet(specifier)
    except InvalidSpecifier:
        raise typer.BadParameter(
            f"{requirer} requires {name} {specifier!r}, which is neither a version nor a "
            "version specifier."
        ) from None


def read_manifest(plugin_dir: Path) -> dict[str, Any]:
    """The parsed ``CANVAS_MANIFEST.json`` in ``plugin_dir``."""
    manifest = plugin_dir / MANIFEST_FILE
    if not manifest.exists():
        raise typer.BadParameter(f"'{plugin_dir}' has no {MANIFEST_FILE}")
    try:
        parsed = json.loads(manifest.read_text())
    except (ValueError, OSError) as exc:
        raise typer.BadParameter(f"Could not read {manifest}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise typer.BadParameter(f"{manifest} does not hold a JSON object")
    return parsed


# -- the lock file -----------------------------------------------------------


def read_lock(plugin_dir: Path) -> dict[str, dict[str, Any]]:
    """The plugins ``CANVAS_LOCK.json`` beside the manifest pins, by name; empty without one."""
    path = plugin_dir / LOCK_FILE
    if not path.exists():
        return {}
    try:
        lock = json.loads(path.read_text())
    except (ValueError, OSError) as exc:
        raise typer.BadParameter(f"Could not read {path}: {exc}") from exc
    if not isinstance(lock, dict) or lock.get("lock_version") != LOCK_VERSION:
        raise typer.BadParameter(
            f"{path} is not a lock file this version of canvas reads (lock_version "
            f"{LOCK_VERSION}). Run `canvas deploy --update` to write it again."
        )
    plugins = lock.get("plugins")
    return plugins if isinstance(plugins, dict) else {}


@dataclass
class Resolved:
    """What one dependency resolved to, and whether it has to be pushed to platform."""

    name: str
    version: str
    publisher: str
    # Written to the lock as is: the source as declared, plus the tag and commit
    # the version was fetched from.
    source: dict[str, str] | None
    required_by: list[str]
    revision: str | None = None  # the commit on platform, once known
    checkout: Path | None = None  # the cloned package folder, when it is pushed
    locked: bool = False

    def describe(self) -> str:
        """One line of the plan ``canvas deploy`` prints before it acts."""
        line = f"  {self.name} {self.version} ({self.publisher})"
        if self.checkout is not None and self.source is not None:
            line += f": fetch {self.source['tag']} from {self.source['git']} and push it"
        else:
            line += f": on Canvas Platform at {(self.revision or '')[:12]}"
        if self.locked:
            line += ", as locked"
        return f"{line}, required by {', '.join(self.required_by)}"

    def lock_entry(self) -> dict[str, Any]:
        """This plugin's entry in ``CANVAS_LOCK.json``."""
        entry: dict[str, Any] = {"version": self.version, "publisher": self.publisher}
        if self.source is not None:
            entry["source"] = self.source
        entry["revision"] = self.revision
        entry["required_by"] = self.required_by
        return entry


def write_lock(plugin_dir: Path, plugins: list[Resolved]) -> bool:
    """Write ``CANVAS_LOCK.json`` beside the manifest; whether its content changed."""
    path = plugin_dir / LOCK_FILE
    content = (
        json.dumps(
            {
                "lock_version": LOCK_VERSION,
                "plugins": {plugin.name: plugin.lock_entry() for plugin in plugins},
            },
            indent=2,
        )
        + "\n"
    )
    if path.exists() and path.read_text() == content:
        return False
    path.write_text(content)
    return True


# -- resolving ---------------------------------------------------------------


def _tag_pattern(template: str) -> re.Pattern[str]:
    escaped = re.escape(template).replace(re.escape("{version}"), "(?P<version>.+)")
    return re.compile(f"^{escaped}$")


def best_tag(
    name: str, specifier: str, source: dict[str, str], tags: dict[str, str]
) -> tuple[Version, str, str] | None:
    """The newest release tag meeting ``specifier``, as (version, tag, commit).

    A release is tagged as the source's ``tag`` says, or else ``<name>-v<version>``
    or ``v<version>``; when both name one version, ``<name>-v<version>`` wins.
    """
    templates = (
        [source["tag"]] if "tag" in source else [t.replace("{name}", name) for t in DEFAULT_TAGS]
    )
    candidates: list[tuple[Version, int, str, str]] = []
    for rank, template in enumerate(templates):
        pattern = _tag_pattern(template)
        for tag, commit in tags.items():
            match = pattern.match(tag)
            version = _version(match["version"]) if match else None
            if version is not None and satisfies(version, specifier):
                candidates.append((version, -rank, tag, commit))
    if not candidates:
        return None
    version, _, tag, commit = max(candidates)
    return version, tag, commit


@dataclass
class Resolver:
    """Walks a manifest's dependencies depth first and resolves each one."""

    client: PlatformClient
    # The publisher of a dependency platform does not know and that names none.
    default_publisher: str
    # The organizations the person may push plugin code in.
    pushable: set[str]
    lock: dict[str, dict[str, Any]]
    workdir: Path
    plugins: dict[str, Resolved] = field(default_factory=dict)

    def resolve(self, manifest: dict[str, Any]) -> list[Resolved]:
        """Every dependency of ``manifest`` and of the plugins it fetches, depth first."""
        self._walk(manifest, (str(manifest.get("name")),))
        return list(self.plugins.values())

    def _walk(self, manifest: dict[str, Any], path: tuple[str, ...]) -> None:
        requirer = path[-1]
        for dependency in manifest.get("dependencies") or []:
            name, specifier = dependency["name"], dependency["version"]
            _require_specifier(name, specifier, requirer)
            if name in path:
                cycle = " -> ".join((*path[path.index(name) :], name))
                raise typer.BadParameter(f"The dependencies form a cycle: {cycle}.")
            existing = self.plugins.get(name)
            if existing is not None:
                if not satisfies(existing.version, specifier):
                    raise typer.BadParameter(
                        f"{requirer} requires {name} {specifier}, but "
                        f"{', '.join(existing.required_by)} resolved it to {existing.version}."
                    )
                if requirer not in existing.required_by:
                    existing.required_by.append(requirer)
                continue
            resolved = self._resolve_one(dependency, requirer)
            self.plugins[name] = resolved
            if resolved.checkout is not None:
                self._walk(read_manifest(resolved.checkout), (*path, name))
            elif resolved.locked:
                self._walk_locked(name, (*path, name))

    def _walk_locked(self, name: str, path: tuple[str, ...]) -> None:
        """Follow the lock to the dependencies of a locked plugin that is not fetched."""
        dependencies = [
            {"name": entry_name, "version": entry["version"], "publisher": entry["publisher"]}
            for entry_name, entry in self.lock.items()
            if name in entry.get("required_by", [])
        ]
        self._walk({"dependencies": dependencies}, path)

    def _resolve_one(self, dependency: dict[str, Any], requirer: str) -> Resolved:
        name, specifier = dependency["name"], dependency["version"]
        entry = self.lock.get(name)
        if (
            entry is not None
            and satisfies(entry.get("version"), specifier)
            and dependency.get("publisher") in (None, entry.get("publisher"))
        ):
            return self._from_lock(name, entry, requirer)
        return self._fresh(dependency, requirer)

    def _from_lock(self, name: str, entry: dict[str, Any], requirer: str) -> Resolved:
        """The locked revision, fetched again from its tag only when platform lacks it."""
        version, publisher, revision = entry["version"], entry["publisher"], entry.get("revision")
        source = entry.get("source")
        resolved = Resolved(
            name, version, publisher, source, [requirer], revision=revision, locked=True
        )
        held = self.client.plugin_versions(name, publisher)
        if held and any(v.get("sha") == revision for v in held.get("versions", [])):
            return resolved

        refused = (
            f"{LOCK_FILE} pins {name} {version} at revision {str(revision)[:12]}, which "
            "Canvas Platform does not hold"
        )
        if not (source and source.get("commit") and publisher in self.pushable):
            raise typer.BadParameter(
                f"{refused}, and it was not fetched from a source you can push. Run "
                "`canvas deploy --update` to resolve it again."
            )
        commit = git.ls_remote_tags(source["git"]).get(source["tag"])
        if commit != source["commit"]:
            raise typer.BadParameter(
                f"{refused}, and the tag {source['tag']} in {source['git']} now points at "
                f"{(commit or 'nothing')[:12]} rather than the locked {source['commit'][:12]}. "
                "Check why the tag moved, then run `canvas deploy --update` to resolve it again."
            )
        resolved.checkout = self._clone(name, version, source, source["tag"], commit)
        resolved.revision = None
        return resolved

    def _fresh(self, dependency: dict[str, Any], requirer: str) -> Resolved:
        """The newest version meeting the specifier, among platform's and the source's."""
        name, specifier = dependency["name"], dependency["version"]
        held = self.client.plugin_versions(name, dependency.get("publisher"))
        publisher = str(
            dependency.get("publisher") or (held or {}).get("publisher") or self.default_publisher
        )
        best_held: dict[str, Any] | None = None
        # Newest pushed first, so of two revisions of one version the newer wins.
        for candidate in (held or {}).get("versions", []):
            if satisfies(candidate.get("version"), specifier) and (
                best_held is None or Version(candidate["version"]) > Version(best_held["version"])
            ):
                best_held = candidate

        source: dict[str, str] | None = dependency.get("source")
        exact = _version(specifier) is not None
        tag = None
        if source and publisher in self.pushable and (best_held is None or not exact):
            tag = best_tag(name, specifier, source, git.ls_remote_tags(source["git"]))
        if tag is not None and (best_held is None or tag[0] > Version(best_held["version"])):
            version, tag_name, commit = tag
            checkout = self._clone(name, str(version), source or {}, tag_name, commit)
            return Resolved(
                name,
                str(read_manifest(checkout)["plugin_version"]),
                publisher,
                {**(source or {}), "tag": tag_name, "commit": commit},
                [requirer],
                checkout=checkout,
            )
        if best_held is not None:
            return Resolved(
                name,
                str(best_held["version"]),
                publisher,
                source,
                [requirer],
                revision=str(best_held["sha"]),
            )

        missing = (
            f"Canvas Platform holds no version of {name} meeting {specifier!r} that you can see"
        )
        if not source:
            why = "and its dependency declares no source to fetch it from"
        elif publisher not in self.pushable:
            why = (
                f"and its publisher, {publisher}, is not an organization you can push plugin code "
                "in, so it has to be published there first"
            )
        else:
            why = f"and no release tag in {source['git']} names one"
        raise typer.BadParameter(f"{requirer} requires {name}: {missing}, {why}.")

    def _clone(
        self, name: str, version: str, source: dict[str, str], tag: str, commit: str
    ) -> Path:
        """Clone ``tag`` and return the plugin's package folder in it, refusing a mismatch.

        The folder is ``path`` in the repository, or its root, or, in the
        ``canvas init`` layout, the folder named after the plugin below either.
        """
        destination = self.workdir / str(len(list(self.workdir.iterdir()))) / name
        print(f"Fetching {name} {version} ({tag}) from {source['git']}…")
        if git.clone_tag(source["git"], tag, destination) != commit:
            raise typer.BadParameter(
                f"The tag {tag} in {source['git']} moved while {name} was being fetched."
            )
        folder = destination / source["path"] if "path" in source else destination
        if not (folder / MANIFEST_FILE).exists() and (folder / name / MANIFEST_FILE).exists():
            folder = folder / name
        manifest = read_manifest(folder)
        found = (manifest.get("name"), manifest.get("plugin_version"))
        if found[0] != name or _version(found[1]) != Version(version):
            raise typer.BadParameter(
                f"The tag {tag} in {source['git']} holds {found[0]} {found[1]}, not {name} "
                f"{version}."
            )
        if folder.name != name:
            raise typer.BadParameter(
                f"{name} is in the folder '{folder.name}' in {source['git']} at {tag}, but an "
                "instance imports a plugin from a folder named after it."
            )
        return folder
