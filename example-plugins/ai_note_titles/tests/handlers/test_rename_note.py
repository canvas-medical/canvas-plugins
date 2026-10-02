import json
from unittest.mock import MagicMock, Mock, patch

import pytest

from ai_note_titles.handlers.rename_note import Handler
from canvas_sdk.v1.data.note import NoteStates


@pytest.fixture
def handler():
    """Create a Handler instance with mocked event."""
    mock_event = MagicMock()
    mock_event.target.id = "test-event-id"
    return Handler(event=mock_event)


@pytest.fixture
def handler_with_context(handler, monkeypatch):
    """Create a Handler instance with note_id in context."""
    dummy_context = {"note_id": "test-note-id"}
    monkeypatch.setattr(type(handler), "context", property(lambda self: dummy_context))
    return handler


@pytest.fixture
def handler_without_context(handler, monkeypatch):
    """Create a Handler instance without note_id in context."""
    dummy_context = {}
    monkeypatch.setattr(type(handler), "context", property(lambda self: dummy_context))
    return handler


class TestHandlerCompute:
    """Tests for the Handler.compute() method."""

    def test_compute_no_note_id_in_context(self, handler_without_context):
        """Test compute() returns empty list when note_id is not in context."""
        effects = handler_without_context.compute()
        assert effects == []

    def test_compute_note_not_locked(self, handler_with_context):
        """Test compute() returns empty list when note is not locked."""
        with patch.object(handler_with_context, "is_locked_note_event", return_value=False):
            effects = handler_with_context.compute()
            assert effects == []

    def test_compute_note_locked_title_generation_fails(self, handler_with_context):
        """Test compute() returns empty list when title generation fails."""
        with patch.object(handler_with_context, "is_locked_note_event", return_value=True):
            with patch.object(handler_with_context, "get_note_title", return_value=None):
                effects = handler_with_context.compute()
                assert effects == []

    def test_compute_note_locked_title_generation_succeeds(self, handler_with_context):
        """Test compute() returns NoteEffect when title generation succeeds."""
        new_title = "Test Note Title"

        with patch.object(handler_with_context, "is_locked_note_event", return_value=True):
            with patch.object(handler_with_context, "get_note_title", return_value=new_title):
                with patch("ai_note_titles.handlers.rename_note.NoteEffect") as mock_note_effect:
                    mock_effect_instance = MagicMock()
                    mock_updated_effect = MagicMock()
                    mock_effect_instance.update.return_value = mock_updated_effect
                    mock_note_effect.return_value = mock_effect_instance

                    effects = handler_with_context.compute()

                    # Verify NoteEffect was created with correct parameters
                    mock_note_effect.assert_called_once_with(
                        instance_id="test-note-id",
                        title=new_title
                    )

                    # Verify update() was called
                    mock_effect_instance.update.assert_called_once()

                    # Verify the result contains the updated effect
                    assert len(effects) == 1
                    assert effects[0] == mock_updated_effect


class TestGetNoteTitle:
    """Tests for the Handler.get_note_title() method."""

    def test_get_note_title_successful_api_call(self, handler_with_context, monkeypatch):
        """Test get_note_title() returns title on successful API call."""
        # Mock secrets
        handler_with_context.secrets = {"OPENAI_API_KEY": "test-api-key"}

        # Mock get_input, get_instructions, get_model
        with patch.object(handler_with_context, "get_input", return_value="test input"):
            with patch.object(handler_with_context, "get_instructions", return_value="test instructions"):
                with patch.object(handler_with_context, "get_model", return_value="gpt-4.1"):
                    # Mock Http response
                    with patch("ai_note_titles.handlers.rename_note.Http") as mock_http:
                        mock_response = Mock()
                        mock_response.ok = True
                        mock_response.json.return_value = {
                            "output": [
                                {
                                    "content": [
                                        {"text": "Generated Note Title"}
                                    ]
                                }
                            ]
                        }
                        mock_http.return_value.post.return_value = mock_response

                        title = handler_with_context.get_note_title("test-note-id")

                        assert title == "Generated Note Title"

                        # Verify Http.post was called with correct parameters
                        mock_http.return_value.post.assert_called_once()
                        call_args = mock_http.return_value.post.call_args
                        assert call_args[0][0] == "https://api.openai.com/v1/responses"
                        assert call_args[1]["headers"]["Authorization"] == "Bearer test-api-key"

    def test_get_note_title_api_call_fails(self, handler_with_context, monkeypatch):
        """Test get_note_title() returns None when API call fails."""
        # Mock secrets
        handler_with_context.secrets = {"OPENAI_API_KEY": "test-api-key"}

        # Mock get_input, get_instructions, get_model
        with patch.object(handler_with_context, "get_input", return_value="test input"):
            with patch.object(handler_with_context, "get_instructions", return_value="test instructions"):
                with patch.object(handler_with_context, "get_model", return_value="gpt-4.1"):
                    # Mock Http response with error
                    with patch("ai_note_titles.handlers.rename_note.Http") as mock_http:
                        mock_response = Mock()
                        mock_response.ok = False
                        mock_response.status_code = 500
                        mock_response.text = "Internal Server Error"
                        mock_http.return_value.post.return_value = mock_response

                        title = handler_with_context.get_note_title("test-note-id")

                        assert title is None

    def test_get_note_title_parsing_fails(self, handler_with_context, monkeypatch):
        """Test get_note_title() returns None when response parsing fails."""
        # Mock secrets
        handler_with_context.secrets = {"OPENAI_API_KEY": "test-api-key"}

        # Mock get_input, get_instructions, get_model
        with patch.object(handler_with_context, "get_input", return_value="test input"):
            with patch.object(handler_with_context, "get_instructions", return_value="test instructions"):
                with patch.object(handler_with_context, "get_model", return_value="gpt-4.1"):
                    # Mock Http response with malformed data
                    with patch("ai_note_titles.handlers.rename_note.Http") as mock_http:
                        mock_response = Mock()
                        mock_response.ok = True
                        mock_response.text = "malformed response"
                        mock_response.json.return_value = {"malformed": "data"}
                        mock_http.return_value.post.return_value = mock_response

                        title = handler_with_context.get_note_title("test-note-id")

                        assert title is None


class TestIsLockedNoteEvent:
    """Tests for the Handler.is_locked_note_event() method."""

    def test_is_locked_note_event_true(self, handler):
        """Test is_locked_note_event() returns True when note is locked."""
        with patch("ai_note_titles.handlers.rename_note.CurrentNoteStateEvent.objects.values_list") as mock_values_list:
            mock_queryset = MagicMock()
            mock_queryset.get.return_value = NoteStates.LOCKED
            mock_values_list.return_value = mock_queryset

            result = handler.is_locked_note_event()

            assert result is True
            mock_values_list.assert_called_once_with("state", flat=True)
            mock_queryset.get.assert_called_once_with(id="test-event-id")

    def test_is_locked_note_event_false(self, handler):
        """Test is_locked_note_event() returns False when note is not locked."""
        with patch("ai_note_titles.handlers.rename_note.CurrentNoteStateEvent.objects.values_list") as mock_values_list:
            mock_queryset = MagicMock()
            mock_queryset.get.return_value = "UNLOCKED"
            mock_values_list.return_value = mock_queryset

            result = handler.is_locked_note_event()

            assert result is False


class TestHelperMethods:
    """Tests for helper methods."""

    def test_get_model(self, handler):
        """Test get_model() returns the correct model name."""
        assert handler.get_model() == "gpt-4.1"

    def test_get_input(self, handler):
        """Test get_input() returns JSON string of commands."""
        with patch("ai_note_titles.handlers.rename_note.Command.objects.filter") as mock_filter:
            mock_commands = MagicMock()
            mock_commands.values.return_value = [
                {"schema_key": "prescribe", "data": {"medication": "aspirin"}},
                {"schema_key": "assess", "data": {"diagnosis": "headache"}},
            ]
            mock_filter.return_value = mock_commands

            result = handler.get_input("test-note-id")

            # Verify the filter was called correctly
            mock_filter.assert_called_once_with(
                note__id="test-note-id",
                entered_in_error__isnull=True,
                committer__isnull=False
            )

            # Verify the result is valid JSON
            parsed_result = json.loads(result)
            assert len(parsed_result) == 2
            assert parsed_result[0]["schema_key"] == "prescribe"
            assert parsed_result[1]["schema_key"] == "assess"

    def test_get_instructions(self, handler):
        """Test get_instructions() returns the correct instructions."""
        instructions = handler.get_instructions()
        assert "clinical documentation specialist" in instructions
        assert "10 words or less" in instructions
        assert "Return the exact title ONLY" in instructions


class TestHandlerConfiguration:
    """Tests for Handler configuration."""

    def test_responds_to_configuration(self):
        """Test that Handler responds to the correct event types."""
        from canvas_sdk.events import EventType

        assert Handler.RESPONDS_TO == [
            EventType.Name(EventType.NOTE_STATE_CHANGE_EVENT_CREATED),
        ]
