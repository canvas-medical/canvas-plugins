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
from canvas_sdk.clients.llms.libraries.llm_openai import LlmOpenai
from canvas_sdk.clients.llms.structures.base_model_llm_json import BaseModelLlmJson
from canvas_sdk.clients.llms.structures.llm_file_url import LlmFileUrl
from canvas_sdk.clients.llms.structures.llm_response import LlmResponse
from canvas_sdk.clients.llms.structures.llm_tokens import LlmTokens
from canvas_sdk.clients.llms.structures.llm_turn import LlmTurn
from canvas_sdk.clients.llms.structures.settings.llm_settings import LlmSettings


def test_to_dict() -> None:
    """Test conversion of prompts to OpenAI API format."""
    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmOpenai(settings)

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

    # System prompts replace each other (only last one is kept), others are in input
    expected = {
        "input": [
            {
                "content": [{"text": "user message 1", "type": "input_text"}],
                "role": "user",
            },
            {
                "content": [{"text": "user message 2", "type": "input_text"}],
                "role": "user",
            },
            {
                "content": [{"text": "user message 3", "type": "input_text"}],
                "role": "user",
            },
            {
                "content": [{"text": "model response 1", "type": "output_text"}],
                "role": "assistant",
            },
            {
                "content": [{"text": "model response 2", "type": "output_text"}],
                "role": "assistant",
            },
            {
                "content": [{"text": "user message 4", "type": "input_text"}],
                "role": "user",
            },
        ],
        "instructions": "system prompt 2",
        "model": "test_model",
    }

    assert result == expected


@pytest.mark.parametrize(
    ("prompts", "expected", "exp_files"),
    [
        pytest.param(
            [],
            {"model": "test_model", "instructions": "", "input": []},
            3,
            id="no_turn",
        ),
        pytest.param(
            [LlmTurn(role="model", text=["the response"])],
            {
                "model": "test_model",
                "instructions": "",
                "input": [
                    {
                        "content": [{"text": "the response", "type": "output_text"}],
                        "role": "assistant",
                    }
                ],
            },
            3,
            id="model_turn",
        ),
        pytest.param(
            [LlmTurn(role="system", text=["the system prompt"])],
            {"model": "test_model", "instructions": "the system prompt", "input": []},
            3,
            id="system_turn",
        ),
        pytest.param(
            [LlmTurn(role="user", text=["the user prompt"])],
            {
                "model": "test_model",
                "instructions": "",
                "input": [
                    {
                        "content": [
                            {"text": "the user prompt", "type": "input_text"},
                            {"file_url": "https://example.com/doc.pdf", "type": "input_file"},
                            {"image_url": "https://example.com/pic.jpg", "type": "input_image"},
                        ],
                        "role": "user",
                    }
                ],
            },
            0,
            id="user_turn",
        ),
    ],
)
def test_to_dict__with_files(prompts: list, expected: dict, exp_files: int) -> None:
    """Test conversion of prompts with file attachments to OpenAI API format."""
    settings = LlmSettings(api_key="test_key", model="test_model")

    tested = LlmOpenai(settings)

    tested.file_urls = [
        LlmFileUrl(url="https://example.com/doc.pdf", type=FileType.PDF),
        LlmFileUrl(url="https://example.com/pic.jpg", type=FileType.IMAGE),
        LlmFileUrl(url="https://example.com/text.txt", type=FileType.TEXT),
    ]
    assert len(tested.file_urls) == 3

    for prompt in prompts:
        tested.add_prompt(prompt)

    result = tested.to_dict()
    assert result == expected
    assert len(tested.file_urls) == exp_files


def test_to_dict__schema() -> None:
    """Test conversion of prompts with schema to Google API format."""

    class SchemaLlm(BaseModelLlmJson):
        first_field: int = Field(description="the first field")
        second_field: str = Field(description="the second field")
        third_field: date = Field(description="the third field")

    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmOpenai(settings)
    tested.add_prompt(LlmTurn(role="system", text=["system prompt"]))
    tested.add_prompt(LlmTurn(role="user", text=["user message"]))

    tested.set_schema(SchemaLlm)
    result = tested.to_dict()
    expected = {
        "input": [
            {
                "content": [{"text": "user message", "type": "input_text"}],
                "role": "user",
            },
        ],
        "instructions": "system prompt",
        "model": "test_model",
        "text": {
            "format": {
                "name": "SchemaLlm",
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
                "strict": True,
                "type": "json_schema",
            },
        },
    }

    assert result == expected


def test__api_base_url() -> None:
    """Test the defined URL of the Http instance."""
    tested = LlmOpenai
    result = tested._api_base_url()
    expected = "https://us.api.openai.com"
    assert result == expected


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        pytest.param(
            SimpleNamespace(
                status_code=200,
                text="{"
                '"output": [{"type": "message", "content": [{"text": "response text"}]}], '
                '"usage": {"input_tokens": 10, "output_tokens": 20}'
                "}",
            ),
            LlmResponse(
                code=HTTPStatus.OK,
                response="response text",
                tokens=LlmTokens(prompt=10, generated=20),
            ),
            id="all_good",
        ),
        pytest.param(
            SimpleNamespace(
                status_code=429,
                text="Rate limit exceeded",
            ),
            LlmResponse(
                code=HTTPStatus.TOO_MANY_REQUESTS,
                response="Rate limit exceeded",
                tokens=LlmTokens(prompt=0, generated=0),
            ),
            id="error",
        ),
        pytest.param(
            SimpleNamespace(
                status_code=200,
                text="{"
                '"output": ['
                '{"type": "message", "content": [{"text": "part1"}]}, '
                '{"type": "something", "content": [{"text": "nope"}]}, '
                '{"type": "message", "content": [{"text": "part2"}]}'
                "], "
                '"usage": {"input_tokens": 10, "output_tokens": 20}'
                "}",
            ),
            LlmResponse(
                code=HTTPStatus.OK,
                response="part1part2",
                tokens=LlmTokens(prompt=10, generated=20),
            ),
            id="multiple-output-messages",
        ),
        pytest.param(
            exceptions.RequestException("Connection error"),
            LlmResponse(
                code=HTTPStatus.BAD_REQUEST,
                response="Request failed: Connection error",
                tokens=LlmTokens(prompt=0, generated=0),
            ),
            id="exception--no-response",
        ),
        pytest.param(
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
def test_request(mocker: MockerFixture, response: Any, expected: LlmResponse) -> None:
    """Test successful API request to OpenAI."""
    http = mocker.patch("canvas_sdk.clients.llms.libraries.llm_api.Http")
    http.return_value.post.side_effect = [response]

    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmOpenai(settings)
    tested.add_prompt(LlmTurn(role="user", text=["test"]))

    result = tested.request()
    assert result == expected

    calls = [
        call("https://us.api.openai.com"),
        call().post(
            "/v1/responses",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer test_key",
            },
            data="{"
            '"model": "test_model", '
            '"instructions": "", '
            '"input": [{'
            '"role": "user", '
            '"content": [{"type": "input_text", "text": "test"}]'
            "}]"
            "}",
        ),
    ]
    assert http.mock_calls == calls
