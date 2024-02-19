from urllib.parse import urlparse

import typer

from canvas_cli.apps.auth.utils import delete_password, get_password, set_password
from canvas_cli.utils.context.context import context
from canvas_cli.utils.print import print

app = typer.Typer()


def validate_host(host: str) -> str:
    """Validates the host is valid and returns the network location part."""
    # Add a little help for the devs who want to specify 'localhost'
    if host == "localhost":
        host = "http://localhost"

    parsed_host = urlparse(host)
    scheme = parsed_host.scheme
    if scheme != "http" and scheme != "https":
        raise typer.BadParameter(f"{scheme} isn't a valid scheme: We only support http and https")

    if not parsed_host.netloc:
        raise typer.BadParameter(f"{host} isn't a valid host")
    return f"{scheme}://{parsed_host.netloc}"


@app.command(
    short_help="Add a host=api-key pair to the keychain, so it can be used in other requests"
)
def add_api_key(
    host: str = typer.Option(..., prompt=True, callback=validate_host),
    api_key: str = typer.Option(..., prompt=True),
    is_default: bool = typer.Option(..., prompt=True),
) -> None:
    """Add a host=api-key pair to the keychain, so it can be used in other requests.
    Optionally set a default so `--host` isn't required everywhere
    """
    print.verbose(f"Saving an api key for {host}...")

    current_credential = get_password(host)
    if current_credential:
        typer.confirm(f"An api-key already exists for {host}, override?", abort=True)

    set_password(username=host, password=api_key)

    if is_default:
        context.default_host = host
        print(f"{host} saved as default for future usage")
    else:
        print(f"{host} saved")


@app.command(short_help="Removes a host from the keychain, and as the default if it's the one")
def remove_api_key(host: str = typer.Argument(..., callback=validate_host)) -> None:
    """Removes a host from the keychain, and as the default if it's the one.
    This method always succeeds, regardless of username existence.
    """
    print.verbose(f"Removing {host} from the keychain")

    delete_password(username=host)

    if context.default_host == host:
        print.verbose(f"{host} was marked as default, removing from config")
        context.default_host = None

    print(f"{host} removed")


@app.command(short_help="Print the api_key for the given host")
def get_api_key(host: str = typer.Argument(..., callback=validate_host)) -> None:
    """Print the api_key for the given host."""
    api_key = get_password(host)

    if api_key:
        print.json(message=None, host=host, api_key=api_key)
    else:
        print.json(f"{host} not found.", success=False)


@app.command(short_help="Set the host as the default host in the config file")
def set_default_host(host: str = typer.Argument(..., callback=validate_host)) -> None:
    """Set the host as the default host in the config file. Validates it exists in the keychain."""
    print.verbose(f"Setting {host} as default")

    api_key = get_password(host)

    if not api_key:
        print.json(f"{host} doesn't exist in the keychain. Please add it first.", success=False)
        raise typer.Abort()

    context.default_host = host
