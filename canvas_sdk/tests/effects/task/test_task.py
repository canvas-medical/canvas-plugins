import json
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.task import AddTask, LinkedItemType, TaskStatus, UpdateTask


@pytest.fixture
def mock_db_queries() -> Generator[dict[str, MagicMock]]:
    """Mock all database queries to return True/exist by default."""
    with (
        patch("canvas_sdk.v1.data.Patient.objects") as mock_patient,
        patch("canvas_sdk.v1.data.Staff.objects") as mock_staff,
        patch("canvas_sdk.v1.data.Team.objects") as mock_team,
        patch("canvas_sdk.v1.data.Task.objects") as mock_task,
    ):
        # Setup default behaviors
        mock_patient.filter.return_value.exists.return_value = True
        mock_staff.filter.return_value.exists.return_value = True
        mock_team.filter.return_value.exists.return_value = True
        mock_task.filter.return_value.exists.return_value = True

        yield {
            "patient": mock_patient,
            "staff": mock_staff,
            "team": mock_team,
            "task": mock_task,
        }


@pytest.fixture
def valid_add_task_data() -> dict[str, Any]:
    """Valid data for creating a task."""
    return {
        "patient_id": str(uuid4()),
        "title": "Test Task",
        "assignee_id": str(uuid4()),
        "team_id": str(uuid4()),
    }


@pytest.fixture
def valid_update_task_data() -> dict[str, Any]:
    """Valid data for updating a task."""
    return {
        "id": str(uuid4()),
        "title": "Updated Task",
    }


# LinkedItemType enum tests
def test_linked_item_type_enum_values() -> None:
    """Test that LinkedItemType enum has all expected values."""
    expected_values = {
        "COMMAND",
        "NOTE",
        "TASK",
        "CLAIM",
        "PATIENT_ADMINISTRATIVE_DOCUMENT",
        "UNCATEGORIZED_CLINICAL_DOCUMENT",
        "IMAGING_REPORT",
        "REFERRAL_REPORT",
        "LAB_REPORT",
    }
    actual_values = {item.value for item in LinkedItemType}
    assert actual_values == expected_values


def test_linked_item_type_enum_access() -> None:
    """Test that LinkedItemType enum members can be accessed correctly."""
    assert LinkedItemType.COMMAND == "COMMAND"
    assert LinkedItemType.NOTE == "NOTE"
    assert LinkedItemType.TASK == "TASK"
    assert LinkedItemType.CLAIM == "CLAIM"
    assert LinkedItemType.LAB_REPORT == "LAB_REPORT"


# AddTask tests
def test_add_task_basic_creation(
    mock_db_queries: dict[str, MagicMock], valid_add_task_data: dict[str, Any]
) -> None:
    """Test basic task creation without linked items."""
    task = AddTask(**valid_add_task_data)
    effect = task.apply()

    assert effect.type == EffectType.CREATE_TASK
    payload = json.loads(effect.payload)
    assert payload["data"]["title"] == "Test Task"
    assert payload["data"]["status"] == "OPEN"


def test_add_task_requires_title(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that title is required for task creation."""
    task = AddTask(patient_id=str(uuid4()), title=None)
    with pytest.raises(ValidationError) as exc_info:
        task.apply()

    errors = exc_info.value.errors()
    assert any("title" in str(e).lower() for e in errors)


def test_add_task_add_single_linked_item(
    mock_db_queries: dict[str, MagicMock], valid_add_task_data: dict[str, Any]
) -> None:
    """Test adding a single linked item to a task."""
    task = AddTask(**valid_add_task_data)
    lab_report_urn = "base64encodedurn123"
    task.add_linked_item(LinkedItemType.LAB_REPORT, lab_report_urn)

    effect = task.apply()
    payload = json.loads(effect.payload)

    assert "linked_items_urns" in payload["data"]
    assert len(payload["data"]["linked_items_urns"]) == 1
    assert payload["data"]["linked_items_urns"][0] == lab_report_urn


def test_add_task_add_multiple_linked_items(
    mock_db_queries: dict[str, MagicMock], valid_add_task_data: dict[str, Any]
) -> None:
    """Test adding multiple linked items to a task."""
    task = AddTask(**valid_add_task_data)

    lab_report_urn = "base64encodedurn123"
    note_urn = "base64encodedurn456"
    claim_urn = "base64encodedurn789"

    task.add_linked_item(LinkedItemType.LAB_REPORT, lab_report_urn)
    task.add_linked_item(LinkedItemType.NOTE, note_urn)
    task.add_linked_item(LinkedItemType.CLAIM, claim_urn)

    effect = task.apply()
    payload = json.loads(effect.payload)

    assert "linked_items_urns" in payload["data"]
    assert len(payload["data"]["linked_items_urns"]) == 3
    assert lab_report_urn in payload["data"]["linked_items_urns"]
    assert note_urn in payload["data"]["linked_items_urns"]
    assert claim_urn in payload["data"]["linked_items_urns"]


def test_add_task_add_linked_item_returns_self(
    mock_db_queries: dict[str, MagicMock], valid_add_task_data: dict[str, Any]
) -> None:
    """Test that add_linked_item returns self for method chaining."""
    task = AddTask(**valid_add_task_data)
    result = task.add_linked_item(LinkedItemType.NOTE, "urn123")

    assert result is task


def test_add_task_method_chaining_multiple_linked_items(
    mock_db_queries: dict[str, MagicMock], valid_add_task_data: dict[str, Any]
) -> None:
    """Test method chaining with multiple add_linked_item calls."""
    task = AddTask(**valid_add_task_data)

    task.add_linked_item(LinkedItemType.LAB_REPORT, "urn1").add_linked_item(
        LinkedItemType.NOTE, "urn2"
    ).add_linked_item(LinkedItemType.CLAIM, "urn3")

    effect = task.apply()
    payload = json.loads(effect.payload)

    assert len(payload["data"]["linked_items_urns"]) == 3


def test_add_task_linked_items_urns_empty_when_none_added(
    mock_db_queries: dict[str, MagicMock], valid_add_task_data: dict[str, Any]
) -> None:
    """Test that linked_items_urns is an empty list when no items are added."""
    task = AddTask(**valid_add_task_data)
    effect = task.apply()
    payload = json.loads(effect.payload)

    assert "linked_items_urns" in payload["data"]
    assert payload["data"]["linked_items_urns"] == []


def test_add_task_with_all_linked_item_types(
    mock_db_queries: dict[str, MagicMock], valid_add_task_data: dict[str, Any]
) -> None:
    """Test adding linked items of all supported types."""
    task = AddTask(**valid_add_task_data)

    urns = [f"urn_{i}" for i in range(len(LinkedItemType))]
    for item_type, urn in zip(LinkedItemType, urns, strict=False):
        task.add_linked_item(item_type, urn)

    effect = task.apply()
    payload = json.loads(effect.payload)

    assert len(payload["data"]["linked_items_urns"]) == len(LinkedItemType)
    for urn in urns:
        assert urn in payload["data"]["linked_items_urns"]


# UpdateTask tests
def test_update_task_basic_update(
    mock_db_queries: dict[str, MagicMock], valid_update_task_data: dict[str, Any]
) -> None:
    """Test basic task update without linked items."""
    task = UpdateTask(**valid_update_task_data)
    effect = task.apply()

    assert effect.type == EffectType.UPDATE_TASK
    payload = json.loads(effect.payload)
    assert payload["data"]["title"] == "Updated Task"


def test_update_task_requires_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that id is required for task update."""
    task = UpdateTask(id=None, title="Test")
    with pytest.raises(ValidationError) as exc_info:
        task.apply()

    errors = exc_info.value.errors()
    assert any("id" in str(e).lower() for e in errors)


def test_update_task_add_single_linked_item(
    mock_db_queries: dict[str, MagicMock], valid_update_task_data: dict[str, Any]
) -> None:
    """Test adding a single linked item to an existing task."""
    task = UpdateTask(**valid_update_task_data)
    claim_urn = "base64encodedurn999"
    task.add_linked_item(LinkedItemType.CLAIM, claim_urn)

    effect = task.apply()
    payload = json.loads(effect.payload)

    assert "linked_items_urns" in payload["data"]
    assert len(payload["data"]["linked_items_urns"]) == 1
    assert payload["data"]["linked_items_urns"][0] == claim_urn


def test_update_task_add_multiple_linked_items(
    mock_db_queries: dict[str, MagicMock], valid_update_task_data: dict[str, Any]
) -> None:
    """Test adding multiple linked items when updating a task."""
    task = UpdateTask(**valid_update_task_data)

    command_urn = "command_urn_123"
    task_urn = "task_urn_456"

    task.add_linked_item(LinkedItemType.COMMAND, command_urn)
    task.add_linked_item(LinkedItemType.TASK, task_urn)

    effect = task.apply()
    payload = json.loads(effect.payload)

    assert len(payload["data"]["linked_items_urns"]) == 2
    assert command_urn in payload["data"]["linked_items_urns"]
    assert task_urn in payload["data"]["linked_items_urns"]


def test_update_task_add_linked_item_returns_self(
    mock_db_queries: dict[str, MagicMock], valid_update_task_data: dict[str, Any]
) -> None:
    """Test that add_linked_item returns self for method chaining on UpdateTask."""
    task = UpdateTask(**valid_update_task_data)
    result = task.add_linked_item(LinkedItemType.NOTE, "urn123")

    assert result is task


def test_update_task_method_chaining_multiple_linked_items(
    mock_db_queries: dict[str, MagicMock], valid_update_task_data: dict[str, Any]
) -> None:
    """Test method chaining with multiple add_linked_item calls on UpdateTask."""
    task = UpdateTask(**valid_update_task_data)

    task.add_linked_item(LinkedItemType.IMAGING_REPORT, "img_urn1").add_linked_item(
        LinkedItemType.REFERRAL_REPORT, "ref_urn2"
    )

    effect = task.apply()
    payload = json.loads(effect.payload)

    assert len(payload["data"]["linked_items_urns"]) == 2


def test_update_task_no_linked_items_urns_when_none_added(
    mock_db_queries: dict[str, MagicMock], valid_update_task_data: dict[str, Any]
) -> None:
    """Test that linked_items_urns is not included when no items are added to UpdateTask."""
    task = UpdateTask(**valid_update_task_data)
    effect = task.apply()
    payload = json.loads(effect.payload)

    # UpdateTask uses exclude_unset, so linked_items_urns should not be in payload if not set
    assert "linked_items_urns" not in payload["data"]


def test_update_task_only_includes_set_fields(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that UpdateTask only includes explicitly set fields."""
    task_id = str(uuid4())
    task = UpdateTask(id=task_id, status=TaskStatus.COMPLETED)

    effect = task.apply()
    payload = json.loads(effect.payload)

    # Should only include id and status, not other optional fields
    assert "id" in payload["data"]
    assert "status" in payload["data"]
    assert payload["data"]["status"] == "COMPLETED"
    # These should not be present since they weren't set
    assert "title" not in payload["data"]
    assert "assignee" not in payload["data"]


def test_update_task_with_linked_items_and_other_fields(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test UpdateTask with both linked items and other field updates."""
    task_id = str(uuid4())
    task = UpdateTask(id=task_id, title="New Title", status=TaskStatus.OPEN)

    task.add_linked_item(LinkedItemType.NOTE, "note_urn_123")

    effect = task.apply()
    payload = json.loads(effect.payload)

    assert payload["data"]["title"] == "New Title"
    assert payload["data"]["status"] == "OPEN"
    assert "linked_items_urns" in payload["data"]
    assert payload["data"]["linked_items_urns"] == ["note_urn_123"]


# Legacy linked_object compatibility tests
def test_add_task_legacy_linked_object_still_works(
    mock_db_queries: dict[str, MagicMock], valid_add_task_data: dict[str, Any]
) -> None:
    """Test that legacy linked_object_id and linked_object_type still work."""
    referral_id = str(uuid4())
    task = AddTask(
        **valid_add_task_data,
        linked_object_id=referral_id,
        linked_object_type=AddTask.LinkableObjectType.REFERRAL,
    )

    effect = task.apply()
    payload = json.loads(effect.payload)

    assert "linked_object" in payload["data"]
    assert payload["data"]["linked_object"]["id"] == referral_id
    assert payload["data"]["linked_object"]["type"] == "REFERRAL"


def test_add_task_can_use_both_linked_object_and_linked_items(
    mock_db_queries: dict[str, MagicMock], valid_add_task_data: dict[str, Any]
) -> None:
    """Test that both legacy linked_object and new linked_items can coexist."""
    referral_id = str(uuid4())
    note_urn = "note_urn_123"

    task = AddTask(
        **valid_add_task_data,
        linked_object_id=referral_id,
        linked_object_type=AddTask.LinkableObjectType.REFERRAL,
    )
    task.add_linked_item(LinkedItemType.NOTE, note_urn)

    effect = task.apply()
    payload = json.loads(effect.payload)

    # Both should be present
    assert "linked_object" in payload["data"]
    assert payload["data"]["linked_object"]["id"] == referral_id
    assert "linked_items_urns" in payload["data"]
    assert note_urn in payload["data"]["linked_items_urns"]
