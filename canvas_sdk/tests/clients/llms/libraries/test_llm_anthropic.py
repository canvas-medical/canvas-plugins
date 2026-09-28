import base64
import json
from datetime import date
from http import HTTPStatus
from types import SimpleNamespace
from typing import Any
from unittest.mock import call

import pytest
from pydantic import Field
from pytest_mock import MockerFixture
from requests import exceptions

from canvas_sdk.clients.llms.constants.file_type import FileType
from canvas_sdk.clients.llms.libraries.llm_anthropic import LlmAnthropic
from canvas_sdk.clients.llms.structures.base_model_llm_json import BaseModelLlmJson
from canvas_sdk.clients.llms.structures.file_content import FileContent
from canvas_sdk.clients.llms.structures.llm_file_url import LlmFileUrl
from canvas_sdk.clients.llms.structures.llm_response import LlmResponse
from canvas_sdk.clients.llms.structures.llm_tokens import LlmTokens
from canvas_sdk.clients.llms.structures.llm_turn import LlmTurn
from canvas_sdk.clients.llms.structures.settings.llm_settings import LlmSettings
from canvas_sdk.clients.llms.structures.settings.llm_settings_anthropic import LlmSettingsAnthropic


@pytest.mark.parametrize(
    ("file_content", "expected"),
    [
        pytest.param(
            FileContent(mime_type="image/jpeg", content=b"imgData", size=10),
            {
                "type": "image",
                "source": {"type": "base64", "media_type": "image/jpeg", "data": "imgData"},
            },
            id="image",
        ),
        pytest.param(
            FileContent(mime_type="application/pdf", content=b"pdfData", size=20),
            {
                "type": "document",
                "source": {"type": "base64", "media_type": "application/pdf", "data": "pdfData"},
            },
            id="pdf",
        ),
        pytest.param(
            FileContent(mime_type="text/plain", content=base64.b64encode(b"textData"), size=30),
            {
                "type": "document",
                "source": {"type": "text", "media_type": "text/plain", "data": "textData"},
            },
            id="text",
        ),
        pytest.param(
            FileContent(mime_type="application/octet-stream", content=b"binData", size=40),
            None,
            id="unknown",
        ),
    ],
)
def test__file_content_to_content_item(file_content: FileContent, expected: dict | None) -> None:
    """Test conversion of FileContent to Anthropic content item."""
    tested = LlmAnthropic
    result = tested._file_content_to_content_item(file_content)
    assert result == expected


@pytest.mark.parametrize(
    ("file_url", "mock_content", "expected", "exp_calls"),
    [
        pytest.param(
            LlmFileUrl(url="https://example.com/doc.pdf", type=FileType.PDF),
            None,
            {"type": "document", "source": {"type": "url", "url": "https://example.com/doc.pdf"}},
            [],
            id="pdf",
        ),
        pytest.param(
            LlmFileUrl(url="https://example.com/image.jpg", type=FileType.IMAGE),
            None,
            {"type": "image", "source": {"type": "url", "url": "https://example.com/image.jpg"}},
            [],
            id="image",
        ),
        pytest.param(
            LlmFileUrl(url="https://example.com/file.txt", type=FileType.TEXT),
            "text content",
            {
                "type": "document",
                "source": {"type": "text", "media_type": "text/plain", "data": "text content"},
            },
            [call(LlmFileUrl(url="https://example.com/file.txt", type=FileType.TEXT))],
            id="text",
        ),
    ],
)
def test__file_url_to_content_item(
    mocker: MockerFixture,
    file_url: LlmFileUrl,
    mock_content: str | None,
    expected: dict | None,
    exp_calls: list,
) -> None:
    """Test conversion of LlmFileUrl to Anthropic content item."""
    mock_str_content = mocker.patch.object(LlmAnthropic, "str_content_of")
    mock_str_content.side_effect = [mock_content] if mock_content else []

    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmAnthropic(settings)

    result = tested._file_url_to_content_item(file_url)
    assert result == expected
    assert mock_str_content.mock_calls == exp_calls


def test_to_dict() -> None:
    """Test conversion of prompts to Anthropic API format."""
    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmAnthropic(settings)

    # Test with system, user, and model prompts
    tested.add_prompt(LlmTurn(role="system", text=["system prompt 1"]))
    tested.add_prompt(LlmTurn(role="user", text=["user message 1"]))
    tested.add_prompt(LlmTurn(role="user", text=["user message 2"]))
    tested.add_prompt(LlmTurn(role="user", text=["user message 3"]))
    tested.add_prompt(LlmTurn(role="model", text=["model response 1"]))
    tested.add_prompt(LlmTurn(role="model", text=["model response 2"]))
    tested.add_prompt(LlmTurn(role="system", text=["system prompt 2"]))
    tested.add_prompt(LlmTurn(role="user", text=["user message 4"]))

    result = tested.to_dict()

    # System and user are both mapped to "user" role and merged
    expected = {
        "messages": [
            {
                "content": [
                    {"text": "system prompt 2", "type": "text"},
                    {"text": "user message 1", "type": "text"},
                    {"text": "user message 2", "type": "text"},
                    {"text": "user message 3", "type": "text"},
                ],
                "role": "user",
            },
            {
                "content": [
                    {"text": "model response 1", "type": "text"},
                    {"text": "model response 2", "type": "text"},
                ],
                "role": "assistant",
            },
            {
                "content": [
                    {"text": "user message 4", "type": "text"},
                ],
                "role": "user",
            },
        ],
        "model": "test_model",
    }

    assert result == expected


@pytest.mark.parametrize(
    ("prompts", "exp_key", "exp_file_urls", "exp_file_contents", "exp_calls"),
    [
        # no turn
        pytest.param(
            [],
            "exp_empty",
            4,
            3,
            [],
            id="no_turn",
        ),
        # model turn
        pytest.param(
            [LlmTurn(role="model", text=["the response"])],
            "exp_model",
            4,
            3,
            [],
            id="model_turn",
        ),
        # system turn
        pytest.param(
            [LlmTurn(role="system", text=["the prompt"])],
            "exp_user",
            0,
            0,
            [call(LlmFileUrl(url="https://example.com/text.txt", type=FileType.TEXT))],
            id="system_turn",
        ),
        # user turn
        pytest.param(
            [LlmTurn(role="user", text=["the prompt"])],
            "exp_user",
            0,
            0,
            [call(LlmFileUrl(url="https://example.com/text.txt", type=FileType.TEXT))],
            id="user_turn",
        ),
    ],
)
def test_to_dict__with_files(
    mocker: MockerFixture,
    prompts: list,
    exp_key: str,
    exp_file_urls: int,
    exp_file_contents: int,
    exp_calls: list,
) -> None:
    """Test conversion of prompts with file attachments to Anthropic API format."""
    str_content_of = mocker.patch.object(LlmAnthropic, "str_content_of")

    to_dict_returns = {
        "exp_empty": {"model": "test_model", "messages": []},
        "exp_model": {
            "model": "test_model",
            "messages": [
                {
                    "content": [{"text": "the response", "type": "text"}],
                    "role": "assistant",
                }
            ],
        },
        "exp_user": {
            "model": "test_model",
            "messages": [
                {
                    "content": [
                        {
                            "text": "the prompt",
                            "type": "text",
                        },
                        {
                            "source": {
                                "type": "url",
                                "url": "https://example.com/doc.pdf",
                            },
                            "type": "document",
                        },
                        {
                            "source": {
                                "type": "url",
                                "url": "https://example.com/pic.jpg",
                            },
                            "type": "image",
                        },
                        {
                            "source": {
                                "data": "theContent",
                                "media_type": "text/plain",
                                "type": "text",
                            },
                            "type": "document",
                        },
                        {
                            "source": {
                                "data": "Y29udGVudDQ=",
                                "media_type": "image/png",
                                "type": "base64",
                            },
                            "type": "image",
                        },
                        {
                            "source": {
                                "data": "Y29udGVudDU=",
                                "media_type": "application/pdf",
                                "type": "base64",
                            },
                            "type": "document",
                        },
                        {
                            "source": {
                                "data": "content6",
                                "media_type": "text/plain",
                                "type": "text",
                            },
                            "type": "document",
                        },
                    ],
                    "role": "user",
                },
            ],
        },
    }

    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmAnthropic(settings)

    tested.file_urls = [
        LlmFileUrl(url="https://example.com/doc.pdf", type=FileType.PDF),
        LlmFileUrl(url="https://example.com/pic.jpg", type=FileType.IMAGE),
        LlmFileUrl(url="https://example.com/text.txt", type=FileType.TEXT),
        LlmFileUrl(url="https://example.com/some.nop", type="unknown"),  # type: ignore
    ]
    assert len(tested.file_urls) == 4
    tested.file_contents = [
        FileContent(
            mime_type="image/png", size=1 * 1024 * 1024, content=base64.b64encode(b"content4")
        ),
        FileContent(
            mime_type="application/pdf", size=2 * 1024 * 1024, content=base64.b64encode(b"content5")
        ),
        FileContent(
            mime_type="text/plain", size=2 * 1024 * 1024, content=base64.b64encode(b"content6")
        ),
    ]
    assert len(tested.file_contents) == 3

    for prompt in prompts:
        tested.add_prompt(prompt)

    str_content_of.side_effect = ["theContent"]
    result = tested.to_dict()
    assert result == to_dict_returns[exp_key]
    assert len(tested.file_urls) == exp_file_urls
    assert len(tested.file_contents) == exp_file_contents

    assert str_content_of.mock_calls == exp_calls


def test_to_dict__schema() -> None:
    """Test conversion of prompts with schema to Anthropic API format."""

    class SchemaLlm(BaseModelLlmJson):
        first_field: int = Field(description="the first field")
        second_field: str = Field(description="the second field")
        third_field: date = Field(description="the third field")

    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmAnthropic(settings)
    tested.add_prompt(LlmTurn(role="system", text=["system prompt"]))
    tested.add_prompt(LlmTurn(role="user", text=["user message"]))

    tested.set_schema(SchemaLlm)
    result = tested.to_dict()
    expected = {
        "messages": [
            {
                "content": [
                    {"text": "system prompt", "type": "text"},
                    {"text": "user message", "type": "text"},
                ],
                "role": "user",
            },
        ],
        "model": "test_model",
        "tool_choice": {
            "name": "SchemaLlm",
            "type": "tool",
        },
        "tools": [
            {
                "input_schema": {
                    "additionalProperties": False,
                    "properties": {
                        "firstField": {
                            "description": "the first field",
                            "title": "Firstfield",
                            "type": "integer",
                        },
                        "secondField": {
                            "description": "the second field",
                            "title": "Secondfield",
                            "type": "string",
                        },
                        "thirdField": {
                            "description": "the third field",
                            "format": "date",
                            "title": "Thirdfield",
                            "type": "string",
                        },
                    },
                    "required": ["firstField", "secondField", "thirdField"],
                    "title": "SchemaLlm",
                    "type": "object",
                },
                "name": "SchemaLlm",
            },
        ],
    }
    assert result == expected


def test__api_base_url() -> None:
    """Test the defined URL of the Http instance."""
    tested = LlmAnthropic
    result = tested._api_base_url()
    expected = "https://api.anthropic.com"
    assert result == expected


@pytest.mark.parametrize(
    ("with_schema", "response", "expected"),
    [
        pytest.param(
            False,
            SimpleNamespace(
                status_code=200,
                text="{"
                '"content": [{"text": "response text"}], '
                '"usage": {"input_tokens": 10, "output_tokens": 20}'
                "}",
            ),
            LlmResponse(
                code=HTTPStatus.OK,
                response="response text",
                tokens=LlmTokens(prompt=10, generated=20),
            ),
            id="all_good_no_schema",
        ),
        pytest.param(
            True,
            SimpleNamespace(
                status_code=200,
                text="{"
                '"content": [{"input": {"firstField":7,"secondField":"second","thirdField":"2025-12-01"}}], '
                '"usage": {"input_tokens": 10, "output_tokens": 20}'
                "}",
            ),
            LlmResponse(
                code=HTTPStatus.OK,
                response='{"firstField": 7, "secondField": "second", "thirdField": "2025-12-01"}',
                tokens=LlmTokens(prompt=10, generated=20),
            ),
            id="all_good_with_schema",
        ),
        pytest.param(
            False,
            SimpleNamespace(
                status_code=403,
                text="forbidden",
            ),
            LlmResponse(
                code=HTTPStatus.FORBIDDEN,
                response="forbidden",
                tokens=LlmTokens(prompt=0, generated=0),
            ),
            id="error",
        ),
        pytest.param(
            False,
            exceptions.RequestException("Connection error"),
            LlmResponse(
                code=HTTPStatus.BAD_REQUEST,
                response="Request failed: Connection error",
                tokens=LlmTokens(prompt=0, generated=0),
            ),
            id="exception--no-response",
        ),
        pytest.param(
            False,
            exceptions.RequestException(
                "Server error",
                response=SimpleNamespace(status_code=404, text="not found"),  # type: ignore[arg-type]
            ),
            LlmResponse(
                code=HTTPStatus.NOT_FOUND,
                response="not found",
                tokens=LlmTokens(prompt=0, generated=0),
            ),
            id="exception--with-response",
        ),
    ],
)
def test_request(
    mocker: MockerFixture,
    with_schema: bool,
    response: Any,
    expected: LlmResponse,
) -> None:
    """Test successful API request to Anthropic."""
    mock_http = mocker.patch("canvas_sdk.clients.llms.libraries.llm_api.Http")
    mock_http.return_value.post.side_effect = [response]

    class SchemaLlm(BaseModelLlmJson):
        first_field: int = Field(description="the first field")
        second_field: str = Field(description="the second field")
        third_field: date = Field(description="the third field")

    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmAnthropic(settings)
    tested.add_prompt(LlmTurn(role="user", text=["test"]))

    if with_schema:
        tested.set_schema(SchemaLlm)
    result = tested.request()
    assert result == expected

    exp_calls = [
        call("https://api.anthropic.com"),
        call().post(
            "/v1/messages",
            headers={
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
                "x-api-key": "test_key",
            },
            data="{"
            '"model": "test_model", '
            '"messages": [{'
            '"role": "user", '
            '"content": [{"type": "text", "text": "test"}]'
            "}]"
            "}",
        ),
    ]
    if with_schema:
        exp_calls[1] = call().post(
            "/v1/messages",
            headers={
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
                "x-api-key": "test_key",
            },
            data="{"
            '"model": "test_model", '
            '"tool_choice": {"type": "tool", "name": "SchemaLlm"}, '
            '"tools": [{'
            '"name": "SchemaLlm", '
            '"input_schema": {'
            '"additionalProperties": false, '
            '"properties": {'
            '"firstField": {"description": "the first field", "title": "Firstfield", "type": "integer"}, '
            '"secondField": {"description": "the second field", "title": "Secondfield", "type": "string"}, '
            '"thirdField": {"description": "the third field", "format": "date", "title": "Thirdfield", "type": "string"}}, '
            '"required": ["firstField", "secondField", "thirdField"], '
            '"title": "SchemaLlm", "type": "object"}}], '
            '"messages": [{"role": "user", "content": [{"type": "text", "text": "test"}]}]}',
        )

    assert mock_http.mock_calls == exp_calls


def _structured_settings() -> LlmSettingsAnthropic:
    return LlmSettingsAnthropic(
        api_key="test_key",
        model="test_model",
        temperature=None,
        max_tokens=16000,
        structured_outputs=True,
    )


class _EffortSettings(LlmSettingsAnthropic):
    def to_dict(self) -> dict:
        return super().to_dict() | {"output_config": {"effort": "high"}}


def test_to_dict__schema_structured_outputs_keeps_settings_output_config() -> None:
    """Test that the schema format merges into an output_config the settings already set."""

    class SchemaLlm(BaseModelLlmJson):
        first_field: int = Field(description="the first field")

    settings = _EffortSettings(
        api_key="test_key",
        model="test_model",
        temperature=None,
        max_tokens=16000,
        structured_outputs=True,
    )
    tested = LlmAnthropic(settings)
    tested.add_prompt(LlmTurn(role="user", text=["user message"]))

    tested.set_schema(SchemaLlm)
    result = tested.to_dict()["output_config"]
    assert result["effort"] == "high"
    assert result["format"]["type"] == "json_schema"
    assert result["format"]["schema"]["title"] == "SchemaLlm"


def test_to_dict__schema_structured_outputs() -> None:
    """Test that structured_outputs requests the schema through output_config instead of a tool."""

    class SchemaLlm(BaseModelLlmJson):
        first_field: int = Field(description="the first field")
        second_field: date = Field(description="the second field")

    tested = LlmAnthropic(_structured_settings())
    tested.add_prompt(LlmTurn(role="user", text=["user message"]))

    tested.set_schema(SchemaLlm)
    result = tested.to_dict()
    expected = {
        "messages": [{"content": [{"text": "user message", "type": "text"}], "role": "user"}],
        "model": "test_model",
        "max_tokens": 16000,
        "output_config": {
            "format": {
                "type": "json_schema",
                "schema": {
                    "additionalProperties": False,
                    "properties": {
                        "firstField": {
                            "description": "the first field",
                            "title": "Firstfield",
                            "type": "integer",
                        },
                        "secondField": {
                            "description": "the second field",
                            "format": "date",
                            "title": "Secondfield",
                            "type": "string",
                        },
                    },
                    "required": ["firstField", "secondField"],
                    "title": "SchemaLlm",
                    "type": "object",
                },
            },
        },
    }
    assert result == expected


class _ConstrainedItemLlm(BaseModelLlmJson):
    label: str = Field(description="the label", min_length=1, max_length=40)


class _ConstrainedSchemaLlm(BaseModelLlmJson):
    confidence: float = Field(description="the confidence", ge=0.0, le=1.0)
    items: list[_ConstrainedItemLlm] = Field(description="the items", min_length=1, max_length=5)
    tags: list[str] = Field(description="the tags", min_length=2)
    secret: str = Field(json_schema_extra={"format": "password"})


def test_to_dict__schema_structured_outputs_unsupported_keywords() -> None:
    """Test that JSON Schema keywords structured outputs rejects are moved into descriptions."""
    tested = LlmAnthropic(_structured_settings())
    tested.add_prompt(LlmTurn(role="user", text=["user message"]))

    tested.set_schema(_ConstrainedSchemaLlm)
    result = tested.to_dict()["output_config"]["format"]["schema"]
    expected = {
        "$defs": {
            "_ConstrainedItemLlm": {
                "additionalProperties": False,
                "properties": {
                    "label": {
                        "description": "the label (maxLength: 40, minLength: 1)",
                        "title": "Label",
                        "type": "string",
                    },
                },
                "required": ["label"],
                "title": "_ConstrainedItemLlm",
                "type": "object",
            },
        },
        "additionalProperties": False,
        "properties": {
            "confidence": {
                "description": "the confidence (maximum: 1.0, minimum: 0.0)",
                "title": "Confidence",
                "type": "number",
            },
            "items": {
                "description": "the items (maxItems: 5)",
                "items": {"$ref": "#/$defs/_ConstrainedItemLlm"},
                "minItems": 1,
                "title": "Items",
                "type": "array",
            },
            "tags": {
                "description": "the tags (minItems: 2)",
                "items": {"type": "string"},
                "title": "Tags",
                "type": "array",
            },
            "secret": {
                "description": "(format: password)",
                "title": "Secret",
                "type": "string",
            },
        },
        "required": ["confidence", "items", "tags", "secret"],
        "title": "_ConstrainedSchemaLlm",
        "type": "object",
    }
    assert result == expected
    # the model's own schema is left untouched
    assert _ConstrainedSchemaLlm.model_json_schema()["properties"]["confidence"]["minimum"] == 0.0


def test_to_dict__schema_tool_keeps_keywords() -> None:
    """Test that the default forced-tool path sends the schema unchanged, constraints included."""
    settings = LlmSettingsAnthropic(
        api_key="test_key", model="test_model", temperature=0.0, max_tokens=8192
    )
    tested = LlmAnthropic(settings)
    tested.add_prompt(LlmTurn(role="user", text=["user message"]))

    tested.set_schema(_ConstrainedSchemaLlm)
    result = tested.to_dict()
    assert result["tool_choice"] == {"type": "tool", "name": "_ConstrainedSchemaLlm"}
    assert result["tools"][0]["input_schema"] == _ConstrainedSchemaLlm.model_json_schema()
    assert result["temperature"] == 0.0
    assert "output_config" not in result


@pytest.mark.parametrize(
    ("structured_outputs", "with_schema", "content", "expected"),
    [
        pytest.param(
            True,
            True,
            [
                {"type": "thinking", "thinking": "", "signature": "sig"},
                {"type": "text", "text": '{"firstField":7,'},
                {"type": "text", "text": '"secondField":"second"}'},
            ],
            '{"firstField":7,"secondField":"second"}',
            id="structured_outputs--thinking_then_split_text",
        ),
        pytest.param(
            False,
            False,
            [
                {"type": "thinking", "thinking": "", "signature": "sig"},
                {"type": "text", "text": "the answer"},
            ],
            "the answer",
            id="no_schema--thinking_then_text",
        ),
        pytest.param(
            False,
            False,
            [{"type": "text", "text": "first"}, {"type": "text", "text": "second"}],
            "first",
            id="no_schema--first_text_block",
        ),
        pytest.param(
            False,
            False,
            [{"type": "thinking", "thinking": "", "signature": "sig"}],
            "",
            id="no_schema--no_text_block",
        ),
    ],
)
def test_request__content_blocks(
    mocker: MockerFixture,
    structured_outputs: bool,
    with_schema: bool,
    content: list[dict],
    expected: str,
) -> None:
    """Test that the response is read from content blocks by type, skipping thinking blocks."""

    class SchemaLlm(BaseModelLlmJson):
        first_field: int = Field(description="the first field")
        second_field: str = Field(description="the second field")

    mock_http = mocker.patch("canvas_sdk.clients.llms.libraries.llm_api.Http")
    mock_http.return_value.post.side_effect = [
        SimpleNamespace(
            status_code=200,
            text=json.dumps(
                {"content": content, "usage": {"input_tokens": 10, "output_tokens": 20}}
            ),
        )
    ]

    settings = _structured_settings()
    settings.structured_outputs = structured_outputs
    tested = LlmAnthropic(settings)
    tested.add_prompt(LlmTurn(role="user", text=["test"]))
    if with_schema:
        tested.set_schema(SchemaLlm)

    result = tested.request()
    assert result == LlmResponse(
        code=HTTPStatus.OK,
        response=expected,
        tokens=LlmTokens(prompt=10, generated=20),
    )
