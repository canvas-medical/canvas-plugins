from datetime import datetime
from typing import Any

import pytest

from canvas_sdk.clients.extend_ai.constants.base_processor import BaseProcessor
from canvas_sdk.clients.extend_ai.constants.parser_chunking import ParserChunking
from canvas_sdk.clients.extend_ai.constants.parser_target import ParserTarget
from canvas_sdk.clients.extend_ai.constants.processor_type import ProcessorType
from canvas_sdk.clients.extend_ai.constants.split_method import SplitMethod
from canvas_sdk.clients.extend_ai.structures.classification import Classification
from canvas_sdk.clients.extend_ai.structures.config.advanced_options_classification import (
    AdvancedOptionsClassification,
)
from canvas_sdk.clients.extend_ai.structures.config.advanced_options_extraction import (
    AdvancedOptionsExtraction,
)
from canvas_sdk.clients.extend_ai.structures.config.advanced_options_splitter import (
    AdvancedOptionsSplitter,
)
from canvas_sdk.clients.extend_ai.structures.config.config_classification import (
    ConfigClassification,
)
from canvas_sdk.clients.extend_ai.structures.config.config_extraction import ConfigExtraction
from canvas_sdk.clients.extend_ai.structures.config.config_splitter import ConfigSplitter
from canvas_sdk.clients.extend_ai.structures.config.parser import Parser
from canvas_sdk.clients.extend_ai.structures.processor_meta import ProcessorMeta
from canvas_sdk.clients.extend_ai.structures.processor_version import ProcessorVersion
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test that ProcessorVersion is a dataclass with the expected field types."""
    tested = ProcessorVersion
    fields = {
        "id": str,
        "version": str,
        "description": str,
        "processor": ProcessorMeta,
        "config": ConfigClassification | ConfigExtraction | ConfigSplitter,
        "created_at": datetime,
        "updated_at": datetime,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "id": "ver123",
                "version": "1.0.0",
                "description": "First version",
                "processorId": "proc123",
                "processorName": "My Processor",
                "processorType": "EXTRACT",
                "config": {
                    "baseProcessor": "extraction_performance",
                    "extractionRule": "Extract all",
                    "schema": {"type": "object"},
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
                "createdAt": "2024-01-15T10:30:00",
                "updatedAt": "2024-01-16T14:20:00",
            },
            ProcessorVersion(
                id="ver123",
                version="1.0.0",
                description="First version",
                processor=ProcessorMeta(
                    id="proc123",
                    name="My Processor",
                    type=ProcessorType.EXTRACT,
                    created_at=None,
                    updated_at=None,
                ),
                config=ConfigExtraction(
                    base_processor=BaseProcessor.EXTRACTION_PERFORMANCE,
                    extraction_rule="Extract all",
                    schema={"type": "object"},
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
                created_at=datetime(2024, 1, 15, 10, 30, 0),
                updated_at=datetime(2024, 1, 16, 14, 20, 0),
            ),
            id="extract_processor_with_config",
        ),
        pytest.param(
            {
                "id": "ver456",
                "version": "2.1.5",
                "processorId": "proc456",
                "processorName": "Another Processor",
                "processorType": "CLASSIFY",
                "config": {
                    "baseProcessor": "extraction_light",
                    "classifications": [
                        {
                            "id": "class1",
                            "type": "invoice",
                            "description": "Invoice documents",
                        }
                    ],
                    "classificationRules": "Classify documents by type",
                    "advancedOptions": {},
                    "parser": {},
                },
                "createdAt": "2024-02-20T08:15:30",
                "updatedAt": "2024-02-21T09:45:15",
            },
            ProcessorVersion(
                id="ver456",
                version="2.1.5",
                description="",
                processor=ProcessorMeta(
                    id="proc456",
                    name="Another Processor",
                    type=ProcessorType.CLASSIFY,
                    created_at=None,
                    updated_at=None,
                ),
                config=ConfigClassification(
                    classifications=[
                        Classification(
                            id="class1",
                            type="invoice",
                            description="Invoice documents",
                        )
                    ],
                    base_processor=BaseProcessor.EXTRACTION_LIGHT,
                    classification_rule="Classify documents by type",
                    advanced_options=AdvancedOptionsClassification(
                        advanced_multimodal_enabled=False,
                        page_ranges=[],
                    ),
                    parser=Parser(
                        target=ParserTarget.MARKDOWN,
                        chunking_strategy=ParserChunking.DOCUMENT,
                    ),
                ),
                created_at=datetime(2024, 2, 20, 8, 15, 30),
                updated_at=datetime(2024, 2, 21, 9, 45, 15),
            ),
            id="classify_processor_minimal_config",
        ),
        pytest.param(
            {
                "id": "ver789",
                "version": "3.0.0",
                "processorId": "proc789",
                "processorName": "Splitter Processor",
                "processorType": "SPLITTER",
                "config": {
                    "baseProcessor": "extraction_performance",
                    "splitClassifications": [
                        {
                            "id": "split1",
                            "type": "section",
                            "description": "Section splits",
                        }
                    ],
                    "splitRules": "Split by section",
                    "advancedOptions": {
                        "splitIdentifierRules": "Use headers",
                        "splitMethod": "high_precision",
                    },
                    "parser": {
                        "target": "markdown",
                        "chunkingStrategy": {"type": "page"},
                    },
                },
                "createdAt": "2024-03-10T09:00:00",
                "updatedAt": "2024-03-11T10:30:00",
            },
            ProcessorVersion(
                id="ver789",
                version="3.0.0",
                description="",
                processor=ProcessorMeta(
                    id="proc789",
                    name="Splitter Processor",
                    type=ProcessorType.SPLITTER,
                    created_at=None,
                    updated_at=None,
                ),
                config=ConfigSplitter(
                    split_classifications=[
                        Classification(
                            id="split1",
                            type="section",
                            description="Section splits",
                        )
                    ],
                    base_processor=BaseProcessor.EXTRACTION_PERFORMANCE,
                    split_rules="Split by section",
                    advanced_options=AdvancedOptionsSplitter(
                        split_identifier_rules="Use headers",
                        split_method=SplitMethod.HIGH_PRECISION,
                        page_ranges=[],
                    ),
                    parser=Parser(
                        target=ParserTarget.MARKDOWN,
                        chunking_strategy=ParserChunking.PAGE,
                    ),
                ),
                created_at=datetime(2024, 3, 10, 9, 0, 0),
                updated_at=datetime(2024, 3, 11, 10, 30, 0),
            ),
            id="splitter_processor_config",
        ),
    ],
)
def test_from_dict(data: Any, expected: Any) -> None:
    """Test ProcessorVersion.from_dict correctly deserializes processor version data with different config types."""
    tested = ProcessorVersion
    result = tested.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("tested", "expected"),
    [
        pytest.param(
            ProcessorVersion(
                id="ver123",
                version="1.0.0",
                description="First version",
                processor=ProcessorMeta(
                    id="proc123",
                    name="My Processor",
                    type=ProcessorType.EXTRACT,
                    created_at=datetime(2024, 1, 1, 0, 0, 0),
                    updated_at=datetime(2024, 1, 2, 0, 0, 0),
                ),
                config=ConfigExtraction(
                    base_processor=BaseProcessor.EXTRACTION_PERFORMANCE,
                    extraction_rule="Extract all",
                    schema={"type": "object"},
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
                created_at=datetime(2024, 1, 15, 10, 30, 0),
                updated_at=datetime(2024, 1, 16, 14, 20, 0),
            ),
            {
                "id": "ver123",
                "version": "1.0.0",
                "description": "First version",
                "processor": {
                    "id": "proc123",
                    "name": "My Processor",
                    "type": "EXTRACT",
                    "createdAt": "2024-01-01T00:00:00",
                    "updatedAt": "2024-01-02T00:00:00",
                },
                "config": {
                    "type": "EXTRACT",
                    "baseProcessor": "extraction_performance",
                    "extractionRule": "Extract all",
                    "schema": {"type": "object"},
                    "advancedOptions": {
                        "modelReasoningInsightsEnabled": True,
                        "advancedMultimodalEnabled": False,
                        "citationsEnabled": False,
                        "pageRanges": [],
                    },
                    "parser": {
                        "target": "markdown",
                        "chunkingStrategy": {"type": "page"},
                    },
                },
                "createdAt": "2024-01-15T10:30:00",
                "updatedAt": "2024-01-16T14:20:00",
            },
            id="full_processor_version",
        ),
        pytest.param(
            ProcessorVersion(
                id="ver456",
                version="2.0.0",
                description="Version with null processor dates",
                processor=ProcessorMeta(
                    id="proc456",
                    name="Another Processor",
                    type=ProcessorType.CLASSIFY,
                    created_at=None,
                    updated_at=None,
                ),
                config=ConfigExtraction(
                    base_processor=BaseProcessor.EXTRACTION_LIGHT,
                    extraction_rule="",
                    schema={},
                    advanced_options=AdvancedOptionsExtraction(
                        model_reasoning_insights_enabled=False,
                        advanced_multimodal_enabled=False,
                        citations_enabled=False,
                        page_ranges=[],
                    ),
                    parser=Parser(
                        target=ParserTarget.SPATIAL,
                        chunking_strategy=ParserChunking.DOCUMENT,
                    ),
                ),
                created_at=datetime(2024, 3, 1, 12, 0, 0),
                updated_at=datetime(2024, 3, 2, 15, 30, 0),
            ),
            {
                "id": "ver456",
                "version": "2.0.0",
                "description": "Version with null processor dates",
                "processor": {
                    "id": "proc456",
                    "name": "Another Processor",
                    "type": "CLASSIFY",
                    "createdAt": None,
                    "updatedAt": None,
                },
                "config": {
                    "type": "EXTRACT",
                    "baseProcessor": "extraction_light",
                    "extractionRule": "",
                    "schema": {},
                    "advancedOptions": {
                        "modelReasoningInsightsEnabled": False,
                        "advancedMultimodalEnabled": False,
                        "citationsEnabled": False,
                        "pageRanges": [],
                    },
                    "parser": {
                        "target": "spatial",
                        "chunkingStrategy": {"type": "document"},
                    },
                },
                "createdAt": "2024-03-01T12:00:00",
                "updatedAt": "2024-03-02T15:30:00",
            },
            id="processor_with_null_dates",
        ),
    ],
)
def test_to_dict(tested: Any, expected: Any) -> None:
    """Test ProcessorVersion.to_dict correctly serializes processor version data for API requests."""
    result = tested.to_dict()
    assert result == expected
