"""Tests for the ApplicationNotificationBadge fluent builder."""

import json
from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.application_notification_badge import ApplicationNotificationBadge


@pytest.fixture(autouse=True)
def _stub_application_exists() -> Iterator[MagicMock]:
    """Stub Application.objects.filter().exists() to True so .broadcast() doesn't hit the DB.

    Individual tests that want to exercise the missing-Application path override
    this by patching ``Application.objects.filter`` themselves.
    """
    with patch(
        "canvas_sdk.effects.application_notification_badge.Application.objects.filter"
    ) as mock_filter:
        mock_filter.return_value.exists.return_value = True
        yield mock_filter


def test_broadcast_returns_effect_with_correct_type() -> None:
    """broadcast() returns an Effect typed SET_APPLICATION_NOTIFICATION_BADGE."""
    effect = ApplicationNotificationBadge("my_plugin__my_app").broadcast(
        count=3, staff_ids=["staff-123"]
    )

    assert isinstance(effect, Effect)
    assert effect.type == EffectType.SET_APPLICATION_NOTIFICATION_BADGE


def test_payload_with_only_staff_ids() -> None:
    """staff_ids on .broadcast() lands in the payload; patient_ids defaults to []."""
    effect = ApplicationNotificationBadge("my_plugin__my_app").broadcast(
        count=7, staff_ids=["staff-a", "staff-b"]
    )

    data = json.loads(effect.payload)["data"]
    assert data["application_identifier"] == "my_plugin__my_app"
    assert data["count"] == 7
    assert data["staff_ids"] == ["staff-a", "staff-b"]
    assert data["patient_ids"] == []


def test_payload_with_only_patient_ids_via_filter() -> None:
    """patient_ids set via .filter() appear in the payload; staff_ids defaults to []."""
    effect = (
        ApplicationNotificationBadge("my_plugin__my_app")
        .filter(patient_ids=["patient-x"])
        .broadcast(count=2)
    )

    data = json.loads(effect.payload)["data"]
    assert data["patient_ids"] == ["patient-x"]
    assert data["staff_ids"] == []
    assert data["count"] == 2


def test_cross_type_targeting_in_single_effect() -> None:
    """A single .filter().broadcast() chain can target both staff and patients."""
    effect = (
        ApplicationNotificationBadge("messages__inbox")
        .filter(patient_ids=["patient-key"])
        .broadcast(count=1, staff_ids=["doctor-key"])
    )

    data = json.loads(effect.payload)["data"]
    assert data["staff_ids"] == ["doctor-key"]
    assert data["patient_ids"] == ["patient-key"]
    assert data["count"] == 1


def test_targets_default_to_empty_lists() -> None:
    """No filter, no staff_ids → both lists empty (broadcast-to-all semantic)."""
    effect = ApplicationNotificationBadge("my_plugin__my_app").broadcast(count=0)

    data = json.loads(effect.payload)["data"]
    assert data["staff_ids"] == []
    assert data["patient_ids"] == []


def test_count_zero_is_allowed() -> None:
    """count=0 is allowed (it clears a previously set badge)."""
    effect = ApplicationNotificationBadge("my_plugin__my_app").broadcast(
        count=0, staff_ids=["staff-1"]
    )

    data = json.loads(effect.payload)["data"]
    assert data["count"] == 0


def test_negative_count_rejected() -> None:
    """Negative counts are invalid."""
    with pytest.raises(ValidationError):
        ApplicationNotificationBadge("my_plugin__my_app").broadcast(count=-1)


def test_empty_application_identifier_rejected() -> None:
    """An empty application_identifier is invalid."""
    with pytest.raises(ValidationError):
        ApplicationNotificationBadge("").broadcast(count=1)


def test_filter_returns_self_for_chaining() -> None:
    """filter() returns the builder so calls can chain into broadcast()."""
    badge = ApplicationNotificationBadge("my_plugin__my_app")
    assert badge.filter(patient_ids=["p1"]) is badge


def test_broadcast_without_filter_does_not_raise() -> None:
    """Calling .broadcast() directly (without .filter() first) works — patient_ids defaults to []."""
    effect = ApplicationNotificationBadge("my_plugin__my_app").broadcast(count=5, staff_ids=["s1"])

    data = json.loads(effect.payload)["data"]
    assert data["staff_ids"] == ["s1"]
    assert data["patient_ids"] == []


def test_filter_with_none_patient_ids_is_a_noop() -> None:
    """Calling .filter() with patient_ids=None leaves the patient list empty."""
    effect = (
        ApplicationNotificationBadge("my_plugin__my_app")
        .filter(patient_ids=None)
        .broadcast(count=1, staff_ids=["s1"])
    )

    data = json.loads(effect.payload)["data"]
    assert data["patient_ids"] == []


# --- Application-existence validation ----------------------------------------


def test_broadcast_rejects_unknown_application_identifier(
    _stub_application_exists: MagicMock,
) -> None:
    """If the application_identifier doesn't match an installed Application, .broadcast() raises."""
    _stub_application_exists.return_value.exists.return_value = False

    with pytest.raises(ValidationError) as exc_info:
        ApplicationNotificationBadge("typo__not_installed").broadcast(count=1, staff_ids=["s1"])

    assert any(
        "Application 'typo__not_installed' not found" in str(e) for e in exc_info.value.errors()
    )


def test_broadcast_queries_application_table_by_identifier(
    _stub_application_exists: MagicMock,
) -> None:
    """The existence check queries the Application table filtering by identifier."""
    ApplicationNotificationBadge("my_plugin__my_app").broadcast(count=1, staff_ids=["s1"])

    _stub_application_exists.assert_called_with(identifier="my_plugin__my_app")
