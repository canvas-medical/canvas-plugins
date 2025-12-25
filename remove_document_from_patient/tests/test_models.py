# To run the tests, use the command `pytest` in the terminal or uv run pytest.
# Each test is wrapped inside a transaction that is rolled back at the end of the test.
# If you want to modify which files are used for testing, check the [tool.pytest.ini_options] section in pyproject.toml.
# For more information on testing Canvas plugins, see: https://docs.canvasmedical.com/sdk/testing-utils/

import json
from unittest.mock import Mock

from remove_document_from_patient.handlers.remove_document_api import (
    RemoveDocumentFromPatientAPI,
)

from canvas_sdk.effects import EffectType


class TestRemoveDocumentFromPatientAPI:
    """Tests for the RemoveDocumentFromPatientAPI."""

    def _create_api_with_request(self, json_body: dict) -> RemoveDocumentFromPatientAPI:
        """Helper to create an API instance with a mocked request."""
        mock_request = Mock()
        mock_request.path = "/remove-document-from-patient"
        mock_request.json = Mock(return_value=json_body)

        api = RemoveDocumentFromPatientAPI.__new__(RemoveDocumentFromPatientAPI)
        api.request = mock_request
        api.secrets = {}
        return api

    def test_post_returns_remove_document_effect(self) -> None:
        """Test that post returns a REMOVE_DOCUMENT_FROM_PATIENT effect."""
        api = self._create_api_with_request(
            {
                "document_id": 12345,
                "patient_id": 67890,
            }
        )

        responses = api.post()

        assert len(responses) == 2
        effect = responses[0]
        assert effect.type == EffectType.REMOVE_DOCUMENT_FROM_PATIENT

        payload = json.loads(effect.payload)
        assert payload["data"]["document_id"] == 12345

    def test_post_without_confidence_score(self) -> None:
        """Test that post without confidence_score does not include it."""
        api = self._create_api_with_request(
            {
                "document_id": 12345,
                "patient_id": 67890,
            }
        )

        responses = api.post()

        effect = responses[0]
        payload = json.loads(effect.payload)
        assert "confidence_scores" not in payload["data"]

    def test_post_with_confidence_score(self) -> None:
        """Test that post with confidence_score includes it."""
        api = self._create_api_with_request(
            {
                "document_id": 12345,
                "patient_id": 67890,
                "confidence_score": 0.95,
            }
        )

        responses = api.post()

        effect = responses[0]
        payload = json.loads(effect.payload)
        assert payload["data"]["document_id"] == 12345
        # JSON serializes int keys as strings
        assert payload["data"]["confidence_scores"] == {"12345": 0.95}

    def test_post_returns_json_response(self) -> None:
        """Test that post returns a success JSONResponse."""
        api = self._create_api_with_request(
            {
                "document_id": 12345,
                "patient_id": 67890,
            }
        )

        responses = api.post()

        json_response = responses[1]
        body = json.loads(json_response.content)
        assert body["success"] is True
        assert body["document_id"] == 12345
        assert body["patient_id"] == 67890

    def test_post_missing_document_id_returns_error(self) -> None:
        """Test that post without document_id returns an error."""
        api = self._create_api_with_request(
            {
                "patient_id": 67890,
            }
        )

        responses = api.post()

        assert len(responses) == 1
        body = json.loads(responses[0].content)
        assert body["error"] == "document_id is required"
        assert responses[0].status_code == 400

    def test_post_missing_patient_id_returns_error(self) -> None:
        """Test that post without patient_id returns an error."""
        api = self._create_api_with_request(
            {
                "document_id": 12345,
            }
        )

        responses = api.post()

        assert len(responses) == 1
        body = json.loads(responses[0].content)
        assert body["error"] == "patient_id is required"
        assert responses[0].status_code == 400

    def test_post_invalid_document_id_type_returns_error(self) -> None:
        """Test that post with non-integer document_id returns an error."""
        api = self._create_api_with_request(
            {
                "document_id": "not_an_int",
                "patient_id": 67890,
            }
        )

        responses = api.post()

        assert len(responses) == 1
        body = json.loads(responses[0].content)
        assert body["error"] == "document_id must be an integer"
        assert responses[0].status_code == 400

    def test_post_invalid_confidence_score_returns_error(self) -> None:
        """Test that post with out-of-range confidence_score returns an error."""
        api = self._create_api_with_request(
            {
                "document_id": 12345,
                "patient_id": 67890,
                "confidence_score": 1.5,
            }
        )

        responses = api.post()

        assert len(responses) == 1
        body = json.loads(responses[0].content)
        assert body["error"] == "confidence_score must be between 0.0 and 1.0"
        assert responses[0].status_code == 400

    def test_authenticate_returns_true(self) -> None:
        """Test that authenticate allows all requests."""
        api = RemoveDocumentFromPatientAPI.__new__(RemoveDocumentFromPatientAPI)
        mock_credentials = Mock()

        result = api.authenticate(mock_credentials)

        assert result is True
