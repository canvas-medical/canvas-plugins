from dataclasses import fields as dataclass_fields
from dataclasses import is_dataclass as dataclass_is_dataclass
from typing import get_type_hints

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


def is_dataclass(cls: type, fields: dict) -> bool:
    """Verify a class is a dataclass with expected fields and types.

    Args:
        cls: Class to verify
        fields: Dictionary mapping field names to their expected types

    Returns:
        True if class is a dataclass with matching fields and types, False otherwise
    """
    return (
        dataclass_is_dataclass(cls)
        and len([field for field in dataclass_fields(cls) if field.name in fields])
        == len(fields.keys())
        and all(fields[field.name] == field.type for field in dataclass_fields(cls))
    )


def is_namedtuple(cls: type, fields: dict) -> bool:
    """Verify a class is a NamedTuple with expected fields and types.

    Args:
        cls: Class to verify
        fields: Dictionary mapping field names to their expected types

    Returns:
        True if class is a NamedTuple with matching fields and types, False otherwise
    """
    return (
        issubclass(cls, tuple)
        and hasattr(cls, "_fields")
        and isinstance(cls._fields, tuple)
        and len([field for field in cls._fields if field in fields]) == len(fields.keys())
        and get_type_hints(cls) == fields
    )
