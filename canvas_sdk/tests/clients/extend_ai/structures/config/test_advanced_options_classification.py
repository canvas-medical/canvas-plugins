from typing import Any

import pytest

from canvas_sdk.clients.extend_ai.structures.config.advanced_options_classification import (
    AdvancedOptionsClassification,
)
from canvas_sdk.clients.extend_ai.structures.config.part_range import PartRange
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test that AdvancedOptionsClassification is a dataclass with the expected field types."""
    tested = AdvancedOptionsClassification
    fields = {
        "advanced_multimodal_enabled": bool,
        "page_ranges": list[PartRange],
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "advancedMultimodalEnabled": False,
                "page_ranges": [
                    {"start": 1, "end": 10},
                    {"start": 20, "end": 30},
                ],
            },
            AdvancedOptionsClassification(
                advanced_multimodal_enabled=False,
                page_ranges=[
                    PartRange(start=1, end=10),
                    PartRange(start=20, end=30),
                ],
            ),
            id="with_all_options_and_page_ranges",
        ),
        pytest.param(
            {
                "advancedMultimodalEnabled": True,
            },
            AdvancedOptionsClassification(
                advanced_multimodal_enabled=True,
                page_ranges=[],
            ),
            id="without_page_ranges",
        ),
        pytest.param(
            {},
            AdvancedOptionsClassification(
                advanced_multimodal_enabled=False,
                page_ranges=[],
            ),
            id="empty_dict_defaults",
        ),
    ],
)
def test_from_dict(data: Any, expected: Any) -> None:
    """Test AdvancedOptionsClassification.from_dict correctly deserializes advanced options with defaults."""
    tested = AdvancedOptionsClassification
    result = tested.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("tested", "expected"),
    [
        pytest.param(
            AdvancedOptionsClassification(
                advanced_multimodal_enabled=False,
                page_ranges=[
                    PartRange(start=1, end=10),
                    PartRange(start=20, end=30),
                ],
            ),
            {
                "advancedMultimodalEnabled": False,
                "pageRanges": [
                    {"start": 1, "end": 10},
                    {"start": 20, "end": 30},
                ],
            },
            id="with_page_ranges",
        ),
        pytest.param(
            AdvancedOptionsClassification(
                advanced_multimodal_enabled=True,
                page_ranges=[],
            ),
            {
                "advancedMultimodalEnabled": True,
                "pageRanges": [],
            },
            id="empty_page_ranges",
        ),
    ],
)
def test_to_dict(tested: Any, expected: Any) -> None:
    """Test AdvancedOptionsClassification.to_dict correctly serializes advanced options for API requests."""
    result = tested.to_dict()
    assert result == expected
