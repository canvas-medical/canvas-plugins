import pytest

from canvas_sdk.test_utils.factories import (
    CampaignFactory,
    InterventionFactory,
    LetterTemplateFactory,
    PatientFactory,
    StaffFactory,
)
from canvas_sdk.v1.data import Intervention


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
    """intervention.patients and patient.interventions traverse api_intervention_patients."""
    first, second = PatientFactory.create_batch(2)
    intervention = InterventionFactory.create()
    intervention.patients.add(first, second)
    other = InterventionFactory.create()
    other.patients.add(first)

    assert set(intervention.patients.all()) == {first, second}
    assert set(first.interventions.all()) == {intervention, other}
    assert list(Intervention.objects.filter(patients=second)) == [intervention]
