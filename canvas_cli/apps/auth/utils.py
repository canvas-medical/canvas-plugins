import configparser
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

import keyring
import requests

from canvas_sdk.utils import Http

# Keyring namespace we'll use
KEYRING_SERVICE = __name__

CONFIG_PATH = Path.home() / ".canvas" / "credentials.ini"

LOCALHOST = "http://localhost:8000"


def get_password(username: str) -> str | None:
    """Return the stored password for username, or None."""
    return keyring.get_password(KEYRING_SERVICE, username)


def set_password(username: str, password: str) -> None:
    """Set the password for the given username."""
    keyring.set_password(KEYRING_SERVICE, username=username, password=password)


def delete_password(username: str) -> None:
    """Delete the password for the given username."""
    keyring.delete_password(KEYRING_SERVICE, username=username)


def get_config() -> configparser.ConfigParser:
    """Reads the config file and returns a ConfigParser object."""
    config = configparser.ConfigParser()
    if not config.read(CONFIG_PATH):
        raise Exception(
            f"""Please add your configuration file at '{CONFIG_PATH}' with the following format:

            [my-canvas-subdomain]
            client_id=myclientid
            client_secret=myclientsecret

            [my-dev-canvas-subdomain]
            client_id=devclientid
            client_secret=devclientsecret
            is_default=true

            [localhost]
            client_id=localclientid
            client_secret=localclientsecret
            """
        )
    return config


def read_config(host: str, property: str) -> str:
    """Reads the config file and returns the property for a given section."""
    config = get_config()
    if host not in config:
        raise Exception(f"'{host}' is not found in the configuration file at '{CONFIG_PATH}'")
    return config.get(host, property)


def get_api_client_credentials(host: str) -> str:
    """Either return the given api_key, or fetch it from the keyring."""
    hostname = urlparse(host).hostname

    if not hostname:
        raise ValueError("Could not parse hostname from URL")

    instance = hostname.removesuffix(".canvasmedical.com")

    client_id = read_config(instance, "client_id")
    client_secret = read_config(instance, "client_secret")

    return f"client_id={client_id}&client_secret={client_secret}"


def get_default_host(host: str | None = None) -> str:
    """Return the explicitly stated default host, or first if none is indicated."""
    if host:
        if "://" in host:
            return host

        if "localhost" in host:
            return LOCALHOST

        return f"https://{host}.canvasmedical.com"

    config = get_config()
    if not (hosts := config.sections()):
        raise Exception(f"No hosts found in the configuration file at '{CONFIG_PATH}'")

    first_default_host = next(
        (host for host in hosts if config.getboolean(host, "is_default", fallback=False) is True),
        hosts[0],
    )
    if first_default_host == "localhost":
        return LOCALHOST

    return f"https://{first_default_host}.canvasmedical.com"


def request_api_token(host: str, api_client_credentials: str) -> dict:
    """Request an api token using the provided client_id and client_secret."""
    grant_type = "grant_type=client_credentials"
    scope = "scope=system/Plugins.*"

    http = Http()
    token_response = http.post(
        f"{host}/auth/token/",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f"{grant_type}&{scope}&{api_client_credentials}",
    )
    if token_response.status_code != requests.codes.ok:
        raise Exception(f"Unable to get a valid access token from the given host '{host}'")
    return token_response.json()


def is_token_valid(host_token_key: str, expiration_date: datetime | None = None) -> bool:
    """True if the token has not expired yet."""
    token_exp_date_key = f"{host_token_key}|exp_date"

    if expiration_date:
        if expiration_date <= datetime.now():
            return False
        set_password(token_exp_date_key, expiration_date.isoformat())
        return True

    stored_expiration_date = get_password(token_exp_date_key)
    return (
        stored_expiration_date is not None
        and datetime.fromisoformat(stored_expiration_date) > datetime.now()
    )


def get_or_request_api_token(host: str | None = None) -> str:
    """Returns an existing stored token if it has not expired, or requests a new one."""
    if not (host := get_default_host(host)):
        raise Exception(
            f"Please specify a host or add one to the configuration file at '{CONFIG_PATH}'"
        )

    host_token_key = f"{host}|token"
    token = get_password(host_token_key)

    if token and is_token_valid(host_token_key):
        return token

    api_client_credentials = get_api_client_credentials(host)

    if not (token_response := request_api_token(host, api_client_credentials)):
        raise Exception(f"A token could not be acquired from the given host '{host}'")

    token_expiration_date = datetime.now() + timedelta(seconds=token_response["expires_in"])
    if not is_token_valid(host_token_key, token_expiration_date):
        raise Exception(f"A valid token could not be acquired from the given host '{host}'")

    new_token = token_response["access_token"]
    set_password(host_token_key, new_token)
    return new_token
