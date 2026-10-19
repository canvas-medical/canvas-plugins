import datetime

import pytest

from canvas_sdk.test_utils.factories import (
    GoogleCalendarBusyBlockFactory,
    GoogleCalendarConnectionFactory,
    GoogleCalendarFactory,
    StaffFactory,
)
from canvas_sdk.v1.data import GoogleCalendarBusyBlock


@pytest.mark.django_db
def test_active_busy_blocks_for_a_provider_on_a_date() -> None:
    """A provider's active busy blocks on a date exclude released blocks and other providers."""
    provider = StaffFactory.create()
    start = datetime.datetime(2026, 10, 20, 15, 0, tzinfo=datetime.UTC)
    busy = GoogleCalendarBusyBlockFactory.create(provider=provider, start_time=start)
    GoogleCalendarBusyBlockFactory.create(provider=provider, start_time=start, active=False)
    GoogleCalendarBusyBlockFactory.create(start_time=start)
    GoogleCalendarBusyBlockFactory.create(
        provider=provider, start_time=start + datetime.timedelta(days=1)
    )

    blocks = provider.google_calendar_busy_blocks.filter(active=True, start_time__date=start.date())

    assert list(blocks) == [busy]
    assert GoogleCalendarBusyBlock.objects.get(dbid=busy.dbid).location == busy.location


@pytest.mark.django_db
def test_connection_and_selected_calendars_resolve_from_staff() -> None:
    """A provider's connection and its selected, non-Canvas calendars resolve from Staff."""
    connection = GoogleCalendarConnectionFactory.create(needs_reconnect=True)
    work = GoogleCalendarFactory.create(connection=connection, summary="Work", selected=True)
    GoogleCalendarFactory.create(connection=connection, summary="Personal", selected=False)
    GoogleCalendarFactory.create(connection=connection, selected=True, is_app_created=True)

    staff_connection = connection.staff.google_calendar_connection

    assert staff_connection.needs_reconnect is True
    assert list(staff_connection.calendars.filter(selected=True, is_app_created=False)) == [work]


@pytest.mark.django_db
def test_staff_without_a_connection_has_no_connection() -> None:
    """A provider who never connected Google has no connection row."""
    staff = StaffFactory.create()

    assert not hasattr(staff, "google_calendar_connection")
