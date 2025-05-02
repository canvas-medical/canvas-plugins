import pytest
import requests
from django.conf import settings
from typer.testing import CliRunner

from canvas_sdk.tests.shared import MaskedValue


@pytest.fixture(scope="session")
def cli_runner() -> CliRunner:
    """Return a CliRunner."""
    return CliRunner()


@pytest.fixture(scope="session")
def token() -> MaskedValue:
    """Get a valid token."""
    response = requests.post(
        f"{settings.INTEGRATION_TEST_URL}/auth/token/",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": settings.INTEGRATION_TEST_CLIENT_ID,
            "client_secret": settings.INTEGRATION_TEST_CLIENT_SECRET,
        },
    )
    response.raise_for_status()

    return MaskedValue(response.json()["access_token"])


@pytest.fixture(scope="session")
def auth_header(token: MaskedValue) -> dict[str, str]:
    """Return the headers."""
    return {
        "Authorization": f"Bearer {token.value}",
    }


@pytest.fixture
def note(auth_header: dict) -> dict:
    """Create a new note."""
    data = {
        "patient": 1,
        "provider": 1,
        "note_type": "office",
        "note_type_version": 1,
        "lastModifiedBySessionKey": "8fee3c03a525cebee1d8a6b8e63dd4dg",
    }
    response = requests.post(
        f"{settings.INTEGRATION_TEST_URL}/api/Note/", headers=auth_header, json=data
    )
    response.raise_for_status()
    return response.json()
