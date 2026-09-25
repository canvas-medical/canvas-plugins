"""Input validation kept separate from network and Canvas framework code."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

ALLOWED_ANALYSES = frozenset(
    {"wellbeing", "parkinsons", "alzheimers", "communication_coach"}
)
MAX_BASE64_CHARACTERS = 67_000_000


def validate_submission(payload: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    """Return a normalized Virtuosis request body or a safe validation message."""
    if payload.get("consent_confirmed") is not True:
        return None, "Explicit recording transmission confirmation is required."

    account_id = payload.get("account_id")
    if not _is_uuid(account_id):
        return None, "account_id must be a UUID."

    recorded_at = payload.get("recorded_at")
    if not _is_timezone_aware_datetime(recorded_at):
        return None, "recorded_at must be an ISO 8601 timestamp with a timezone."

    analyses = payload.get("analysis")
    if not isinstance(analyses, list) or not analyses:
        return None, "Select at least one supported analysis."
    normalized_analyses = list(dict.fromkeys(analyses))
    if any(not isinstance(value, str) or value not in ALLOWED_ANALYSES for value in analyses):
        return None, "Select at least one supported analysis."

    audio = payload.get("audio_base64")
    if not isinstance(audio, str) or not audio or len(audio) > MAX_BASE64_CHARACTERS:
        return None, "audio_base64 is missing or exceeds the 50 MB recording limit."

    return (
        {
            "account_id": account_id,
            "recorded_at": recorded_at,
            "analysis": normalized_analyses,
            "audio": audio,
            "isolate_oldest_speaker": bool(payload.get("isolate_oldest_speaker", False)),
        },
        None,
    )


def validate_recording_id(value: object) -> bool:
    """Return whether the external recording identifier is a UUID."""
    return _is_uuid(value)


def normalize_analysis_query(value: object) -> list[str] | None:
    """Validate an optional comma-separated analysis query."""
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise ValueError("analysis query must be a comma-separated string")
    normalized = list(dict.fromkeys(part.strip() for part in value.split(",") if part.strip()))
    if not normalized or any(part not in ALLOWED_ANALYSES for part in normalized):
        raise ValueError("analysis query contains an unsupported value")
    return normalized


def _is_uuid(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        UUID(value)
    except ValueError:
        return False
    return True


def _is_timezone_aware_datetime(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None
