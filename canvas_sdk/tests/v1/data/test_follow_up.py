import pytest
from django.db import models

from canvas_sdk.test_utils.factories import FollowUpFactory
from canvas_sdk.v1.data.follow_up import FollowUp


def test_follow_up_exposes_scheduling_fields() -> None:
    """FollowUp exposes the requested date, reason for visit, and comment fields."""
    assert isinstance(FollowUp._meta.get_field("requested_appointment_date"), models.DateField)
    assert isinstance(FollowUp._meta.get_field("reason_for_visit"), models.TextField)
    assert isinstance(FollowUp._meta.get_field("internal_comment"), models.TextField)


@pytest.mark.django_db
def test_follow_up_factory_builds_and_links_to_patient() -> None:
    """The SDK FollowUpFactory creates a FollowUp reachable via patient.follow_ups."""
    follow_up = FollowUpFactory.create(reason_for_visit="6 month recheck")

    assert follow_up.reason_for_visit == "6 month recheck"
    assert follow_up.patient_id is not None
    assert follow_up.note_id is not None
    assert list(follow_up.patient.follow_ups.all()) == [follow_up]
