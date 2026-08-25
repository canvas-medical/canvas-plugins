import pytest
from django.db import models

from canvas_sdk.test_utils.factories import CanvasUserFactory, RemoveAllergyEventFactory
from canvas_sdk.v1.data.remove_allergy_event import RemoveAllergyEvent


def test_remove_allergy_event_links_to_allergy() -> None:
    """The allergy FK exposes a `removeallergyevent_set` reverse accessor on AllergyIntolerance."""
    accessor = RemoveAllergyEvent._meta.get_field("allergy").remote_field.get_accessor_name()
    assert accessor == "removeallergyevent_set"


def test_remove_allergy_event_fields() -> None:
    """RemoveAllergyEvent exposes rationale."""
    assert isinstance(RemoveAllergyEvent._meta.get_field("rationale"), models.CharField)


@pytest.mark.django_db
def test_committed_filters_uncommitted_and_entered_in_error() -> None:
    """RemoveAllergyEvent.objects.committed() returns only committed, non-EIE rows."""
    committer = CanvasUserFactory.create()
    committed = RemoveAllergyEventFactory.create(committer=committer)
    RemoveAllergyEventFactory.create(committer=None)
    RemoveAllergyEventFactory.create(
        committer=committer, entered_in_error=CanvasUserFactory.create()
    )
    assert set(RemoveAllergyEvent.objects.committed()) == {committed}
