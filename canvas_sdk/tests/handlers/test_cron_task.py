import pytest

from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.cron_task import CronTask


class ExampleCronTask(CronTask):
    """A concrete implementation of CronTask for testing."""

    SCHEDULE = "0 10 * * *"  # Every day at 10:00 AM

    def execute(self) -> list[Effect]:
        """Return a test effect."""
        return [LaunchModalEffect(url="https://example.com").apply()]


class EveryMinuteCronTask(CronTask):
    """A cron task that runs every minute."""

    SCHEDULE = "* * * * *"

    def execute(self) -> list[Effect]:
        """Return a test effect."""
        return [LaunchModalEffect(url="https://example.com").apply()]


class NoScheduleCronTask(CronTask):
    """A cron task with no schedule set."""

    def execute(self) -> list[Effect]:
        """Return a test effect."""
        return [LaunchModalEffect(url="https://example.com").apply()]


def make_cron_event(timestamp: str) -> Event:
    """Create a CRON event with the given timestamp as the target."""
    request = EventRequest(type=EventType.CRON, target=timestamp)
    return Event(request)


class TestCronTask:
    """Tests for CronTask behavior."""

    def test_exact_time_match_executes(self) -> None:
        """Cron task executes when time exactly matches schedule."""
        event = make_cron_event("2024-01-15T10:00:00+00:00")
        task = ExampleCronTask(event)

        result = task.compute()

        assert len(result) == 1

    def test_with_seconds_still_matches(self) -> None:
        """Cron task executes even with non-zero seconds (same minute)."""
        event = make_cron_event("2024-01-15T10:00:30+00:00")
        task = ExampleCronTask(event)

        result = task.compute()

        assert len(result) == 1

    def test_different_minute_does_not_execute(self) -> None:
        """Cron task does NOT execute when minute doesn't match."""
        event = make_cron_event("2024-01-15T10:01:00+00:00")
        task = ExampleCronTask(event)

        result = task.compute()

        assert len(result) == 0

    def test_one_minute_early_does_not_execute(self) -> None:
        """Cron task does NOT execute when 1 minute early."""
        event = make_cron_event("2024-01-15T09:59:00+00:00")
        task = ExampleCronTask(event)

        result = task.compute()

        assert len(result) == 0

    def test_every_minute_schedule_matches(self) -> None:
        """Every-minute schedule works at any minute."""
        event = make_cron_event("2024-01-15T10:00:00+00:00")
        task = EveryMinuteCronTask(event)

        result = task.compute()

        assert len(result) == 1

    def test_every_minute_different_times(self) -> None:
        """Every-minute schedule works at various times."""
        for timestamp in [
            "2024-01-15T10:00:00+00:00",
            "2024-01-15T10:01:00+00:00",
            "2024-01-15T10:02:00+00:00",
            "2024-01-15T23:59:00+00:00",
        ]:
            event = make_cron_event(timestamp)
            task = EveryMinuteCronTask(event)

            result = task.compute()

            assert len(result) == 1, f"Failed for {timestamp}"

    def test_no_schedule_raises_error(self) -> None:
        """CronTask raises ValueError when SCHEDULE is not set."""
        event = make_cron_event("2024-01-15T10:00:00+00:00")
        task = NoScheduleCronTask(event)

        with pytest.raises(ValueError, match="You must set a SCHEDULE"):
            task.compute()
