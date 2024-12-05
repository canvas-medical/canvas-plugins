import importlib.metadata
from pathlib import Path

import typer

from canvas_cli.apps import plugin
from canvas_cli.apps.emit import emit
from canvas_cli.apps.logs import logs as logs_command
from canvas_cli.apps.run_plugins import run_plugin, run_plugins
from canvas_cli.utils.context import context

APP_NAME = "canvas_cli"

# The main app
app = typer.Typer(no_args_is_help=True, rich_markup_mode=None, add_completion=False)

# Commands
app.command(short_help="Create a new plugin")(plugin.init)
app.command(short_help="Install a plugin into a Canvas instance")(plugin.install)
app.command(short_help="Uninstall a plugin from a Canvas instance")(plugin.uninstall)
app.command(short_help="Enable a plugin from a Canvas instance")(plugin.enable)
app.command(short_help="Disable a plugin from a Canvas instance")(plugin.disable)
app.command(short_help="List all plugins from a Canvas instance")(plugin.list)
app.command(short_help="Validate the Canvas Manifest json file")(plugin.validate_manifest)
app.command(short_help="Listen and print log streams from a Canvas instance")(logs_command)
app.command(
    short_help="Send an event fixture to your locally running plugin-runner process, and print any resultant effects."
)(emit)
app.command(short_help="Run the specified plugins for local development.")(run_plugins)
app.command(short_help="Run the specified plugin for local development.")(run_plugin)

# Our current version
__version__ = importlib.metadata.version("canvas")


def version_callback(value: bool) -> None:
    """Method called when the `--version` flag is set. Prints the version and exits the CLI."""
    if value:
        print(f"{APP_NAME} Version: {__version__}")
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
    version: bool | None = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
) -> None:
    """Canvas swiss army knife CLI tool."""
    # Fetch the config file and load our context from it.
    config_file = get_or_create_config_file()

    context.load_from_file(config_file)


if __name__ == "__main__":
    app()
