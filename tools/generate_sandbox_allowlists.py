#!/usr/bin/env -S uv run python
"""Generate the set of plugins permitted to keep using the deprecated sandbox rules.

Scans every installed plugin in omniplug's local snapshot, and writes an HMAC digest for
each one that depends on the deprecated rules. The output names no customer and no
plugin; the key lives outside this repository.

A plugin can depend on those rules in two ways, and both are checked. Constructs inside
function bodies only diverge once a handler runs, so they are read statically. Anything
that diverges at load time is found by loading the plugin: under the current rules
first, then, if that fails, under the deprecated ones. Each distinct plugin is loaded
once, in worker processes that are recycled so accumulated state stays bounded.

This is a one-shot allowlist. A plugin missing from it is refused at load, so the
snapshot must be current — refresh omniplug's data before running this for real.

    LEGACY_SANDBOX_ALLOWLIST_KEY=... tools/generate_sandbox_allowlists.py \
        --snapshot ~/p/canvas-omniplug/data

Pass --dry-run to print what would be written without writing it.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import logging
import multiprocessing
import os
import re
import sys
import warnings
from collections import defaultdict
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# canvas_sdk configures Django on import, which loading a plugin needs.
import httpretty  # noqa: E402

import canvas_sdk  # noqa: E402, F401
from plugin_runner.plugin_runner import _load_plugin_handlers  # noqa: E402
from plugin_runner.sandbox import SandboxMode  # noqa: E402
from plugin_runner.sandbox_allowlists import (  # noqa: E402
    ALLOWLIST_PATH,
    BLESSED_IMPORTS_PATH,
    KEY_VARIABLE,
    digest,
)
from plugin_runner.sandbox_compatibility import (  # noqa: E402
    _is_importable,
    find_legacy_constructs,
)

# Recycling a worker after this many plugins bounds the Django model registrations and
# module objects that accumulate as plugins load.
PLUGINS_PER_WORKER = 40


def declared_handlers(manifest: dict) -> list[dict]:
    """Return the handler declarations the plugin runner would load."""
    components = manifest.get("components", {}) or {}

    return (
        (components.get("protocols") or [])
        + (components.get("applications") or [])
        + (components.get("handlers") or [])
    )


def entry_modules(manifest: dict) -> set[str]:
    """Return the handler modules a manifest declares."""
    return {
        handler["class"].split(":")[0]
        for handler in declared_handlers(manifest)
        if handler.get("class") and ":" in handler["class"]
    }


@contextmanager
def instance_import_path(plugin_dir: Path) -> Generator[None, None, None]:
    """Make the plugin's instance importable the way the runner does.

    The runner puts the directory every plugin is installed in on the import path, so one
    plugin can import another installed beside it. Assessed without it, such an import
    resolves to nothing and reads as harmless. Whether an import resolves is cached per
    module name, which is right for a runner serving one instance but not for a scan of
    every instance, so the cache is cleared on the way in and out, and modules imported
    meanwhile are forgotten, so instances with same-named plugins do not see each other's.
    """
    directory = str(plugin_dir.parent)
    modules_before = set(sys.modules)
    sys.path.insert(0, directory)
    importlib.invalidate_caches()
    _is_importable.cache_clear()

    try:
        yield
    finally:
        sys.path.remove(directory)
        importlib.invalidate_caches()
        _is_importable.cache_clear()

        for name in set(sys.modules) - modules_before:
            del sys.modules[name]


def static_constructs(plugin_dir: Path, manifest: dict) -> list:
    """The constructs that need the deprecated rules, read the way the runner reads them."""
    with instance_import_path(plugin_dir):
        return find_legacy_constructs(plugin_dir, entry_modules(manifest))


def content_digest(plugin_dir: Path) -> str:
    """Identify a plugin by its code, so identical copies are loaded once."""
    hasher = hashlib.sha256()

    for path in sorted(p for p in plugin_dir.rglob("*") if p.is_file()):
        if path.suffix in {".py", ".json", ".html"}:
            hasher.update(str(path.relative_to(plugin_dir)).encode())
            hasher.update(path.read_bytes())

    return hasher.hexdigest()


def _prepare_worker() -> None:
    """Keep plugin module-level code off the network and out of the log."""
    logging.disable(logging.CRITICAL)
    httpretty.enable(verbose=False, allow_net_connect=False)

    for method in (httpretty.GET, httpretty.POST, httpretty.PUT, httpretty.DELETE):
        httpretty.register_uri(method, re.compile(r".*"), body="{}")


def needs_deprecated_rules_to_load(plugin_dir_name: str) -> tuple[str, bool, str | None]:
    """Whether a plugin loads only under the deprecated rules.

    Returns the plugin directory, the answer, and the error if loading crashed outright,
    since a crash would otherwise read as "does not need them" and leave the plugin off
    the list.
    """
    plugin_dir = Path(plugin_dir_name)

    try:
        handlers = declared_handlers(json.loads((plugin_dir / "CANVAS_MANIFEST.json").read_text()))

        if not handlers:
            return plugin_dir_name, False, None

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            current = _load_plugin_handlers(
                plugin_dir.name, plugin_dir, handlers, None, SandboxMode.STRICT
            )

            if not any(r.error is not None and r.name_and_class is not None for r in current):
                return plugin_dir_name, False, None

            previous = _load_plugin_handlers(
                plugin_dir.name, plugin_dir, handlers, None, SandboxMode.LEGACY_PERMISSIVE
            )
    except Exception as error:
        return plugin_dir_name, False, f"{type(error).__name__}: {error}"

    recovered = any(
        now.error is not None and before.error is None and now.name_and_class is not None
        for now, before in zip(current, previous, strict=True)
    )

    return plugin_dir_name, recovered, None


def plugins_needing_deprecated_rules_to_load(
    plugin_dirs: list[Path],
    workers: int,
) -> tuple[set[Path], dict[Path, str]]:
    """Load every distinct plugin and return those that load only under the old rules."""
    copies: dict[str, list[Path]] = defaultdict(list)

    for plugin_dir in plugin_dirs:
        copies[content_digest(plugin_dir)].append(plugin_dir)

    representatives = {str(dirs[0]): content for content, dirs in copies.items()}
    needing: set[Path] = set()
    crashed: dict[Path, str] = {}

    print(f"loading {len(representatives)} distinct plugins with {workers} workers")

    context = multiprocessing.get_context("spawn")

    with context.Pool(
        processes=workers,
        initializer=_prepare_worker,
        maxtasksperchild=PLUGINS_PER_WORKER,
    ) as pool:
        for done, (plugin_dir_name, recovered, error) in enumerate(
            pool.imap_unordered(needs_deprecated_rules_to_load, representatives, chunksize=4),
            start=1,
        ):
            installs = copies[representatives[plugin_dir_name]]

            if error is not None:
                crashed.update(dict.fromkeys(installs, error))
            elif recovered:
                needing.update(installs)

            if done % 250 == 0:
                print(f"  {done}/{len(representatives)}", flush=True)

    return needing, crashed


def write_blessings(pairs: list[str], key: str, *, dry_run: bool) -> int:
    """Add per-plugin import exceptions, preserving the ones already recorded."""
    existing = (
        {
            line.strip()
            for line in BLESSED_IMPORTS_PATH.read_text().splitlines()
            if line.strip() and not line.startswith("#")
        }
        if BLESSED_IMPORTS_PATH.exists()
        else set()
    )

    for pair in pairs:
        plugin, _, module = pair.partition(":")

        if not plugin or not module:
            print(f"Expected PLUGIN:MODULE, got {pair!r}.", file=sys.stderr)
            return 1

        existing.add(digest(key, plugin, module))

    header = (
        "# Modules a named plugin may import beyond ALLOWED_MODULES.\n"
        "#\n"
        "# One HMAC-SHA256 digest per plugin-and-module pair, keyed with\n"
        f"# {KEY_VARIABLE}. Generated by tools/generate_sandbox_allowlists.py --bless.\n"
        "#\n"
        "# The plugin still runs under the current sandbox rules; only the named import\n"
        "# is permitted. Narrower than the legacy allowlist, and preferred over it.\n"
        f"#\n# entries: {len(existing)}\n"
    )

    print(f"{len(existing)} blessed imports")

    if dry_run:
        return 0

    BLESSED_IMPORTS_PATH.write_text(header + "\n".join(sorted(existing)) + "\n")
    print(f"wrote {BLESSED_IMPORTS_PATH}")

    return 0


def main() -> int:
    """Write the allowlist, or report what it would contain."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--snapshot",
        type=Path,
        required=False,
        help="omniplug data directory (contains plugins/ and plugin_list.json)",
    )
    parser.add_argument(
        "--bless",
        action="append",
        default=[],
        metavar="PLUGIN:MODULE",
        help="permit one plugin to import one module beyond ALLOWED_MODULES; repeatable",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print what would be written without writing it",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=2,
        help="processes to load plugins in (default 2)",
    )
    arguments = parser.parse_args()

    key = os.getenv(KEY_VARIABLE)

    if not key:
        print(f"{KEY_VARIABLE} is not set.", file=sys.stderr)
        return 1

    if arguments.bless:
        return write_blessings(arguments.bless, key, dry_run=arguments.dry_run)

    plugins_root = arguments.snapshot / "plugins"

    if not plugins_root.is_dir():
        print(f"No plugins directory under {arguments.snapshot}.", file=sys.stderr)
        return 1

    digests: set[str] = set()
    scanned = 0
    listed: list[tuple[str, str, str]] = []
    to_load: list[Path] = []

    for manifest_path in sorted(plugins_root.glob("*/*/CANVAS_MANIFEST.json")):
        plugin_dir = manifest_path.parent
        scanned += 1

        try:
            manifest = json.loads(manifest_path.read_text())
        except (OSError, json.JSONDecodeError):
            continue

        try:
            constructs = static_constructs(plugin_dir, manifest)
        except OSError:
            continue

        # The runner keys on the instance and the installed plugin's directory name.
        if constructs:
            digests.add(digest(key, plugin_dir.parent.name, plugin_dir.name))
            listed.append(
                (plugin_dir.parent.name, plugin_dir.name, f"{len(constructs)} constructs")
            )
        else:
            to_load.append(plugin_dir)

    needing, crashed = plugins_needing_deprecated_rules_to_load(to_load, arguments.workers)

    for plugin_dir in sorted(needing):
        digests.add(digest(key, plugin_dir.parent.name, plugin_dir.name))
        listed.append((plugin_dir.parent.name, plugin_dir.name, "loads only under them"))

    if crashed:
        print(f"{len(crashed)} installs could not be assessed:", file=sys.stderr)

        for plugin_dir, error in sorted(crashed.items())[:20]:
            print(f"  {plugin_dir.parent.name}/{plugin_dir.name}: {error[:160]}", file=sys.stderr)

    header = (
        "# Plugins permitted to keep using the deprecated sandbox rules.\n"
        "#\n"
        "# One HMAC-SHA256 digest per allowlisted plugin, keyed with\n"
        f"# {KEY_VARIABLE}. Generated by tools/generate_sandbox_allowlists.py.\n"
        "#\n"
        "# This list is a ratchet: it may shrink as plugins are brought up to the\n"
        "# current rules, and must not grow.\n"
        f"#\n# entries: {len(digests)}\n"
        f"# generated: {datetime.now(UTC).date().isoformat()}\n"
    )
    body = "\n".join(sorted(digests)) + "\n"

    print(f"scanned {scanned} installed plugins, {len(digests)} allowlisted")

    if arguments.dry_run:
        for customer, plugin, reason in sorted(listed)[:20]:
            print(f"  {customer}/{plugin}  ({reason})")

        if len(listed) > 20:
            print(f"  ... and {len(listed) - 20} more")

        return 0

    ALLOWLIST_PATH.write_text(header + body)
    print(f"wrote {ALLOWLIST_PATH}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
