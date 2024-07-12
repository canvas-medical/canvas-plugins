import importlib.metadata
import json
import random
from pathlib import Path
from typing import Annotated, Optional

import grpc
import typer

from canvas_cli.apps import plugin
from canvas_cli.apps.logs import logs as logs_command
from canvas_cli.utils.context import context
from canvas_generated.messages.events_pb2 import Event as PluginRunnerEvent
from canvas_generated.messages.events_pb2 import EventType as PluginRunnerEventType
from canvas_generated.services.plugin_runner_pb2_grpc import PluginRunnerStub

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


@app.command()
def emit(
    event_fixture: str,
    plugin_runner_port: Annotated[
        str, typer.Option(help="Port of your locally running plugin runner")
    ] = "50051",
) -> None:
    """
    Grab an event from a fixture file and send it your locally running plugin-runner process.
    Any resultant effects will be printed.

    Valid fixture files are newline-delimited JSON, with each containing the keys `EventType`, `target`, and `context`. Some fixture files are included in the canvas-plugins repo.
    """
    # Grab a random event from the fixture file ndjson
    lines = Path(event_fixture).read_text().splitlines()
    myline = random.choice(lines)
    event_data = json.loads(myline)
    event = PluginRunnerEvent(
        type=PluginRunnerEventType.Value(event_data["EventType"]),
        target=event_data["target"],
        context=event_data["context"],
    )
    with grpc.insecure_channel(f"localhost:{plugin_runner_port}") as channel:
        stub = PluginRunnerStub(channel)
        responses = stub.HandleEvent(event)

        for response in responses:
            for effect in response.effects:
                print(effect)


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
) -> None:
    """Canvas swiss army knife CLI tool."""
    # Fetch the config file and load our context from it.
    config_file = get_or_create_config_file()

    context.load_from_file(config_file)


if __name__ == "__main__":
    app()
