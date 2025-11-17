"""Tests for charting_api_examples.util module."""

from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from charting_api_examples.util import (
    get_note_from_path_params,
    is_valid_uuid,
    note_not_found_response,
)


class TestIsValidUuid:
    """Tests for is_valid_uuid function."""

    def test_valid_uuid_v4(self):
        """Test that a valid UUID v4 returns True."""
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        assert is_valid_uuid(valid_uuid) is True

    def test_invalid_uuid_string(self):
        """Test that an invalid UUID string returns False."""
        invalid_uuid = "not-a-uuid"
        assert is_valid_uuid(invalid_uuid) is False

    def test_empty_string(self):
        """Test that an empty string returns False."""
        assert is_valid_uuid("") is False

    def test_uuid_with_wrong_format(self):
        """Test that a UUID with wrong format returns False."""
        assert is_valid_uuid("550e8400e29b41d4a716446655440000") is False

    def test_uuid_with_uppercase(self):
        """Test that UUID with uppercase letters is not valid (must match exactly)."""
        # is_valid_uuid checks if str(uuid_obj) == possible_uuid, which means
        # the UUID library will lowercase it, so uppercase won't match
        uppercase_uuid = "550E8400-E29B-41D4-A716-446655440000"
        assert is_valid_uuid(uppercase_uuid) is False


class TestNoteNotFoundResponse:
    """Tests for note_not_found_response function."""

    def test_response_structure(self):
        """Test that the response has the correct structure."""
        import json

        response = note_not_found_response()

        # JSONResponse.content is bytes, need to decode
        data = json.loads(response.content.decode())
        assert data == {"error": "Note not found."}
        assert response.status_code == HTTPStatus.NOT_FOUND


class TestGetNoteFromPathParams:
    """Tests for get_note_from_path_params function."""

    def test_valid_uuid_note_exists(self):
        """Test that a note is returned when UUID is valid and note exists."""
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        path_params = {"id": valid_uuid}

        with patch("charting_api_examples.util.Note.objects.get") as mock_get:
            mock_note = MagicMock()
            mock_get.return_value = mock_note

            result = get_note_from_path_params(path_params)

            assert result == mock_note
            mock_get.assert_called_once_with(id=valid_uuid)

    def test_invalid_uuid(self):
        """Test that None is returned when UUID is invalid."""
        path_params = {"id": "not-a-uuid"}

        result = get_note_from_path_params(path_params)

        assert result is None

    def test_note_does_not_exist(self):
        """Test that None is returned when note does not exist."""
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        path_params = {"id": valid_uuid}

        with patch("charting_api_examples.util.Note.objects.get") as mock_get:
            from canvas_sdk.v1.data.note import Note
            mock_get.side_effect = Note.DoesNotExist()

            result = get_note_from_path_params(path_params)

            assert result is None
