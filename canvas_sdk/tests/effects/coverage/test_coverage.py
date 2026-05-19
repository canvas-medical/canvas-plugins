import json
from collections.abc import Generator
from datetime import date
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from pydantic_core import ValidationError

from canvas_sdk.effects.coverage import Coverage, CoverageReorder, PhotoSide
from canvas_sdk.effects.effect import EffectType
from canvas_sdk.v1.data.coverage import (
    CoverageRank,
    CoverageRelationshipCode,
    CoverageType,
)

COVERAGE_PATH = "canvas_sdk.effects.coverage.coverage"


@pytest.fixture
def mock_db() -> Generator[dict[str, MagicMock], None, None]:
    """Stub Patient/Coverage existence checks to always succeed."""
    with (
        patch(f"{COVERAGE_PATH}.Patient.objects") as mock_patient,
        patch(f"{COVERAGE_PATH}.CoverageModel.objects") as mock_coverage,
    ):
        mock_patient.filter.return_value.exists.return_value = True
        mock_coverage.filter.return_value.exists.return_value = True
        yield {"patient": mock_patient, "coverage": mock_coverage}


@pytest.fixture
def valid_create_kwargs() -> dict[str, Any]:
    """Minimal kwargs that satisfy Coverage.create()'s required-field set."""
    return {
        "patient_id": "abc-patient",
        "issuer_id": "issuer-uuid",
        "coverage_rank": CoverageRank.PRIMARY,
        "plan_type": CoverageType.COMMERCIAL,
        "id_number": "MEM-001",
        "patient_relationship_to_subscriber": CoverageRelationshipCode.SELF,
    }


# =============================================================================
# create()
# =============================================================================


def test_create_emits_create_effect(
    mock_db: dict[str, MagicMock], valid_create_kwargs: dict[str, Any]
) -> None:
    """A minimally valid Coverage.create() emits CREATE_COVERAGE with the
    expected payload shape.
    """
    effect = Coverage(**valid_create_kwargs).create()

    assert effect.type == EffectType.CREATE_COVERAGE
    payload = json.loads(effect.payload)
    data = payload["data"]
    assert data["patient_id"] == "abc-patient"
    assert data["issuer_id"] == "issuer-uuid"
    assert data["id_number"] == "MEM-001"
    assert data["coverage_rank"] == int(CoverageRank.PRIMARY)
    assert data["plan_type"] == CoverageType.COMMERCIAL.value
    assert data["patient_relationship_to_subscriber"] == CoverageRelationshipCode.SELF.value


def test_create_includes_upload_keys(
    mock_db: dict[str, MagicMock], valid_create_kwargs: dict[str, Any]
) -> None:
    """Card upload keys are passed through to the payload verbatim."""
    front_key = "plugin-uploads/my_plugin/20260519T000000Z-aaa-front.jpg"
    back_key = "plugin-uploads/my_plugin/20260519T000000Z-bbb-back.jpg"
    effect = Coverage(
        **valid_create_kwargs,
        card_image_front_upload_key=front_key,
        card_image_back_upload_key=back_key,
    ).create()

    data = json.loads(effect.payload)["data"]
    assert data["card_image_front_upload_key"] == front_key
    assert data["card_image_back_upload_key"] == back_key


def test_create_rejects_upload_key_outside_plugin_uploads_prefix(
    mock_db: dict[str, MagicMock], valid_create_kwargs: dict[str, Any]
) -> None:
    """Keys that don't start with plugin-uploads/ are rejected at validate
    time rather than at the platform boundary.
    """
    bad = Coverage(
        **valid_create_kwargs,
        card_image_front_upload_key="some-other-bucket/path/front.jpg",
    )
    with pytest.raises(ValidationError):
        bad.create()


def test_create_missing_required_fields_raises(
    mock_db: dict[str, MagicMock],
) -> None:
    """Each required-on-create field is enforced."""
    incomplete = Coverage(patient_id="abc-patient")
    with pytest.raises(ValidationError):
        incomplete.create()


def test_create_rejects_explicit_coverage_id(
    mock_db: dict[str, MagicMock], valid_create_kwargs: dict[str, Any]
) -> None:
    """coverage_id must not be set on create."""
    bad = Coverage(**valid_create_kwargs, coverage_id="some-uuid")
    with pytest.raises(ValidationError):
        bad.create()


def test_create_rejects_self_subscriber_mismatch(
    mock_db: dict[str, MagicMock], valid_create_kwargs: dict[str, Any]
) -> None:
    """SELF relationship with a non-matching subscriber_id is rejected."""
    bad_kwargs = dict(valid_create_kwargs)
    bad_kwargs["subscriber_id"] = "different-patient"
    with pytest.raises(ValidationError):
        Coverage(**bad_kwargs).create()


def test_create_rejects_unknown_patient(
    mock_db: dict[str, MagicMock], valid_create_kwargs: dict[str, Any]
) -> None:
    """A patient_id that doesn't match any patient is rejected."""
    mock_db["patient"].filter.return_value.exists.return_value = False
    with pytest.raises(ValidationError):
        Coverage(**valid_create_kwargs).create()


# =============================================================================
# update()
# =============================================================================


def test_update_emits_update_effect_with_partial_fields(
    mock_db: dict[str, MagicMock],
) -> None:
    """A partial update only carries fields explicitly set on the instance."""
    effect = Coverage(
        coverage_id="cov-1",
        card_image_back_upload_key="plugin-uploads/my_plugin/back.jpg",
    ).update()

    assert effect.type == EffectType.UPDATE_COVERAGE
    data = json.loads(effect.payload)["data"]
    assert data["coverage_id"] == "cov-1"
    assert data["card_image_back_upload_key"] == "plugin-uploads/my_plugin/back.jpg"
    # Other fields not set on the instance should not appear in the payload.
    assert "card_image_front_upload_key" not in data
    assert "plan" not in data


def test_update_requires_coverage_id(mock_db: dict[str, MagicMock]) -> None:
    """coverage_id is required on update."""
    with pytest.raises(ValidationError):
        Coverage(plan="Gold").update()


def test_update_rejects_unknown_coverage_id(
    mock_db: dict[str, MagicMock],
) -> None:
    """A coverage_id pointing at no row is rejected."""
    mock_db["coverage"].filter.return_value.exists.return_value = False
    with pytest.raises(ValidationError):
        Coverage(coverage_id="missing", plan="Gold").update()


# =============================================================================
# expire()
# =============================================================================


def test_expire_uses_passed_date(mock_db: dict[str, MagicMock]) -> None:
    """A date passed to .expire(...) takes precedence and lands in the payload."""
    end = date(2026, 5, 31)
    effect = Coverage(coverage_id="cov-1").expire(coverage_end_date=end)

    assert effect.type == EffectType.EXPIRE_COVERAGE
    data = json.loads(effect.payload)["data"]
    assert data["coverage_id"] == "cov-1"
    assert data["coverage_end_date"] == "2026-05-31"


def test_expire_uses_instance_date_when_no_arg(
    mock_db: dict[str, MagicMock],
) -> None:
    """If no date is passed to .expire(), the instance's coverage_end_date is used."""
    effect = Coverage(coverage_id="cov-1", coverage_end_date=date(2026, 1, 1)).expire()
    data = json.loads(effect.payload)["data"]
    assert data["coverage_end_date"] == "2026-01-01"


def test_expire_requires_coverage_end_date(
    mock_db: dict[str, MagicMock],
) -> None:
    """coverage_end_date must be present somewhere."""
    with pytest.raises(ValidationError):
        Coverage(coverage_id="cov-1").expire()


# =============================================================================
# remove() and remove_photo()
# =============================================================================


def test_remove_emits_remove_effect(mock_db: dict[str, MagicMock]) -> None:
    """remove() carries only the coverage_id."""
    effect = Coverage(coverage_id="cov-1").remove()
    assert effect.type == EffectType.REMOVE_COVERAGE
    data = json.loads(effect.payload)["data"]
    assert data == {"coverage_id": "cov-1"}


def test_remove_photo_front(mock_db: dict[str, MagicMock]) -> None:
    """remove_photo accepts the PhotoSide enum and emits REMOVE_COVERAGE_PHOTO."""
    effect = Coverage(coverage_id="cov-1").remove_photo(PhotoSide.FRONT)
    assert effect.type == EffectType.REMOVE_COVERAGE_PHOTO
    data = json.loads(effect.payload)["data"]
    assert data == {"coverage_id": "cov-1", "side": "FRONT"}


def test_remove_photo_accepts_string(mock_db: dict[str, MagicMock]) -> None:
    """remove_photo also accepts the literal 'BACK'/'FRONT' strings."""
    effect = Coverage(coverage_id="cov-1").remove_photo("BACK")
    assert effect.type == EffectType.REMOVE_COVERAGE_PHOTO
    data = json.loads(effect.payload)["data"]
    assert data["side"] == "BACK"


def test_remove_photo_rejects_invalid_side(
    mock_db: dict[str, MagicMock],
) -> None:
    """remove_photo rejects sides other than FRONT/BACK."""
    with pytest.raises(ValueError):
        Coverage(coverage_id="cov-1").remove_photo("MIDDLE")


# =============================================================================
# CoverageReorder
# =============================================================================


def test_reorder_apply_emits_reorder_effect(mock_db: dict[str, MagicMock]) -> None:
    """A two-coverage in-use reorder produces REORDER_COVERAGE with normalized
    string coverage IDs.
    """
    effect = CoverageReorder(
        patient_id="abc-patient",
        ordering=[
            {"coverage_id": "cov-1", "coverage_rank": 1, "stack": "IN_USE"},
            {"coverage_id": "cov-2", "coverage_rank": 2, "stack": "IN_USE"},
        ],
    ).apply()

    assert effect.type == EffectType.REORDER_COVERAGE
    data = json.loads(effect.payload)["data"]
    assert data["patient_id"] == "abc-patient"
    assert data["ordering"] == [
        {"coverage_id": "cov-1", "coverage_rank": 1, "stack": "IN_USE"},
        {"coverage_id": "cov-2", "coverage_rank": 2, "stack": "IN_USE"},
    ]


def test_reorder_rejects_duplicate_coverage_ids(
    mock_db: dict[str, MagicMock],
) -> None:
    """The same coverage_id cannot appear in two ordering entries."""
    with pytest.raises(ValidationError):
        CoverageReorder(
            patient_id="abc-patient",
            ordering=[
                {"coverage_id": "cov-1", "coverage_rank": 1, "stack": "IN_USE"},
                {"coverage_id": "cov-1", "coverage_rank": 2, "stack": "IN_USE"},
            ],
        ).apply()


def test_reorder_rejects_non_consecutive_ranks(
    mock_db: dict[str, MagicMock],
) -> None:
    """Within a stack, ranks must be consecutive starting at 1."""
    with pytest.raises(ValidationError):
        CoverageReorder(
            patient_id="abc-patient",
            ordering=[
                {"coverage_id": "cov-1", "coverage_rank": 1, "stack": "IN_USE"},
                {"coverage_id": "cov-2", "coverage_rank": 3, "stack": "IN_USE"},
            ],
        ).apply()


def test_reorder_rejects_unknown_stack(mock_db: dict[str, MagicMock]) -> None:
    """Stack values other than IN_USE/OTHER/REMOVED are rejected."""
    with pytest.raises(ValidationError):
        CoverageReorder(
            patient_id="abc-patient",
            ordering=[
                {"coverage_id": "cov-1", "coverage_rank": 1, "stack": "MAYBE"},
            ],
        ).apply()


def test_reorder_requires_patient_id(mock_db: dict[str, MagicMock]) -> None:
    """patient_id is required."""
    with pytest.raises(ValidationError):
        CoverageReorder(
            ordering=[
                {"coverage_id": "cov-1", "coverage_rank": 1, "stack": "IN_USE"},
            ],
        ).apply()


def test_reorder_requires_ordering(mock_db: dict[str, MagicMock]) -> None:
    """Ordering must contain at least one entry."""
    with pytest.raises(ValidationError):
        CoverageReorder(patient_id="abc-patient", ordering=[]).apply()
