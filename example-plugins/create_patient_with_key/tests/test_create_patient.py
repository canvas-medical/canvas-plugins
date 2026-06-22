"""Tests for the create_patient_with_key SimpleAPI route."""

import json
from unittest.mock import Mock, patch

from create_patient_with_key.routes.create_patient import CreateTestPatientAPI

from canvas_sdk.effects.simple_api import JSONResponse
from canvas_sdk.handlers.simple_api import APIKeyCredentials

FIXED_KEY = "0123456789abcdef0123456789abcdef"


class DummyEvent:
    """A dummy event object for instantiating the API handler."""

    def __init__(self, context: dict[str, object] | None = None) -> None:
        self.context = context or {}


def _api() -> CreateTestPatientAPI:
    context = {"method": "POST", "path": "/create-test-patient"}
    return CreateTestPatientAPI(event=DummyEvent(context=context))  # type: ignore[arg-type]


def test_authenticate_with_valid_key() -> None:
    """Authentication succeeds when the credential matches the pre-shared-key secret."""
    api = _api()
    api.secrets = {"pre-shared-key": "valid-secret-key"}
    credentials = Mock(spec=APIKeyCredentials)
    credentials.key = "valid-secret-key"

    assert api.authenticate(credentials) is True


def test_authenticate_with_invalid_key() -> None:
    """Authentication fails when the credential does not match."""
    api = _api()
    api.secrets = {"pre-shared-key": "valid-secret-key"}
    credentials = Mock(spec=APIKeyCredentials)
    credentials.key = "wrong-key"

    assert api.authenticate(credentials) is False


def test_post_creates_patient_with_generated_key() -> None:
    """POST returns a CREATE_PATIENT effect carrying the generated key and echoes it as JSON."""
    api = _api()

    with patch(
        "create_patient_with_key.routes.create_patient.generate_patient_key",
        return_value=FIXED_KEY,
    ):
        result = api.post()

    assert len(result) == 2
    effect, response = result

    # The create effect persists the patient under the plugin-defined key.
    assert json.loads(effect.payload)["data"]["patient_id"] == FIXED_KEY

    # The JSON response hands the key back so the caller can look the patient up.
    assert isinstance(response, JSONResponse)
    assert json.loads(response.content)["patient_key"] == FIXED_KEY
