import pytest

from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    CarePlanCodingFactory,
    CarePlanFactory,
    PatientFactory,
)
from canvas_sdk.v1.data import CarePlan, CarePlanCoding, CarePlanIntent, CarePlanStatus


@pytest.mark.django_db
def test_care_plan_is_found_by_id_with_status_and_intent() -> None:
    """A care plan is found by its id, and its status and intent round-trip."""
    care_plan = CarePlanFactory.create(
        status=CarePlanStatus.ON_HOLD, intent=CarePlanIntent.PROPOSAL
    )
    CarePlanFactory.create()

    fetched = CarePlan.objects.get(id=care_plan.id)

    assert fetched.dbid == care_plan.dbid
    assert fetched.status == CarePlanStatus.ON_HOLD
    assert fetched.intent == CarePlanIntent.PROPOSAL
    assert list(CarePlan.objects.filter(status=CarePlanStatus.ON_HOLD)) == [fetched]


@pytest.mark.django_db
def test_for_patient_returns_only_that_patients_care_plan() -> None:
    """for_patient filters by the patient's public id."""
    patient = PatientFactory.create()
    mine = CarePlanFactory.create(patient=patient)
    CarePlanFactory.create()

    assert list(CarePlan.objects.for_patient(patient.id)) == [mine]


@pytest.mark.django_db
def test_care_plan_resolves_patient_originator_and_category() -> None:
    """The patient, originator and category foreign keys resolve, with care_plans reverses."""
    patient = PatientFactory.create()
    originator = CanvasUserFactory.create()
    category = CarePlanCodingFactory.create(code="736353004", display="Inpatient care plan")
    care_plan = CarePlanFactory.create(patient=patient, originator=originator, category=category)
    CarePlanFactory.create()

    fetched = CarePlan.objects.get(id=care_plan.id)

    assert fetched.patient == patient
    assert fetched.originator == originator
    assert fetched.category == category
    assert list(patient.care_plans.all()) == [care_plan]
    assert list(category.care_plans.all()) == [care_plan]


@pytest.mark.django_db
def test_care_plan_category_is_nullable() -> None:
    """A care plan without a category reads back with category None."""
    care_plan = CarePlanFactory.create(category=None)

    assert CarePlan.objects.get(id=care_plan.id).category is None


@pytest.mark.django_db
def test_care_plan_coding_fields_round_trip() -> None:
    """A care plan coding's system, version, code, display and user_selected round-trip."""
    coding = CarePlanCodingFactory.create(version="2024-03", user_selected=True)

    fetched = CarePlanCoding.objects.get(dbid=coding.dbid)

    assert (fetched.system, fetched.version, fetched.code, fetched.display) == (
        "http://snomed.info/sct",
        "2024-03",
        "734163000",
        "Care plan",
    )
    assert fetched.user_selected is True


def test_choices_match_home_app() -> None:
    """Status and intent values match home-app's CarePlanStatus and CarePlanIntent."""
    assert CarePlanStatus.values == [
        "draft",
        "active",
        "on-hold",
        "revoked",
        "completed",
        "entered-in-error",
        "unknown",
    ]
    assert CarePlanIntent.values == ["proposal", "plan", "order", "option"]
