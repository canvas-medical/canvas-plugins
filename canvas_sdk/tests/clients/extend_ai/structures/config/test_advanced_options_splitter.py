from typing import Any

import pytest

from canvas_sdk.clients.extend_ai.constants.split_method import SplitMethod
from canvas_sdk.clients.extend_ai.structures.config.advanced_options_splitter import (
    AdvancedOptionsSplitter,
)
from canvas_sdk.clients.extend_ai.structures.config.part_range import PartRange
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test that AdvancedOptionsSplitter is a dataclass with the expected field types."""
    tested = AdvancedOptionsSplitter
    fields = {
        "split_identifier_rules": str,
        "split_method": SplitMethod,
        "page_ranges": list[PartRange],
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "splitIdentifierRules": "Split by document type",
                "splitMethod": "high_precision",
                "page_ranges": [
                    {"start": 1, "end": 10},
                    {"start": 20, "end": 30},
                ],
            },
            AdvancedOptionsSplitter(
                split_identifier_rules="Split by document type",
                split_method=SplitMethod.HIGH_PRECISION,
                page_ranges=[
                    PartRange(start=1, end=10),
                    PartRange(start=20, end=30),
                ],
            ),
            id="with_all_options_and_page_ranges",
        ),
        pytest.param(
            {
                "splitMethod": "low_latency",
            },
            AdvancedOptionsSplitter(
                split_identifier_rules="",
                split_method=SplitMethod.LOW_LATENCY,
                page_ranges=[],
            ),
            id="without_page_ranges",
        ),
        pytest.param(
            {},
            AdvancedOptionsSplitter(
                split_identifier_rules="",
                split_method=SplitMethod.HIGH_PRECISION,
                page_ranges=[],
            ),
            id="empty_dict_defaults",
        ),
    ],
)
def test_from_dict(data: Any, expected: Any) -> None:
    """Test AdvancedOptionsSplitter.from_dict correctly deserializes advanced splitter options with defaults."""
    tested = AdvancedOptionsSplitter
    result = tested.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("tested", "expected"),
    [
        pytest.param(
            AdvancedOptionsSplitter(
                split_identifier_rules="Split by document type",
                split_method=SplitMethod.HIGH_PRECISION,
                page_ranges=[
                    PartRange(start=1, end=10),
                    PartRange(start=20, end=30),
                ],
            ),
            {
                "splitIdentifierRules": "Split by document type",
                "splitMethod": "high_precision",
                "pageRanges": [
                    {"start": 1, "end": 10},
                    {"start": 20, "end": 30},
                ],
            },
            id="with_page_ranges",
        ),
        pytest.param(
            AdvancedOptionsSplitter(
                split_identifier_rules="",
                split_method=SplitMethod.LOW_LATENCY,
                page_ranges=[],
            ),
            {
                "splitIdentifierRules": "",
                "splitMethod": "low_latency",
                "pageRanges": [],
            },
            id="empty_page_ranges",
        ),
    ],
)
def test_to_dict(tested: Any, expected: Any) -> None:
    """Test AdvancedOptionsSplitter.to_dict correctly serializes advanced splitter options for API requests."""
    result = tested.to_dict()
    assert result == expected
