import pytest

from canvas_sdk.test_utils.factories import CanvasUserFactory, CreateCodingGapEventFactory
from canvas_sdk.v1.data.coding_gap_event import (
    AssessCodingGapEvent,
    CreateCodingGapEvent,
    DeferCodingGapEvent,
    ValidateCodingGapEvent,
)


def test_detected_issue_reverse_accessors() -> None:
    """Each coding-gap event links to DetectedIssue via a distinct reverse accessor."""
    assert (
        CreateCodingGapEvent._meta.get_field("detected_issue").remote_field.get_accessor_name()
        == "created_coding_gap_events"
    )
    assert (
        ValidateCodingGapEvent._meta.get_field("detected_issue").remote_field.get_accessor_name()
        == "validated_coding_gap_events"
    )
    assert (
        AssessCodingGapEvent._meta.get_field("detected_issue").remote_field.get_accessor_name()
        == "assessed_coding_gap_events"
    )
    assert (
        DeferCodingGapEvent._meta.get_field("detected_issue").remote_field.get_accessor_name()
        == "deferred_coding_gap_events"
    )


def test_assess_exposes_conditions_m2m() -> None:
    """AssessCodingGapEvent exposes a conditions M2M reachable via condition.assessed_coding_gaps."""
    field = AssessCodingGapEvent._meta.get_field("conditions")
    assert field.many_to_many is True
    assert field.remote_field.get_accessor_name() == "assessed_coding_gaps"


@pytest.mark.django_db
def test_committed_filters_uncommitted_and_entered_in_error() -> None:
    """committed() returns only committed, non-EIE coding-gap events."""
    committer = CanvasUserFactory.create()
    committed = CreateCodingGapEventFactory.create(committer=committer)
    CreateCodingGapEventFactory.create(committer=None)
    CreateCodingGapEventFactory.create(
        committer=committer, entered_in_error=CanvasUserFactory.create()
    )

    assert set(CreateCodingGapEvent.objects.committed()) == {committed}
