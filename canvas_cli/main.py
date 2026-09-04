import atexit
import importlib.metadata
import os
from pathlib import Path

import typer

from canvas_cli.apps import namespace, plugin
from canvas_cli.apps.control_room import (
    cr_init,
    deploy,
    git_credential,
    set_variables,
    uninstall,
    unset_variables,
)
from canvas_cli.apps.emit import emit
from canvas_cli.apps.logs import logs as logs_command
from canvas_cli.apps.run_plugins import run_plugin, run_plugins
from canvas_cli.utils.context import context
from canvas_cli.utils.update_check import check_for_updates

APP_NAME = "canvas_cli"

# The main app
app = typer.Typer(no_args_is_help=True, rich_markup_mode=None, add_completion=False)

_CONTROL_ROOM_BETA = os.environ.get("CONTROL_ROOM_BETA", "").lower() == "true"

# Commands
app.command(short_help="Create a new plugin")(plugin.init)
app.command(short_help="Install a plugin into a Canvas instance")(plugin.install)
# In the beta, `uninstall` routes through Control Room (home-app refuses a direct
# CLI uninstall of a control_room_managed plugin — KOALA-5877); otherwise direct.
if _CONTROL_ROOM_BETA:
    app.command(short_help="Uninstall a plugin via Control Room.")(uninstall)
else:
    app.command(short_help="Uninstall a plugin from a Canvas instance")(plugin.uninstall)
app.command(short_help="Enable a plugin from a Canvas instance")(plugin.enable)
app.command(short_help="Disable a plugin from a Canvas instance")(plugin.disable)
app.command(short_help="List all plugins from a Canvas instance")(plugin.list)
app.command(short_help="Validate the Canvas Manifest json file")(plugin.validate_manifest)
app.command(short_help="Validate a plugin's manifest and that its handlers load in the sandbox.")(
    plugin.validate
)
app.command(
    short_help="Listen and print log streams or fetches historical logs from a Canvas instance."
)(logs_command)
app.command(
    short_help="Send an event fixture to your locally running plugin-runner process, and print any resultant effects."
)(emit)
app.command(short_help="Run the specified plugins for local development.")(run_plugins)
app.command(short_help="Run the specified plugin for local development.")(run_plugin)

if _CONTROL_ROOM_BETA:
    app.command(
        name="git-credential",
        hidden=True,
        short_help="Git credential helper for Control Room pushes (invoked by git).",
    )(git_credential)
    app.command(
        name="cr-init",
        short_help="Connect a plugin's git repo to Control Room (sets up the 'cr' remote).",
    )(cr_init)
    app.command(short_help="Deploy a published plugin to this instance via Control Room.")(deploy)

# Config app
config_app = typer.Typer(
    help="Manage plugin variables. Values are write-only; only key names and whether they are set are returned.",
    rich_markup_mode=None,
    add_completion=False,
)
app.add_typer(config_app, name="config")
config_app.command(name="list", short_help="List plugin variables on a Canvas instance.")(
    plugin.list_secrets
)
# In the Control Room beta, `config set` routes through CR (the headless path
# that survives the KOALA-5877 install-write lockout) instead of writing the
# instance directly; the CR path errors clearly if the instance isn't
# CR-managed, mirroring publish/deploy. Outside the beta it stays direct.
if _CONTROL_ROOM_BETA:
    config_app.command(name="set", short_help="Set plugin variables via Control Room.")(
        set_variables
    )
    # Unset is CR-only — the headless clear + reconcile path (KOALA-5923). There's
    # no direct-instance equivalent, so it's registered only in the beta.
    config_app.command(name="unset", short_help="Unset plugin variables via Control Room.")(
        unset_variables
    )
else:
    config_app.command(name="set", short_help="Set plugin variables on a Canvas instance.")(
        plugin.set_secrets
    )

# Namespace app
namespace_app = typer.Typer(
    help="Manage custom data namespaces.", rich_markup_mode=None, add_completion=False
)
app.add_typer(namespace_app, name="namespace")
namespace_app.command(name="list", short_help="List all custom data namespaces.")(
    namespace.list_namespaces
)
namespace_app.command(name="inspect", short_help="Inspect tables in a namespace.")(
    namespace.inspect
)
namespace_app.command(
    name="reset", short_help="Reset a namespace to initial state (dry-run by default)."
)(namespace.reset)
namespace_app.command(name="drop", short_help="Drop a namespace (dry-run by default).")(
    namespace.drop
)

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


# Register the update check to run at exit so it fires for --version, --help,
# and all subcommands regardless of how typer/click handles early exits.
atexit.register(check_for_updates, __version__, get_app_dir())


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
