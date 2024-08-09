from typing import cast

from pydantic import computed_field

from datetime import datetime
from enum import Enum
from typing import Self

from canvas_sdk.data import DataModel
from canvas_sdk.data.patient import Patient
from canvas_sdk.data.staff import Staff
from canvas_sdk.data.team import Team
from canvas_sdk.effects import Effect, EffectType

from .data_access_layer_client import DAL_CLIENT

from logger import log


class Task(DataModel):
    class Meta(DataModel.Meta):
        create_required_fields = ("title",)

    class Status(Enum):
        COMPLETED = "COMPLETED"
        CLOSED = "CLOSED"
        OPEN = "OPEN"

    id: str | None = None
    assignee: Staff | None = None
    patient: Patient | None = None
    title: str | None = None
    due: datetime | None = None
    status: Status | None = None
    created: datetime | None = None
    modified: datetime | None = None
    team: Team | None = None
    task_type: str | None = None
    creator: Staff | None = None

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

    # @computed_field
    @property
    def labels(self) -> list[str] | None:
        task_labels = DAL_CLIENT.get_task_labels(str(self.id))
        # TODO - is there a better way to convert this RepeatedScalarContainer to a list?
        return [l for l in task_labels.labels]

    # @computed_field
    @property
    def comments(self) -> list["TaskComment"] | None:
        task_comments = DAL_CLIENT.get_task_comments(cast(str, self.id))
        return [t for t in task_comments.comments]

    @classmethod
    def get(cls, id: str) -> Self:
        """Given an ID, get the Task from the Data Access Layer."""
        task = DAL_CLIENT.get_task(id)
        return cls.from_grpc(task)

    @classmethod
    def from_grpc(cls, grpc_task) -> Self:
        return cls(
            id=str(grpc_task.id),
            title=grpc_task.title,
            status=Task.Status(grpc_task.status),
            assignee=Staff(id=grpc_task.assignee.id),
            patient=Patient(id=grpc_task.patient.id),
            due=datetime.fromisoformat(grpc_task.due),
            created=datetime.fromisoformat(grpc_task.created),
            modified=datetime.fromisoformat(grpc_task.modified),
            team=Team(id=grpc_task.team.id),
            task_type=grpc_task.task_type,
            creator=Staff(id=grpc_task.creator.id)
        )


class TaskComment(DataModel):
    class Meta:
        create_required_fields = (
            "body",
            "task",
        )

    id: str | None = None
    task: Task | None = None
    body: str | None = None
    created: datetime | None = None
    modified: datetime | None = None


Task.model_rebuild()
