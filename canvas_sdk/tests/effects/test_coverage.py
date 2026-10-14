"""Tests for the Coverage and CoverageReorder effects."""

import json
from datetime import date
from typing import Any

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.coverage import Coverage, CoverageReorder, CoverageReorderEntry, PhotoSide
from canvas_sdk.test_utils.factories import CoverageFactory, PatientFactory
from canvas_sdk.v1.data import Coverage as CoverageModel
from canvas_sdk.v1.data import Patient, Transactor
from canvas_sdk.v1.data.coverage import CoverageRank, CoverageRelationshipCode, CoverageStack

UPLOAD_KEY = "customer/plugin-uploads/my_plugin/20261014T120000Z-abc-front.jpg"


@pytest.fixture
def patient() -> Patient:
    """A patient to attach coverages to."""
    return PatientFactory.create()


@pytest.fixture
def payer() -> Transactor:
    """A payer to use as the coverage issuer."""
    return Transactor.objects.create(
        payer_id="12345",
        name="Acme Health",
        type="",
        transactor_type="commercial",
        clearinghouse_payer=True,
        state="active",
        description="",
        active=True,
        use_provider_for_eligibility=False,
        coverage_types=[],
    )


@pytest.fixture
def coverage(patient: Patient) -> CoverageModel:
    """An existing coverage."""
    return CoverageFactory.create(patient=patient)


def _create_kwargs(patient: Patient, payer: Transactor, **overrides: Any) -> dict[str, Any]:
    return {
        "patient_id": patient.id,
        "issuer_id": payer.id,
        "coverage_rank": CoverageRank.PRIMARY,
        "id_number": "ABC123",
        "patient_relationship_to_subscriber": CoverageRelationshipCode.SELF,
        **overrides,
    }


def _payload(effect: Any) -> dict[str, Any]:
    return json.loads(effect.payload)["data"]


@pytest.mark.django_db
def test_create_sends_required_and_explicitly_set_fields(
    patient: Patient, payer: Transactor
) -> None:
    """create() sends the required fields plus only the optional fields that were set."""
    effect = Coverage(
        **_create_kwargs(patient, payer),
        group="G-1",
        coverage_start_date=date(2026, 1, 1),
        card_image_front_upload_key=UPLOAD_KEY,
    ).create()

    assert effect.type == EffectType.CREATE_COVERAGE
    assert _payload(effect) == {
        "patient_id": patient.id,
        "issuer_id": str(payer.id),
        "coverage_rank": 1,
        "id_number": "ABC123",
        "patient_relationship_to_subscriber": "18",
        "group": "G-1",
        "coverage_start_date": "2026-01-01",
        "card_image_front_upload_key": UPLOAD_KEY,
    }


@pytest.mark.django_db
def test_create_accepts_raw_choice_values(patient: Patient, payer: Transactor) -> None:
    """Enum fields accept their raw values as well as the enum members."""
    effect = Coverage(
        **_create_kwargs(patient, payer, coverage_rank=2, patient_relationship_to_subscriber="18")
    ).create()

    data = _payload(effect)
    assert data["coverage_rank"] == 2
    assert data["patient_relationship_to_subscriber"] == "18"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "missing",
    ["patient_id", "issuer_id", "coverage_rank", "id_number", "patient_relationship_to_subscriber"],
)
def test_create_requires_fields(patient: Patient, payer: Transactor, missing: str) -> None:
    """create() rejects a coverage missing any required field."""
    kwargs = _create_kwargs(patient, payer)
    del kwargs[missing]

    with pytest.raises(ValidationError, match=f"Field '{missing}' is required"):
        Coverage(**kwargs).create()


@pytest.mark.django_db
def test_create_rejects_coverage_id(
    patient: Patient, payer: Transactor, coverage: CoverageModel
) -> None:
    """create() rejects a coverage_id."""
    with pytest.raises(ValidationError, match="'coverage_id' should not be set"):
        Coverage(**_create_kwargs(patient, payer), coverage_id=coverage.id).create()


@pytest.mark.django_db
def test_create_rejects_unknown_patient_and_payer(patient: Patient, payer: Transactor) -> None:
    """create() reports a patient or payer that does not exist."""
    kwargs = _create_kwargs(
        patient, payer, patient_id="0" * 32, issuer_id="00000000-0000-0000-0000-000000000000"
    )

    with pytest.raises(ValidationError) as exc_info:
        Coverage(**kwargs).create()

    message = str(exc_info.value)
    assert "Patient with id" in message
    assert "Payer with id" in message


@pytest.mark.django_db
def test_create_rejects_other_subscriber_for_self(patient: Patient, payer: Transactor) -> None:
    """When the patient is the subscriber, subscriber_id must be the patient."""
    with pytest.raises(ValidationError, match="'subscriber_id' must be omitted"):
        Coverage(**_create_kwargs(patient, payer), subscriber_id="someone-else").create()


@pytest.mark.django_db
def test_create_requires_subscriber_for_dependents(patient: Patient, payer: Transactor) -> None:
    """When the patient is not the subscriber, the subscriber must be named."""
    kwargs = _create_kwargs(
        patient, payer, patient_relationship_to_subscriber=CoverageRelationshipCode.SPOUSE
    )

    with pytest.raises(ValidationError, match="'subscriber_id' is required"):
        Coverage(**kwargs).create()

    subscriber = PatientFactory.create()
    effect = Coverage(**kwargs, subscriber_id=subscriber.id).create()
    assert _payload(effect)["subscriber_id"] == subscriber.id


@pytest.mark.django_db
@pytest.mark.parametrize("key", ["", "some/other/prefix/front.jpg", "front.jpg"])
def test_create_rejects_keys_outside_plugin_uploads(
    patient: Patient, payer: Transactor, key: str
) -> None:
    """Card upload keys must come from a file_uploads='stored' route."""
    with pytest.raises(ValidationError, match="card_image_back_upload_key"):
        Coverage(**_create_kwargs(patient, payer), card_image_back_upload_key=key).create()


@pytest.mark.django_db
def test_create_never_sends_plan_type(patient: Patient, payer: Transactor) -> None:
    """The plan type comes from the payer, so it is not a field on the effect."""
    effect = Coverage(**_create_kwargs(patient, payer), plan_type="medicare").create()  # type: ignore[call-arg]

    assert "plan_type" not in _payload(effect)


@pytest.mark.django_db
def test_update_sends_only_set_fields(coverage: CoverageModel) -> None:
    """update() leaves out fields that were never set."""
    effect = Coverage(coverage_id=coverage.id, card_image_back_upload_key=UPLOAD_KEY).update()

    assert effect.type == EffectType.UPDATE_COVERAGE
    assert _payload(effect) == {
        "coverage_id": str(coverage.id),
        "card_image_back_upload_key": UPLOAD_KEY,
    }


@pytest.mark.django_db
def test_update_sends_explicit_none_to_clear(coverage: CoverageModel) -> None:
    """Setting a clearable field to None sends it as null."""
    effect = Coverage(coverage_id=coverage.id, coverage_end_date=None, group=None).update()

    assert _payload(effect) == {
        "coverage_id": str(coverage.id),
        "coverage_end_date": None,
        "group": None,
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    "field",
    [
        "issuer_id",
        "coverage_rank",
        "id_number",
        "patient_relationship_to_subscriber",
        "stack",
        "subscriber_id",
        "coverage_start_date",
        "card_image_front_upload_key",
        "card_image_back_upload_key",
    ],
)
def test_update_rejects_none_for_required_fields(coverage: CoverageModel, field: str) -> None:
    """Required fields cannot be cleared on update."""
    with pytest.raises(ValidationError, match=f"Field '{field}' cannot be set to null"):
        Coverage(coverage_id=coverage.id, **{field: None}).update()


@pytest.mark.django_db
def test_update_rejects_patient_change(coverage: CoverageModel, patient: Patient) -> None:
    """A coverage cannot be moved to another patient."""
    with pytest.raises(ValidationError, match="'patient_id' cannot be changed"):
        Coverage(coverage_id=coverage.id, patient_id=patient.id).update()


@pytest.mark.django_db
@pytest.mark.parametrize("method", ["update", "remove"])
def test_requires_existing_coverage(method: str) -> None:
    """Methods acting on a coverage need a coverage_id that exists."""
    with pytest.raises(ValidationError, match="'coverage_id' is required"):
        getattr(Coverage(), method)()
    with pytest.raises(ValidationError, match="does not exist"):
        getattr(Coverage(coverage_id="00000000-0000-0000-0000-000000000000"), method)()


@pytest.mark.django_db
def test_expire(coverage: CoverageModel) -> None:
    """expire() sends the coverage and its end date."""
    effect = Coverage(coverage_id=coverage.id).expire(coverage_end_date=date(2026, 12, 31))

    assert effect.type == EffectType.EXPIRE_COVERAGE
    assert _payload(effect) == {"coverage_id": str(coverage.id), "coverage_end_date": "2026-12-31"}


@pytest.mark.django_db
def test_expire_requires_end_date(coverage: CoverageModel) -> None:
    """expire() needs an end date."""
    with pytest.raises(ValidationError, match="'coverage_end_date' is required"):
        Coverage(coverage_id=coverage.id).expire()


@pytest.mark.django_db
def test_remove(coverage: CoverageModel) -> None:
    """remove() sends the coverage id."""
    effect = Coverage(coverage_id=coverage.id).remove()

    assert effect.type == EffectType.REMOVE_COVERAGE
    assert _payload(effect) == {"coverage_id": str(coverage.id)}


@pytest.mark.django_db
@pytest.mark.parametrize("side", [PhotoSide.FRONT, "BACK"])
def test_remove_photo(coverage: CoverageModel, side: PhotoSide | str) -> None:
    """remove_photo() sends the coverage id and card side."""
    effect = Coverage(coverage_id=coverage.id).remove_photo(side=PhotoSide(side))

    assert effect.type == EffectType.REMOVE_COVERAGE_PHOTO
    assert _payload(effect) == {"coverage_id": str(coverage.id), "side": str(side)}


def test_remove_photo_rejects_unknown_side() -> None:
    """remove_photo() only accepts FRONT or BACK."""
    with pytest.raises(ValueError):
        Coverage(coverage_id="any").remove_photo(side="SIDEWAYS")  # type: ignore[arg-type]


@pytest.mark.django_db
def test_reorder(patient: Patient) -> None:
    """apply() sends each coverage's new rank and stack."""
    first = CoverageFactory.create(patient=patient)
    second = CoverageFactory.create(patient=patient, coverage_rank=2)

    effect = CoverageReorder(
        patient_id=patient.id,
        ordering=[
            CoverageReorderEntry(
                coverage_id=second.id,
                coverage_rank=CoverageRank.PRIMARY,
                stack=CoverageStack.IN_USE,
            ),
            CoverageReorderEntry(
                coverage_id=first.id, coverage_rank=CoverageRank.PRIMARY, stack=CoverageStack.OTHER
            ),
        ],
    ).apply()

    assert effect.type == EffectType.REORDER_COVERAGE
    assert _payload(effect) == {
        "patient_id": patient.id,
        "ordering": [
            {"coverage_id": str(second.id), "coverage_rank": 1, "stack": "IN_USE"},
            {"coverage_id": str(first.id), "coverage_rank": 1, "stack": "OTHER"},
        ],
    }


@pytest.mark.django_db
def test_reorder_rejects_gaps_in_ranks(patient: Patient) -> None:
    """Ranks within a stack must start at 1 with no gaps."""
    first = CoverageFactory.create(patient=patient)
    second = CoverageFactory.create(patient=patient)

    with pytest.raises(ValidationError, match="unique and consecutive"):
        CoverageReorder(
            patient_id=patient.id,
            ordering=[
                CoverageReorderEntry(
                    coverage_id=first.id,
                    coverage_rank=CoverageRank.PRIMARY,
                    stack=CoverageStack.IN_USE,
                ),
                CoverageReorderEntry(
                    coverage_id=second.id,
                    coverage_rank=CoverageRank.TERTIARY,
                    stack=CoverageStack.IN_USE,
                ),
            ],
        ).apply()


@pytest.mark.django_db
def test_reorder_rejects_duplicate_coverage(patient: Patient, coverage: CoverageModel) -> None:
    """A coverage can appear only once."""
    entry = CoverageReorderEntry(
        coverage_id=coverage.id, coverage_rank=CoverageRank.PRIMARY, stack=CoverageStack.IN_USE
    )

    with pytest.raises(ValidationError, match="more than once"):
        CoverageReorder(patient_id=patient.id, ordering=[entry, entry]).apply()


@pytest.mark.django_db
def test_reorder_rejects_another_patients_coverage(coverage: CoverageModel) -> None:
    """Every coverage must belong to the patient."""
    other_patient = PatientFactory.create()

    with pytest.raises(ValidationError, match="belong to the patient"):
        CoverageReorder(
            patient_id=other_patient.id,
            ordering=[
                CoverageReorderEntry(
                    coverage_id=coverage.id,
                    coverage_rank=CoverageRank.PRIMARY,
                    stack=CoverageStack.IN_USE,
                )
            ],
        ).apply()


@pytest.mark.django_db
def test_reorder_rejects_empty_ordering(patient: Patient) -> None:
    """At least one coverage is needed."""
    with pytest.raises(ValidationError, match="at least one coverage"):
        CoverageReorder(patient_id=patient.id, ordering=[]).apply()
