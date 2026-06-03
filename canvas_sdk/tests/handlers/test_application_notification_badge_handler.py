"""Tests for the compute_notification_badge hook on the Application handler."""

import json
from collections.abc import Iterator
from typing import Any
from unittest.mock import patch

import pytest

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.application import Application, ApplicationScope, EmbeddedApplication


@pytest.fixture(autouse=True)
def _stub_application_exists() -> Iterator[None]:
    """Bypass the Application existence check in the effect's _get_error_details.

    The handler tests use synthetic identifiers (module:qualname) that aren't
    backed by real Application rows. Real plugin handlers always have a matching
    row from CANVAS_MANIFEST.json install, so this is test scaffolding only.
    """
    with patch(
        "canvas_sdk.effects.application_notification_badge.Application.objects.filter"
    ) as mock_filter:
        mock_filter.return_value.exists.return_value = True
        yield


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


def _make_badge_event(target: str, context: dict[str, Any] | None = None) -> Event:
    """Build an APPLICATION__GET_NOTIFICATION_BADGE event."""
    return Event(
        EventRequest(
            type=EventType.APPLICATION__GET_NOTIFICATION_BADGE,
            target=target,
            context=json.dumps(context or {}),
        )
    )


def test_get_notification_badge_wraps_int_with_staff_ids_when_staff_in_context() -> None:
    """When event context carries staff.id, the auto-wrapped effect targets that staff via staff_ids."""
    identifier = f"{_BadgeApp.__module__}:{_BadgeApp.__qualname__}"
    app = _BadgeApp(_make_badge_event(target=identifier, context={"staff": {"id": "staff-123"}}))

    result = app.compute()

    assert len(result) == 1
    assert result[0].type == EffectType.SET_APPLICATION_NOTIFICATION_BADGE
    data = json.loads(result[0].payload)["data"]
    assert data["application_identifier"] == identifier
    assert data["count"] == 5
    assert data["staff_ids"] == ["staff-123"]
    assert data["patient_ids"] == []


def test_get_notification_badge_wraps_int_with_patient_ids_when_patient_in_context() -> None:
    """When event context carries patient.id (no staff), wrap into patient_ids."""
    identifier = f"{_BadgeApp.__module__}:{_BadgeApp.__qualname__}"
    app = _BadgeApp(
        _make_badge_event(target=identifier, context={"patient": {"id": "patient-abc"}})
    )

    result = app.compute()

    assert len(result) == 1
    data = json.loads(result[0].payload)["data"]
    assert data["staff_ids"] == []
    assert data["patient_ids"] == ["patient-abc"]
    assert data["count"] == 5


def test_get_notification_badge_returns_empty_when_target_does_not_match() -> None:
    """compute() returns [] when the event target is for a different application."""
    app = _BadgeApp(_make_badge_event(target="some_other_app", context={"staff": {"id": "x"}}))

    assert app.compute() == []


def test_compute_notification_badge_default_returns_none() -> None:
    """Application subclasses that do not override compute_notification_badge produce no effect."""
    identifier = f"{_NoBadgeApp.__module__}:{_NoBadgeApp.__qualname__}"
    app = _NoBadgeApp(_make_badge_event(target=identifier, context={"staff": {"id": "x"}}))

    assert app.compute() == []


def test_compute_notification_badge_returning_none_yields_no_effect() -> None:
    """Returning None from compute_notification_badge emits no effect even when targeted."""

    class _NoneBadgeApp(Application):
        def on_open(self) -> Effect:
            return LaunchModalEffect(url="https://example.com").apply()

        def compute_notification_badge(self) -> int | None:
            return None

    identifier = f"{_NoneBadgeApp.__module__}:{_NoneBadgeApp.__qualname__}"
    app = _NoneBadgeApp(_make_badge_event(target=identifier, context={"staff": {"id": "x"}}))

    assert app.compute() == []


def test_embedded_application_ignores_badge_event() -> None:
    """EmbeddedApplications don't respond to APPLICATION__GET_NOTIFICATION_BADGE.

    They're transient (re-registered on every APPLICATION__ON_GET), so they aren't
    stored as Application rows and the home-app resolver's fan-out doesn't reach
    them. Any direct dispatch of the badge event is a no-op even if the subclass
    overrides ``compute_notification_badge``.
    """
    app = _BadgeEmbeddedApp(_make_badge_event(target="badge_app", context={"staff": {"id": "s1"}}))

    assert app.compute() == []


def test_missing_user_context_yields_both_lists_empty() -> None:
    """If neither staff nor patient is in context, both lists are empty (broadcast)."""
    identifier = f"{_BadgeApp.__module__}:{_BadgeApp.__qualname__}"
    app = _BadgeApp(_make_badge_event(target=identifier, context={}))

    result = app.compute()

    data = json.loads(result[0].payload)["data"]
    assert data["staff_ids"] == []
    assert data["patient_ids"] == []


def test_combined_context_produces_both_lists() -> None:
    """When both staff and patient are present, the effect carries both lists.

    This is the patient-chart resolver path: home-app emits the event with both
    keys so the auto-wrapped effect routes to the composite staff.{s}.patient.{p}
    channel.
    """
    identifier = f"{_BadgeApp.__module__}:{_BadgeApp.__qualname__}"
    app = _BadgeApp(
        _make_badge_event(
            target=identifier,
            context={"staff": {"id": "s1"}, "patient": {"id": "p1"}},
        )
    )

    result = app.compute()

    data = json.loads(result[0].payload)["data"]
    assert data["staff_ids"] == ["s1"]
    assert data["patient_ids"] == ["p1"]
