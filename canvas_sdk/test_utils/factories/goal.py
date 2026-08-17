import datetime

import factory

from canvas_sdk.v1.data import Goal, UpdateGoal


class GoalFactory(factory.django.DjangoModelFactory[Goal]):
    """Factory for Goal."""

    class Meta:
        model = Goal

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )
    due_date = factory.LazyFunction(datetime.date.today)
    goal_statement = factory.Faker("sentence")
    start_date = factory.LazyFunction(datetime.date.today)


class UpdateGoalFactory(factory.django.DjangoModelFactory[UpdateGoal]):
    """Factory for UpdateGoal."""

    class Meta:
        model = UpdateGoal

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
    )
    goal = factory.SubFactory(
        GoalFactory,
        patient=factory.SelfAttribute("..patient"),
        note=factory.SelfAttribute("..note"),
    )
    due_date = factory.LazyFunction(datetime.date.today)
