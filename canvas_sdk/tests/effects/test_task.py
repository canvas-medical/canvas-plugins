import datetime
from typing import Any
from uuid import uuid4

import pytest
from pydantic_core import ValidationError

from canvas_sdk.commands.commands.imaging_order import ImagingOrderCommand
from canvas_sdk.commands.commands.refer import ReferCommand
from canvas_sdk.commands.commands.task import TaskCommand
from canvas_sdk.commands.constants import TaskPriority
from canvas_sdk.effects.task import AddTask, TaskStatus, UpdateTask


@pytest.fixture
def valid_add_task_data() -> dict[str, Any]:
    """Valid data for creating a task."""
    return {
        "title": "Test Task",
        "patient_id": str(uuid4()),
        "assignee_id": str(uuid4()),
        "team_id": str(uuid4()),
        "due": datetime.datetime.now() + datetime.timedelta(days=1),
        "status": TaskStatus.OPEN,
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


@pytest.mark.parametrize(
    "priority,expected_value",
    [
        (TaskPriority.STAT, "stat"),
        (TaskPriority.URGENT, "urgent"),
        (TaskPriority.ROUTINE, "routine"),
    ],
)
def test_add_task_with_priority(
    valid_add_task_data: dict[str, Any], priority: TaskPriority, expected_value: str
) -> None:
    """Test creating a task with different priority levels."""
    valid_add_task_data["priority"] = priority
    
    task = AddTask(**valid_add_task_data)
    values = task.values
    
    assert task.priority == priority
    assert values["priority"] == expected_value
    assert "priority" in values


def test_add_task_without_priority(valid_add_task_data: dict[str, Any]) -> None:
    """Test creating a task without priority field (should default to None)."""
    task = AddTask(**valid_add_task_data)
    values = task.values
    
    assert task.priority is None
    assert values["priority"] is None


@pytest.mark.parametrize(
    "priority,expected_value",
    [
        (TaskPriority.STAT, "stat"),
        (TaskPriority.URGENT, "urgent"),
        (TaskPriority.ROUTINE, "routine"),
    ],
)
def test_update_task_with_priority(
    valid_update_task_data: dict[str, Any], priority: TaskPriority, expected_value: str
) -> None:
    """Test updating a task with different priority levels."""
    valid_update_task_data["priority"] = priority
    
    task = UpdateTask(**valid_update_task_data)
    values = task.values
    
    assert task.priority == priority
    assert values["priority"] == expected_value


def test_update_task_clear_priority(valid_update_task_data: dict[str, Any]) -> None:
    """Test clearing a task's priority by explicitly setting it to None."""
    valid_update_task_data["priority"] = None
    
    task = UpdateTask(**valid_update_task_data)
    values = task.values
    
    assert task.priority is None
    assert values["priority"] is None
    assert "priority" in values  # None should be explicitly included when set


def test_update_task_without_priority(valid_update_task_data: dict[str, Any]) -> None:
    """Test updating a task without changing priority - field should not be in values."""
    task = UpdateTask(**valid_update_task_data)
    values = task.values
    
    # Priority should not be in values if not explicitly set
    assert "priority" not in values


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
    
    # Should NOT contain fields that weren't explicitly set
    assert "status" not in values
    assert "labels" not in values
    assert "assignee" not in values


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


def test_update_task_change_priority_serialization() -> None:
    """Test that different priority values serialize correctly in UpdateTask."""
    task_id = str(uuid4())
    
    # Test ROUTINE priority serialization
    task1 = UpdateTask(id=task_id, priority=TaskPriority.ROUTINE)
    values1 = task1.values
    assert values1["priority"] == "routine"
    
    # Test STAT priority serialization
    task2 = UpdateTask(id=task_id, priority=TaskPriority.STAT)
    values2 = task2.values
    assert values2["priority"] == "stat"


def test_task_priority_enum_values() -> None:
    """Test that TaskPriority enum has correct lowercase string values."""
    assert TaskPriority.STAT.value == "stat"
    assert TaskPriority.URGENT.value == "urgent"
    assert TaskPriority.ROUTINE.value == "routine"


def test_task_priority_enum_members() -> None:
    """Test that TaskPriority enum has exactly 3 members with expected values."""
    priority_values = [p.value for p in TaskPriority]
    assert "stat" in priority_values
    assert "urgent" in priority_values
    assert "routine" in priority_values
    assert len(priority_values) == 3  # Ensures no accidental additions


@pytest.mark.parametrize(
    "priority",
    [TaskPriority.STAT, TaskPriority.URGENT, TaskPriority.ROUTINE, None],
)
def test_task_command_with_priority(priority: TaskPriority | None) -> None:
    """Test that TaskCommand accepts all valid priority values."""
    command = TaskCommand(title="Test Task", priority=priority)
    assert command.priority == priority


def test_task_command_priority_is_optional() -> None:
    """Test that priority is optional in TaskCommand."""
    command = TaskCommand(title="Test Task")
    assert command.priority is None


@pytest.mark.parametrize(
    "priority",
    [TaskPriority.STAT, TaskPriority.URGENT, TaskPriority.ROUTINE, None],
)
def test_refer_command_with_priority(priority: TaskPriority | None) -> None:
    """Test that ReferCommand accepts all valid priority values."""
    command = ReferCommand(priority=priority)
    assert command.priority == priority


def test_refer_command_priority_is_optional() -> None:
    """Test that priority is optional in ReferCommand."""
    command = ReferCommand()
    assert command.priority is None


def test_refer_command_with_full_data_and_priority() -> None:
    """Test ReferCommand with priority and other fields."""
    command = ReferCommand(
        diagnosis_codes=["Z00.00"],
        clinical_question=ReferCommand.ClinicalQuestion.COGNITIVE_ASSISTANCE,
        priority=TaskPriority.URGENT,
        notes_to_specialist="Urgent referral needed",
        comment="Patient needs immediate attention",
    )
    
    assert command.priority == TaskPriority.URGENT
    assert command.diagnosis_codes == ["Z00.00"]
    assert command.clinical_question == ReferCommand.ClinicalQuestion.COGNITIVE_ASSISTANCE
    assert command.notes_to_specialist == "Urgent referral needed"


@pytest.mark.parametrize(
    "priority",
    [TaskPriority.STAT, TaskPriority.URGENT, TaskPriority.ROUTINE, None],
)
def test_imaging_order_command_with_priority(priority: TaskPriority | None) -> None:
    """Test that ImagingOrderCommand accepts all valid priority values."""
    command = ImagingOrderCommand(priority=priority)
    assert command.priority == priority


def test_imaging_order_command_priority_is_optional() -> None:
    """Test that priority is optional in ImagingOrderCommand."""
    command = ImagingOrderCommand()
    assert command.priority is None


def test_imaging_order_command_with_full_data_and_priority() -> None:
    """Test ImagingOrderCommand with priority and other fields."""
    command = ImagingOrderCommand(
        image_code="71010",
        diagnosis_codes=["J18.9"],
        priority=TaskPriority.STAT,
        additional_details="STAT chest X-ray needed",
        comment="Patient showing respiratory distress",
    )
    
    assert command.priority == TaskPriority.STAT
    assert command.image_code == "71010"
    assert command.diagnosis_codes == ["J18.9"]
    assert command.additional_details == "STAT chest X-ray needed"


def test_add_task_and_update_task_priority_workflow() -> None:
    """Test complete workflow: create task with priority, update it, then clear it."""
    task_id = str(uuid4())
    patient_id = str(uuid4())
    
    # Step 1: Create task with ROUTINE priority
    add_task = AddTask(
        id=task_id,
        title="Refill Request",
        patient_id=patient_id,
        priority=TaskPriority.ROUTINE,
    )
    add_values = add_task.values
    
    assert add_values["priority"] == "routine"
    assert add_values["title"] == "Refill Request"
    assert "patient" in add_values
    
    # Step 2: Update task to URGENT priority
    update_task = UpdateTask(
        id=task_id,
        priority=TaskPriority.URGENT,
    )
    update_values = update_task.values
    
    assert update_values["priority"] == "urgent"
    assert "id" in update_values
    
    # Step 3: Clear priority
    clear_task = UpdateTask(
        id=task_id,
        priority=None,
    )
    clear_values = clear_task.values
    
    assert clear_values["priority"] is None
    assert "priority" in clear_values  # Should be explicitly present even when None


def test_command_to_effect_priority_consistency() -> None:
    """Test that priority flows correctly from commands to effects."""
    # TaskCommand with priority
    task_command = TaskCommand(title="Test", priority=TaskPriority.URGENT)
    add_task = AddTask(title="Test", priority=task_command.priority)
    assert add_task.values["priority"] == "urgent"
    
    # ReferCommand with priority
    refer_command = ReferCommand(priority=TaskPriority.STAT)
    add_task_refer = AddTask(title="Refer Task", priority=refer_command.priority)
    assert add_task_refer.values["priority"] == "stat"
    
    # ImagingOrderCommand with priority
    imaging_command = ImagingOrderCommand(priority=TaskPriority.ROUTINE)
    add_task_imaging = AddTask(title="Imaging Task", priority=imaging_command.priority)
    assert add_task_imaging.values["priority"] == "routine"


@pytest.mark.parametrize(
    "invalid_value,description",
    [
        ("none", "string 'none'"),
        ("stat", "string 'stat' instead of enum"),
        ("urgent", "string 'urgent' instead of enum"),
        ("STAT", "uppercase string 'STAT'"),
        (1, "integer 1"),
        (0, "integer 0"),
        ("", "empty string"),
        ("invalid", "invalid string"),
    ],
)
def test_add_task_rejects_invalid_priority(invalid_value: Any, description: str) -> None:
    """Test that AddTask rejects various invalid priority values."""
    with pytest.raises(ValidationError) as exc_info:
        AddTask(title="Test Task", priority=invalid_value)  # type: ignore
    
    errors = exc_info.value.errors()
    # Verify it's a validation error for the priority field
    assert any("priority" in str(e).lower() for e in errors)


@pytest.mark.parametrize(
    "invalid_value",
    ["none", "stat", 1, "", "invalid"],
)
def test_update_task_rejects_invalid_priority(invalid_value: Any) -> None:
    """Test that UpdateTask rejects invalid priority values."""
    with pytest.raises(ValidationError) as exc_info:
        UpdateTask(id=str(uuid4()), priority=invalid_value)  # type: ignore
    
    errors = exc_info.value.errors()
    assert any("priority" in str(e).lower() for e in errors)


def test_task_priority_enum_rejects_invalid_values() -> None:
    """Test that TaskPriority enum constructor rejects invalid string values."""
    with pytest.raises(ValueError) as exc_info:
        TaskPriority("none")
    assert "'none' is not a valid TaskPriority" in str(exc_info.value)
    
    with pytest.raises(ValueError) as exc_info:
        TaskPriority("invalid")
    assert "'invalid' is not a valid TaskPriority" in str(exc_info.value)


def test_task_command_rejects_invalid_priority() -> None:
    """Test that TaskCommand rejects invalid priority values."""
    with pytest.raises(ValidationError):
        TaskCommand(title="Test", priority="stat")  # type: ignore


def test_refer_command_rejects_invalid_priority() -> None:
    """Test that ReferCommand rejects invalid priority values."""
    with pytest.raises(ValidationError):
        ReferCommand(priority="urgent")  # type: ignore


def test_imaging_order_command_rejects_invalid_priority() -> None:
    """Test that ImagingOrderCommand rejects invalid priority values."""
    with pytest.raises(ValidationError):
        ImagingOrderCommand(priority=1)  # type: ignore


def test_priority_only_accepts_enum_or_none() -> None:
    """Test comprehensive validation: only TaskPriority enum or None is accepted."""
    # Valid: TaskPriority enum values
    task1 = AddTask(title="Test", priority=TaskPriority.STAT)
    assert task1.priority == TaskPriority.STAT
    
    task2 = AddTask(title="Test", priority=TaskPriority.URGENT)
    assert task2.priority == TaskPriority.URGENT
    
    task3 = AddTask(title="Test", priority=TaskPriority.ROUTINE)
    assert task3.priority == TaskPriority.ROUTINE
    
    # Valid: None
    task4 = AddTask(title="Test", priority=None)
    assert task4.priority is None
    
    # Invalid: strings (even matching enum values)
    with pytest.raises(ValidationError):
        AddTask(title="Test", priority="stat")  # type: ignore
    
    with pytest.raises(ValidationError):
        AddTask(title="Test", priority="none")  # type: ignore
    
    # Invalid: numbers
    with pytest.raises(ValidationError):
        AddTask(title="Test", priority=1)  # type: ignore
    
    # Invalid: empty string
    with pytest.raises(ValidationError):
        AddTask(title="Test", priority="")  # type: ignore
