from django.contrib.postgres.fields import ArrayField
from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, Model
from canvas_sdk.v1.data.common import ColorEnum, Origin


class TaskType(models.TextChoices):
    """Choices for task types."""

    TASK = "T", "Task"
    REMINDER = "R", "Reminder"


class EventType(models.TextChoices):
    """Choices for event types."""

    EVENT_CHART_OPEN = "CHART_OPEN", "Chart Open"


class TaskStatus(models.TextChoices):
    """Choices for task statuses."""

    COMPLETED = "COMPLETED", "Completed"
    CLOSED = "CLOSED", "Closed"
    OPEN = "OPEN", "Open"


class TaskLabelModule(models.TextChoices):
    """Choices for task label modules."""

    CLAIMS = "claims", "Claims"
    TASKS = "tasks", "Tasks"


class Task(IdentifiableModel):
    """Task."""

    class Meta:
        db_table = "canvas_sdk_data_api_task_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="creator_tasks", null=True
    )
    assignee = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="assignee_tasks", null=True
    )
    # TODO - uncomment when Team model is created
    # team = models.ForeignKey('v1.Team', on_delete=models.DO_NOTHING, related_name="tasks", null=True)
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, blank=True, related_name="tasks", null=True
    )
    task_type = models.CharField(choices=TaskType.choices, max_length=1)
    tag = models.CharField(max_length=64)
    title = models.TextField()
    due = models.DateTimeField(null=True)
    due_event = models.CharField(choices=EventType.choices, blank=True, max_length=16)
    status = models.CharField(choices=TaskStatus.choices, max_length=9)


class TaskComment(IdentifiableModel):
    """TaskComment."""

    class Meta:
        db_table = "canvas_sdk_data_api_taskcomment_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="comments", null=True
    )
    task = models.ForeignKey(Task, on_delete=models.DO_NOTHING, related_name="comments", null=True)
    body = models.TextField()


class TaskLabel(IdentifiableModel):
    """TaskLabel."""

    class Meta:
        db_table = "canvas_sdk_data_api_tasklabel_001"

    tasks = models.ManyToManyField(Task, related_name="labels", through="TaskTaskLabel")  # type: ignore[var-annotated]
    position = models.IntegerField()
    color = models.CharField(choices=ColorEnum.choices, max_length=50)
    task_association = ArrayField(models.CharField(choices=Origin.choices, max_length=32))
    name = models.CharField(max_length=255)
    active = models.BooleanField()
    modules = ArrayField(models.CharField(choices=TaskLabelModule.choices, max_length=32))


class TaskTaskLabel(Model):
    """M2M for Task -> TaskLabels."""

    class Meta:
        db_table = "canvas_sdk_data_api_tasktasklabel_001"

    task_label = models.ForeignKey(TaskLabel, on_delete=models.DO_NOTHING, null=True)
    task = models.ForeignKey(Task, on_delete=models.DO_NOTHING, null=True)


__exports__ = (
    "TaskType",
    "EventType",
    "TaskStatus",
    "TaskLabelModule",
    "Task",
    "TaskComment",
    "TaskLabel",
    "TaskTaskLabel",
)
