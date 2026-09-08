import pytest
from django.db import models

from canvas_sdk.test_utils.factories import CanvasUserFactory, ResolveConditionEventFactory
from canvas_sdk.v1.data.resolve_condition_event import ResolveConditionEvent


def test_resolve_condition_event_links_to_condition_via_resolutions() -> None:
    """The condition FK exposes a `resolutions` reverse accessor on Condition."""
    accessor = ResolveConditionEvent._meta.get_field("condition").remote_field.get_accessor_name()
    assert accessor == "resolutions"


def test_resolve_condition_event_fields() -> None:
    """ResolveConditionEvent exposes rationale and show_in_condition_list."""
    assert isinstance(ResolveConditionEvent._meta.get_field("rationale"), models.CharField)
    assert isinstance(
        ResolveConditionEvent._meta.get_field("show_in_condition_list"), models.BooleanField
    )


@pytest.mark.django_db
def test_committed_filters_uncommitted_and_entered_in_error() -> None:
    """ResolveConditionEvent.objects.committed() returns only committed, non-EIE rows."""
    committer = CanvasUserFactory.create()
    committed = ResolveConditionEventFactory.create(committer=committer)
    ResolveConditionEventFactory.create(committer=None)
    ResolveConditionEventFactory.create(
        committer=committer, entered_in_error=CanvasUserFactory.create()
    )
    assert set(ResolveConditionEvent.objects.committed()) == {committed}
