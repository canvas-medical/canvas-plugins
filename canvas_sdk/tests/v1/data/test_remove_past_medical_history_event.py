import pytest
from django.db import models

from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    RemovePastMedicalHistoryEventFactory,
)
from canvas_sdk.v1.data.remove_past_medical_history_event import RemovePastMedicalHistoryEvent


def test_remove_past_medical_history_event_links_to_condition() -> None:
    """The condition FK exposes a `past_medical_history_removals` reverse accessor on Condition."""
    accessor = RemovePastMedicalHistoryEvent._meta.get_field(
        "condition"
    ).remote_field.get_accessor_name()
    assert accessor == "past_medical_history_removals"


def test_remove_past_medical_history_event_fields() -> None:
    """RemovePastMedicalHistoryEvent exposes rationale."""
    assert isinstance(RemovePastMedicalHistoryEvent._meta.get_field("rationale"), models.CharField)


@pytest.mark.django_db
def test_committed_filters_uncommitted_and_entered_in_error() -> None:
    """RemovePastMedicalHistoryEvent.objects.committed() returns only committed, non-EIE rows."""
    committer = CanvasUserFactory.create()
    committed = RemovePastMedicalHistoryEventFactory.create(committer=committer)
    RemovePastMedicalHistoryEventFactory.create(committer=None)
    RemovePastMedicalHistoryEventFactory.create(
        committer=committer, entered_in_error=CanvasUserFactory.create()
    )
    assert set(RemovePastMedicalHistoryEvent.objects.committed()) == {committed}


@pytest.mark.django_db
def test_for_patient_scopes_to_the_patient() -> None:
    """RemovePastMedicalHistoryEvent.objects.for_patient() returns only that patient's removals."""
    event = RemovePastMedicalHistoryEventFactory.create()
    RemovePastMedicalHistoryEventFactory.create()
    assert set(RemovePastMedicalHistoryEvent.objects.for_patient(event.patient.id)) == {event}
