import factory

from canvas_sdk.v1.data import Task, TaskComment, TaskLabel, TaskMetadata, TaskTaskLabel
from canvas_sdk.v1.data.common import ColorEnum, Origin
from canvas_sdk.v1.data.task import TaskLabelModule, TaskStatus, TaskType


class TaskFactory(factory.django.DjangoModelFactory[Task]):
    """Factory for creating Task."""

    class Meta:
        model = Task

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    creator = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    assignee = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    task_type = TaskType.TASK
    tag = factory.Faker("word")
    title = factory.Faker("sentence", nb_words=4)
    status = TaskStatus.OPEN


class TaskMetadataFactory(factory.django.DjangoModelFactory[TaskMetadata]):
    """Factory for creating TaskMetadata."""

    class Meta:
        model = TaskMetadata

    task = factory.SubFactory(TaskFactory)
    key = factory.Faker("word")
    value = factory.Faker("word")


class TaskCommentFactory(factory.django.DjangoModelFactory[TaskComment]):
    """Factory for creating TaskComment."""

    class Meta:
        model = TaskComment

    creator = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    task = factory.SubFactory(TaskFactory)
    body = factory.Faker("sentence", nb_words=10)


class TaskLabelFactory(factory.django.DjangoModelFactory[TaskLabel]):
    """Factory for creating TaskLabel."""

    class Meta:
        model = TaskLabel

    position = factory.Sequence(lambda n: n)
    color = ColorEnum.BLUE
    task_association = [Origin.REFERAL]
    name = factory.Faker("word")
    active = True
    modules = [TaskLabelModule.TASKS]


class TaskTaskLabelFactory(factory.django.DjangoModelFactory[TaskTaskLabel]):
    """Factory for creating TaskTaskLabel."""

    class Meta:
        model = TaskTaskLabel

    task = factory.SubFactory(TaskFactory)
    task_label = factory.SubFactory(TaskLabelFactory)
