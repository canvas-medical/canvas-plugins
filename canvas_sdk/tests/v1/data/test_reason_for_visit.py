import pytest
from django.db import models

from canvas_sdk.test_utils.factories import ReasonForVisitCodingFactory, ReasonForVisitFactory
from canvas_sdk.v1.data.reason_for_visit import ReasonForVisit, ReasonForVisitCoding


def test_rfv_narrative_storage_fields() -> None:
    """ReasonForVisit stores the legacy free-text (db column ``narrative``) and narrative_json."""
    legacy_field = ReasonForVisit._meta.get_field("legacy_narrative")
    assert isinstance(legacy_field, models.TextField)
    assert legacy_field.db_column == "narrative"
    assert isinstance(ReasonForVisit._meta.get_field("narrative_json"), models.JSONField)


def test_narrative_property_prefers_legacy_then_json() -> None:
    """The narrative property returns legacy text when present, else renders narrative_json."""
    rfv = ReasonForVisit()
    rfv.legacy_narrative = "Legacy free text"
    rfv.narrative_json = None
    assert rfv.narrative == "Legacy free text"

    rfv.legacy_narrative = ""
    rfv.narrative_json = {
        "document": {"nodes": [{"object": "text", "leaves": [{"text": "From JSON"}]}]}
    }
    assert rfv.narrative == "From JSON"


@pytest.mark.django_db
def test_rfv_factory_builds() -> None:
    """The SDK ReasonForVisitFactory persists a ReasonForVisit whose narrative resolves."""
    rfv = ReasonForVisitFactory.create(legacy_narrative="Annual checkup")
    assert rfv.narrative == "Annual checkup"
    assert rfv.patient_id is not None
    assert rfv.note_id is not None


@pytest.mark.django_db
def test_rfv_coding_persists_and_links_to_reason_for_visit() -> None:
    """A ReasonForVisitCoding round-trips its fields and is reachable via the ``codings`` relation."""
    rfv = ReasonForVisitFactory.create()
    ReasonForVisitCodingFactory.create(
        reason_for_visit=rfv,
        system="http://snomed.info/sct",
        code="699134002",
        display="Caregiver Annual Health Check",
    )
    ReasonForVisitCodingFactory.create(reason_for_visit=ReasonForVisitFactory.create())

    fetched = rfv.codings.get()

    assert isinstance(fetched, ReasonForVisitCoding)
    assert fetched.system == "http://snomed.info/sct"
    assert fetched.code == "699134002"
    assert fetched.display == "Caregiver Annual Health Check"
