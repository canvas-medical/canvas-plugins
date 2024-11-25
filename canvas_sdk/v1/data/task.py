from django.contrib.postgres.fields import ArrayField
from django.db import models

from canvas_sdk.v1.data.common import ColorEnum, Origin
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.staff import Staff


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
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_task_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    creator = models.ForeignKey(Staff, related_name="creator_tasks", on_delete=models.DO_NOTHING)
    assignee = models.ForeignKey(
        Staff, related_name="assignee_tasks", null=True, on_delete=models.DO_NOTHING
    )
    # TODO - uncomment when Team model is created
    # team = models.ForeignKey(Team, related_name="tasks", null=True, on_delete=models.DO_NOTHING)
    patient = models.ForeignKey(
        Patient, blank=True, null=True, on_delete=models.DO_NOTHING, related_name="tasks"
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
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_taskcomment_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    creator = models.ForeignKey(Staff, related_name="comments", on_delete=models.DO_NOTHING)
    task = models.ForeignKey(Task, on_delete=models.DO_NOTHING, related_name="comments")
    body = models.TextField()


class TaskLabel(models.Model):
    """TaskLabel."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
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
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_api_tasktasklabel_001"

    dbid = models.BigIntegerField(primary_key=True)
    task_label = models.ForeignKey(TaskLabel, on_delete=models.DO_NOTHING)
    task = models.ForeignKey(Task, on_delete=models.DO_NOTHING)
