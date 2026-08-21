import pytest
from django.db import models

from canvas_sdk.test_utils.factories import HistoryOfPresentIllnessFactory
from canvas_sdk.v1.data.history_present_illness import HistoryOfPresentIllness


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
    assert HistoryOfPresentIllness.string_from_narrative_json(None) == ""
    assert (
        HistoryOfPresentIllness.string_from_narrative_json(
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


def test_string_from_narrative_json_returns_input_when_not_valid_json() -> None:
    """A plain (non-JSON) string is returned unchanged when ``json.loads`` raises ValueError."""
    assert (
        HistoryOfPresentIllness.string_from_narrative_json("Patient has a headache.")
        == "Patient has a headache."
    )


def test_string_from_narrative_json_unwraps_json_encoded_scalar_string() -> None:
    """A JSON-encoded scalar string decodes to that string rather than a Slate document."""
    assert HistoryOfPresentIllness.string_from_narrative_json('"just a string"') == "just a string"


def test_string_from_narrative_json_renders_inline_nodes() -> None:
    """A top-level inline node renders its ``data.concept`` (ported home-app behavior)."""
    narrative_json = {"document": {"nodes": [{"object": "inline", "data": {"concept": "Aspirin"}}]}}
    assert HistoryOfPresentIllness.string_from_narrative_json(narrative_json) == "Aspirin '"


def test_string_from_narrative_json_renders_blocks_with_paragraph_breaks() -> None:
    """Block nodes render nested text/inline children, newline-joined except after the last block."""
    narrative_json = {
        "document": {
            "nodes": [
                {
                    "object": "block",
                    "nodes": [
                        {"object": "text", "leaves": [{"text": "First line"}]},
                        {"object": "inline", "data": {"concept": "concept1"}},
                    ],
                },
                {
                    "object": "block",
                    "nodes": [{"object": "text", "leaves": [{"text": "Second line"}]}],
                },
            ]
        }
    }
    assert (
        HistoryOfPresentIllness.string_from_narrative_json(narrative_json)
        == "First lineconcept1 '\nSecond line"
    )
