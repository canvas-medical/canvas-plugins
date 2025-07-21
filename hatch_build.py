import pathlib
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

ALLOWED_MODULE_IMPORTS_PATH = "plugin_runner/allowed-module-imports.pickle"


class CustomBuildHook(BuildHookInterface):
    """
    Custom build hooks for `uv build`.
    """

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        """
        Verify that the command to generate the allow modules file has been run
        before the build is allowed.
        """
        allowed_modules_path = pathlib.Path(__file__).parent / ALLOWED_MODULE_IMPORTS_PATH

        if not allowed_modules_path.exists():
            raise Exception(
                f"'{ALLOWED_MODULE_IMPORTS_PATH}' does not exist; run the "
                "generation command (`uv run python -m plugin_runner.generate_allowed_imports`)"
            )
