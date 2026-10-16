import datetime

import factory

from canvas_sdk.v1.data import GoogleCalendar, GoogleCalendarBusyBlock, GoogleCalendarConnection


class GoogleCalendarBusyBlockFactory(factory.django.DjangoModelFactory[GoogleCalendarBusyBlock]):
    """Factory for creating a GoogleCalendarBusyBlock."""

    class Meta:
        model = GoogleCalendarBusyBlock

    provider = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    location = factory.SubFactory("canvas_sdk.test_utils.factories.PracticeLocationFactory")
    start_time = factory.LazyFunction(lambda: datetime.datetime.now(datetime.UTC))
    duration_minutes = 30
    active = True


class GoogleCalendarConnectionFactory(factory.django.DjangoModelFactory[GoogleCalendarConnection]):
    """Factory for creating a GoogleCalendarConnection."""

    class Meta:
        model = GoogleCalendarConnection

    staff = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    google_account_email = factory.Faker("email")
    needs_reconnect = False


class GoogleCalendarFactory(factory.django.DjangoModelFactory[GoogleCalendar]):
    """Factory for creating a GoogleCalendar."""

    class Meta:
        model = GoogleCalendar

    connection = factory.SubFactory(GoogleCalendarConnectionFactory)
    summary = factory.Faker("word")
    selected = True
    is_app_created = False
