"""Tests for the compute_notification_badge hook on the Application handler."""

import json

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.application import Application, ApplicationScope, EmbeddedApplication


class _BadgeApp(Application):
    """An Application that returns a notification badge of 5."""

    def on_open(self) -> Effect:
        """Required abstract method; not exercised by these tests."""
        return LaunchModalEffect(url="https://example.com").apply()

    def compute_notification_badge(self) -> int | None:
        """Return a badge count of 5."""
        return 5


class _NoBadgeApp(Application):
    """An Application that does not provide a badge."""

    def on_open(self) -> Effect:
        """Required abstract method; not exercised by these tests."""
        return LaunchModalEffect(url="https://example.com").apply()


class _BadgeEmbeddedApp(EmbeddedApplication):
    """An EmbeddedApplication that returns a notification badge of 3."""

    NAME = "Badge Embedded App"
    SCOPE = ApplicationScope.NOTE
    IDENTIFIER = "badge_app"

    def on_open(self) -> list[Effect]:
        """Required abstract method; not exercised by these tests."""
        return []

    def compute_notification_badge(self) -> int | None:
        """Return a badge count of 3."""
        return 3


def _make_badge_event(target: str, context: dict[str, str] | None = None) -> Event:
    """Build an APPLICATION__GET_NOTIFICATION_BADGE event."""
    return Event(
        EventRequest(
            type=EventType.APPLICATION__GET_NOTIFICATION_BADGE,
            target=target,
            context=json.dumps(context or {}),
        )
    )


def test_get_notification_badge_wraps_int_with_staff_ids_when_staff_key_in_context() -> None:
    """When event context carries staff_key, the auto-wrapped effect targets that staff via staff_ids."""
    identifier = f"{_BadgeApp.__module__}:{_BadgeApp.__qualname__}"
    app = _BadgeApp(_make_badge_event(target=identifier, context={"staff_key": "staff-123"}))

    result = app.compute()

    assert len(result) == 1
    assert result[0].type == EffectType.SET_APPLICATION_NOTIFICATION_BADGE
    data = json.loads(result[0].payload)["data"]
    assert data["application_identifier"] == identifier
    assert data["count"] == 5
    assert data["staff_ids"] == ["staff-123"]
    assert data["patient_ids"] == []


def test_get_notification_badge_wraps_int_with_patient_ids_when_patient_key_in_context() -> None:
    """When event context carries patient_key (no staff_key), wrap into patient_ids."""
    identifier = f"{_BadgeApp.__module__}:{_BadgeApp.__qualname__}"
    app = _BadgeApp(_make_badge_event(target=identifier, context={"patient_key": "patient-abc"}))

    result = app.compute()

    assert len(result) == 1
    data = json.loads(result[0].payload)["data"]
    assert data["staff_ids"] == []
    assert data["patient_ids"] == ["patient-abc"]
    assert data["count"] == 5


def test_get_notification_badge_returns_empty_when_target_does_not_match() -> None:
    """compute() returns [] when the event target is for a different application."""
    app = _BadgeApp(_make_badge_event(target="some_other_app", context={"staff_key": "x"}))

    assert app.compute() == []


def test_compute_notification_badge_default_returns_none() -> None:
    """Application subclasses that do not override compute_notification_badge produce no effect."""
    identifier = f"{_NoBadgeApp.__module__}:{_NoBadgeApp.__qualname__}"
    app = _NoBadgeApp(_make_badge_event(target=identifier, context={"staff_key": "x"}))

    assert app.compute() == []


def test_compute_notification_badge_returning_none_yields_no_effect() -> None:
    """Returning None from compute_notification_badge emits no effect even when targeted."""

    class _NoneBadgeApp(Application):
        def on_open(self) -> Effect:
            return LaunchModalEffect(url="https://example.com").apply()

        def compute_notification_badge(self) -> int | None:
            return None

    identifier = f"{_NoneBadgeApp.__module__}:{_NoneBadgeApp.__qualname__}"
    app = _NoneBadgeApp(_make_badge_event(target=identifier, context={"staff_key": "x"}))

    assert app.compute() == []


def test_embedded_application_falls_back_to_base_handler() -> None:
    """EmbeddedApplication subclasses inherit the badge hook from Application."""
    app = _BadgeEmbeddedApp(_make_badge_event(target="badge_app", context={"staff_key": "s1"}))

    result = app.compute()

    assert len(result) == 1
    assert result[0].type == EffectType.SET_APPLICATION_NOTIFICATION_BADGE
    data = json.loads(result[0].payload)["data"]
    assert data["application_identifier"] == "badge_app"
    assert data["count"] == 3
    assert data["staff_ids"] == ["s1"]


def test_missing_user_keys_in_context_yields_both_lists_empty() -> None:
    """If neither staff_key nor patient_key is in context, both lists are empty (broadcast)."""
    identifier = f"{_BadgeApp.__module__}:{_BadgeApp.__qualname__}"
    app = _BadgeApp(_make_badge_event(target=identifier, context={}))

    result = app.compute()

    data = json.loads(result[0].payload)["data"]
    assert data["staff_ids"] == []
    assert data["patient_ids"] == []


def test_staff_key_takes_precedence_when_both_keys_present() -> None:
    """If both staff_key and patient_key are present, staff_key wins (one or the other, not both)."""
    identifier = f"{_BadgeApp.__module__}:{_BadgeApp.__qualname__}"
    app = _BadgeApp(
        _make_badge_event(
            target=identifier,
            context={"staff_key": "s1", "patient_key": "p1"},
        )
    )

    result = app.compute()

    data = json.loads(result[0].payload)["data"]
    assert data["staff_ids"] == ["s1"]
    assert data["patient_ids"] == []
