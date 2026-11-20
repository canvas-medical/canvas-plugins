import pytest

from canvas_sdk.test_utils.factories import (
    CampaignFactory,
    InterventionFactory,
    LetterTemplateFactory,
    PatientFactory,
    StaffFactory,
    SuspectHCCFactory,
)
from canvas_sdk.v1.data import Intervention, SuspectHCC, SuspectHCCKind, SuspectHCCStatus


@pytest.mark.django_db
def test_patient_suspect_hccs_filters_by_status_and_kind() -> None:
    """patient.suspect_hccs returns the patient's suspected HCCs, filterable by status and kind."""
    patient = PatientFactory.create()
    active = SuspectHCCFactory.create(
        patient=patient,
        kind=SuspectHCCKind.PREVIOUS_CONDITION,
        previous_condition="Bitten by orca, sequela (W56.21XS)",
        reasons=["Diagnosis: Coded last year"],
    )
    SuspectHCCFactory.create(patient=patient, status=SuspectHCCStatus.INACTIVE)
    SuspectHCCFactory.create()

    fetched = patient.suspect_hccs.get(status=SuspectHCCStatus.ACTIVE)

    assert fetched == active
    assert fetched.kind == SuspectHCCKind.PREVIOUS_CONDITION
    assert fetched.reasons == ["Diagnosis: Coded last year"]
    assert patient.suspect_hccs.count() == 2
    assert SuspectHCC.objects.count() == 3


@pytest.mark.django_db
def test_campaign_interventions_resolve_template_and_author() -> None:
    """campaign.interventions lists its steps, each with its letter template and author."""
    campaign = CampaignFactory.create(protocol_id=42)
    template = LetterTemplateFactory.create()
    author = StaffFactory.create()
    intervention = InterventionFactory.create(campaign=campaign, template=template, author=author)
    InterventionFactory.create()

    fetched = campaign.interventions.get()

    assert fetched == intervention
    assert fetched.campaign.protocol_id == 42
    assert list(template.interventions.all()) == [intervention]
    assert list(author.interventions.all()) == [intervention]


@pytest.mark.django_db
def test_intervention_patients_is_many_to_many() -> None:
    """intervention.patients and patient.intervention_set traverse api_intervention_patients."""
    first, second = PatientFactory.create_batch(2)
    intervention = InterventionFactory.create()
    intervention.patients.add(first, second)
    other = InterventionFactory.create()
    other.patients.add(first)

    assert set(intervention.patients.all()) == {first, second}
    assert set(first.intervention_set.all()) == {intervention, other}
    assert list(Intervention.objects.filter(patients=second)) == [intervention]
