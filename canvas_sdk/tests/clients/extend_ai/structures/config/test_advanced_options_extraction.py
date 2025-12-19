from typing import Any

import pytest

from canvas_sdk.clients.extend_ai.structures.config.advanced_options_extraction import (
    AdvancedOptionsExtraction,
)
from canvas_sdk.clients.extend_ai.structures.config.part_range import PartRange
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test that AdvancedOptionsExtraction is a dataclass with the expected field types."""
    tested = AdvancedOptionsExtraction
    fields = {
        "model_reasoning_insights_enabled": bool,
        "advanced_multimodal_enabled": bool,
        "citations_enabled": bool,
        "page_ranges": list[PartRange],
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "modelReasoningInsightsEnabled": True,
                "advancedMultimodalEnabled": False,
                "citationsEnabled": True,
                "page_ranges": [
                    {"start": 1, "end": 10},
                    {"start": 20, "end": 30},
                ],
            },
            AdvancedOptionsExtraction(
                model_reasoning_insights_enabled=True,
                advanced_multimodal_enabled=False,
                citations_enabled=True,
                page_ranges=[
                    PartRange(start=1, end=10),
                    PartRange(start=20, end=30),
                ],
            ),
            id="with_all_options_and_page_ranges",
        ),
        pytest.param(
            {
                "modelReasoningInsightsEnabled": False,
                "advancedMultimodalEnabled": True,
                "citationsEnabled": False,
            },
            AdvancedOptionsExtraction(
                model_reasoning_insights_enabled=False,
                advanced_multimodal_enabled=True,
                citations_enabled=False,
                page_ranges=[],
            ),
            id="without_page_ranges",
        ),
        pytest.param(
            {},
            AdvancedOptionsExtraction(
                model_reasoning_insights_enabled=False,
                advanced_multimodal_enabled=False,
                citations_enabled=False,
                page_ranges=[],
            ),
            id="empty_dict_defaults",
        ),
    ],
)
def test_from_dict(data: Any, expected: Any) -> None:
    """Test AdvancedOptionsExtraction.from_dict correctly deserializes advanced options with defaults."""
    tested = AdvancedOptionsExtraction
    result = tested.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("tested", "expected"),
    [
        pytest.param(
            AdvancedOptionsExtraction(
                model_reasoning_insights_enabled=True,
                advanced_multimodal_enabled=False,
                citations_enabled=True,
                page_ranges=[
                    PartRange(start=1, end=10),
                    PartRange(start=20, end=30),
                ],
            ),
            {
                "modelReasoningInsightsEnabled": True,
                "advancedMultimodalEnabled": False,
                "citationsEnabled": True,
                "pageRanges": [
                    {"start": 1, "end": 10},
                    {"start": 20, "end": 30},
                ],
            },
            id="with_page_ranges",
        ),
        pytest.param(
            AdvancedOptionsExtraction(
                model_reasoning_insights_enabled=False,
                advanced_multimodal_enabled=True,
                citations_enabled=False,
                page_ranges=[],
            ),
            {
                "modelReasoningInsightsEnabled": False,
                "advancedMultimodalEnabled": True,
                "citationsEnabled": False,
                "pageRanges": [],
            },
            id="empty_page_ranges",
        ),
    ],
)
def test_to_dict(tested: Any, expected: Any) -> None:
    """Test AdvancedOptionsExtraction.to_dict correctly serializes advanced options for API requests."""
    result = tested.to_dict()
    assert result == expected
