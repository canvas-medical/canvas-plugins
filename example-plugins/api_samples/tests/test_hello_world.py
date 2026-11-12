"""Tests for the hello_world route's API key check."""

from unittest.mock import Mock

import pytest
from api_samples.routes.hello_world import HelloWorldAPI

from canvas_sdk.handlers.simple_api import APIKeyCredentials


@pytest.mark.parametrize(("key", "expected"), [("valid-secret-key", True), ("wrong-key", False)])
def test_authenticate_compares_the_key_with_the_secret(key: str, expected: bool) -> None:
    """Only the key stored in the `my-api-key` secret is accepted."""
    api = HelloWorldAPI.__new__(HelloWorldAPI)
    api.secrets = {"my-api-key": "valid-secret-key"}
    credentials = Mock(spec=APIKeyCredentials)
    credentials.key = key

    assert api.authenticate(credentials) is expected
