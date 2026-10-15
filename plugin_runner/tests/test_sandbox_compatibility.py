"""Tests for detecting plugin code that depends on the previous sandbox rules."""

from pathlib import Path
from textwrap import dedent

import pytest

from canvas_sdk.tests.shared import params_from_dict
from plugin_runner import sandbox_compatibility
from plugin_runner.sandbox_compatibility import find_legacy_constructs


def _plugin(tmp_path: Path, tree: dict[str, str], name: str = "compat_plugin") -> Path:
    """Write a plugin tree and return its directory.

    A tree that supplies `helpers.py` but no handler gets one that imports it, since
    only modules an entry module reaches are evaluated at load.
    """
    base = tmp_path / name

    if "helpers.py" in tree and "handlers/handler.py" not in tree:
        tree = {
            **tree,
            "handlers/__init__.py": "",
            "handlers/handler.py": f"from {name} import helpers\n",
        }

    for relative, source in tree.items():
        path = base / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(dedent(source))

    return base


ENTRY = {"compat_plugin.handlers.handler"}


@pytest.mark.parametrize(
    "source",
    params_from_dict(
        {
            "format_traversal": """
                def render(obj):
                    return "{0.__class__.__init__.__globals__}".format(obj)
            """,
            "deferred_import": """
                def cwd():
                    import os

                    return os.getcwd()
            """,
            "vars_call": """
                def peek(obj):
                    return vars(obj)
            """,
            "dunder_dict": """
                def peek(obj):
                    return obj.__dict__
            """,
            "manager_raw": """
                def query(manager):
                    return manager.raw("SELECT 1")
            """,
            "dangerous_attr": """
                def climb(obj):
                    return obj.mro
            """,
            "ungranted_module_attribute": """
                import random

                def pick(items):
                    return random.shuffle(items)
            """,
            "ungranted_module_attribute_through_alias": """
                import urllib.parse as up

                def split(url):
                    return up.urlsplit(url)
            """,
            "ungranted_nested_module_attribute": """
                import requests

                def kinds():
                    return requests.exceptions.SSLError
            """,
            "ungranted_from_import_name": """
                def encoder():
                    from json import JSONEncoder

                    return JSONEncoder
            """,
        }
    ),
)
def test_reports_constructs_in_submodule_functions(tmp_path: Path, source: str) -> None:
    """Each construct the strict guards police is reported from a submodule function."""
    plugin = _plugin(tmp_path, {"__init__.py": "", "helpers.py": source})

    assert find_legacy_constructs(plugin, ENTRY)


def test_ordinary_formatting_is_not_reported(tmp_path: Path) -> None:
    """The sandbox formats normally, so `.format` alone is not a reason to fall back.

    Only reaching into an argument from inside the format string differs between the
    rule sets, and that is reported separately.
    """
    plugin = _plugin(
        tmp_path,
        {
            "__init__.py": "",
            "helpers.py": """
                def render(name, mapping):
                    first = "hi {}".format(name)
                    second = "{greeting}!".format(greeting=first)

                    return "{a}".format_map(mapping) + second
            """,
        },
    )

    assert find_legacy_constructs(plugin, ENTRY) == []


def test_ignores_constructs_at_a_submodule_top_level(tmp_path: Path) -> None:
    """Top-level submodule code is sandbox-evaluated under both rule sets."""
    plugin = _plugin(
        tmp_path,
        {"__init__.py": "", "helpers.py": "VALUE = 'hi {}'.format('there')\n"},
    )

    assert find_legacy_constructs(plugin, ENTRY) == []


def test_ignores_constructs_in_a_declared_handler_module(tmp_path: Path) -> None:
    """A declared handler is sandbox-compiled under both rule sets, so it is unchanged."""
    plugin = _plugin(
        tmp_path,
        {
            "__init__.py": "",
            "handlers/__init__.py": "",
            "handlers/handler.py": """
                def render(name):
                    return "hi {}".format(name)
            """,
        },
    )

    assert find_legacy_constructs(plugin, ENTRY) == []


def test_ignores_allowed_and_plugin_owned_deferred_imports(tmp_path: Path) -> None:
    """Deferred imports the sandbox already permits are not a reason to fall back."""
    plugin = _plugin(
        tmp_path,
        {
            "__init__.py": "",
            "sibling.py": "value = 1\n",
            "helpers.py": """
                def load():
                    from canvas_sdk.v1.data import Patient
                    from compat_plugin.sibling import value
                    from .sibling import value as other

                    return Patient, value, other
            """,
        },
    )

    assert find_legacy_constructs(plugin, ENTRY) == []


def test_ignores_granted_names_read_off_modules(tmp_path: Path) -> None:
    """Module names the allowlist grants, and the plugin's own modules, read the same."""
    plugin = _plugin(
        tmp_path,
        {
            "__init__.py": "",
            "sibling.py": "VALUE = 1\n",
            "helpers.py": """
                import json
                import requests
                import urllib.parse as up
                from compat_plugin import sibling

                def use(text):
                    from requests.exceptions import Timeout

                    return (
                        json.loads(text),
                        requests.exceptions.RequestException,
                        up.urlparse(text),
                        sibling.VALUE,
                        Timeout,
                    )
            """,
        },
    )

    assert find_legacy_constructs(plugin, ENTRY) == []


def test_reports_the_location_of_each_construct(tmp_path: Path) -> None:
    """Findings name the module and line so a plugin author can act on them."""
    plugin = _plugin(
        tmp_path,
        {
            "__init__.py": "",
            "helpers.py": """
                def peek(obj):
                    return obj.__dict__
            """,
        },
    )

    found = find_legacy_constructs(plugin, ENTRY)

    assert [str(construct) for construct in found] == ["compat_plugin.helpers:3 .__dict__"]


def test_a_clean_plugin_reports_nothing(tmp_path: Path) -> None:
    """A plugin with no dependency on the previous rules is left to load strictly."""
    plugin = _plugin(
        tmp_path,
        {
            "__init__.py": "",
            "helpers.py": """
                def render(name):
                    return f"hi {name}"
            """,
        },
    )

    assert find_legacy_constructs(plugin, ENTRY) == []


def test_ignores_modules_the_runner_never_loads(tmp_path: Path) -> None:
    """Only modules an entry module imports are evaluated, so only those are reported.

    Tests, tooling and dead code sit in the plugin directory but are never imported by a
    handler, so they are never compiled and cannot change behavior between rule sets.
    """
    plugin = _plugin(
        tmp_path,
        {
            "__init__.py": "",
            "handlers/__init__.py": "",
            "handlers/handler.py": "from compat_plugin.used import helper\n",
            "used.py": "def helper():\n    return 1\n",
            "tests/__init__.py": "",
            "tests/test_things.py": """
                def test_it():
                    import os

                    return os.getcwd()
            """,
            "tools/script.py": """
                def run():
                    import sqlite3

                    return sqlite3
            """,
        },
    )

    assert find_legacy_constructs(plugin, ENTRY | {"compat_plugin.handlers.handler"}) == []


def test_reports_a_module_reached_through_an_import_chain(tmp_path: Path) -> None:
    """Reachability is transitive: a helper's own helper is evaluated too."""
    plugin = _plugin(
        tmp_path,
        {
            "__init__.py": "",
            "handlers/__init__.py": "",
            "handlers/handler.py": "from compat_plugin.first import one\n",
            "first.py": "from compat_plugin.second import two\n\n\ndef one():\n    return two()\n",
            "second.py": """
                def two():
                    import sqlite3

                    return sqlite3
            """,
        },
    )

    found = find_legacy_constructs(plugin, {"compat_plugin.handlers.handler"})

    assert [str(c) for c in found] == ["compat_plugin.second:3 import sqlite3"]


def test_reports_a_package_init_along_the_import_path(tmp_path: Path) -> None:
    """Ancestor `__init__.py` files are evaluated on the way in, so they count."""
    plugin = _plugin(
        tmp_path,
        {
            "__init__.py": "",
            "handlers/__init__.py": "",
            "handlers/handler.py": "from compat_plugin.services.thing import go\n",
            "services/__init__.py": """
                def setup():
                    import sqlite3

                    return sqlite3
            """,
            "services/thing.py": "def go():\n    return 1\n",
        },
    )

    found = find_legacy_constructs(plugin, {"compat_plugin.handlers.handler"})

    assert [str(c) for c in found] == ["compat_plugin.services:3 import sqlite3"]


def test_a_blessed_import_is_not_reported(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A module the plugin is permitted to import behaves the same under both rule sets.

    Without this the blessing would not work: the plugin would still be routed onto the
    deprecated rules, or refused, for an import it is allowed to make.
    """
    monkeypatch.setattr(
        sandbox_compatibility,
        "is_blessed_import",
        lambda plugin, module: (plugin, module) == ("compat_plugin", "sqlite3"),
    )
    plugin = _plugin(
        tmp_path,
        {
            "__init__.py": "",
            "helpers.py": """
                def connect():
                    import sqlite3

                    return sqlite3
            """,
        },
    )

    assert find_legacy_constructs(plugin, ENTRY) == []


def test_an_unblessed_import_is_still_reported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The blessing is scoped to one plugin and one module."""
    monkeypatch.setattr(
        sandbox_compatibility,
        "is_blessed_import",
        lambda plugin, module: (plugin, module) == ("other_plugin", "sqlite3"),
    )
    plugin = _plugin(
        tmp_path,
        {
            "__init__.py": "",
            "helpers.py": """
                def connect():
                    import sqlite3

                    return sqlite3
            """,
        },
    )

    assert find_legacy_constructs(plugin, ENTRY)


def test_an_uninstallable_import_is_not_reported(tmp_path: Path) -> None:
    """A module nothing can import is not a difference between the rule sets.

    It fails under both, so the plugin is already broken on that path and putting it on
    the previous rules would not fix anything.
    """
    plugin = _plugin(
        tmp_path,
        {
            "__init__.py": "",
            "helpers.py": """
                def load():
                    import a_module_that_is_not_installed_anywhere

                    return a_module_that_is_not_installed_anywhere
            """,
        },
    )

    assert find_legacy_constructs(plugin, ENTRY) == []


def test_an_installed_but_disallowed_import_is_reported(tmp_path: Path) -> None:
    """A module that resolves outside the sandbox but not inside it is a real difference."""
    plugin = _plugin(
        tmp_path,
        {
            "__init__.py": "",
            "helpers.py": """
                def cwd():
                    import os

                    return os.getcwd()
            """,
        },
    )

    assert [str(c) for c in find_legacy_constructs(plugin, ENTRY)] == [
        "compat_plugin.helpers:3 import os"
    ]
