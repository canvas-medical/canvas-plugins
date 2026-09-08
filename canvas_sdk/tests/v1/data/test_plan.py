import pytest
from django.db import models

from canvas_sdk.test_utils.factories import PlanFactory
from canvas_sdk.v1.data.plan import Plan


def test_plan_narrative_fields() -> None:
    """Plan stores the legacy narrative under the `narrative` column and keeps narrative_json."""
    legacy_field = Plan._meta.get_field("legacy_narrative")
    assert isinstance(legacy_field, models.TextField)
    assert legacy_field.db_column == "narrative"

    json_field = Plan._meta.get_field("narrative_json")
    assert isinstance(json_field, models.JSONField)


def test_narrative_property_prefers_legacy() -> None:
    """The narrative property returns legacy_narrative when it is set."""
    plan = Plan()
    plan.legacy_narrative = "old style narrative"
    plan.narrative_json = {"document": {"nodes": [{"object": "text", "leaves": [{"text": "new"}]}]}}
    assert plan.narrative == "old style narrative"


def test_narrative_property_falls_back_to_json() -> None:
    """When legacy_narrative is empty, the narrative property renders narrative_json."""
    plan = Plan()
    plan.legacy_narrative = ""
    plan.narrative_json = {
        "document": {"nodes": [{"object": "text", "leaves": [{"text": "hello"}]}]}
    }
    assert plan.narrative == "hello"


def test_string_from_narrative_json_handles_blocks_and_none() -> None:
    """The porter renders block/text nodes and treats empty input as an empty string."""
    assert Plan.string_from_narrative_json(None) == ""
    doc = {
        "document": {
            "nodes": [
                {"object": "block", "nodes": [{"object": "text", "leaves": [{"text": "line"}]}]}
            ]
        }
    }
    assert Plan.string_from_narrative_json(doc) == "line"


@pytest.mark.django_db
def test_plan_factory_builds() -> None:
    """The SDK PlanFactory creates a Plan whose narrative resolves from legacy_narrative."""
    plan = PlanFactory.create()
    assert plan.narrative == plan.legacy_narrative
    assert plan.patient_id is not None
    assert plan.note_id is not None
