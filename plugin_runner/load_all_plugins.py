#!/usr/bin/env uv run

import logging
import sys
from contextlib import redirect_stderr, redirect_stdout
from glob import glob
from io import StringIO
from pathlib import Path
from textwrap import indent

from plugin_runner.plugin_runner import load_or_reload_plugin

ORIGINAL_PATH = sys.path.copy()


def main() -> None:
    """
    Iterate through all of our plugins to verify they work with this version of the SDK.
    """
    if len(sys.argv) < 2:
        print("You must specify a base path.")
        sys.exit(1)

    base_path = sys.argv[1]

    for folder in glob(f"{base_path}/**/*"):
        path = Path(folder)

        if "{{" in folder:
            print(f"Ignoring templated path: {folder}")
            continue

        if not path.is_dir():
            continue

        if not (path / "CANVAS_MANIFEST.json").exists():
            print(f"Missing CANVAS_MANIFEST.json in {folder}")
            continue

        sys.path = ORIGINAL_PATH.copy()

        # this makes plugin imports work and mirrors what the plugin_runner does
        sys.path.append((Path(".") / path.parent).as_posix())

        print(path)

        output = StringIO()

        plugin_runner_logger = logging.getLogger("plugin_runner_logger")
        old_handlers = plugin_runner_logger.handlers.copy()
        plugin_runner_logger.handlers = [logging.StreamHandler(output)]

        with redirect_stdout(output), redirect_stderr(output):
            success = load_or_reload_plugin(path)

        output_string = output.getvalue()

        if not success:
            print()
            print(indent(output_string, prefix="    ").rstrip())
            print()

        plugin_runner_logger.handlers = old_handlers


if __name__ == "__main__":
    main()
