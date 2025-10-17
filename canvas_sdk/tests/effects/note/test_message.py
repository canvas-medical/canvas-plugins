import json
from collections.abc import Generator
from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.note.message import Message


@pytest.fixture
def mock_db_queries() -> Generator[dict[str, MagicMock]]:
    """Mock all database queries to return True/exist by default."""
    with (
        patch("canvas_sdk.v1.data.Patient.objects") as mock_patient,
        patch("canvas_sdk.v1.data.Staff.objects") as mock_staff,
        patch("canvas_sdk.v1.data.Message.objects") as mock_message,
    ):
        # Setup default behaviors
        mock_patient.filter.return_value.exists.return_value = True
        mock_staff.filter.return_value.exists.return_value = True
        mock_message.filter.return_value.exists.return_value = True

        yield {
            "patient": mock_patient,
            "staff": mock_staff,
            "message": mock_message,
        }


@pytest.fixture
def valid_message_data() -> dict[str, Any]:
    """Valid data for creating a Message."""
    return {
        "content": "This is a test message",
        "sender_id": str(uuid4()),
        "recipient_id": str(uuid4()),
    }


def test_create_message_success(
    mock_db_queries: dict[str, MagicMock], valid_message_data: dict[str, Any]
) -> None:
    """Test successful message creation."""
    message = Message(**valid_message_data)
    effect = message.create()

    assert effect.type == EffectType.CREATE_MESSAGE
    payload = json.loads(effect.payload)
    assert payload["data"]["content"] == "This is a test message"
    assert payload["data"]["sender_id"] == valid_message_data["sender_id"]
    assert payload["data"]["recipient_id"] == valid_message_data["recipient_id"]


def test_create_message_missing_content(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test message creation without content."""
    message = Message(sender_id=str(uuid4()), recipient_id=str(uuid4()), content=None)

    with pytest.raises(ValidationError) as exc_info:
        message.create()

    errors = exc_info.value.errors()
    assert any("Message content cannot be empty" in str(e) for e in errors)


def test_create_message_empty_content(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test message creation with whitespace-only content."""
    message = Message(sender_id=str(uuid4()), recipient_id=str(uuid4()), content="   ")

    with pytest.raises(ValidationError) as exc_info:
        message.create()

    errors = exc_info.value.errors()
    assert any("Message content cannot be empty" in str(e) for e in errors)


def test_create_message_with_message_id_fails(
    mock_db_queries: dict[str, MagicMock], valid_message_data: dict[str, Any]
) -> None:
    """Test that message ID cannot be set when creating."""
    valid_message_data["message_id"] = str(uuid4())
    message = Message(**valid_message_data)

    with pytest.raises(ValidationError) as exc_info:
        message.create()

    errors = exc_info.value.errors()
    assert any("Can't set message ID when creating a message" in str(e) for e in errors)


def test_create_message_nonexistent_sender(
    mock_db_queries: dict[str, MagicMock], valid_message_data: dict[str, Any]
) -> None:
    """Test message creation with nonexistent sender."""
    mock_db_queries["patient"].filter.return_value.exists.return_value = False
    mock_db_queries["staff"].filter.return_value.exists.return_value = False

    message = Message(**valid_message_data)

    with pytest.raises(ValidationError) as exc_info:
        message.create()

    errors = exc_info.value.errors()
    assert any("Sender with ID" in str(e) and "does not exist" in str(e) for e in errors)


def test_create_message_nonexistent_recipient(
    mock_db_queries: dict[str, MagicMock], valid_message_data: dict[str, Any]
) -> None:
    """Test message creation with nonexistent recipient."""

    # Sender exists as patient
    def patient_filter_side_effect(id: str) -> MagicMock:
        mock = MagicMock()
        mock.exists.return_value = str(id) == valid_message_data["sender_id"]
        return mock

    def staff_filter_side_effect(id: str) -> MagicMock:
        mock = MagicMock()
        mock.exists.return_value = False
        return mock

    mock_db_queries["patient"].filter.side_effect = patient_filter_side_effect
    mock_db_queries["staff"].filter.side_effect = staff_filter_side_effect

    message = Message(**valid_message_data)

    with pytest.raises(ValidationError) as exc_info:
        message.create()

    errors = exc_info.value.errors()
    assert any("Recipient with ID" in str(e) and "does not exist" in str(e) for e in errors)


def test_create_and_send_message_success(
    mock_db_queries: dict[str, MagicMock], valid_message_data: dict[str, Any]
) -> None:
    """Test successful create and send message."""
    message = Message(**valid_message_data)
    effect = message.create_and_send()

    assert effect.type == EffectType.CREATE_AND_SEND_MESSAGE
    payload = json.loads(effect.payload)
    assert payload["data"]["content"] == "This is a test message"
    assert payload["data"]["sender_id"] == valid_message_data["sender_id"]
    assert payload["data"]["recipient_id"] == valid_message_data["recipient_id"]


def test_create_and_send_message_missing_content(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test create and send without content."""
    message = Message(sender_id=str(uuid4()), recipient_id=str(uuid4()), content=None)

    with pytest.raises(ValidationError) as exc_info:
        message.create_and_send()

    errors = exc_info.value.errors()
    assert any("Message content cannot be empty" in str(e) for e in errors)


def test_create_and_send_message_with_message_id_fails(
    mock_db_queries: dict[str, MagicMock], valid_message_data: dict[str, Any]
) -> None:
    """Test that message ID cannot be set when using create_and_send."""
    valid_message_data["message_id"] = str(uuid4())
    message = Message(**valid_message_data)

    with pytest.raises(ValidationError) as exc_info:
        message.create_and_send()

    errors = exc_info.value.errors()
    assert any("Can't set message ID when creating a message" in str(e) for e in errors)


def test_send_message_success(
    mock_db_queries: dict[str, MagicMock], valid_message_data: dict[str, Any]
) -> None:
    """Test successful send message."""
    valid_message_data["message_id"] = str(uuid4())
    message = Message(**valid_message_data)
    effect = message.send()

    assert effect.type == EffectType.SEND_MESSAGE
    payload = json.loads(effect.payload)
    assert payload["data"]["message_id"] == valid_message_data["message_id"]
    assert payload["data"]["sender_id"] == valid_message_data["sender_id"]
    assert payload["data"]["recipient_id"] == valid_message_data["recipient_id"]


def test_edit_message_success(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test successful message edit."""
    message_id = str(uuid4())
    message = Message(
        message_id=message_id,
        content="Updated content",
        sender_id=str(uuid4()),
        recipient_id=str(uuid4()),
    )
    effect = message.edit()

    assert effect.type == EffectType.EDIT_MESSAGE
    payload = json.loads(effect.payload)
    assert payload["data"]["message_id"] == message_id
    assert payload["data"]["content"] == "Updated content"


def test_edit_message_missing_message_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that edit without message_id raises error."""
    message = Message(content="Updated content", sender_id=str(uuid4()), recipient_id=str(uuid4()))

    with pytest.raises(ValidationError) as exc_info:
        message.edit()

    errors = exc_info.value.errors()
    assert any("Message ID is required when editing a message" in str(e) for e in errors)


def test_edit_message_nonexistent_message(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test editing a message that doesn't exist."""
    mock_db_queries["message"].filter.return_value.exists.return_value = False

    message = Message(
        message_id=str(uuid4()),
        content="Updated content",
        sender_id=str(uuid4()),
        recipient_id=str(uuid4()),
    )

    with pytest.raises(ValidationError) as exc_info:
        message.edit()

    errors = exc_info.value.errors()
    assert any(
        "Can't edit message with ID" in str(e) and "Does not exist" in str(e) for e in errors
    )


def test_edit_message_without_content_succeeds(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that editing a message does not require content."""
    message = Message(
        message_id=str(uuid4()),
        content=None,
        sender_id=str(uuid4()),
        recipient_id=str(uuid4()),
    )

    # Should not raise ValidationError
    effect = message.edit()
    assert effect.type == EffectType.EDIT_MESSAGE


def test_message_with_read_timestamp(
    mock_db_queries: dict[str, MagicMock], valid_message_data: dict[str, Any]
) -> None:
    """Test message with read timestamp."""
    read_time = datetime.now()
    valid_message_data["read"] = read_time
    message = Message(**valid_message_data)
    effect = message.create()

    payload = json.loads(effect.payload)
    assert "read" in payload["data"]


def test_message_sender_patient_recipient_staff(
    mock_db_queries: dict[str, MagicMock], valid_message_data: dict[str, Any]
) -> None:
    """Test message where sender is patient and recipient is staff."""
    sender_id = valid_message_data["sender_id"]
    recipient_id = valid_message_data["recipient_id"]

    def patient_filter_side_effect(id: str) -> MagicMock:
        mock = MagicMock()
        mock.exists.return_value = str(id) == sender_id
        return mock

    def staff_filter_side_effect(id: str) -> MagicMock:
        mock = MagicMock()
        mock.exists.return_value = str(id) == recipient_id
        return mock

    mock_db_queries["patient"].filter.side_effect = patient_filter_side_effect
    mock_db_queries["staff"].filter.side_effect = staff_filter_side_effect

    message = Message(**valid_message_data)
    effect = message.create()

    assert effect.type == EffectType.CREATE_MESSAGE


def test_message_sender_staff_recipient_patient(
    mock_db_queries: dict[str, MagicMock], valid_message_data: dict[str, Any]
) -> None:
    """Test message where sender is staff and recipient is patient."""
    sender_id = valid_message_data["sender_id"]
    recipient_id = valid_message_data["recipient_id"]

    def patient_filter_side_effect(id: str) -> MagicMock:
        mock = MagicMock()
        mock.exists.return_value = str(id) == recipient_id
        return mock

    def staff_filter_side_effect(id: str) -> MagicMock:
        mock = MagicMock()
        mock.exists.return_value = str(id) == sender_id
        return mock

    mock_db_queries["patient"].filter.side_effect = patient_filter_side_effect
    mock_db_queries["staff"].filter.side_effect = staff_filter_side_effect

    message = Message(**valid_message_data)
    effect = message.create()

    assert effect.type == EffectType.CREATE_MESSAGE


def test_message_both_patients(
    mock_db_queries: dict[str, MagicMock], valid_message_data: dict[str, Any]
) -> None:
    """Test message where both sender and recipient are patients."""
    mock_db_queries["patient"].filter.return_value.exists.return_value = True
    mock_db_queries["staff"].filter.return_value.exists.return_value = False

    message = Message(**valid_message_data)
    effect = message.create()

    assert effect.type == EffectType.CREATE_MESSAGE


def test_message_both_staff(
    mock_db_queries: dict[str, MagicMock], valid_message_data: dict[str, Any]
) -> None:
    """Test message where both sender and recipient are staff."""
    mock_db_queries["patient"].filter.return_value.exists.return_value = False
    mock_db_queries["staff"].filter.return_value.exists.return_value = True

    message = Message(**valid_message_data)
    effect = message.create()

    assert effect.type == EffectType.CREATE_MESSAGE
