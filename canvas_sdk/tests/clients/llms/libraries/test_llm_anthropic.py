import base64
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
    ("prompts", "exp_key", "exp_files", "exp_calls"),
    [
        # no turn
        pytest.param(
            [],
            "exp_empty",
            4,
            [],
            id="no_turn",
        ),
        # model turn
        pytest.param(
            [LlmTurn(role="model", text=["the response"])],
            "exp_model",
            4,
            [],
            id="model_turn",
        ),
        # system turn
        pytest.param(
            [LlmTurn(role="system", text=["the prompt"])],
            "exp_user",
            0,
            [call(LlmFileUrl(url="https://example.com/text.txt", type=FileType.TEXT))],
            id="system_turn",
        ),
        # user turn
        pytest.param(
            [LlmTurn(role="user", text=["the prompt"])],
            "exp_user",
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
    exp_files: int,
    exp_calls: list,
) -> None:
    """Test conversion of prompts with file attachments to Anthropic API format."""
    base64_encoded_content_of = mocker.patch.object(LlmAnthropic, "base64_encoded_content_of")

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

    for prompt in prompts:
        tested.add_prompt(prompt)

    base64_encoded_content_of.side_effect = [
        FileContent(
            mime_type="theMimeType",
            content=base64.b64encode(b"theContent"),
            size=123,
        )
    ]
    result = tested.to_dict()
    assert result == to_dict_returns[exp_key]
    assert len(tested.file_urls) == exp_files

    assert base64_encoded_content_of.mock_calls == exp_calls


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
    http = mocker.patch("canvas_sdk.clients.llms.libraries.llm_api.Http")
    http.return_value.post.side_effect = [response]

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

    calls = [
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
        calls[1] = call().post(
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

    assert http.mock_calls == calls
