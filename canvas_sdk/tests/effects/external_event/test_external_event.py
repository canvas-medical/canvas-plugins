import json
from collections.abc import Generator
from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from pydantic_core import ValidationError

from canvas_sdk.effects.external_event.external_event import ExternalEvent


@pytest.fixture
def mock_db_queries() -> Generator[dict[str, MagicMock], None, None]:
    """Mock all database queries to return True/exist by default."""
    with patch(
        "canvas_sdk.effects.external_event.external_event.ExternalEventModel.objects"
    ) as mock_event:
        # Setup default behaviors - objects exist
        mock_event.filter.return_value.exists.return_value = True

        yield {
            "external_event": mock_event,
        }


@pytest.fixture
def valid_create_data() -> dict[str, Any]:
    """Valid data for creating an ExternalEvent."""
    return {
        "patient_id": "patient-123",
        "visit_identifier": "visit-456",
        "message_control_id": "msg-789",
        "event_type": "ADT^A01",
    }


@pytest.fixture
def valid_create_data_with_optional() -> dict[str, Any]:
    """Valid data with all optional fields."""
    return {
        "patient_id": "patient-123",
        "visit_identifier": "visit-456",
        "message_control_id": "msg-789",
        "event_type": "ADT^A01",
        "event_datetime": datetime(2024, 3, 15, 10, 30, 0),
        "event_cancelation_datetime": datetime(2024, 3, 16, 14, 0, 0),
        "message_datetime": datetime(2024, 3, 15, 10, 25, 0),
        "information_source": "Test Hospital",
        "facility_name": "Main Building",
        "raw_message": "MSH|^~\\&|TEST|...",
    }


# Create Tests


@patch("canvas_sdk.effects.external_event.external_event.Effect")
def test_create_external_event_success(
    mock_effect: MagicMock,
    valid_create_data: dict[str, Any],
) -> None:
    """Test that create() generates correct effect."""
    external_event = ExternalEvent(**valid_create_data)

    external_event.create()

    mock_effect.assert_called_once()
    call_args = mock_effect.call_args
    assert call_args.kwargs["type"] == "CREATE_EXTERNAL_EVENT"

    payload_data = json.loads(call_args.kwargs["payload"])
    assert payload_data["data"]["patient_id"] == "patient-123"
    assert payload_data["data"]["visit_identifier"] == "visit-456"
    assert payload_data["data"]["message_control_id"] == "msg-789"
    assert payload_data["data"]["event_type"] == "ADT^A01"


@patch("canvas_sdk.effects.external_event.external_event.Effect")
def test_create_external_event_with_optional_fields(
    mock_effect: MagicMock,
    valid_create_data_with_optional: dict[str, Any],
) -> None:
    """Test that create() includes optional fields in the payload."""
    external_event = ExternalEvent(**valid_create_data_with_optional)

    external_event.create()

    mock_effect.assert_called_once()
    call_args = mock_effect.call_args
    assert call_args.kwargs["type"] == "CREATE_EXTERNAL_EVENT"

    payload_data = json.loads(call_args.kwargs["payload"])
    assert payload_data["data"]["patient_id"] == "patient-123"
    assert payload_data["data"]["information_source"] == "Test Hospital"
    assert payload_data["data"]["facility_name"] == "Main Building"
    assert payload_data["data"]["raw_message"] == "MSH|^~\\&|TEST|..."
    assert payload_data["data"]["event_datetime"] is not None
    assert payload_data["data"]["event_cancelation_datetime"] is not None
    assert payload_data["data"]["message_datetime"] is not None


def test_create_validation_fails_with_external_event_id(
    valid_create_data: dict[str, Any],
) -> None:
    """Test that create validation fails when external_event_id is provided."""
    external_event = ExternalEvent(
        external_event_id="event-123",
        **valid_create_data,
    )

    with pytest.raises(ValidationError):
        external_event.create()


def test_create_validation_fails_without_patient_id() -> None:
    """Test that create validation fails when patient_id is missing."""
    external_event = ExternalEvent(
        visit_identifier="visit-456",
        message_control_id="msg-789",
        event_type="ADT^A01",
    )

    with pytest.raises(ValidationError):
        external_event.create()


def test_create_validation_fails_without_visit_identifier() -> None:
    """Test that create validation fails when visit_identifier is missing."""
    external_event = ExternalEvent(
        patient_id="patient-123",
        message_control_id="msg-789",
        event_type="ADT^A01",
    )

    with pytest.raises(ValidationError):
        external_event.create()


def test_create_validation_fails_without_message_control_id() -> None:
    """Test that create validation fails when message_control_id is missing."""
    external_event = ExternalEvent(
        patient_id="patient-123",
        visit_identifier="visit-456",
        event_type="ADT^A01",
    )

    with pytest.raises(ValidationError):
        external_event.create()


def test_create_validation_fails_without_event_type() -> None:
    """Test that create validation fails when event_type is missing."""
    external_event = ExternalEvent(
        patient_id="patient-123",
        visit_identifier="visit-456",
        message_control_id="msg-789",
    )

    with pytest.raises(ValidationError):
        external_event.create()


# Update Tests


@patch("canvas_sdk.effects.external_event.external_event.Effect")
def test_update_external_event_success(
    mock_effect: MagicMock,
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that update() generates correct effect."""
    external_event = ExternalEvent(
        external_event_id="event-123",
        event_type="ADT^A03",
    )

    external_event.update()

    mock_effect.assert_called_once()
    call_args = mock_effect.call_args
    assert call_args.kwargs["type"] == "UPDATE_EXTERNAL_EVENT"

    payload_data = json.loads(call_args.kwargs["payload"])
    assert payload_data["data"]["external_event_id"] == "event-123"
    assert payload_data["data"]["event_type"] == "ADT^A03"


@patch("canvas_sdk.effects.external_event.external_event.Effect")
def test_update_external_event_with_cancelation(
    mock_effect: MagicMock,
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that update() includes cancelation datetime in the payload."""
    cancelation_time = datetime(2024, 4, 15, 14, 30, 0)
    external_event = ExternalEvent(
        external_event_id="event-123",
        event_cancelation_datetime=cancelation_time,
    )

    external_event.update()

    mock_effect.assert_called_once()
    call_args = mock_effect.call_args

    payload_data = json.loads(call_args.kwargs["payload"])
    assert payload_data["data"]["external_event_id"] == "event-123"
    assert payload_data["data"]["event_cancelation_datetime"] is not None


@patch("canvas_sdk.effects.external_event.external_event.Effect")
def test_update_only_includes_dirty_fields(
    mock_effect: MagicMock,
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that update() only includes fields that were set."""
    external_event = ExternalEvent(
        external_event_id="event-123",
        raw_message="Updated message",
    )

    external_event.update()

    mock_effect.assert_called_once()
    call_args = mock_effect.call_args

    payload_data = json.loads(call_args.kwargs["payload"])
    assert payload_data["data"]["external_event_id"] == "event-123"
    assert payload_data["data"]["raw_message"] == "Updated message"
    # These should not be in the payload since they weren't set
    assert "patient_id" not in payload_data["data"]
    assert "visit_identifier" not in payload_data["data"]
    assert "event_type" not in payload_data["data"]


def test_update_validation_fails_without_external_event_id(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that update validation fails when external_event_id is missing."""
    external_event = ExternalEvent(
        event_type="ADT^A03",
    )

    with pytest.raises(ValidationError):
        external_event.update()


def test_update_validation_fails_with_nonexistent_event(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that update validation fails when external event doesn't exist."""
    mock_db_queries["external_event"].filter.return_value.exists.return_value = False

    external_event = ExternalEvent(
        external_event_id="nonexistent-event",
        event_type="ADT^A03",
    )

    with pytest.raises(ValidationError):
        external_event.update()


# Values Tests


def test_values_includes_all_set_fields(
    valid_create_data_with_optional: dict[str, Any],
) -> None:
    """Test that values property includes all fields that were set."""
    external_event = ExternalEvent(**valid_create_data_with_optional)
    values = external_event.values

    assert "patient_id" in values
    assert "visit_identifier" in values
    assert "message_control_id" in values
    assert "event_type" in values
    assert "event_datetime" in values
    assert "information_source" in values
    assert "facility_name" in values
    assert "raw_message" in values


def test_values_excludes_unset_fields() -> None:
    """Test that values property excludes fields that were not set."""
    external_event = ExternalEvent(
        patient_id="patient-123",
        visit_identifier="visit-456",
        message_control_id="msg-789",
        event_type="ADT^A01",
    )
    values = external_event.values

    assert "patient_id" in values
    assert "visit_identifier" in values
    assert "message_control_id" in values
    assert "event_type" in values
    # Optional fields should not be in values if not set
    assert "information_source" not in values
    assert "facility_name" not in values
    assert "raw_message" not in values


def test_datetime_values_serialized_as_iso_format(
    valid_create_data_with_optional: dict[str, Any],
) -> None:
    """Test that datetime values are serialized as ISO format strings."""
    external_event = ExternalEvent(**valid_create_data_with_optional)
    values = external_event.values

    # The values should be ISO format strings, not datetime objects
    assert isinstance(values["event_datetime"], str)
    assert isinstance(values["event_cancelation_datetime"], str)
    assert isinstance(values["message_datetime"], str)


# Meta Class Tests


def test_effect_type_is_external_event() -> None:
    """Test that Meta.effect_type is set correctly."""
    assert ExternalEvent.Meta.effect_type == "EXTERNAL_EVENT"


# UUID Tests


def test_external_event_id_accepts_string() -> None:
    """Test that external_event_id accepts a string."""
    external_event = ExternalEvent(
        external_event_id="abc-123-def",
        event_type="ADT^A03",
    )
    assert external_event.external_event_id == "abc-123-def"


def test_external_event_id_accepts_uuid() -> None:
    """Test that external_event_id accepts a UUID."""
    from uuid import UUID

    uuid_val = UUID("12345678-1234-5678-1234-567812345678")
    external_event = ExternalEvent(
        external_event_id=uuid_val,
        event_type="ADT^A03",
    )
    assert external_event.external_event_id == uuid_val


def test_create_external_event_with_delay_seconds(
    valid_create_data: dict[str, Any],
) -> None:
    """Test that create(delay_seconds=60) sets the field on the Effect."""
    external_event = ExternalEvent(**valid_create_data)
    effect = external_event.create(delay_seconds=60)
    assert effect.HasField("delay_seconds")
    assert effect.delay_seconds == 60


def test_create_external_event_without_delay_seconds(
    valid_create_data: dict[str, Any],
) -> None:
    """Test that create() without delay_seconds does not set the field."""
    external_event = ExternalEvent(**valid_create_data)
    effect = external_event.create()
    assert not effect.HasField("delay_seconds")


def test_update_external_event_with_delay_seconds(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that update(delay_seconds=30) sets the field on the Effect."""
    external_event = ExternalEvent(
        external_event_id="event-123",
        event_type="ADT^A03",
    )
    effect = external_event.update(delay_seconds=30)
    assert effect.HasField("delay_seconds")
    assert effect.delay_seconds == 30
