import importlib
import json
import pkgutil
from collections.abc import Iterable
from pathlib import Path
from typing import Any

CANVAS_TOP_LEVEL_MODULES = (
    "canvas_sdk.caching",
    "canvas_sdk.commands",
    "canvas_sdk.effects",
    "canvas_sdk.events",
    "canvas_sdk.handlers",
    "canvas_sdk.protocols",
    "canvas_sdk.questionnaires",
    "canvas_sdk.templates",
    "canvas_sdk.utils",
    "canvas_sdk.v1",
    "canvas_sdk.value_set",
    "canvas_sdk.views",
    "logger",
)


def find_submodules(starting_modules: Iterable[str]) -> list[str]:
    """
    Given a list of modules, return a list of those modules and their submodules.
    """
    submodules = set(starting_modules)

    for module_path in starting_modules:
        try:
            module = importlib.import_module(module_path)

            if not hasattr(module, "__path__"):
                continue

            for _, name, _ in pkgutil.walk_packages(module.__path__, prefix=module.__name__ + "."):
                submodules.add(name)

        except Exception as e:
            print(f"could not import {module_path}: {e}")

    return sorted(submodules)


def main() -> None:
    """
    Generate a JSON file of the allowed canvas_sdk imports.
    """
    print("Generating allowed canavs_sdk imports...")

    CANVAS_SUBMODULE_NAMES = [
        found_module
        for found_module in find_submodules(CANVAS_TOP_LEVEL_MODULES)
        # tests are excluded from the built and distributed module in pyproject.toml
        if "tests" not in found_module and "test_" not in found_module
    ]

    CANVAS_MODULES: dict[str, set[str]] = {}

    for module_name in CANVAS_SUBMODULE_NAMES:
        module = importlib.import_module(module_name)

        exports = getattr(module, "__exports__", None)

        if not exports:
            continue

        if module_name not in CANVAS_MODULES:
            CANVAS_MODULES[module_name] = set()

        CANVAS_MODULES[module_name].update(exports)

    # In use by a current plugin...
    CANVAS_MODULES["canvas_sdk.commands"].add("*")

    def default(o: Any) -> Any:
        if isinstance(o, set):
            return sorted(o)

        raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")

    allowed_module_imports_path = Path(__file__).parent / "allowed-module-imports.json"

    allowed_module_imports_path.write_text(
        json.dumps(
            CANVAS_MODULES,
            default=default,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
