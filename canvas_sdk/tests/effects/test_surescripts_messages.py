import json

from canvas_sdk.effects.surescripts.surescripts_messages import (
    SendSurescriptsEligibilityRequestEffect,
)


def test_send_eligibility_effect_includes_correlation_id_in_payload() -> None:
    """The effect serializes correlation_id alongside patient/staff IDs."""
    effect = SendSurescriptsEligibilityRequestEffect(
        patient_id="patient-key-1",
        staff_id="staff-key-1",
        correlation_id="abc-123",
    )

    applied = effect.apply()
    payload = json.loads(applied.payload)

    assert payload == {
        "patient_id": "patient-key-1",
        "staff_id": "staff-key-1",
        "correlation_id": "abc-123",
    }


def test_send_eligibility_effect_auto_generates_correlation_id() -> None:
    """When the caller doesn't pass a correlation_id, the effect generates one."""
    effect = SendSurescriptsEligibilityRequestEffect(
        patient_id="patient-key-1",
        staff_id="staff-key-1",
    )

    assert effect.correlation_id
    assert isinstance(effect.correlation_id, str)
    assert len(effect.correlation_id) >= 16  # uuid4().hex is 32 chars

    payload = json.loads(effect.apply().payload)
    assert payload["correlation_id"] == effect.correlation_id


def test_send_eligibility_effect_auto_generated_ids_are_unique() -> None:
    """Two effects constructed without explicit IDs get distinct correlation_ids."""
    a = SendSurescriptsEligibilityRequestEffect(patient_id="p", staff_id="s")
    b = SendSurescriptsEligibilityRequestEffect(patient_id="p", staff_id="s")

    assert a.correlation_id != b.correlation_id
