from datetime import datetime
from enum import Enum
from typing import Any, cast

from canvas_sdk.effects.base import EffectType, _BaseEffect


class TaskStatus(Enum):
    """TaskStatus."""

    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"
    OPEN = "OPEN"


class AddTask(_BaseEffect):
    """
    An Effect that will create a Task in Canvas.
    """

    class Meta:
        effect_type = EffectType.CREATE_TASK
        apply_required_fields = ("title",)

    assignee_id: str | None = None
    team_id: str | None = None
    patient_id: str | None = None
    title: str | None = None
    due: datetime | None = None
    status: TaskStatus = TaskStatus.OPEN
    labels: list[str] = []

    @property
    def values(self) -> dict[str, Any]:
        """The values for Task addition."""
        return {
            "patient": {"id": self.patient_id},
            "due": self.due.isoformat() if self.due else None,
            "assignee": {"id": self.assignee_id},
            "team": {"id": self.team_id},
            "title": self.title,
            "status": self.status.value,
            "labels": self.labels,
        }


class AddTaskComment(_BaseEffect):
    """
    An Effect that will create a Task Comment on a Task.
    """

    class Meta:
        effect_type = EffectType.CREATE_TASK_COMMENT
        apply_required_fields = (
            "body",
            "task_id",
        )

    body: str | None = None
    task_id: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The values for adding a task comment."""
        return {"task": {"id": self.task_id}, "body": self.body}


class UpdateTask(_BaseEffect):
    """
    An Effect that will update a Task in Canvas.
    """

    class Meta:
        effect_type = EffectType.UPDATE_TASK
        apply_required_fields = ("id",)

    id: str | None = None
    assignee_id: str | None = None
    team_id: str | None = None
    patient_id: str | None = None
    title: str | None = None
    due: datetime | None = None
    status: TaskStatus = TaskStatus.OPEN
    labels: list[str] = []

    @property
    def values(self) -> dict[str, Any]:
        """The values for adding a task comment."""
        value_dict: dict[str, Any] = {}
        # Only add the fields that have been explicitly set on the model (exclude_unset=True).
        # Oherwise, the effect interpreter will set values to null based on their defaults.
        set_fields = self.model_dump(exclude_unset=True)
        for field, val in set_fields.items():
            if field.endswith("_id"):
                value_dict[field.split("_")[0]] = {"id": val}
            elif field == "due" and val is not None:
                value_dict[field] = cast(datetime, val).isoformat()
            elif field == "status":
                value_dict[field] = cast(TaskStatus, val).value
            else:
                value_dict[field] = getattr(self, field)
        return value_dict


__exports__ = (
    "AddTask",
    "AddTaskComment",
    "TaskStatus",
    "UpdateTask",
)
