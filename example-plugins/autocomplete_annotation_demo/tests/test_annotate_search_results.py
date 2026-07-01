"""Tests for autocomplete_annotation_demo."""

import json
from unittest.mock import Mock

from canvas_sdk.effects import EffectType
from canvas_sdk.events import EventType


def test_responds_to_search_events() -> None:
    """Handler subscribes to the Diagnose and Assess Condition post-search events."""
    from autocomplete_annotation_demo.handlers.annotate_search_results import Handler

    assert EventType.Name(EventType.DIAGNOSE__DIAGNOSE__POST_SEARCH) in Handler.RESPONDS_TO
    assert EventType.Name(EventType.ASSESS__CONDITION__POST_SEARCH) in Handler.RESPONDS_TO


def test_annotates_every_result() -> None:
    """Every result gets the demo annotations, echoed back as an AUTOCOMPLETE_SEARCH_RESULTS effect."""
    from autocomplete_annotation_demo.handlers.annotate_search_results import Handler

    mock_event = Mock()
    mock_event.context = {
        "results": [
            {"value": "1", "text": "Type 2 diabetes mellitus"},
            {"value": "2", "text": "Prediabetes"},
        ]
    }
    handler = Handler(event=mock_event)

    result = handler.compute()

    assert len(result) == 1
    assert result[0].type == EffectType.AUTOCOMPLETE_SEARCH_RESULTS
    payload = json.loads(result[0].payload)
    assert [r["annotations"] for r in payload] == [["Demo", "Annotation"], ["Demo", "Annotation"]]


def test_handles_missing_results() -> None:
    """With no results in context, return a null-payload effect rather than crashing."""
    from autocomplete_annotation_demo.handlers.annotate_search_results import Handler

    mock_event = Mock()
    mock_event.context = {}
    handler = Handler(event=mock_event)

    result = handler.compute()

    assert len(result) == 1
    assert result[0].type == EffectType.AUTOCOMPLETE_SEARCH_RESULTS
    assert json.loads(result[0].payload) is None
