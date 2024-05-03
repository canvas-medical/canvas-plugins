import importlib.metadata
from pathlib import Path
from typing import Optional

import typer

from canvas_cli.apps import plugin
from canvas_cli.apps.logs import logs as logs_command
from canvas_cli.utils.context import context
from canvas_cli.utils.print import print

APP_NAME = "canvas_cli"

# The main app
app = typer.Typer(no_args_is_help=True)

# Commands
app.command(short_help="Create a new plugin")(plugin.init)
app.command(short_help="Install a plugin into a Canvas instance")(plugin.install)
app.command(short_help="Uninstall a plugin from a Canvas instance")(plugin.uninstall)
app.command(short_help="List all plugins from a Canvas instance")(plugin.list)
app.command(short_help="Validate the Canvas Manifest json file")(plugin.validate_manifest)
app.command(short_help="Listen and print log streams from a Canvas instance")(logs_command)

# Our current version
__version__ = importlib.metadata.version("canvas")


def version_callback(value: bool) -> None:
    """Method called when the `--version` flag is set. Prints the version and exits the CLI."""
    if value:
        print.json(f"{APP_NAME} Version: {__version__}", version=__version__)
        raise typer.Exit()


def get_app_dir() -> str:
    """Return the app dir, where the config file will be saved.
    This method is monkeypatched in conftest.py, for testing purposes.
    """
    return typer.get_app_dir(APP_NAME)


def get_or_create_config_file() -> Path:
    """Method called to get a Path to the existent JSON config file, or create one if it doesn't exist."""
    app_dir = get_app_dir()
    config_path: Path = Path(app_dir) / "config.json"
    if not config_path.is_file():
        Path(app_dir).mkdir(parents=True, exist_ok=True)
        with open(config_path, "w+") as file:
            file.write("{}")

    return config_path


@app.callback()
def main(
    no_ansi: bool = typer.Option(False, "--no-ansi", help="Disable colorized output"),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Show extra output"),
) -> None:
    """Canvas swiss army knife CLI tool."""
    # Fetch the config file and load our context from it.
    config_file = get_or_create_config_file()

    context.load_from_file(config_file)

    context.no_ansi = no_ansi

    # Set the --verbose flag
    if verbose:
        context.verbose = verbose
        print.verbose("Verbose mode enabled")


if __name__ == "__main__":
    app()
