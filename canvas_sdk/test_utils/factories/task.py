from typing import Any

import factory

from canvas_sdk.v1.data import Task, TaskLabel
from canvas_sdk.v1.data.task import TaskStatus, TaskType


class TaskFactory(factory.django.DjangoModelFactory[Task]):
    """Factory for creating Task."""

    class Meta:
        model = Task

    creator = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    task_type = TaskType.REMINDER
    tag = "Unit Test"
    title = "Unit Test"
    status = TaskStatus.OPEN


class TaskLabelFactory(factory.django.DjangoModelFactory[TaskLabel]):
    """Factory for creating TaskLabel."""

    class Meta:
        model = TaskLabel

    position = 1
    color = "red"
    task_association = ["FLG_PST_REV"]
    name = "needs review"

    @factory.post_generation
    def tasks(self, create: bool, extracted: list | None, **kwargs: Any) -> None:
        """Attach tasks to the TaskLabel via the M2M relationship.

        Pass a list of Task instances or dicts to create tasks via TaskFactory.

        Example:
            TaskLabelFactory(tasks=[TaskFactory(), {'title': 't2'}])
        """
        if not extracted:
            return

        TaskFactory_t: Any = TaskFactory

        for item in extracted:
            if isinstance(item, Task):
                self.tasks.add(item)
            elif isinstance(item, dict):
                # create a Task from provided kwargs
                self.tasks.add(TaskFactory_t(**item))
