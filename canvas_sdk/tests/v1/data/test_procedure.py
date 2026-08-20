import pytest
from django.db import models

from canvas_sdk.test_utils.factories import ProcedureCodingFactory
from canvas_sdk.v1.data.procedure import Procedure, ProcedureCoding, ProcedureStatus


def test_procedure_exposes_home_app_fields() -> None:
    """Procedure exposes the status, notes, and provider fields from home-app."""
    status_field = Procedure._meta.get_field("status")
    assert isinstance(status_field, models.IntegerField)
    assert status_field.null is True

    notes_field = Procedure._meta.get_field("notes")
    assert isinstance(notes_field, models.TextField)

    provider_field = Procedure._meta.get_field("provider")
    assert provider_field.null is True


def test_procedure_status_choices_match_home_app() -> None:
    """ProcedureStatus mirrors the home-app in-progress/aborted/completed integer codes."""
    assert ProcedureStatus.IN_PROGRESS == 1
    assert ProcedureStatus.ABORTED == 2
    assert ProcedureStatus.COMPLETED == 3


def test_procedure_coding_links_back_via_codings() -> None:
    """ProcedureCoding links to Procedure with a `codings` reverse accessor for ValueSet lookup."""
    accessor = ProcedureCoding._meta.get_field("procedure").remote_field.get_accessor_name()
    assert accessor == "codings"
    assert hasattr(Procedure, "codings")


@pytest.mark.django_db
def test_procedure_factory_builds_with_coding() -> None:
    """The SDK ProcedureFactory creates a Procedure reachable via its coding's `codings` accessor."""
    coding = ProcedureCodingFactory()
    assert coding.procedure.status == ProcedureStatus.COMPLETED
    assert list(coding.procedure.codings.all()) == [coding]
