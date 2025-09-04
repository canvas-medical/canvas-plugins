from datetime import datetime
from enum import Enum, StrEnum
from typing import Any, Self, cast
from uuid import UUID

from pydantic import model_validator

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

    class LinkableObjectType(StrEnum):
        """Types of objects that can be linked to a Task."""

        REFERRAL = "REFERRAL"
        IMAGING = "IMAGING"

    class Meta:
        effect_type = EffectType.CREATE_TASK
        apply_required_fields = ("title",)

    id: str | UUID | None = None
    assignee_id: str | None = None
    team_id: str | None = None
    patient_id: str | None = None
    title: str | None = None
    due: datetime | None = None
    status: TaskStatus = TaskStatus.OPEN
    labels: list[str] = []
    linked_object_id: str | UUID | None = None
    linked_object_type: LinkableObjectType | None = None
    author_id: str | UUID | None = None

    @model_validator(mode="after")
    def check_needed_together_fields(self) -> Self:
        """Check that linked_object_id and linked_object_type are set together."""
        if self.linked_object_id is not None and self.linked_object_type is None:
            raise ValueError(
                "'linked_object_id' must be set with 'linked_object_type' if it is provided"
            )
        if self.linked_object_id is None and self.linked_object_type is not None:
            raise ValueError(
                "'linked_object_type' must be set with 'linked_object_id' if it is provided"
            )

        return self

    @property
    def values(self) -> dict[str, Any]:
        """The values for Task addition."""
        return {
            "id": str(self.id) if self.id else None,
            "patient": {"id": self.patient_id},
            "due": self.due.isoformat() if self.due else None,
            "assignee": {"id": self.assignee_id},
            "team": {"id": self.team_id},
            "title": self.title,
            "status": self.status.value,
            "labels": self.labels,
            "author_id": str(self.author_id) if self.author_id else None,
            "linked_object": {
                "id": str(self.linked_object_id) if self.linked_object_id else None,
                "type": self.linked_object_type.value if self.linked_object_type else None,
            },
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
    task_id: str | UUID | None = None
    author_id: str | UUID | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The values for adding a task comment."""
        return {
            "task": {"id": str(self.task_id) if self.task_id else None},
            "body": self.body,
            "author_id": str(self.author_id) if self.author_id else None,
        }


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
