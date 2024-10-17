from datetime import datetime
from enum import Enum

from canvas_sdk.data import DataModel
from canvas_sdk.data.patient import Patient
from canvas_sdk.data.staff import Staff
from canvas_sdk.effects import Effect, EffectType


class Task(DataModel):
    """Data model for a task."""

    class Meta(DataModel.Meta):
        create_required_fields = ("title",)

    class Status(Enum):
        COMPLETED = "Completed"
        CLOSED = "Closed"
        OPEN = "Open"

    id: str | None = None
    assignee: Staff | None = None
    patient: Patient | None = None
    title: str | None = None
    due: datetime | None = None
    status: Status | None = None
    comments: "list[TaskComment] | None" = None
    labels: list[str] | None = None

    def create(self) -> Effect:
        """Return an effect to create the task."""
        self._validate_before_effect("create")
        return Effect(type=EffectType.CREATE_TASK, payload=self.model_dump_json_nested())

    def update(self) -> Effect:
        """Return an effect to update the task."""
        self._validate_before_effect("update")
        payload = self.model_dump_json_nested(exclude_unset=True)
        return Effect(type=EffectType.UPDATE_TASK, payload=payload)

    def add_comment(self, comment: str) -> Effect:
        """Return an effect to add a comment to the task."""
        if not self.id:
            raise ValueError("Cannot add a comment to a Task without an id")
        task_comment = TaskComment(task=self, body=comment)
        task_comment._validate_before_effect("create")
        return Effect(
            type=EffectType.CREATE_TASK_COMMENT,
            payload=task_comment.model_dump_json_nested(exclude_unset=True),
        )


class TaskComment(DataModel):
    """Data model for a task comment."""

    class Meta:
        create_required_fields = (
            "body",
            "task",
        )

    id: str | None = None
    task: Task | None = None
    body: str | None = None


Task.model_rebuild()
