from django.db import models

from canvas_sdk.v1.data.history_present_illness import (
    HistoryOfPresentIllness,
    string_from_narrative_json,
)


def test_hpi_narrative_storage_fields() -> None:
    """HPI stores the legacy free-text (db column ``narrative``) and the structured narrative_json."""
    legacy_field = HistoryOfPresentIllness._meta.get_field("legacy_narrative")
    assert isinstance(legacy_field, models.TextField)
    assert legacy_field.db_column == "narrative"

    assert isinstance(
        HistoryOfPresentIllness._meta.get_field("narrative_json"), models.JSONField
    )


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
