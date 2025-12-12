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


def has_constants(cls: type, constants: dict) -> bool:
    """Verify a class has expected constant attributes with specific values.

    Validates that a class has all expected constants (uppercase attributes that are not
    callable and don't start with underscore) with matching values. Prints diagnostic
    messages for any mismatches.

    Args:
        cls: Class to verify
        constants: Dictionary mapping constant names to their expected values

    Returns:
        True if class has all expected constants with matching values, False otherwise
    """
    result = True
    count = 0
    tested_keys = set()
    for attr in dir(cls):
        if attr.upper() == attr and not (attr.startswith("_") or callable(getattr(cls, attr))):
            tested_keys.add(attr)
            count += 1
            if attr not in constants:
                print(f"Tested has new attribute not expected: '{attr}'")
                result = False

    if count != len(constants.keys()):
        print(f"----> counts: {count} != {len(constants.keys())}")
        result = False

    for key, value in constants.items():
        if key not in tested_keys:
            print(f"Expected attributes not in tested: '{key}'")
        if getattr(cls, key) != value:
            print(f"----> {key} value is {getattr(cls, key)}")
            result = False

    return result


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
