"""Named exceptions to the sandbox rules, held as digests rather than names.

Two lists, both keyed with `LEGACY_SANDBOX_ALLOWLIST_KEY`, which is held outside this
repository so neither file names a customer or a plugin:

`legacy-sandbox-allowlist.txt`
    Plugins permitted to keep using the deprecated sandbox rules. A plugin that depends
    on them and is not listed is refused at load, so the dependency cannot be newly
    acquired and the list only shrinks.

`blessed-imports.txt`
    Individual modules a named plugin may import beyond `ALLOWED_MODULES`. Narrower than
    the list above: the plugin still runs under the current rules and gains only the one
    import, rather than the whole previous rule set.

`legacy-sandbox-always.txt`
    Plugins that always run under the deprecated sandbox rules, even when they load
    cleanly under the current ones. The legacy allowlist only takes effect when a plugin
    fails to load; this list covers plugins whose incompatibility appears only when their
    code runs. It has its own cap and also only shrinks.

Both key on identity rather than code, so a plugin keeps its exception across version
uploads. The two differ in what an unusable list means, which is set by the direction of
the harm: a missing legacy allowlist refuses every dependent plugin at once, so it raises
and the runner can say why, while a missing blessing list simply grants nothing, which is
the default anyway.
"""

from __future__ import annotations

import hmac
import os
from functools import cache
from hashlib import sha256
from pathlib import Path

ALLOWLIST_PATH = Path(__file__).parent / "legacy-sandbox-allowlist.txt"
BLESSED_IMPORTS_PATH = Path(__file__).parent / "blessed-imports.txt"
ALWAYS_LEGACY_PATH = Path(__file__).parent / "legacy-sandbox-always.txt"

KEY_VARIABLE = "LEGACY_SANDBOX_ALLOWLIST_KEY"


class AllowlistUnavailable(RuntimeError):
    """Raised when the allowlist has to be consulted but is not usable.

    An unusable allowlist is not the same as an empty one: reading it as empty would
    refuse every plugin that depends on the deprecated rules, on every instance at once.
    """


class MissingAllowlistKey(AllowlistUnavailable):
    """The allowlist key is not configured."""

    def __init__(self) -> None:
        super().__init__(
            f"{KEY_VARIABLE} is not set, so the legacy sandbox allowlist cannot be "
            f"checked. Set it to the value used to generate {ALLOWLIST_PATH.name}."
        )


class MissingAllowlist(AllowlistUnavailable):
    """The allowlist file is not present."""

    def __init__(self) -> None:
        super().__init__(
            f"{ALLOWLIST_PATH} is missing, so no plugin can be recognized as permitted "
            "to use the deprecated sandbox rules. Generate it with "
            "tools/generate_sandbox_allowlists.py."
        )


def digest(key: str, *parts: str) -> str:
    """Return the entry for one subject, which is opaque without the key."""
    return hmac.new(key.encode(), ":".join(parts).encode(), sha256).hexdigest()


def _read(path: Path) -> frozenset[str]:
    """Read a digest file, ignoring comments and blank lines."""
    return frozenset(
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    )


@cache
def _allowlist() -> frozenset[str]:
    """Read the legacy allowlist."""
    if not ALLOWLIST_PATH.exists():
        raise MissingAllowlist

    return _read(ALLOWLIST_PATH)


@cache
def _blessed_imports() -> frozenset[str]:
    """Read the per-plugin import exceptions, which are optional."""
    if not BLESSED_IMPORTS_PATH.exists():
        return frozenset()

    return _read(BLESSED_IMPORTS_PATH)


@cache
def _always_legacy() -> frozenset[str]:
    """Read the list of plugins that always run under the deprecated rules, if present."""
    if not ALWAYS_LEGACY_PATH.exists():
        return frozenset()

    return _read(ALWAYS_LEGACY_PATH)


def is_always_legacy(customer: str, plugin: str) -> bool:
    """Whether this plugin always runs under the deprecated sandbox rules.

    Without the key nobody is listed, which leaves the plugin on the normal load path.
    """
    key = os.getenv(KEY_VARIABLE)

    if not key:
        return False

    return digest(key, customer, plugin) in _always_legacy()


def is_allowlisted(customer: str, plugin: str) -> bool:
    """Whether this plugin may keep using the deprecated sandbox rules."""
    key = os.getenv(KEY_VARIABLE)

    if not key:
        raise MissingAllowlistKey

    return digest(key, customer, plugin) in _allowlist()


def is_blessed_import(plugin: str, module: str) -> bool:
    """Whether this plugin may import this module despite it not being generally allowed.

    Only consulted once an import has already been rejected, so a plugin that imports
    nothing unusual never needs the key. Without the key nothing is blessed, which
    leaves the import refused: the same answer as having no entry.
    """
    key = os.getenv(KEY_VARIABLE)

    if not key:
        return False

    return digest(key, plugin, module) in _blessed_imports()
