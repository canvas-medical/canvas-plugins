import datetime
import json
from typing import Any
from uuid import UUID, uuid4

import pytest
from pydantic_core import ValidationError

from canvas_sdk.effects.task import AddTask, TaskStatus, UpdateTask
from canvas_sdk.test_utils.factories import NoteFactory, PatientFactory
from canvas_sdk.v1.data.task import TaskPriority


@pytest.fixture
def valid_add_task_data() -> dict[str, Any]:
    """Valid data for creating a task."""
    return {
        "title": "Test Task",
        "patient_id": str(uuid4()),
        "assignee_id": str(uuid4()),
        "team_id": str(uuid4()),
        "due": datetime.datetime.now() + datetime.timedelta(days=1),
    }


@pytest.fixture
def valid_update_task_data() -> dict[str, Any]:
    """Valid data for updating a task."""
    return {
        "id": str(uuid4()),
        "title": "Updated Task",
    }


def test_add_task_basic_success(valid_add_task_data: dict[str, Any]) -> None:
    """Test successful task creation with basic fields."""
    task = AddTask(**valid_add_task_data)
    values = task.values

    assert task.title == valid_add_task_data["title"]
    assert task.patient_id == valid_add_task_data["patient_id"]
    assert task.status == TaskStatus.OPEN
    assert values["title"] == valid_add_task_data["title"]
    assert values["status"] == "OPEN"
    assert values["priority"] is None
    assert values["linked_note_ids"] == []


def test_add_task_with_linked_note_ids(valid_add_task_data: dict[str, Any]) -> None:
    """Test that linked_note_ids are serialized as strings in the effect values."""
    note_ids: list[str | UUID] = [uuid4(), str(uuid4())]
    task = AddTask(**valid_add_task_data, linked_note_ids=note_ids)

    assert task.values["linked_note_ids"] == [str(note_id) for note_id in note_ids]


def test_add_task_rejects_more_than_five_linked_note_ids(
    valid_add_task_data: dict[str, Any],
) -> None:
    """Test that AddTask rejects more than five linked notes."""
    with pytest.raises(ValidationError) as exc_info:
        AddTask(**valid_add_task_data, linked_note_ids=[str(uuid4()) for _ in range(6)])

    assert any("linked_note_ids" in str(e["loc"]) for e in exc_info.value.errors())


@pytest.mark.parametrize("patient_id", [None, ""])
def test_add_task_apply_requires_patient_id_with_linked_note_ids(
    valid_add_task_data: dict[str, Any], patient_id: str | None
) -> None:
    """Test that apply() requires a patient_id when linked_note_ids is set."""
    valid_add_task_data["patient_id"] = patient_id
    task = AddTask(**valid_add_task_data, linked_note_ids=[str(uuid4())])

    with pytest.raises(ValidationError) as exc_info:
        task.apply()

    assert "'patient_id' is required when 'linked_note_ids' is provided" in str(exc_info.value)


def test_add_task_accepts_linked_note_ids_before_patient_id(
    valid_add_task_data: dict[str, Any],
) -> None:
    """Test that linked_note_ids can be assigned before patient_id."""
    patient_id = valid_add_task_data.pop("patient_id")
    task = AddTask(**valid_add_task_data)

    task.linked_note_ids = [str(uuid4())]
    task.patient_id = patient_id

    assert task.patient_id == patient_id


def test_add_task_apply_rejects_malformed_linked_note_id(
    valid_add_task_data: dict[str, Any],
) -> None:
    """Test that apply() rejects a linked note id that is not a UUID."""
    task = AddTask(**valid_add_task_data, linked_note_ids=["not-a-uuid"])

    with pytest.raises(ValidationError) as exc_info:
        task.apply()

    assert "Linked note id not-a-uuid is not a valid UUID" in str(exc_info.value)


@pytest.mark.django_db
def test_add_task_apply_accepts_notes_of_the_task_patient() -> None:
    """Test that apply() accepts notes that belong to the task's patient."""
    patient = PatientFactory.create()
    notes = [NoteFactory.create(patient=patient), NoteFactory.create(patient=patient)]
    note_ids: list[str | UUID] = [str(note.id) for note in notes]

    effect = AddTask(title="Review notes", patient_id=patient.id, linked_note_ids=note_ids).apply()

    assert json.loads(effect.payload)["data"]["linked_note_ids"] == note_ids


@pytest.mark.django_db
def test_add_task_apply_rejects_note_of_another_patient() -> None:
    """Test that apply() rejects an existing note that belongs to a different patient."""
    patient = PatientFactory.create()
    other_patient_note = NoteFactory.create()
    task = AddTask(
        title="Review note", patient_id=patient.id, linked_note_ids=[str(other_patient_note.id)]
    )

    with pytest.raises(ValidationError) as exc_info:
        task.apply()

    assert f"Note {other_patient_note.id} is not associated with the task's patient" in str(
        exc_info.value
    )


@pytest.mark.django_db
def test_add_task_apply_accepts_note_id_with_no_note_yet() -> None:
    """Test that apply() accepts an id with no note, such as a note created in the same batch."""
    patient = PatientFactory.create()
    note_id = str(uuid4())

    effect = AddTask(title="Review note", patient_id=patient.id, linked_note_ids=[note_id]).apply()

    assert json.loads(effect.payload)["data"]["linked_note_ids"] == [note_id]


@pytest.mark.parametrize(
    "priority,expected_value",
    [
        (TaskPriority.STAT, "stat"),
        (TaskPriority.URGENT, "urgent"),
        (TaskPriority.ROUTINE, "routine"),
        (None, None),
    ],
)
def test_add_and_update_task_with_priority(
    valid_add_task_data: dict[str, Any], priority: TaskPriority, expected_value: str
) -> None:
    """Test creating and updating a task with different priority levels."""
    valid_add_task_data["priority"] = priority

    add_task = AddTask(**valid_add_task_data)
    add_values = add_task.values
    assert add_task.priority == priority
    assert "priority" in add_values
    assert add_values["priority"] == expected_value

    update_task = UpdateTask(id=str(add_task.id), priority=priority)
    update_values = update_task.values
    assert update_task.priority == priority
    assert "priority" in update_values
    assert update_values["priority"] == expected_value


def test_update_task_only_includes_set_fields(valid_update_task_data: dict[str, Any]) -> None:
    """Test that UpdateTask.values only includes explicitly set fields."""
    task = UpdateTask(
        id=valid_update_task_data["id"],
        title="New Title",
        priority=TaskPriority.URGENT,
    )
    values = task.values

    # Should only contain id, title, and priority
    assert set(values.keys()) == {"id", "title", "priority"}
    assert values["title"] == "New Title"
    assert values["priority"] == "urgent"


def test_update_task_multiple_fields_with_priority(valid_update_task_data: dict[str, Any]) -> None:
    """Test updating multiple fields including priority."""
    task = UpdateTask(
        id=valid_update_task_data["id"],
        title="Updated Title",
        priority=TaskPriority.STAT,
        status=TaskStatus.COMPLETED,
        labels=["completed", "reviewed"],
    )
    values = task.values

    assert "id" in values
    assert values["id"] == valid_update_task_data["id"]
    assert values["title"] == "Updated Title"
    assert values["priority"] == "stat"
    assert values["status"] == "COMPLETED"
    assert values["labels"] == ["completed", "reviewed"]


@pytest.mark.parametrize(
    "task_cls,invalid_value",
    [
        (AddTask, "none"),
        (AddTask, "stat"),
        (AddTask, 1),
        (AddTask, ""),
        (AddTask, "invalid"),
        (UpdateTask, "none"),
        (UpdateTask, "stat"),
        (UpdateTask, 1),
        (UpdateTask, ""),
        (UpdateTask, "invalid"),
    ],
)
def test_task_effects_reject_invalid_priority(task_cls: type, invalid_value: Any) -> None:
    """Test that AddTask and UpdateTask reject invalid priority values."""
    with pytest.raises(ValidationError) as exc_info:
        task_cls(id=str(uuid4()), priority=invalid_value)

    errors = exc_info.value.errors()
    assert any("priority" in str(e).lower() for e in errors)


def test_update_task_clears_priority_explicitly() -> None:
    """Test that UpdateTask can explicitly clear priority by setting it to None."""
    task = UpdateTask(id=str(uuid4()), priority=None)
    values = task.values

    assert task.priority is None
    assert "priority" in values
    assert values["priority"] is None
