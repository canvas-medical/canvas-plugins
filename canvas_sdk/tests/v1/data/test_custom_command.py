import pytest

from canvas_sdk.test_utils.factories import CanvasUserFactory, CustomCommandFactory
from canvas_sdk.v1.data.custom_command import CustomCommand


@pytest.mark.django_db
def test_committed_filters_and_links_to_patient() -> None:
    """committed() returns only committed, non-EIE rows, reachable via patient.custom_commands."""
    committer = CanvasUserFactory.create()
    committed = CustomCommandFactory.create(committer=committer)
    CustomCommandFactory.create(committer=None)
    CustomCommandFactory.create(committer=committer, entered_in_error=CanvasUserFactory.create())

    assert set(CustomCommand.objects.committed()) == {committed}
    assert list(committed.patient.custom_commands.all()) == [committed]
