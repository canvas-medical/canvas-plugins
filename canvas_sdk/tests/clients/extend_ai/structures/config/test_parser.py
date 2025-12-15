from typing import Any

import pytest

from canvas_sdk.clients.extend_ai.constants.parser_chunking import ParserChunking
from canvas_sdk.clients.extend_ai.constants.parser_target import ParserTarget
from canvas_sdk.clients.extend_ai.structures.config.parser import Parser
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test that Parser is a dataclass with the expected field types."""
    tested = Parser
    fields = {
        "target": ParserTarget,
        "chunking_strategy": ParserChunking,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "target": "markdown",
                "chunkingStrategy": {"type": "page"},
            },
            Parser(
                target=ParserTarget.MARKDOWN,
                chunking_strategy=ParserChunking.PAGE,
            ),
            id="markdown_page",
        ),
        pytest.param(
            {
                "target": "spatial",
                "chunkingStrategy": {"type": "document"},
            },
            Parser(
                target=ParserTarget.SPATIAL,
                chunking_strategy=ParserChunking.DOCUMENT,
            ),
            id="spatial_document",
        ),
        pytest.param(
            {},
            Parser(
                target=ParserTarget.MARKDOWN,
                chunking_strategy=ParserChunking.DOCUMENT,
            ),
            id="empty_dict_defaults",
        ),
        pytest.param(
            {
                "chunkingStrategy": {},
            },
            Parser(
                target=ParserTarget.MARKDOWN,
                chunking_strategy=ParserChunking.DOCUMENT,
            ),
            id="empty_chunking_strategy_defaults",
        ),
    ],
)
def test_from_dict(data: Any, expected: Any) -> None:
    """Test Parser.from_dict correctly deserializes parser config with defaults for empty values."""
    tested = Parser
    result = tested.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("tested", "expected"),
    [
        pytest.param(
            Parser(
                target=ParserTarget.MARKDOWN,
                chunking_strategy=ParserChunking.PAGE,
            ),
            {
                "target": "markdown",
                "chunkingStrategy": {"type": "page"},
            },
            id="markdown_page",
        ),
        pytest.param(
            Parser(
                target=ParserTarget.SPATIAL,
                chunking_strategy=ParserChunking.DOCUMENT,
            ),
            {
                "target": "spatial",
                "chunkingStrategy": {"type": "document"},
            },
            id="spatial_document",
        ),
        pytest.param(
            Parser(
                target=ParserTarget.MARKDOWN,
                chunking_strategy=ParserChunking.SECTION,
            ),
            {
                "target": "markdown",
                "chunkingStrategy": {"type": "section"},
            },
            id="markdown_section",
        ),
    ],
)
def test_to_dict(tested: Any, expected: Any) -> None:
    """Test Parser.to_dict correctly serializes parser configuration for API requests."""
    result = tested.to_dict()
    assert result == expected
