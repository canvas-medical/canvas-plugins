import typer
from canvas_brush.apps.auth import app as auth_app
from canvas_brush.apps.logs import logs as logs_command
from canvas_brush.apps.plugin import app as plugin_app
from canvas_brush.main import main, print_config

app = typer.Typer()

app.add_typer(auth_app, name="auth", help="Manage authenticating in Canvas instances")
app.add_typer(plugin_app, name="plugin", help="Manage plugins in a Canvas instance")

app.command(short_help="Listens and prints log streams from the instance")(logs_command)
app.command(short_help="Print the config and exit")(print_config)

app.callback()(main)


if __name__ == "__main__":
    app()
