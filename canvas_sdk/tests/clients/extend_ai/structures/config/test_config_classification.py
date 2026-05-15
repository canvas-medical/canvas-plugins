from typing import Any

import pytest

from canvas_sdk.clients.extend_ai.constants.base_processor import BaseProcessor
from canvas_sdk.clients.extend_ai.constants.parser_chunking import ParserChunking
from canvas_sdk.clients.extend_ai.constants.parser_target import ParserTarget
from canvas_sdk.clients.extend_ai.constants.processor_type import ProcessorType
from canvas_sdk.clients.extend_ai.structures.classification import Classification
from canvas_sdk.clients.extend_ai.structures.config.advanced_options_classification import (
    AdvancedOptionsClassification,
)
from canvas_sdk.clients.extend_ai.structures.config.config_classification import (
    ConfigClassification,
)
from canvas_sdk.clients.extend_ai.structures.config.parser import Parser
from canvas_sdk.clients.extend_ai.structures.config.part_range import PartRange
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test that ConfigClassification is a dataclass with the expected field types."""
    tested = ConfigClassification
    fields = {
        "classifications": list[Classification],
        "base_processor": BaseProcessor,
        "classification_rule": str,
        "advanced_options": AdvancedOptionsClassification,
        "parser": Parser,
    }
    assert is_dataclass(tested, fields)


def test_processor_type() -> None:
    """Test ConfigClassification.processor_type returns ProcessorType.CLASSIFY."""
    tested = ConfigClassification
    result = tested.processor_type()
    expected = ProcessorType.CLASSIFY
    assert result == expected


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "baseProcessor": "extraction_performance",
                "classifications": [
                    {
                        "id": "class1",
                        "type": "invoice",
                        "description": "Invoice documents",
                    },
                    {
                        "id": "class2",
                        "type": "receipt",
                        "description": "Receipt documents",
                    },
                ],
                "classificationRules": "Classify by document type",
                "advancedOptions": {
                    "advancedMultimodalEnabled": True,
                    "page_ranges": [
                        {"start": 1, "end": 10},
                    ],
                },
                "parser": {
                    "target": "markdown",
                    "chunkingStrategy": {"type": "page"},
                },
            },
            ConfigClassification(
                classifications=[
                    Classification(
                        id="class1",
                        type="invoice",
                        description="Invoice documents",
                    ),
                    Classification(
                        id="class2",
                        type="receipt",
                        description="Receipt documents",
                    ),
                ],
                base_processor=BaseProcessor.EXTRACTION_PERFORMANCE,
                classification_rule="Classify by document type",
                advanced_options=AdvancedOptionsClassification(
                    advanced_multimodal_enabled=True,
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
                "classifications": [
                    {
                        "id": "class1",
                        "type": "invoice",
                        "description": "Invoice documents",
                    },
                ],
                "advancedOptions": {},
                "parser": {},
            },
            ConfigClassification(
                classifications=[
                    Classification(
                        id="class1",
                        type="invoice",
                        description="Invoice documents",
                    ),
                ],
                base_processor=BaseProcessor.EXTRACTION_LIGHT,
                classification_rule="",
                advanced_options=AdvancedOptionsClassification(
                    advanced_multimodal_enabled=False,
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
    """Test ConfigClassification.from_dict correctly deserializes classification configuration with defaults."""
    tested = ConfigClassification
    result = tested.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("tested", "expected"),
    [
        pytest.param(
            ConfigClassification(
                classifications=[
                    Classification(
                        id="class1",
                        type="invoice",
                        description="Invoice documents",
                    ),
                    Classification(
                        id="class2",
                        type="receipt",
                        description="Receipt documents",
                    ),
                ],
                base_processor=BaseProcessor.EXTRACTION_PERFORMANCE,
                classification_rule="Classify by document type",
                advanced_options=AdvancedOptionsClassification(
                    advanced_multimodal_enabled=True,
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
                "type": "CLASSIFY",
                "classifications": [
                    {
                        "id": "class1",
                        "type": "invoice",
                        "description": "Invoice documents",
                    },
                    {
                        "id": "class2",
                        "type": "receipt",
                        "description": "Receipt documents",
                    },
                ],
                "baseProcessor": "extraction_performance",
                "classificationRules": "Classify by document type",
                "advancedOptions": {
                    "advancedMultimodalEnabled": True,
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
            ConfigClassification(
                classifications=[
                    Classification(
                        id="class1",
                        type="invoice",
                        description="Invoice documents",
                    ),
                ],
                base_processor=BaseProcessor.EXTRACTION_LIGHT,
                classification_rule="",
                advanced_options=AdvancedOptionsClassification(
                    advanced_multimodal_enabled=False,
                    page_ranges=[],
                ),
                parser=Parser(
                    target=ParserTarget.SPATIAL,
                    chunking_strategy=ParserChunking.SECTION,
                ),
            ),
            {
                "type": "CLASSIFY",
                "classifications": [
                    {
                        "id": "class1",
                        "type": "invoice",
                        "description": "Invoice documents",
                    },
                ],
                "baseProcessor": "extraction_light",
                "classificationRules": "",
                "advancedOptions": {
                    "advancedMultimodalEnabled": False,
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
    """Test ConfigClassification.to_dict correctly serializes classification configuration for API requests."""
    result = tested.to_dict()
    assert result == expected
