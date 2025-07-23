import uuid
from typing import cast
from unittest.mock import Mock, PropertyMock, patch

import pytest

from canvas_sdk.commands.commands.questionnaire import QuestionnaireCommand
from canvas_sdk.commands.commands.questionnaire.toggle_questions import ToggleQuestionsMixin
from canvas_sdk.v1.data import Command


@pytest.fixture(scope="module")
def TestCommand() -> type[ToggleQuestionsMixin]:
    """Create a test command class that uses the ToggleQuestionsMixin."""

    class TestCommand(ToggleQuestionsMixin, QuestionnaireCommand):
        """Test command that uses the ToggleQuestionsMixin."""

        __test__ = False  # Prevent pytest from treating this as a test case

        class Meta:
            key = "test"

    return cast(type[ToggleQuestionsMixin], TestCommand)


COMMAND_ID = str(uuid.uuid4())
QUESTIONNAIRE_ID = str(uuid.uuid4())


@pytest.fixture
def command_without_uuid(TestCommand: type[QuestionnaireCommand]) -> ToggleQuestionsMixin:
    """Create a command instance without a command_uuid."""
    return cast(ToggleQuestionsMixin, TestCommand(questionnaire_id=QUESTIONNAIRE_ID))


@pytest.fixture
def command_with_uuid(TestCommand: type[QuestionnaireCommand]) -> ToggleQuestionsMixin:
    """Create a command instance with a command_uuid."""
    cmd = TestCommand(questionnaire_id=QUESTIONNAIRE_ID)
    cmd.command_uuid = COMMAND_ID
    return cast(ToggleQuestionsMixin, cmd)


def test_initial_state_without_command_uuid(command_without_uuid: ToggleQuestionsMixin) -> None:
    """Test that a new command without UUID has empty toggle states."""
    assert command_without_uuid._question_toggles is None
    toggles = command_without_uuid.question_toggles
    assert toggles == {}
    assert command_without_uuid._question_toggles == {}


def test_load_persisted_toggles_success(command_with_uuid: ToggleQuestionsMixin) -> None:
    """Test loading toggle states from an existing command."""
    # Mock the database response
    with patch(
        "canvas_sdk.commands.commands.questionnaire.toggle_questions.Command.objects.values_list"
    ) as mock_values_list:
        mock_get = Mock()
        mock_get.get.return_value = {
            "skip-123": True,
            "skip-456": False,
            "skip-789": True,
            "other-field": "ignored",
        }
        mock_values_list.return_value = mock_get

        # Trigger loading
        toggles = command_with_uuid.question_toggles

        # Verify correct loading
        assert toggles == {"123": True, "456": False, "789": True}
        mock_values_list.assert_called_once_with("data", flat=True)
        mock_get.get.assert_called_once_with(id=COMMAND_ID)


def test_load_persisted_toggles_command_not_found(command_with_uuid: ToggleQuestionsMixin) -> None:
    """Test behavior when command doesn't exist in database."""
    with patch(
        "canvas_sdk.commands.commands.questionnaire.toggle_questions.Command.objects.values_list"
    ) as mock_values_list:
        # Mock DoesNotExist exception
        mock_get = Mock()
        mock_get.get.side_effect = Command.DoesNotExist()
        mock_values_list.return_value = mock_get

        # Should not raise, just return empty
        toggles = command_with_uuid.question_toggles
        assert toggles == {}


def test_is_question_enabled_default(command_without_uuid: ToggleQuestionsMixin) -> None:
    """Test that questions default to None when not found."""
    assert command_without_uuid.is_question_enabled("123") is None
    assert command_without_uuid.is_question_enabled(456) is None


def test_is_question_enabled_with_persisted_state(command_with_uuid: ToggleQuestionsMixin) -> None:
    """Test is_question_enabled with persisted states."""
    with patch(
        "canvas_sdk.commands.commands.questionnaire.toggle_questions.Command.objects.values_list"
    ) as mock_values_list:
        # Mock persisted states
        mock_get = Mock()
        mock_get.get.return_value = {
            "skip-123": True,
            "skip-456": False,
        }
        mock_values_list.return_value = mock_get

        assert command_with_uuid.is_question_enabled("123") is True
        assert command_with_uuid.is_question_enabled("456") is False
        assert command_with_uuid.is_question_enabled("789") is None


def test_set_question_enabled(command_without_uuid: ToggleQuestionsMixin) -> None:
    """Test setting question enabled states."""
    # Enable a question
    command_without_uuid.set_question_enabled("123", True)
    assert command_without_uuid.is_question_enabled("123") is True

    # Disable a question
    command_without_uuid.set_question_enabled("123", False)
    assert command_without_uuid.is_question_enabled("123") is False

    # Test with int input
    command_without_uuid.set_question_enabled(456, True)
    assert command_without_uuid.is_question_enabled("456") is True


def test_runtime_changes_override_persisted(command_with_uuid: ToggleQuestionsMixin) -> None:
    """Test that runtime changes override persisted states."""
    with patch(
        "canvas_sdk.commands.commands.questionnaire.toggle_questions.Command.objects.values_list"
    ) as mock_values_list:
        # Mock persisted state
        mock_get = Mock()
        mock_get.get.return_value = {"skip-123": True}  # Persisted as enabled
        mock_values_list.return_value = mock_get

        # Runtime change to disabled
        command_with_uuid.set_question_enabled("123", False)
        assert command_with_uuid.is_question_enabled("123") is False

        # Verify toggles show runtime state
        toggles = command_with_uuid.question_toggles
        assert toggles["123"] is False


@patch(
    "canvas_sdk.commands.commands.questionnaire.QuestionnaireCommand.values",
    new_callable=PropertyMock,
)
def test_values_includes_skip_prefix(
    mock_parent_values: PropertyMock, command_without_uuid: ToggleQuestionsMixin
) -> None:
    """Test that values property adds skip- prefix correctly."""
    # Mock parent class values to avoid DB access
    mock_parent_values.return_value = {"questionnaire_id": QUESTIONNAIRE_ID}

    command_without_uuid.set_question_enabled("123", True)
    command_without_uuid.set_question_enabled("456", False)

    values = command_without_uuid.values

    # Should include questionnaire_id from parent class
    assert values["questionnaire_id"] == QUESTIONNAIRE_ID

    # Should include skip states with prefix
    assert values["skip-123"] is True
    assert values["skip-456"] is False


@patch(
    "canvas_sdk.commands.commands.questionnaire.QuestionnaireCommand.values",
    new_callable=PropertyMock,
)
def test_values_merges_persisted_and_runtime(
    mock_parent_values: PropertyMock, command_with_uuid: ToggleQuestionsMixin
) -> None:
    """Test that values merges persisted and runtime states correctly."""
    # Mock parent class values
    with patch(
        "canvas_sdk.commands.commands.questionnaire.toggle_questions.Command.objects.values_list"
    ) as mock_values_list:
        mock_parent_values.return_value = {"questionnaire_id": QUESTIONNAIRE_ID}

        # Mock persisted states
        mock_get = Mock()
        mock_get.get.return_value = {
            "skip-123": True,
            "skip-456": False,
        }
        mock_values_list.return_value = mock_get

        # Add runtime changes
        command_with_uuid.set_question_enabled("456", True)  # Override persisted
        command_with_uuid.set_question_enabled("789", False)  # New toggle

        values = command_with_uuid.values

        assert values["skip-123"] is True  # From persisted
        assert values["skip-456"] is True  # Runtime override
        assert values["skip-789"] is False  # New runtime


def test_question_toggles_returns_copy(command_without_uuid: ToggleQuestionsMixin) -> None:
    """Test that question_toggles returns a copy, not the internal dict."""
    command_without_uuid.set_question_enabled("123", True)

    toggles = command_without_uuid.question_toggles
    toggles["456"] = False  # Modify returned dict

    # Internal state should not be affected
    assert command_without_uuid.is_question_enabled("456") is None


def test_ensure_toggles_loaded_called_once(command_with_uuid: ToggleQuestionsMixin) -> None:
    """Test that database is only queried once, not on every access."""
    with patch(
        "canvas_sdk.commands.commands.questionnaire.toggle_questions.Command.objects.values_list"
    ) as mock_values_list:
        mock_get = Mock()
        mock_get.get.return_value = {"skip-123": True}
        mock_values_list.return_value = mock_get

        # Multiple accesses
        command_with_uuid.is_question_enabled("123")
        command_with_uuid.set_question_enabled("456", True)
        _ = command_with_uuid.question_toggles

        # Access values with mocked parent
        with patch(
            "canvas_sdk.commands.commands.questionnaire.QuestionnaireCommand.values",
            new_callable=PropertyMock,
        ) as mock_parent_values:
            mock_parent_values.return_value = {"questionnaire_id": QUESTIONNAIRE_ID}
            _ = command_with_uuid.values

        # Database should only be queried once
        assert mock_values_list.call_count == 1


def test_type_conversion_for_question_ids(command_without_uuid: ToggleQuestionsMixin) -> None:
    """Test that question IDs are consistently converted to strings."""
    command_without_uuid.set_question_enabled(123, True)
    command_without_uuid.set_question_enabled("456", False)

    # Both should work with string or int lookup
    assert command_without_uuid.is_question_enabled(123) is True
    assert command_without_uuid.is_question_enabled("123") is True
    assert command_without_uuid.is_question_enabled(456) is False
    assert command_without_uuid.is_question_enabled("456") is False

    # Internal storage should use strings
    toggles = command_without_uuid.question_toggles
    assert all(isinstance(k, str) for k in toggles)


@patch(
    "canvas_sdk.commands.commands.questionnaire.QuestionnaireCommand.values",
    new_callable=PropertyMock,
)
def test_values_with_no_toggles(
    mock_parent_values: PropertyMock, command_without_uuid: ToggleQuestionsMixin
) -> None:
    """Test values property when no toggles are set."""
    mock_parent_values.return_value = {"questionnaire_id": QUESTIONNAIRE_ID}

    values = command_without_uuid.values

    # Should only have parent values, no skip fields
    assert values == {"questionnaire_id": QUESTIONNAIRE_ID}


@patch(
    "canvas_sdk.commands.commands.questionnaire.QuestionnaireCommand.values",
    new_callable=PropertyMock,
)
def test_complex_scenario(
    mock_parent_values: PropertyMock, command_with_uuid: ToggleQuestionsMixin
) -> None:
    """Test a complex scenario with multiple operations."""
    with patch(
        "canvas_sdk.commands.commands.questionnaire.toggle_questions.Command.objects.values_list"
    ) as mock_values_list:
        # Mock parent values
        mock_parent_values.return_value = {
            "questionnaire_id": QUESTIONNAIRE_ID,
            "questions": {"question-123": "response"},
        }

        # Mock persisted states
        mock_get = Mock()
        mock_get.get.return_value = {
            "skip-123": True,
            "skip-456": False,
            "skip-789": True,
        }
        mock_values_list.return_value = mock_get

        # Check initial state
        assert command_with_uuid.is_question_enabled("123") is True
        assert command_with_uuid.is_question_enabled("456") is False

        # Make changes
        command_with_uuid.set_question_enabled("123", False)  # Disable previously enabled
        command_with_uuid.set_question_enabled("999", True)  # Add new

        # Get final values
        values = command_with_uuid.values

        # Should have all parent values plus all skip states
        assert values["questionnaire_id"] == QUESTIONNAIRE_ID
        assert values["questions"] == {"question-123": "response"}
        assert values["skip-123"] is False  # Changed
        assert values["skip-456"] is False  # Unchanged
        assert values["skip-789"] is True  # Unchanged
        assert values["skip-999"] is True  # New
