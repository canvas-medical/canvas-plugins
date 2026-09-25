import pytest

from canvas_sdk.test_utils.factories import CanvasUserFactory, ClipboardFactory
from canvas_sdk.v1.data.clipboard import Clipboard


def test_clipboard_reverse_accessors_and_text() -> None:
    """Clipboard exposes patient/note via the `clipboards` reverse accessor plus a text field."""
    assert Clipboard._meta.get_field("patient").remote_field.get_accessor_name() == "clipboards"
    assert Clipboard._meta.get_field("note").remote_field.get_accessor_name() == "clipboards"
    assert Clipboard._meta.get_field("text").get_internal_type() == "TextField"


@pytest.mark.django_db
def test_committed_filters_uncommitted_and_entered_in_error() -> None:
    """committed() returns only committed, non-entered-in-error clipboards."""
    committer = CanvasUserFactory.create()
    committed = ClipboardFactory.create(committer=committer)
    ClipboardFactory.create(committer=None)
    ClipboardFactory.create(committer=committer, entered_in_error=CanvasUserFactory.create())

    assert set(Clipboard.objects.committed()) == {committed}
