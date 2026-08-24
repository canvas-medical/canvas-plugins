import pytest
from django.db import models

from canvas_sdk.test_utils.factories import ReasonForVisitFactory
from canvas_sdk.v1.data.reason_for_visit import ReasonForVisit


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
    rfv = ReasonForVisitFactory(legacy_narrative="Annual checkup")
    assert rfv.narrative == "Annual checkup"
    assert rfv.patient_id is not None
    assert rfv.note_id is not None
