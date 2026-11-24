import pytest

from canvas_sdk.test_utils.factories import ContentTypeFactory, PatientFactory, ProvenanceFactory
from canvas_sdk.v1.data import Provenance
from canvas_sdk.v1.data.provenance import ProvenanceAction, ProvenanceParticipantType


@pytest.mark.django_db
def test_provenance_is_read_through_its_patient() -> None:
    """A patient's provenance records read their action, agent and generic links."""
    patient = PatientFactory.create()
    provenance = ProvenanceFactory.create(
        patient=patient,
        action=ProvenanceAction.UPDATED,
        agent_participation_type=ProvenanceParticipantType.PERFORMER,
        target_object_id=42,
    )
    ProvenanceFactory.create()

    fetched = Provenance.objects.get(patient=patient)

    assert fetched.id == provenance.id
    assert fetched.action == ProvenanceAction.UPDATED
    assert fetched.agent_participation_type == ProvenanceParticipantType.PERFORMER
    assert fetched.target_object_type == provenance.target_object_type
    assert fetched.target_object_id == 42
    assert fetched.agent_object_type == provenance.agent_object_type
    assert fetched.on_behalf_of_object_type is None
    assert list(patient.provenance_set.all()) == [fetched]


@pytest.mark.django_db
def test_provenance_default_manager_hides_rows_with_a_disallowed_target_type() -> None:
    """Rows targeting a type no valid Provenance points at are hidden, also from the patient."""
    patient = PatientFactory.create()
    valid = ProvenanceFactory.create(patient=patient)
    ProvenanceFactory.create(
        target_object_type=ContentTypeFactory.create(model="note"), patient=patient
    )

    assert list(Provenance.objects.all()) == [valid]
    assert list(patient.provenance_set.all()) == [valid]
