"""Resolving a plugin's dependencies for ``canvas deploy``, and its lock file.

A manifest's ``dependencies`` name plugins by an exact version or a PEP 440
specifier set. Each resolves among the versions Canvas Platform holds and, for a
dependency with a ``source`` that one of the person's organizations publishes,
the release tags of that git repository. A version only the repository holds is
cloned, so that ``canvas deploy`` can validate it and push it to platform, and
the cloned plugin's own dependencies are resolved the same way, depth first.
When two plugins ask for different versions of one dependency, the dependency is
picked again at a version meeting both, as Canvas Platform's resolver does.

``CANVAS_LOCK.json`` beside the manifest records what each dependency resolved
to. A later deploy installs exactly that, until ``canvas deploy --update``
resolves again or the manifest asks for a version the lock does not satisfy.
"""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import typer
from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

from canvas_cli.apps.platform import git
from canvas_cli.apps.platform.client import PlatformClient, PlatformError

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
    name: str, specifiers: Sequence[str], source: dict[str, str], tags: dict[str, str]
) -> tuple[Version, str, str] | None:
    """The newest release tag meeting every one of ``specifiers``, as (version, tag, commit).

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
            if version is not None and _meets_all(version, specifiers):
                candidates.append((version, -rank, tag, commit))
    if not candidates:
        return None
    version, _, tag, commit = max(candidates)
    return version, tag, commit


def _meets_all(version: object, specifiers: Sequence[str]) -> bool:
    return all(satisfies(version, specifier) for specifier in specifiers)


@dataclass(frozen=True)
class Requirement:
    """One manifest's requirement on a dependency, as the version of the plugin asking."""

    name: str
    specifier: str
    requirer: str
    requirer_version: str
    publisher: str | None = None
    # Whether the requirer's entry declares a source for the dependency.
    names_source: bool = False

    def describe(self) -> str:
        """The requirement in a sentence naming who asks for what."""
        requirer = f"{self.requirer} {self.requirer_version}".rstrip()
        return f"{requirer} requires {self.name} {self.specifier!r}"


class _Restart(Exception):
    """A requirement the version a dependency was picked at does not meet."""

    def __init__(self, requirement: Requirement) -> None:
        super().__init__(requirement.describe())
        self.requirement = requirement


@dataclass
class Resolver:
    """Walks a manifest's dependencies depth first and resolves each one.

    A dependency is picked when the walk first reaches it, at the newest version meeting
    every requirement known on it. When a later requirement is not met by that version, the
    requirement is learned and the walk starts over, so the next pick of that dependency
    takes it into account. A learned requirement belongs to the version of the plugin that
    asked, and is dropped once a walk ends without that version picked.
    """

    client: PlatformClient
    # The publisher of a dependency platform does not know and that names none.
    default_publisher: str
    # The organizations the person may push plugin code in.
    pushable: set[str]
    lock: dict[str, dict[str, Any]]
    workdir: Path
    plugins: dict[str, Resolved] = field(default_factory=dict)
    # The source the deploying manifest declares for each dependency, by name: the only
    # sources a version is ever fetched from.
    sources: dict[str, dict[str, str]] = field(default_factory=dict)
    # Requirements a walk broke off on, in the order they were learned.
    learned: list[Requirement] = field(default_factory=list)
    root: tuple[str, str] = ("", "")
    # What platform and git answered, kept across walks: platform's versions by (name,
    # publisher), the release tags by repository, and the package folder cloned by
    # (repository, tag).
    held: dict[tuple[str, str | None], dict[str, Any] | None] = field(default_factory=dict)
    tags: dict[str, dict[str, str]] = field(default_factory=dict)
    clones: dict[tuple[str, str], Path] = field(default_factory=dict)

    def resolve(self, manifest: dict[str, Any]) -> list[Resolved]:
        """Every dependency of ``manifest`` and of the plugins it fetches, depth first.

        A dependency is fetched only from the source the deploying manifest declares for
        that plugin, exactly as declared. A fetched plugin's manifest is someone else's
        word, so a source it declares is never cloned and pushed into the person's
        organization.
        """
        self.sources = {
            d["name"]: d["source"] for d in manifest.get("dependencies") or [] if "source" in d
        }
        self.root = (str(manifest.get("name")), str(manifest.get("plugin_version") or ""))
        # This loop ends. A walk is decided by the requirements it starts with, and every
        # learned requirement is read from the manifest of a version on offer (platform's
        # versions and the source's tags), so there are finitely many sets of them and the
        # loop stops at the first set it has already walked with. Learning only grows the
        # set, so returning to a set takes a drop, which only follows a walk that met every
        # requirement: `resolved` then holds a complete answer.
        walked: set[frozenset[Requirement]] = set()
        resolved: list[Resolved] | None = None
        while (state := frozenset(self.learned)) not in walked:
            walked.add(state)
            self.plugins = {}
            try:
                self._walk(manifest, (self.root[0],), self.root[1])
            except _Restart as restart:
                self.learned.append(restart.requirement)
                continue
            resolved = list(self.plugins.values())
            picked = {name: plugin.version for name, plugin in self.plugins.items()}
            picked[self.root[0]] = self.root[1]
            kept = [r for r in self.learned if picked.get(r.requirer) == r.requirer_version]
            if kept == self.learned:
                return resolved
            self.learned = kept
        if resolved is None:
            raise RuntimeError("The dependency walk repeated without ever completing.")
        return resolved

    def _walk(self, manifest: dict[str, Any], path: tuple[str, ...], version: str) -> None:
        requirer = path[-1]
        for dependency in manifest.get("dependencies") or []:
            name, specifier = dependency["name"], dependency["version"]
            _require_specifier(name, specifier, requirer)
            if name in path:
                cycle = " -> ".join((*path[path.index(name) :], name))
                raise typer.BadParameter(f"The dependencies form a cycle: {cycle}.")
            requirement = Requirement(
                name,
                specifier,
                requirer,
                version,
                dependency.get("publisher"),
                "source" in dependency,
            )
            existing = self.plugins.get(name)
            if existing is not None:
                if not satisfies(existing.version, specifier):
                    raise _Restart(requirement)
                if requirer not in existing.required_by:
                    existing.required_by.append(requirer)
                continue
            resolved = self._pick(requirement)
            self.plugins[name] = resolved
            if resolved.checkout is not None:
                self._walk(read_manifest(resolved.checkout), (*path, name), resolved.version)
            elif resolved.locked:
                self._walk_locked(name, (*path, name), resolved.version)

    def _walk_locked(self, name: str, path: tuple[str, ...], version: str) -> None:
        """Follow the lock to the dependencies of a locked plugin that is not fetched."""
        dependencies = [
            {"name": entry_name, "version": entry["version"], "publisher": entry["publisher"]}
            for entry_name, entry in self.lock.items()
            if name in entry.get("required_by", [])
        ]
        self._walk({"dependencies": dependencies}, path, version)

    def _applies(self, requirement: Requirement) -> bool:
        """Whether a learned requirement still holds: its requirer is the deploying plugin,
        is not picked yet in this walk, or is picked at the version that asked.
        """
        if requirement.requirer == self.root[0]:
            return True
        requirer = self.plugins.get(requirement.requirer)
        return requirer is None or requirer.version == requirement.requirer_version

    def _pick(self, first: Requirement) -> Resolved:
        """The version of a dependency meeting ``first`` and every learned requirement on it:
        the locked one while it meets them all, else the newest.
        """
        requirements = [first] + [
            r for r in self.learned if r.name == first.name and r != first and self._applies(r)
        ]
        specifiers = [r.specifier for r in requirements]
        publishers = {r.publisher for r in requirements if r.publisher}
        entry = self.lock.get(first.name)
        if (
            entry is not None
            and _meets_all(entry.get("version"), specifiers)
            and publishers <= {entry.get("publisher")}
        ):
            return self._from_lock(first.name, entry, first.requirer)
        return self._fresh(requirements)

    def _versions(self, name: str, publisher: str | None, requirer: str) -> dict[str, Any] | None:
        """Platform's versions of ``name``, asked once per resolve.

        A name several publishers share is refused by platform until a publisher is named,
        so that refusal says which entry to add one to.
        """
        key = (name, publisher)
        if key not in self.held:
            try:
                self.held[key] = self.client.plugin_versions(name, publisher)
            except PlatformError as error:
                if error.code != "ambiguous":
                    raise
                raise PlatformError(
                    f"{error.message} {name} is a dependency of {requirer}: add `publisher` to "
                    f"the {name} entry in the dependencies of {requirer}.",
                    status=error.status,
                    code=error.code,
                ) from error
        return self.held[key]

    def _remote_tags(self, url: str) -> dict[str, str]:
        """The release tags of ``url``, listed once per resolve."""
        if url not in self.tags:
            self.tags[url] = git.ls_remote_tags(url)
        return self.tags[url]

    def _from_lock(self, name: str, entry: dict[str, Any], requirer: str) -> Resolved:
        """The locked revision, fetched again from its tag only when platform lacks it."""
        version, publisher, revision = entry["version"], entry["publisher"], entry.get("revision")
        source = entry.get("source")
        resolved = Resolved(
            name, version, publisher, source, [requirer], revision=revision, locked=True
        )
        held = self._versions(name, publisher, requirer)
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
        commit = self._remote_tags(source["git"]).get(source["tag"])
        if commit != source["commit"]:
            raise typer.BadParameter(
                f"{refused}, and the tag {source['tag']} in {source['git']} now points at "
                f"{(commit or 'nothing')[:12]} rather than the locked {source['commit'][:12]}. "
                "Check why the tag moved, then run `canvas deploy --update` to resolve it again."
            )
        resolved.checkout = self._clone(name, version, source, source["tag"], commit)
        resolved.revision = None
        return resolved

    def _fresh(self, requirements: list[Requirement]) -> Resolved:
        """The newest version meeting every requirement, among platform's and the source's."""
        first = requirements[0]
        name, requirer = first.name, first.requirer
        specifiers = [r.specifier for r in requirements]
        named = next((r.publisher for r in requirements if r.publisher), None)
        held = self._versions(name, named, requirer)
        publisher = str(named or (held or {}).get("publisher") or self.default_publisher)
        best_held: dict[str, Any] | None = None
        # Newest pushed first, so of two revisions of one version the newer wins.
        for candidate in (held or {}).get("versions", []):
            if _meets_all(candidate.get("version"), specifiers) and (
                best_held is None or Version(candidate["version"]) > Version(best_held["version"])
            ):
                best_held = candidate

        source = self.sources.get(name)
        exact = any(_version(specifier) is not None for specifier in specifiers)
        tag = None
        if source and publisher in self.pushable and (best_held is None or not exact):
            tag = best_tag(name, specifiers, source, self._remote_tags(source["git"]))
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

        if len(requirements) == 1:
            refused = (
                f"{requirer} requires {name}: Canvas Platform holds no version of {name} "
                f"meeting {first.specifier!r} that you can see"
            )
        else:
            refused = (
                f"No version of {name} meets every requirement on it: "
                f"{', '.join(r.describe() for r in requirements)}. Canvas Platform holds none "
                "that you can see"
            )
        naming = next((r.requirer for r in requirements if r.names_source), None)
        if source is None and naming is not None:
            why = (
                f"and only {naming} names a source for it. Add {name} with its source to "
                "your own manifest's dependencies to fetch it from there"
            )
        elif not source:
            why = "and its dependency declares no source to fetch it from"
        elif publisher not in self.pushable:
            why = (
                f"and its publisher, {publisher}, is not an organization you can push plugin code "
                "in, so it has to be published there first"
            )
        else:
            why = f"and no release tag in {source['git']} names one"
        raise typer.BadParameter(f"{refused}, {why}.")

    def _clone(
        self, name: str, version: str, source: dict[str, str], tag: str, commit: str
    ) -> Path:
        """Clone ``tag`` and return the plugin's package folder in it, refusing a mismatch.

        A tag already cloned in this resolve is not cloned again. The folder is ``path``
        in the repository, or its root, or, in the ``canvas init`` layout, the folder
        named after the plugin below either.
        """
        key = (source["git"], tag)
        if key in self.clones:
            return self.clones[key]
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
        self.clones[key] = folder
        return folder
