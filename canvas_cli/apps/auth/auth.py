from typing import Optional
from urllib.parse import parse_qs, urlparse

import typer

from canvas_cli.apps.auth.utils import (
    delete_password,
    get_or_request_api_token,
    get_password,
    set_password,
)
from canvas_cli.utils.context.context import context
from canvas_cli.utils.print import print
from canvas_cli.utils.validators import get_default_host

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
    short_help="Adds host=client_id&client_secret pair to the keychain, so it can be used to request future tokens"
)
def add_api_client_credentials(
    host: str = typer.Option(..., prompt=True, callback=validate_host),
    client_id: str = typer.Option(..., prompt=True),
    client_secret: str = typer.Option(..., prompt=True),
    is_default: bool = typer.Option(..., prompt=True),
) -> None:
    """Adds host=client_id and host=client_secret pair to the keychain, so it can be used to request future tokens.
    Optionally set a default so `--host` isn't required everywhere
    """
    print.verbose(f"Saving a client_id and client_secret for {host}...")

    current_creds = get_password(host)
    if current_creds:
        typer.confirm(
            f"An client_id and client_secret already exist for {host}, override?", abort=True
        )

    set_password(username=host, password=f"client_id={client_id}&client_secret={client_secret}")

    if is_default:
        context.default_host = host
        print(f"{host} saved as default for future usage")
    else:
        print(f"{host} saved")


@app.command(short_help="Removes a host from the keychain, and as the default if it's the one")
def remove_api_client_credentials(host: str = typer.Argument(..., callback=validate_host)) -> None:
    """Removes a host from the keychain, and as the default if it's the one.
    This method always succeeds, regardless of username existence.
    """
    print.verbose(f"Removing {host} from the keychain")

    delete_password(username=host)

    if context.default_host == host:
        print.verbose(f"{host} was marked as default, removing from config")
        context.default_host = None

    print(f"{host} removed")


@app.command(short_help="Print the api_client_credentials for the given host")
def get_api_client_credentials(host: str = typer.Argument(..., callback=validate_host)) -> None:
    """Print the api_client_credentials for the given host."""
    api_client_credentials = get_password(host)

    if api_client_credentials:
        creds = parse_qs(api_client_credentials)
        print.json(message=None, host=host, **creds)
    else:
        print.json(f"{host} not found.", success=False)


@app.command(short_help="Set the host as the default host in the config file")
def set_default_host(host: str = typer.Argument(..., callback=validate_host)) -> None:
    """Set the host as the default host in the config file. Validates it exists in the keychain."""
    print.verbose(f"Setting {host} as default")

    if not get_password(host):
        print.json(f"{host} doesn't exist in the keychain. Please add it first.", success=False)
        raise typer.Abort()

    context.default_host = host


@app.command(short_help="Print the current api_token for the given host.")
def get_api_token(
    host: Optional[str] = typer.Option(callback=get_default_host, default=None),
    client_id: Optional[str] = typer.Option(default=None),
    client_secret: Optional[str] = typer.Option(default=None),
) -> None:
    """Print the current api_token for the given host."""
    if not host:
        raise typer.BadParameter("Please specify a host or set a default via the `auth` command")

    try:
        token = get_or_request_api_token(host, client_id, client_secret)
    except Exception as e:
        raise typer.BadParameter(e.__str__())

    print.json(message=None, token=token)
