from datetime import datetime
from enum import Enum
from typing import Optional

from canvas_sdk.data import DataModel
from canvas_sdk.data.patient import Patient
from canvas_sdk.data.staff import Staff
from canvas_sdk.effects import Effect, EffectType


class Task(DataModel):
    class Meta(DataModel.Meta):
        create_required_fields = ("title",)

    class Status(Enum):
        COMPLETED = "Completed"
        CLOSED = "Closed"
        OPEN = "Open"

    id: Optional[str] = None
    assignee: Optional[Staff] = None
    patient: Optional[Patient] = None
    title: Optional[str] = None
    due: Optional[datetime] = None
    status: Optional[Status] = None
    comments: "Optional[list[TaskComment]]" = None
    labels: Optional[list[str]] = None

    def create(self) -> Effect:
        self._validate_before_effect("create")
        return Effect(type=EffectType.CREATE_TASK, payload=self.model_dump_json_nested())

    def update(self) -> Effect:
        self._validate_before_effect("update")
        payload = self.model_dump_json_nested(exclude_unset=True)
        return Effect(type=EffectType.UPDATE_TASK, payload=payload)

    def add_comment(self, comment: str) -> Effect:
        if not self.id:
            raise ValueError("Cannot add a comment to a Task without an id")
        task_comment = TaskComment(task=self, body=comment)
        task_comment._validate_before_effect("create")
        return Effect(
            type=EffectType.CREATE_TASK_COMMENT,
            payload=task_comment.model_dump_json_nested(exclude_unset=True),
        )


class TaskComment(DataModel):
    class Meta:
        create_required_fields = (
            "body",
            "task",
        )

    id: Optional[str] = None
    task: Optional[Task] = None
    body: Optional[str] = None


Task.model_rebuild()
