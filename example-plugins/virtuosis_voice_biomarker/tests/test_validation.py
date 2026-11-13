from __future__ import annotations

from virtuosis_voice_biomarker.validation import (
    normalize_analysis_query,
    validate_recording_id,
    validate_submission,
)

ACCOUNT_ID = "00000000-0000-0000-0000-000000000000"


def test_submission_requires_consent() -> None:
    body, error = validate_submission({"consent_confirmed": False})
    assert body is None
    assert error == "Explicit recording transmission confirmation is required."


def test_submission_is_normalized() -> None:
    body, error = validate_submission(
        {
            "consent_confirmed": True,
            "account_id": ACCOUNT_ID,
            "recorded_at": "2026-08-23T10:00:00Z",
            "analysis": ["wellbeing", "wellbeing"],
            "audio_base64": "YXVkaW8=",
        }
    )
    assert error is None
    assert body is not None
    assert body["analysis"] == ["wellbeing"]
    assert body["audio"] == "YXVkaW8="


def test_recording_id_and_query_validation() -> None:
    assert validate_recording_id(ACCOUNT_ID)
    assert not validate_recording_id("../../recording")
    assert normalize_analysis_query("wellbeing,communication_coach,wellbeing") == [
        "wellbeing",
        "communication_coach",
    ]
