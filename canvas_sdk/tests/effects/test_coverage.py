"""Tests for the Coverage and CoverageReorder effects."""

import json
import uuid
from datetime import date, timedelta
from typing import Any

import pytest
from freezegun import freeze_time
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects import Effect
from canvas_sdk.effects.coverage import (
    Coverage,
    CoverageReorder,
    CoverageReorderEntry,
    PhotoSide,
    _today,
)
from canvas_sdk.test_utils.factories import CoverageFactory, PatientFactory
from canvas_sdk.v1.data import Coverage as CoverageModel
from canvas_sdk.v1.data import Patient, Transactor
from canvas_sdk.v1.data.coverage import (
    CoverageRank,
    CoverageRelationshipCode,
    CoverageStack,
    TransactorAddress,
)

UPLOAD_KEY = "customer/plugin-uploads/my_plugin/20261014T120000Z-abc-front.jpg"
MISSING_ID = uuid.UUID("00000000-0000-0000-0000-000000000000")


def _transactor(name: str) -> Transactor:
    return Transactor.objects.create(
        payer_id=name,
        name=name,
        type="",
        transactor_type="commercial",
        clearinghouse_payer=True,
        state="active",
        description="",
        active=True,
        use_provider_for_eligibility=False,
        coverage_types=[],
    )


def _address(payer: Transactor) -> TransactorAddress:
    return TransactorAddress.objects.create(
        transactor=payer,
        line1="1 Main St",
        line2="",
        city="Springfield",
        district="",
        state_code="CA",
        postal_code="94000",
        use="work",
        type="both",
        country="US",
        state="active",
    )


@pytest.fixture
def patient() -> Patient:
    """A patient to attach coverages to."""
    return PatientFactory.create()


@pytest.fixture
def payer() -> Transactor:
    """A payer to use as the coverage issuer."""
    return _transactor("Acme Health")


@pytest.fixture
def coverage(patient: Patient) -> CoverageModel:
    """An existing self-subscribed primary coverage that started a year ago."""
    return CoverageFactory.create(
        patient=patient,
        subscriber=patient,
        patient_relationship_to_subscriber=CoverageRelationshipCode.SELF,
        coverage_start_date=date.today() - timedelta(days=365),
    )


def _create_kwargs(
    patient: Patient,
    payer: Transactor,
    **overrides: Any,
) -> dict[str, Any]:
    return {
        "patient_id": patient.id,
        "issuer_id": payer.id,
        "coverage_rank": CoverageRank.SECONDARY,
        "id_number": "ABC123",
        "patient_relationship_to_subscriber": CoverageRelationshipCode.SELF,
        **overrides,
    }


def _payload(effect: Effect) -> dict[str, Any]:
    return json.loads(effect.payload)["data"]


@pytest.mark.django_db
def test_create_sends_required_and_explicitly_set_fields(
    patient: Patient,
    payer: Transactor,
) -> None:
    """create() sends the required fields plus only the optional fields that were set."""
    effect = Coverage(
        **_create_kwargs(patient, payer),
        group="G-1",
        coverage_start_date=date(
            2026,
            1,
            1,
        ),
        card_image_front_upload_key=UPLOAD_KEY,
    ).create()

    assert effect.type == EffectType.CREATE_COVERAGE
    assert _payload(effect) == {
        "patient_id": patient.id,
        "issuer_id": str(payer.id),
        "coverage_rank": 2,
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
        **_create_kwargs(
            patient,
            payer,
            coverage_rank=2,
            patient_relationship_to_subscriber="18",
        )
    ).create()

    data = _payload(effect)
    assert data["coverage_rank"] == 2
    assert data["patient_relationship_to_subscriber"] == "18"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "missing",
    ["patient_id", "issuer_id", "coverage_rank", "id_number", "patient_relationship_to_subscriber"],
)
def test_create_requires_fields(
    patient: Patient,
    payer: Transactor,
    missing: str,
) -> None:
    """create() rejects a coverage missing any required field."""
    kwargs = _create_kwargs(patient, payer)
    del kwargs[missing]

    with pytest.raises(ValidationError, match=f"Field '{missing}' is required"):
        Coverage(**kwargs).create()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "field, value",
    [("id_number", ""), ("stack", None), ("subscriber_id", None), ("coverage_start_date", None)],
)
def test_create_rejects_blank_values(
    patient: Patient,
    payer: Transactor,
    field: str,
    value: Any,
) -> None:
    """A field set to None or an empty string is rejected on create, as on update."""
    with pytest.raises(ValidationError, match=f"Field '{field}'"):
        Coverage(
            **_create_kwargs(
                patient,
                payer,
                **{field: value},
            )
        ).create()


@pytest.mark.django_db
def test_create_rejects_coverage_id(
    patient: Patient,
    payer: Transactor,
    coverage: CoverageModel,
) -> None:
    """create() rejects a coverage_id."""
    with pytest.raises(ValidationError, match="'coverage_id' should not be set"):
        Coverage(**_create_kwargs(patient, payer), coverage_id=coverage.id).create()


@pytest.mark.django_db
def test_create_rejects_unknown_patient_and_payer(patient: Patient, payer: Transactor) -> None:
    """create() reports a patient or payer that does not exist."""
    kwargs = _create_kwargs(
        patient,
        payer,
        patient_id="0" * 32,
        issuer_id=MISSING_ID,
    )

    with pytest.raises(ValidationError) as exc_info:
        Coverage(**kwargs).create()

    message = str(exc_info.value)
    assert f"No patient has id {'0' * 32}." in message
    assert f"No payer has id {MISSING_ID}." in message


@pytest.mark.django_db
def test_create_rejects_a_taken_rank(patient: Patient, payer: Transactor) -> None:
    """A rank already held by an active coverage in the stack is rejected."""
    CoverageFactory.create(patient=patient, coverage_rank=2)

    with pytest.raises(ValidationError, match="already has an active IN_USE coverage with rank 2"):
        Coverage(**_create_kwargs(patient, payer)).create()


@pytest.mark.django_db
def test_create_allows_the_rank_of_an_ended_coverage(patient: Patient, payer: Transactor) -> None:
    """A coverage that ends today or earlier does not hold its rank, so it can be replaced today."""
    CoverageFactory.create(patient=patient, coverage_rank=2, coverage_end_date=_today())

    Coverage(**_create_kwargs(patient, payer)).create()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "relationship, subscriber, message",
    [
        (CoverageRelationshipCode.SELF, "someone-else", "must be omitted or equal the patient"),
        (CoverageRelationshipCode.SPOUSE, None, "must name someone other than the patient"),
        (CoverageRelationshipCode.SPOUSE, "PATIENT", "must name someone other than the patient"),
    ],
)
def test_create_enforces_the_subscriber_rules(
    patient: Patient,
    payer: Transactor,
    relationship: CoverageRelationshipCode,
    subscriber: str | None,
    message: str,
) -> None:
    """The subscriber is the patient exactly when the relationship is SELF, as in the chart."""
    kwargs = _create_kwargs(
        patient,
        payer,
        patient_relationship_to_subscriber=relationship,
    )
    if subscriber is not None:
        kwargs["subscriber_id"] = patient.id if subscriber == "PATIENT" else subscriber

    with pytest.raises(ValidationError, match=message):
        Coverage(**kwargs).create()


@pytest.mark.django_db
def test_create_names_a_dependent_subscriber(patient: Patient, payer: Transactor) -> None:
    """A dependent coverage sends the subscriber."""
    subscriber = PatientFactory.create()
    kwargs = _create_kwargs(
        patient,
        payer,
        patient_relationship_to_subscriber=CoverageRelationshipCode.SPOUSE,
        subscriber_id=subscriber.id,
    )

    assert _payload(Coverage(**kwargs).create())["subscriber_id"] == subscriber.id


@pytest.mark.django_db
def test_create_rejects_an_end_date_before_the_start(patient: Patient, payer: Transactor) -> None:
    """The start date must be on or before the end date, as in the chart."""
    kwargs = _create_kwargs(
        patient,
        payer,
        coverage_start_date=date(
            2026,
            6,
            1,
        ),
        coverage_end_date=date(
            2026,
            1,
            1,
        ),
    )

    with pytest.raises(ValidationError, match="start date must be on or before its end date"):
        Coverage(**kwargs).create()


@pytest.mark.django_db
def test_create_rejects_another_payers_address(patient: Patient, payer: Transactor) -> None:
    """The payer address must belong to the coverage's payer."""
    other_address = _address(_transactor("Other Health"))

    with pytest.raises(ValidationError, match="'issuer_address_id' must belong"):
        Coverage(**_create_kwargs(patient, payer), issuer_address_id=other_address.id).create()

    Coverage(**_create_kwargs(patient, payer), issuer_address_id=_address(payer).id).create()


@pytest.mark.django_db
@pytest.mark.parametrize("key", ["", "some/other/prefix/front.jpg", "front.jpg"])
def test_create_rejects_keys_outside_plugin_uploads(
    patient: Patient,
    payer: Transactor,
    key: str,
) -> None:
    """Card upload keys must come from a file_uploads='stored' route."""
    with pytest.raises(ValidationError, match="card_image_back_upload_key"):
        Coverage(**_create_kwargs(patient, payer), card_image_back_upload_key=key).create()


@pytest.mark.django_db
def test_create_rejects_the_removed_stack(patient: Patient, payer: Transactor) -> None:
    """The removed stack is only reachable through remove()."""
    with pytest.raises(ValidationError, match="Use remove"):
        Coverage(**_create_kwargs(patient, payer), stack=CoverageStack.REMOVED).create()


def test_unknown_fields_are_rejected() -> None:
    """A misspelled or unsupported field fails instead of being dropped."""
    with pytest.raises(ValidationError, match="plan_type"):
        Coverage(plan_type="medicare")  # type: ignore[call-arg]


def test_ids_must_be_uuids() -> None:
    """A malformed id fails validation instead of reaching the database."""
    with pytest.raises(ValidationError, match="coverage_id"):
        Coverage(coverage_id="coverage-id")  # type: ignore[arg-type]


def test_text_fields_fit_their_columns() -> None:
    """Values longer than their database column are rejected."""
    with pytest.raises(ValidationError, match="id_number"):
        Coverage(id_number="x" * 101)


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
    effect = Coverage(
        coverage_id=coverage.id,
        coverage_end_date=None,
        group=None,
    ).update()

    assert _payload(effect) == {
        "coverage_id": str(coverage.id),
        "coverage_end_date": None,
        "group": None,
    }


@pytest.mark.django_db
def test_update_never_sends_a_rejected_assignment(coverage: CoverageModel) -> None:
    """A value that failed validation is not sent as a null that would clear the field."""
    effect = Coverage(coverage_id=coverage.id, id_number="NEW")
    with pytest.raises(ValidationError):
        effect.coverage_end_date = "not a date"  # type: ignore[assignment]

    assert _payload(effect.update()) == {"coverage_id": str(coverage.id), "id_number": "NEW"}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "field, value",
    [
        ("issuer_id", None),
        ("coverage_rank", None),
        ("id_number", None),
        ("id_number", ""),
        ("patient_relationship_to_subscriber", None),
        ("stack", None),
        ("subscriber_id", None),
        ("subscriber_id", ""),
        ("coverage_start_date", None),
    ],
)
def test_update_rejects_blank_values_for_required_fields(
    coverage: CoverageModel,
    field: str,
    value: Any,
) -> None:
    """Required fields cannot be cleared on update."""
    with pytest.raises(ValidationError, match=f"Field '{field}'"):
        Coverage(coverage_id=coverage.id, **{field: value}).update()


@pytest.mark.django_db
def test_update_rejects_patient_change(coverage: CoverageModel, patient: Patient) -> None:
    """A coverage cannot be moved to another patient."""
    with pytest.raises(ValidationError, match="'patient_id' cannot be changed"):
        Coverage(coverage_id=coverage.id, patient_id=patient.id).update()


@pytest.mark.django_db
def test_update_checks_the_subscriber_rules_against_the_stored_coverage(
    coverage: CoverageModel,
) -> None:
    """Making a self coverage a dependent one needs a subscriber other than the patient."""
    with pytest.raises(ValidationError, match="must name someone other than the patient"):
        Coverage(
            coverage_id=coverage.id,
            patient_relationship_to_subscriber=CoverageRelationshipCode.SPOUSE,
        ).update()


@pytest.mark.django_db
def test_update_checks_dates_against_the_stored_coverage(coverage: CoverageModel) -> None:
    """An end date before the stored start date is rejected."""
    with pytest.raises(ValidationError, match="start date must be on or before its end date"):
        Coverage(
            coverage_id=coverage.id, coverage_end_date=date.today() - timedelta(days=400)
        ).update()


@pytest.mark.django_db
def test_update_rejects_moving_to_the_removed_stack(coverage: CoverageModel) -> None:
    """update() cannot remove a coverage."""
    with pytest.raises(ValidationError, match="Use remove"):
        Coverage(coverage_id=coverage.id, stack=CoverageStack.REMOVED).update()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method, kwargs",
    [
        ("update", {}),
        (
            "expire",
            {
                "coverage_end_date": date(
                    2026,
                    12,
                    31,
                )
            },
        ),
        ("remove", {}),
        ("remove_photo", {"side": PhotoSide.FRONT}),
    ],
)
def test_requires_existing_coverage(method: str, kwargs: dict[str, Any]) -> None:
    """Every method acting on a coverage needs a coverage_id that exists."""
    with pytest.raises(ValidationError, match="'coverage_id' is required"):
        getattr(Coverage(), method)(**kwargs)
    with pytest.raises(ValidationError, match="No coverage has id"):
        getattr(Coverage(coverage_id=MISSING_ID), method)(**kwargs)


@pytest.mark.django_db
def test_expire(coverage: CoverageModel) -> None:
    """expire() sends the coverage and its end date."""
    effect = Coverage(coverage_id=coverage.id).expire(
        coverage_end_date=date(
            2026,
            12,
            31,
        )
    )

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
    effect = Coverage(coverage_id=coverage.id).remove_photo(side=side)  # type: ignore[arg-type]

    assert effect.type == EffectType.REMOVE_COVERAGE_PHOTO
    assert _payload(effect) == {"coverage_id": str(coverage.id), "side": str(side)}


def test_remove_photo_rejects_unknown_side() -> None:
    """remove_photo() only accepts FRONT or BACK."""
    with pytest.raises(ValueError):
        Coverage(coverage_id=MISSING_ID).remove_photo(side="SIDEWAYS")  # type: ignore[arg-type]


def _entry(
    coverage: CoverageModel,
    rank: int,
    stack: CoverageStack,
) -> CoverageReorderEntry:
    return CoverageReorderEntry(
        coverage_id=coverage.id,
        coverage_rank=CoverageRank(rank),
        stack=stack,
    )


@pytest.mark.django_db
def test_reorder(patient: Patient) -> None:
    """apply() sends each coverage's new rank and stack."""
    first = CoverageFactory.create(patient=patient)
    second = CoverageFactory.create(patient=patient, coverage_rank=2)

    effect = CoverageReorder(
        patient_id=patient.id,
        ordering=[
            _entry(
                second,
                1,
                CoverageStack.IN_USE,
            ),
            _entry(
                first,
                1,
                CoverageStack.OTHER,
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
                _entry(
                    first,
                    1,
                    CoverageStack.IN_USE,
                ),
                _entry(
                    second,
                    3,
                    CoverageStack.IN_USE,
                ),
            ],
        ).apply()


@pytest.mark.django_db
def test_reorder_rejects_duplicate_coverage(patient: Patient, coverage: CoverageModel) -> None:
    """A coverage can appear only once."""
    entry = _entry(
        coverage,
        1,
        CoverageStack.IN_USE,
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
                _entry(
                    coverage,
                    1,
                    CoverageStack.IN_USE,
                )
            ],
        ).apply()


@pytest.mark.django_db
def test_reorder_rejects_the_removed_stack(patient: Patient, coverage: CoverageModel) -> None:
    """The removed stack is only reachable through Coverage.remove()."""
    with pytest.raises(ValidationError, match="Use Coverage.remove"):
        CoverageReorder(
            patient_id=patient.id,
            ordering=[
                _entry(
                    coverage,
                    1,
                    CoverageStack.REMOVED,
                )
            ],
        ).apply()


def test_reorder_rejects_empty_ordering() -> None:
    """At least one coverage is needed."""
    with pytest.raises(ValidationError, match="ordering"):
        CoverageReorder(patient_id="patient", ordering=[])


def test_reorder_entries_validate_reassignment() -> None:
    """Renumbering an entry after construction keeps its values valid."""
    entry = CoverageReorderEntry(
        coverage_id=MISSING_ID, coverage_rank=CoverageRank.PRIMARY, stack=CoverageStack.IN_USE
    )

    entry.coverage_rank = 2  # type: ignore[assignment]

    assert entry.coverage_rank == CoverageRank.SECONDARY
    with pytest.raises(ValidationError):
        entry.coverage_rank = 9  # type: ignore[assignment]


@pytest.mark.django_db
def test_remove_photo_rejects_an_unknown_side(coverage: CoverageModel) -> None:
    """An unknown side is a validation error, like every other invalid input."""
    with pytest.raises(ValidationError, match="Field 'side' must be FRONT or BACK"):
        Coverage(coverage_id=coverage.id).remove_photo(side="front")  # type: ignore[arg-type]


@pytest.mark.django_db
def test_reorder_rejects_an_ordering_that_leaves_out_an_active_coverage(patient: Patient) -> None:
    """Every active coverage of a stack the ordering places a coverage in must be listed."""
    first = CoverageFactory.create(patient=patient, coverage_rank=1)
    second = CoverageFactory.create(patient=patient, coverage_rank=2)
    CoverageFactory.create(patient=patient, coverage_rank=3)

    with pytest.raises(ValidationError, match="must list every active coverage"):
        CoverageReorder(
            patient_id=patient.id,
            ordering=[
                _entry(second, 1, CoverageStack.IN_USE),
                _entry(first, 2, CoverageStack.IN_USE),
            ],
        ).apply()


@pytest.mark.django_db
@freeze_time("2026-10-15 03:00:00")
def test_create_counts_today_in_the_installation_time_zone(
    patient: Patient,
    payer: Transactor,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A coverage ending on the practice's tomorrow keeps its rank, though that is UTC today."""
    monkeypatch.setattr("canvas_sdk.effects.coverage.INSTALLATION_TIME_ZONE", "America/Los_Angeles")
    CoverageFactory.create(
        patient=patient,
        coverage_rank=CoverageRank.SECONDARY,
        coverage_start_date=date(2026, 1, 1),
        coverage_end_date=date(2026, 10, 15),
    )

    with pytest.raises(ValidationError, match="already has an active"):
        Coverage(**_create_kwargs(patient, payer)).create()


@pytest.mark.django_db
def test_create_takes_none_as_no_card_file(patient: Patient, payer: Transactor) -> None:
    """A side passed as None, as when no file was picked, has no file and is not an error."""
    effect = Coverage(
        **_create_kwargs(patient, payer),
        card_image_front_upload_key=f"{patient.id}/plugin-uploads/p/front.png",
        card_image_back_upload_key=None,
    ).create()

    assert _payload(effect)["card_image_back_upload_key"] is None


@pytest.mark.django_db
def test_expire_rejects_an_end_date_before_the_start(coverage: CoverageModel) -> None:
    """expire() holds the end date to the same order rule as update()."""
    before_start = coverage.coverage_start_date - timedelta(days=1)

    with pytest.raises(ValidationError, match="start date must be on or before its end date"):
        Coverage(coverage_id=coverage.id).expire(coverage_end_date=before_start)


@pytest.mark.django_db
def test_expire_accepts_an_end_date_on_the_start(coverage: CoverageModel) -> None:
    """A coverage can end on the day it starts."""
    effect = Coverage(coverage_id=coverage.id).expire(
        coverage_end_date=coverage.coverage_start_date
    )

    assert _payload(effect)["coverage_end_date"] == coverage.coverage_start_date.isoformat()
