import pytest

from canvas_sdk.test_utils.factories import CanvasUserFactory, PrivateNoteFactory
from canvas_sdk.v1.data.private_note import PrivateNote


def test_private_note_does_not_expose_text() -> None:
    """The clinician-only text is intentionally not part of the SDK model."""
    field_names = {f.name for f in PrivateNote._meta.get_fields()}
    assert "text" not in field_names


@pytest.mark.django_db
def test_committed_filters_and_links_to_patient() -> None:
    """committed() returns only committed, non-EIE rows, reachable via patient.private_notes."""
    committer = CanvasUserFactory.create()
    committed = PrivateNoteFactory.create(committer=committer)
    PrivateNoteFactory.create(committer=None)
    PrivateNoteFactory.create(committer=committer, entered_in_error=CanvasUserFactory.create())

    assert set(PrivateNote.objects.committed()) == {committed}
    assert list(committed.patient.private_notes.all()) == [committed]
