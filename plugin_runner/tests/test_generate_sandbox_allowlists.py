import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "tools"))

from generate_sandbox_allowlists import static_constructs  # noqa: E402

HANDLER = """
from canvas_sdk.effects import Effect
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler

from {package}.helpers import value


class Handler(BaseHandler):
    RESPONDS_TO = EventType.Name(EventType.UNKNOWN)

    def compute(self) -> list[Effect]:
        return []
"""


def _instance(root: Path, package: str, helpers: str) -> Path:
    """An instance directory with a plugin whose helper imports another plugin beside it."""
    plugin = root / package
    (plugin / "handlers").mkdir(parents=True)
    (plugin / "__init__.py").touch()
    (plugin / "handlers" / "__init__.py").touch()
    (plugin / "CANVAS_MANIFEST.json").write_text(
        json.dumps({"components": {"handlers": [{"class": f"{package}.handlers.main:Handler"}]}})
    )
    (plugin / "handlers" / "main.py").write_text(HANDLER.format(package=package))
    (plugin / "helpers.py").write_text(helpers)

    sibling = root / f"{package}_sibling"
    sibling.mkdir()
    (sibling / "__init__.py").write_text("VALUE = 1\n")
    (sibling / "CANVAS_MANIFEST.json").write_text(json.dumps({"components": {}}))

    return plugin


def test_static_constructs_see_imports_of_plugins_on_the_same_instance(tmp_path: Path) -> None:
    """The runner puts every installed plugin on the import path, so an import of another
    plugin on the same instance resolves there and is reported here too.
    """
    plugin = _instance(
        tmp_path,
        "deferred_consumer",
        "def value():\n    import deferred_consumer_sibling\n\n    return 1\n",
    )
    manifest = json.loads((plugin / "CANVAS_MANIFEST.json").read_text())

    constructs = static_constructs(plugin, manifest)

    assert [str(c) for c in constructs] == [
        "deferred_consumer.helpers:2 import deferred_consumer_sibling"
    ]
    assert str(tmp_path) not in sys.path
    assert "deferred_consumer_sibling" not in sys.modules


def test_static_constructs_answer_each_instance_for_itself(tmp_path: Path) -> None:
    """Whether an import resolves depends on the instance; an earlier instance where it did
    not resolve must not decide the answer for a later one where it does.
    """
    helpers = "def value():\n    import shared_consumer_sibling\n\n    return 1\n"
    without_sibling = _instance(tmp_path / "first", "shared_consumer", helpers)
    (tmp_path / "first" / "shared_consumer_sibling" / "__init__.py").unlink()
    (tmp_path / "first" / "shared_consumer_sibling" / "CANVAS_MANIFEST.json").unlink()
    (tmp_path / "first" / "shared_consumer_sibling").rmdir()
    with_sibling = _instance(tmp_path / "second", "shared_consumer", helpers)
    manifest = json.loads((with_sibling / "CANVAS_MANIFEST.json").read_text())

    assert static_constructs(without_sibling, manifest) == []
    assert [str(c) for c in static_constructs(with_sibling, manifest)] == [
        "shared_consumer.helpers:2 import shared_consumer_sibling"
    ]
