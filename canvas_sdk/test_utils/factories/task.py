from typing import Any

import factory

from canvas_sdk.v1.data import Task, TaskLabel


class TaskFactory(factory.django.DjangoModelFactory[Task]):
    """Factory for creating Task."""

    class Meta:
        model = Task

    creator = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    assignee = None
    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    task_type = "R"
    tag = "Unit Test"
    title = "Unit Test"
    due = None
    due_event = ""
    status = "OPEN"


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
        # If the object wasn't actually created in the DB, skip M2M handling.
        if not create:
            return

        if not extracted:
            return

        TaskFactory_t: Any = TaskFactory

        for item in extracted:
            if isinstance(item, Task):
                self.tasks.add(item)
            elif isinstance(item, dict):
                # create a Task from provided kwargs
                self.tasks.add(TaskFactory_t(**item))
            else:
                # assume it's already an object that can be added (e.g. a PK or factory instance)
                try:
                    self.tasks.add(item)
                except Exception:
                    # fallback: create a new Task
                    self.tasks.add(TaskFactory_t())
