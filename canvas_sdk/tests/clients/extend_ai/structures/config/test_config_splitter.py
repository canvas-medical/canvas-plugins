from typing import Any

import pytest

from canvas_sdk.clients.extend_ai.constants.base_processor import BaseProcessor
from canvas_sdk.clients.extend_ai.constants.parser_chunking import ParserChunking
from canvas_sdk.clients.extend_ai.constants.parser_target import ParserTarget
from canvas_sdk.clients.extend_ai.constants.processor_type import ProcessorType
from canvas_sdk.clients.extend_ai.constants.split_method import SplitMethod
from canvas_sdk.clients.extend_ai.structures.classification import Classification
from canvas_sdk.clients.extend_ai.structures.config.advanced_options_splitter import (
    AdvancedOptionsSplitter,
)
from canvas_sdk.clients.extend_ai.structures.config.config_splitter import ConfigSplitter
from canvas_sdk.clients.extend_ai.structures.config.parser import Parser
from canvas_sdk.clients.extend_ai.structures.config.part_range import PartRange
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test that ConfigSplitter is a dataclass with the expected field types."""
    tested = ConfigSplitter
    fields = {
        "split_classifications": list[Classification],
        "base_processor": BaseProcessor,
        "split_rules": str,
        "advanced_options": AdvancedOptionsSplitter,
        "parser": Parser,
    }
    assert is_dataclass(tested, fields)


def test_processor_type() -> None:
    """Test ConfigSplitter.processor_type returns ProcessorType.SPLITTER."""
    tested = ConfigSplitter
    result = tested.processor_type()
    expected = ProcessorType.SPLITTER
    assert result == expected


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "baseProcessor": "extraction_performance",
                "splitClassifications": [
                    {
                        "id": "split1",
                        "type": "section",
                        "description": "Section splits",
                    },
                    {
                        "id": "split2",
                        "type": "chapter",
                        "description": "Chapter splits",
                    },
                ],
                "splitRules": "Split by section markers",
                "advancedOptions": {
                    "splitIdentifierRules": "Use document headers",
                    "splitMethod": "high_precision",
                    "page_ranges": [
                        {"start": 1, "end": 10},
                    ],
                },
                "parser": {
                    "target": "markdown",
                    "chunkingStrategy": {"type": "page"},
                },
            },
            ConfigSplitter(
                split_classifications=[
                    Classification(
                        id="split1",
                        type="section",
                        description="Section splits",
                    ),
                    Classification(
                        id="split2",
                        type="chapter",
                        description="Chapter splits",
                    ),
                ],
                base_processor=BaseProcessor.EXTRACTION_PERFORMANCE,
                split_rules="Split by section markers",
                advanced_options=AdvancedOptionsSplitter(
                    split_identifier_rules="Use document headers",
                    split_method=SplitMethod.HIGH_PRECISION,
                    page_ranges=[
                        PartRange(start=1, end=10),
                    ],
                ),
                parser=Parser(
                    target=ParserTarget.MARKDOWN,
                    chunking_strategy=ParserChunking.PAGE,
                ),
            ),
            id="performance_with_all_options",
        ),
        pytest.param(
            {
                "baseProcessor": "extraction_light",
                "splitClassifications": [
                    {
                        "id": "split1",
                        "type": "section",
                        "description": "Section splits",
                    },
                ],
                "advancedOptions": {},
                "parser": {},
            },
            ConfigSplitter(
                split_classifications=[
                    Classification(
                        id="split1",
                        type="section",
                        description="Section splits",
                    ),
                ],
                base_processor=BaseProcessor.EXTRACTION_LIGHT,
                split_rules="",
                advanced_options=AdvancedOptionsSplitter(
                    split_identifier_rules="",
                    split_method=SplitMethod.HIGH_PRECISION,
                    page_ranges=[],
                ),
                parser=Parser(
                    target=ParserTarget.MARKDOWN,
                    chunking_strategy=ParserChunking.DOCUMENT,
                ),
            ),
            id="light_with_defaults",
        ),
    ],
)
def test_from_dict(data: Any, expected: Any) -> None:
    """Test ConfigSplitter.from_dict correctly deserializes splitter configuration with defaults."""
    tested = ConfigSplitter
    result = tested.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("tested", "expected"),
    [
        pytest.param(
            ConfigSplitter(
                split_classifications=[
                    Classification(
                        id="split1",
                        type="section",
                        description="Section splits",
                    ),
                    Classification(
                        id="split2",
                        type="chapter",
                        description="Chapter splits",
                    ),
                ],
                base_processor=BaseProcessor.EXTRACTION_PERFORMANCE,
                split_rules="Split by section markers",
                advanced_options=AdvancedOptionsSplitter(
                    split_identifier_rules="Use document headers",
                    split_method=SplitMethod.HIGH_PRECISION,
                    page_ranges=[
                        PartRange(start=1, end=10),
                    ],
                ),
                parser=Parser(
                    target=ParserTarget.MARKDOWN,
                    chunking_strategy=ParserChunking.PAGE,
                ),
            ),
            {
                "type": "SPLITTER",
                "splitClassifications": [
                    {
                        "id": "split1",
                        "type": "section",
                        "description": "Section splits",
                    },
                    {
                        "id": "split2",
                        "type": "chapter",
                        "description": "Chapter splits",
                    },
                ],
                "baseProcessor": "extraction_performance",
                "splitRules": "Split by section markers",
                "advancedOptions": {
                    "splitIdentifierRules": "Use document headers",
                    "splitMethod": "high_precision",
                    "pageRanges": [
                        {"start": 1, "end": 10},
                    ],
                },
                "parser": {
                    "target": "markdown",
                    "chunkingStrategy": {"type": "page"},
                },
            },
            id="performance_with_page_ranges",
        ),
        pytest.param(
            ConfigSplitter(
                split_classifications=[
                    Classification(
                        id="split1",
                        type="section",
                        description="Section splits",
                    ),
                ],
                base_processor=BaseProcessor.EXTRACTION_LIGHT,
                split_rules="",
                advanced_options=AdvancedOptionsSplitter(
                    split_identifier_rules="",
                    split_method=SplitMethod.LOW_LATENCY,
                    page_ranges=[],
                ),
                parser=Parser(
                    target=ParserTarget.SPATIAL,
                    chunking_strategy=ParserChunking.SECTION,
                ),
            ),
            {
                "type": "SPLITTER",
                "splitClassifications": [
                    {
                        "id": "split1",
                        "type": "section",
                        "description": "Section splits",
                    },
                ],
                "baseProcessor": "extraction_light",
                "splitRules": "",
                "advancedOptions": {
                    "splitIdentifierRules": "",
                    "splitMethod": "low_latency",
                    "pageRanges": [],
                },
                "parser": {
                    "target": "spatial",
                    "chunkingStrategy": {"type": "section"},
                },
            },
            id="light_spatial_section",
        ),
    ],
)
def test_to_dict(tested: Any, expected: Any) -> None:
    """Test ConfigSplitter.to_dict correctly serializes splitter configuration for API requests."""
    result = tested.to_dict()
    assert result == expected
