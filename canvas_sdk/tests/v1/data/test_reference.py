import pytest
from django.db import models

from canvas_sdk.test_utils.factories import CanvasUserFactory, ReferenceFactory
from canvas_sdk.v1.data.reference import Reference


def test_reference_fields() -> None:
    """Reference exposes the name and content fields."""
    assert isinstance(Reference._meta.get_field("name"), models.CharField)
    assert isinstance(Reference._meta.get_field("content"), models.JSONField)


@pytest.mark.django_db
def test_committed_filters_and_links_to_patient() -> None:
    """committed() returns only committed, non-EIE rows, reachable via patient.references."""
    committer = CanvasUserFactory.create()
    committed = ReferenceFactory.create(committer=committer)
    ReferenceFactory.create(committer=None)
    ReferenceFactory.create(committer=committer, entered_in_error=CanvasUserFactory.create())

    assert set(Reference.objects.committed()) == {committed}
    assert list(committed.patient.references.all()) == [committed]
