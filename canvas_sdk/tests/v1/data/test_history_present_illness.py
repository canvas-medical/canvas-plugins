import pytest
from django.db import models

from canvas_sdk.test_utils.factories import HistoryOfPresentIllnessFactory
from canvas_sdk.v1.data.history_present_illness import (
    HistoryOfPresentIllness,
    string_from_narrative_json,
)


def test_hpi_narrative_storage_fields() -> None:
    """HPI stores the legacy free-text (db column ``narrative``) and the structured narrative_json."""
    legacy_field = HistoryOfPresentIllness._meta.get_field("legacy_narrative")
    assert isinstance(legacy_field, models.TextField)
    assert legacy_field.db_column == "narrative"

    assert isinstance(HistoryOfPresentIllness._meta.get_field("narrative_json"), models.JSONField)


def test_narrative_property_prefers_legacy_then_json() -> None:
    """The narrative property returns the legacy text when present, else renders narrative_json."""
    hpi = HistoryOfPresentIllness()

    hpi.legacy_narrative = "Legacy free text"
    hpi.narrative_json = None
    assert hpi.narrative == "Legacy free text"

    hpi.legacy_narrative = ""
    hpi.narrative_json = {
        "document": {"nodes": [{"object": "text", "leaves": [{"text": "From JSON"}]}]}
    }
    assert hpi.narrative == "From JSON"


def test_string_from_narrative_json_edge_cases() -> None:
    """The porter returns '' for empty input and parses a JSON-string document."""
    assert string_from_narrative_json(None) == ""
    assert (
        string_from_narrative_json(
            '{"document": {"nodes": [{"object": "text", "leaves": [{"text": "Hi"}]}]}}'
        )
        == "Hi"
    )


@pytest.mark.django_db
def test_factory_round_trips_and_shares_patient() -> None:
    """The factory persists an HPI, wires the note to the same patient, and exposes the narrative."""
    hpi = HistoryOfPresentIllnessFactory.create(legacy_narrative="Patient reports headache.")

    fetched = HistoryOfPresentIllness.objects.get(dbid=hpi.dbid)

    assert fetched.note_id == hpi.note_id
    assert fetched.patient_id == fetched.note.patient_id
    assert fetched.narrative == "Patient reports headache."
