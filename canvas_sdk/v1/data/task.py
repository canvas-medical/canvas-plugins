from django.contrib.postgres.fields import ArrayField
from django.db import models

from canvas_sdk.v1.data.common import ColorEnum, Origin


class TaskType(models.TextChoices):
    """Choices for task types."""

    TASK = "Task", "Task"
    REMINDER = "Reminder", "Reminder"


class EventType(models.TextChoices):
    """Choices for event types."""

    EVENT_CHART_OPEN = "Chart Open", "Chart Open"


class TaskStatus(models.TextChoices):
    """Choices for task statuses."""

    COMPLETED = "COMPLETED", "Completed"
    CLOSED = "CLOSED", "Closed"
    OPEN = "OPEN", "Open"


class TaskLabelModule(models.TextChoices):
    """Choices for task label modules."""

    CLAIMS = "claims", "Claims"
    TASKS = "tasks", "Tasks"


class Task(models.Model):
    """Task."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_task_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
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
    task_type = models.CharField(choices=TaskType.choices)
    tag = models.CharField()
    title = models.CharField()
    due = models.DateTimeField(null=True)
    due_event = models.CharField(choices=EventType.choices, blank=True)
    status = models.CharField(choices=TaskStatus.choices)


class TaskComment(models.Model):
    """TaskComment."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_taskcomment_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    creator = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="comments", null=True
    )
    task = models.ForeignKey(Task, on_delete=models.DO_NOTHING, related_name="comments", null=True)
    body = models.TextField()


class TaskLabel(models.Model):
    """TaskLabel."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_tasklabel_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    tasks = models.ManyToManyField(Task, related_name="labels", through="TaskTaskLabel")  # type: ignore[var-annotated]
    position = models.IntegerField()
    color = models.CharField(choices=ColorEnum.choices)
    task_association = ArrayField(models.CharField(choices=Origin.choices))
    name = models.CharField()
    active = models.BooleanField()
    modules = ArrayField(models.CharField(choices=TaskLabelModule.choices))


class TaskTaskLabel(models.Model):
    """M2M for Task -> TaskLabels."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_tasktasklabel_001"

    dbid = models.BigIntegerField(primary_key=True)
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
