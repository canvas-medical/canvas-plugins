from typing import Any

import pytest

from canvas_sdk.clients.extend_ai.constants.base_processor import BaseProcessor
from canvas_sdk.clients.extend_ai.constants.parser_chunking import ParserChunking
from canvas_sdk.clients.extend_ai.constants.parser_target import ParserTarget
from canvas_sdk.clients.extend_ai.constants.processor_type import ProcessorType
from canvas_sdk.clients.extend_ai.structures.config.advanced_options_extraction import (
    AdvancedOptionsExtraction,
)
from canvas_sdk.clients.extend_ai.structures.config.config_extraction import ConfigExtraction
from canvas_sdk.clients.extend_ai.structures.config.parser import Parser
from canvas_sdk.clients.extend_ai.structures.config.part_range import PartRange
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test that ConfigExtraction is a dataclass with the expected field types."""
    tested = ConfigExtraction
    fields = {
        "base_processor": BaseProcessor,
        "extraction_rule": str,
        "schema": dict,
        "advanced_options": AdvancedOptionsExtraction,
        "parser": Parser,
    }
    assert is_dataclass(tested, fields)


def test_processor_type() -> None:
    """Test ConfigExtraction.processor_type returns ProcessorType.EXTRACT."""
    tested = ConfigExtraction
    result = tested.processor_type()
    expected = ProcessorType.EXTRACT
    assert result == expected


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "baseProcessor": "extraction_performance",
                "extractionRule": "Extract all data",
                "schema": {"field1": "string", "field2": "number"},
                "advancedOptions": {
                    "modelReasoningInsightsEnabled": True,
                    "advancedMultimodalEnabled": False,
                    "citationsEnabled": False,
                    "page_ranges": [],
                },
                "parser": {
                    "target": "markdown",
                    "chunkingStrategy": {"type": "page"},
                },
            },
            ConfigExtraction(
                base_processor=BaseProcessor.EXTRACTION_PERFORMANCE,
                extraction_rule="Extract all data",
                schema={"field1": "string", "field2": "number"},
                advanced_options=AdvancedOptionsExtraction(
                    model_reasoning_insights_enabled=True,
                    advanced_multimodal_enabled=False,
                    citations_enabled=False,
                    page_ranges=[],
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
                "schema": {"type": "object"},
                "advancedOptions": {},
            },
            ConfigExtraction(
                base_processor=BaseProcessor.EXTRACTION_LIGHT,
                extraction_rule="",
                schema={"type": "object"},
                advanced_options=AdvancedOptionsExtraction(
                    model_reasoning_insights_enabled=False,
                    advanced_multimodal_enabled=False,
                    citations_enabled=False,
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
    """Test ConfigExtraction.from_dict correctly deserializes extraction configuration with defaults."""
    tested = ConfigExtraction
    result = tested.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("tested", "expected"),
    [
        pytest.param(
            ConfigExtraction(
                base_processor=BaseProcessor.EXTRACTION_PERFORMANCE,
                extraction_rule="Extract all data",
                schema={"field1": "string", "field2": "number"},
                advanced_options=AdvancedOptionsExtraction(
                    model_reasoning_insights_enabled=True,
                    advanced_multimodal_enabled=False,
                    citations_enabled=False,
                    page_ranges=[
                        PartRange(start=1, end=10),
                        PartRange(start=20, end=30),
                    ],
                ),
                parser=Parser(
                    target=ParserTarget.MARKDOWN,
                    chunking_strategy=ParserChunking.PAGE,
                ),
            ),
            {
                "type": "EXTRACT",
                "baseProcessor": "extraction_performance",
                "extractionRule": "Extract all data",
                "schema": {"field1": "string", "field2": "number"},
                "advancedOptions": {
                    "modelReasoningInsightsEnabled": True,
                    "advancedMultimodalEnabled": False,
                    "citationsEnabled": False,
                    "pageRanges": [
                        {"start": 1, "end": 10},
                        {"start": 20, "end": 30},
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
            ConfigExtraction(
                base_processor=BaseProcessor.EXTRACTION_LIGHT,
                extraction_rule="",
                schema={},
                advanced_options=AdvancedOptionsExtraction(
                    model_reasoning_insights_enabled=False,
                    advanced_multimodal_enabled=True,
                    citations_enabled=True,
                    page_ranges=[],
                ),
                parser=Parser(
                    target=ParserTarget.SPATIAL,
                    chunking_strategy=ParserChunking.SECTION,
                ),
            ),
            {
                "type": "EXTRACT",
                "baseProcessor": "extraction_light",
                "extractionRule": "",
                "schema": {},
                "advancedOptions": {
                    "modelReasoningInsightsEnabled": False,
                    "advancedMultimodalEnabled": True,
                    "citationsEnabled": True,
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
    """Test ConfigExtraction.to_dict correctly serializes extraction configuration for API requests."""
    result = tested.to_dict()
    assert result == expected
