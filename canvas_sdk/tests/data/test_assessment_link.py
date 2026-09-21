import datetime

import pytest

from canvas_sdk.test_utils.factories import NoteFactory, PatientFactory
from canvas_sdk.v1.data import (
    Assessment,
    Condition,
    FollowUp,
    Goal,
    Immunization,
    Instruction,
    Note,
    NoteTask,
    Patient,
    Plan,
    Procedure,
    StopMedicationEvent,
    UpdateGoal,
)
from canvas_sdk.v1.data.base import Model

ASSESSMENT_LINKED_MODELS = (
    FollowUp,
    Goal,
    Immunization,
    Instruction,
    NoteTask,
    Plan,
    Procedure,
    StopMedicationEvent,
    UpdateGoal,
)


@pytest.fixture
def patient(db: None) -> Patient:
    """The patient whose chart the note is on."""
    return PatientFactory.create()


@pytest.fixture
def note(patient: Patient) -> Note:
    """A note on the patient's chart."""
    return NoteFactory.create(patient=patient)


@pytest.mark.parametrize(
    argnames="model",
    argvalues=ASSESSMENT_LINKED_MODELS,
    ids=[model.__name__ for model in ASSESSMENT_LINKED_MODELS],
)
def test_every_linked_anchor_reads_the_views_assessment_column(model: type[Model]) -> None:
    """The column the `canvas_sdk_data_*` views expose is `assessment_id`, and it is nullable."""
    field = model._meta.get_field("assessment")

    assert field.column == "assessment_id"
    assert field.related_model is Assessment
    assert field.null is True


def test_a_linked_command_resolves_through_the_assessment_to_its_condition(
    patient: Patient, note: Note
) -> None:
    """What the link is for: a plan item reaches the condition it addresses in two hops."""
    condition = Condition.objects.create(
        patient=patient,
        deleted=False,
        onset_date=datetime.date(2024, 1, 1),
        resolution_date=datetime.date(2024, 6, 1),
        clinical_status="active",
        notes="",
        surgical=False,
    )
    assessment = Assessment.objects.create(
        patient=patient,
        note=note,
        condition=condition,
        status="stable",
        narrative="Stable on current regimen.",
        background="",
        care_team="",
    )
    instruction = Instruction.objects.create(
        patient=patient, note=note, assessment=assessment, narrative="Rest and fluids"
    )

    stored = Instruction.objects.get(dbid=instruction.dbid)

    assert stored.assessment is not None
    assert stored.assessment.condition == condition
    assert list(assessment.instructions.all()) == [instruction]


def test_an_unlinked_command_is_valid(patient: Patient, note: Note) -> None:
    """A command committed with no link is ordinary, not an incomplete row."""
    instruction = Instruction.objects.create(
        patient=patient, note=note, narrative="Rest and fluids"
    )

    assert Instruction.objects.get(dbid=instruction.dbid).assessment is None
