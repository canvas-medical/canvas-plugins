from datetime import datetime, timedelta

import keyring
import requests

from canvas_cli.utils.context.context import context

# Keyring namespace we'll use
KEYRING_SERVICE = __name__


def get_password(username: str) -> str | None:
    """Return the stored password for username, or None."""
    return keyring.get_password(KEYRING_SERVICE, username)


def set_password(username: str, password: str) -> None:
    """Set the password for the given username."""
    keyring.set_password(KEYRING_SERVICE, username=username, password=password)


def delete_password(username: str) -> None:
    """Delete the password for the given username."""
    keyring.delete_password(KEYRING_SERVICE, username=username)


def get_api_client_credentials(
    host: str, client_id: str | None, client_secret: str | None
) -> str | None:
    """Either return the given api_key, or fetch it from the keyring."""
    if client_id and client_secret:
        return f"client_id={client_id}&client_secret={client_secret}"

    return get_password(host)


def request_api_token(host: str, api_client_credentials: str) -> str | None:
    """Request an api token using the provided client_id and client_secret."""
    token_response = requests.post(
        f"{host}/auth/token/",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f"grant_type=client_credentials&{api_client_credentials}",
    )
    if token_response.status_code != requests.codes.ok:
        raise Exception(
            "Unable to get a valid access token. Please check your host, client_id, and client_secret"
        )

    token_response_json = token_response.json()

    token_expiration_date = datetime.now() + timedelta(seconds=token_response_json["expires_in"])
    context.token_expiration_date = token_expiration_date.isoformat()
    return token_response_json["access_token"]


def is_token_valid() -> bool:
    """True if the token has not expired yet."""
    expiration_date = context.token_expiration_date
    return expiration_date is not None and datetime.fromisoformat(expiration_date) > datetime.now()


def get_or_request_api_token(host: str, client_id: str | None, client_secret: str | None) -> str:
    """Returns an existing stored token if it has not expired, or requests a new one."""
    host_token_key = f"{host}|token"
    token = get_password(host_token_key)

    if token and is_token_valid():
        return token

    if not (api_client_credentials := get_api_client_credentials(host, client_id, client_secret)):
        raise Exception(
            "Please specify a client_id and client_secret or add them via the `auth` command"
        )

    if not (new_token := request_api_token(host, api_client_credentials)):
        raise Exception(
            "A token could not be acquired from the given host, client_id, and client_secret"
        )
    set_password(host_token_key, new_token)
    return new_token
