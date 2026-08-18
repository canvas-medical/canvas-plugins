from django.db import models

from canvas_sdk.v1.data.history_present_illness import HistoryOfPresentIllness


def test_hpi_exposes_narrative_fields() -> None:
    """HPI exposes both the plain narrative and the structured narrative_json."""
    narrative_field = HistoryOfPresentIllness._meta.get_field("narrative")
    assert isinstance(narrative_field, models.TextField)

    narrative_json_field = HistoryOfPresentIllness._meta.get_field("narrative_json")
    assert isinstance(narrative_json_field, models.JSONField)


def test_hpi_links_to_patient_and_note() -> None:
    """HPI exposes patient and note foreign keys."""
    assert HistoryOfPresentIllness._meta.get_field("patient").is_relation
    assert HistoryOfPresentIllness._meta.get_field("note").is_relation
