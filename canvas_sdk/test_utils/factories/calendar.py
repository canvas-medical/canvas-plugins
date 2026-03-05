import datetime

import factory

from canvas_sdk.v1.data import Calendar, Event


class EventFactory(factory.django.DjangoModelFactory[Event]):
    """Factory for creating an Event."""

    class Meta:
        model = Event

    title = "Calendar Event"
    calendar = factory.SubFactory("canvas_sdk.test_utils.factories.CalendarFactory")
    starts_at = factory.Faker("date_time", tzinfo=datetime.UTC)
    ends_at = factory.Faker("date_time", tzinfo=datetime.UTC)


class CalendarFactory(factory.django.DjangoModelFactory[Calendar]):
    """Factory for creating Calendar."""

    class Meta:
        model = Calendar

    title = "Calendar"
