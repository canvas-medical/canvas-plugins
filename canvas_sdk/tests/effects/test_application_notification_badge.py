"""Tests for the SetApplicationNotificationBadge effect."""

import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.application_notification_badge import SetApplicationNotificationBadge


def test_apply_returns_effect_with_correct_type() -> None:
    """apply() returns an Effect typed SET_APPLICATION_NOTIFICATION_BADGE."""
    effect = SetApplicationNotificationBadge(
        application_identifier="my_plugin__my_app",
        count=3,
        staff_ids=["staff-123"],
    ).apply()

    assert isinstance(effect, Effect)
    assert effect.type == EffectType.SET_APPLICATION_NOTIFICATION_BADGE


def test_payload_contains_application_identifier_count_and_target_lists() -> None:
    """The effect payload carries application_identifier, count, staff_ids, patient_ids."""
    effect = SetApplicationNotificationBadge(
        application_identifier="my_plugin__my_app",
        count=7,
        staff_ids=["staff-a", "staff-b"],
        patient_ids=["patient-x"],
    ).apply()

    data = json.loads(effect.payload)["data"]
    assert data["application_identifier"] == "my_plugin__my_app"
    assert data["count"] == 7
    assert data["staff_ids"] == ["staff-a", "staff-b"]
    assert data["patient_ids"] == ["patient-x"]


def test_staff_ids_and_patient_ids_default_to_empty_lists() -> None:
    """Omitting both target lists serializes them as empty arrays (broadcast-to-all semantic)."""
    effect = SetApplicationNotificationBadge(
        application_identifier="my_plugin__my_app",
        count=0,
    ).apply()

    data = json.loads(effect.payload)["data"]
    assert data["staff_ids"] == []
    assert data["patient_ids"] == []


def test_count_zero_is_allowed() -> None:
    """count=0 is allowed (it clears a previously set badge)."""
    effect = SetApplicationNotificationBadge(
        application_identifier="my_plugin__my_app",
        count=0,
        staff_ids=["staff-1"],
    ).apply()

    data = json.loads(effect.payload)["data"]
    assert data["count"] == 0


def test_negative_count_rejected() -> None:
    """Negative counts are invalid."""
    with pytest.raises(ValidationError):
        SetApplicationNotificationBadge(
            application_identifier="my_plugin__my_app",
            count=-1,
        )


def test_empty_application_identifier_rejected() -> None:
    """An empty application_identifier is invalid."""
    with pytest.raises(ValidationError):
        SetApplicationNotificationBadge(
            application_identifier="",
            count=1,
        )


def test_cross_type_targeting_in_single_effect() -> None:
    """A single effect can target staff and patients together (driving use case)."""
    effect = SetApplicationNotificationBadge(
        application_identifier="messages__inbox",
        count=1,
        staff_ids=["doctor-key"],
        patient_ids=["patient-key"],
    ).apply()

    data = json.loads(effect.payload)["data"]
    assert data["staff_ids"] == ["doctor-key"]
    assert data["patient_ids"] == ["patient-key"]
    assert data["count"] == 1
