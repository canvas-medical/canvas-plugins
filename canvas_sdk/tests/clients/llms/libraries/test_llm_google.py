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
from canvas_sdk.clients.llms.libraries.llm_google import LlmGoogle
from canvas_sdk.clients.llms.structures.base_model_llm_json import BaseModelLlmJson
from canvas_sdk.clients.llms.structures.file_content import FileContent
from canvas_sdk.clients.llms.structures.llm_file_url import LlmFileUrl
from canvas_sdk.clients.llms.structures.llm_response import LlmResponse
from canvas_sdk.clients.llms.structures.llm_tokens import LlmTokens
from canvas_sdk.clients.llms.structures.llm_turn import LlmTurn
from canvas_sdk.clients.llms.structures.settings.llm_settings import LlmSettings


def test_to_dict() -> None:
    """Test conversion of prompts to Google API format."""
    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmGoogle(settings)

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
        "contents": [
            {
                "parts": [
                    {"text": "system prompt 2"},
                    {"text": "user message 1"},
                    {"text": "user message 2"},
                    {"text": "user message 3"},
                ],
                "role": "user",
            },
            {
                "parts": [
                    {"text": "model response 1"},
                    {"text": "model response 2"},
                ],
                "role": "model",
            },
            {
                "parts": [
                    {"text": "user message 4"},
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
        pytest.param(
            [],
            "exp_empty",
            3,
            3,
            False,
            id="no_turn",
        ),
        pytest.param(
            [LlmTurn(role="model", text=["the response"])],
            "exp_model",
            3,
            3,
            False,
            id="model_turn",
        ),
        pytest.param(
            [LlmTurn(role="system", text=["the prompt"])],
            "exp_user",
            0,
            0,
            True,
            id="system_turn",
        ),
        pytest.param(
            [LlmTurn(role="user", text=["the prompt"])],
            "exp_user",
            0,
            0,
            True,
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
    exp_calls: bool,
) -> None:
    """Test conversion of prompts with file attachments to Google API format."""
    base64_encoded_content_of = mocker.patch.object(LlmGoogle, "base64_encoded_content_of")

    to_dict_returns = {
        "exp_empty": {"model": "test_model", "contents": []},
        "exp_model": {
            "model": "test_model",
            "contents": [
                {
                    "parts": [{"text": "the response"}],
                    "role": "model",
                }
            ],
        },
        "exp_user": {
            "model": "test_model",
            "contents": [
                {
                    "parts": [
                        {"text": "the prompt"},
                        {"inline_data": {"data": "Y29udGVudDE=", "mime_type": "type1"}},
                        {"inline_data": {"data": "Y29udGVudDI=", "mime_type": "type2"}},
                        {"inline_data": {"data": "Y29udGVudDM=", "mime_type": "type3"}},
                        {"inline_data": {"data": "Y29udGVudDQ=", "mime_type": "type4"}},
                    ],
                    "role": "user",
                }
            ],
        },
    }
    call_on_files = [
        call(LlmFileUrl(url="https://example.com/doc1.pdf", type=FileType.PDF)),
        call(LlmFileUrl(url="https://example.com/pic1.jpg", type=FileType.IMAGE)),
        call(LlmFileUrl(url="https://example.com/text1.txt", type=FileType.TEXT)),
    ]

    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmGoogle(settings)
    tested.file_urls = [
        LlmFileUrl(url="https://example.com/doc1.pdf", type=FileType.PDF),
        LlmFileUrl(url="https://example.com/pic1.jpg", type=FileType.IMAGE),
        LlmFileUrl(url="https://example.com/text1.txt", type=FileType.TEXT),
    ]
    assert len(tested.file_urls) == 3
    tested.file_contents = [
        FileContent(mime_type="type4", size=1 * 1024 * 1024, content=base64.b64encode(b"content4")),
        FileContent(mime_type="type5", size=2 * 1024 * 1024, content=base64.b64encode(b"content5")),
        FileContent(mime_type="type6", size=2 * 1024 * 1024, content=base64.b64encode(b"content6")),
    ]
    assert len(tested.file_contents) == 3

    for prompt in prompts:
        tested.add_prompt(prompt)

    base64_encoded_content_of.side_effect = [
        FileContent(mime_type="type1", content=base64.b64encode(b"content1"), size=3 * 1024 * 1024),
        FileContent(mime_type="type2", content=base64.b64encode(b"content2"), size=3 * 1024 * 1024),
        FileContent(mime_type="type3", content=base64.b64encode(b"content3"), size=2 * 1024 * 1024),
    ]
    result = tested.to_dict()
    assert result == to_dict_returns[exp_key]
    assert len(tested.file_urls) == exp_file_urls
    assert len(tested.file_contents) == exp_file_contents
    calls = []
    if exp_calls:
        calls = call_on_files
    assert base64_encoded_content_of.mock_calls == calls


def test_to_dict__schema() -> None:
    """Test conversion of prompts with schema to Google API format."""

    class SchemaLlm(BaseModelLlmJson):
        first_field: int = Field(description="the first field")
        second_field: str = Field(description="the second field")
        third_field: date = Field(description="the third field")

    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmGoogle(settings)
    tested.add_prompt(LlmTurn(role="system", text=["system prompt"]))
    tested.add_prompt(LlmTurn(role="user", text=["user message"]))

    tested.set_schema(SchemaLlm)
    result = tested.to_dict()
    expected = {
        "contents": [
            {
                "parts": [
                    {"text": "system prompt"},
                    {"text": "user message"},
                ],
                "role": "user",
            },
        ],
        "generationConfig": {
            "responseJsonSchema": {
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
            "responseMimeType": "application/json",
        },
        "model": "test_model",
    }

    assert result == expected


def test__api_base_url() -> None:
    """Test the defined URL of the Http instance."""
    tested = LlmGoogle
    result = tested._api_base_url()
    expected = "https://generativelanguage.googleapis.com"
    assert result == expected


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        pytest.param(
            SimpleNamespace(
                status_code=200,
                text="{"
                '"candidates": [{"content": {"parts": [{"text": "response text"}]}}], '
                '"usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 15, "thoughtsTokenCount": 5}'
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
    """Test successful API request to Google."""
    mock_http = mocker.patch("canvas_sdk.clients.llms.libraries.llm_api.Http")
    mock_http.return_value.post.side_effect = [response]

    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmGoogle(settings)
    tested.add_prompt(LlmTurn(role="user", text=["test"]))

    result = tested.request()
    assert result == expected

    exp_calls = [
        call("https://generativelanguage.googleapis.com"),
        call().post(
            "/v1beta/test_model:generateContent?key=test_key",
            headers={
                "Content-Type": "application/json",
            },
            data="{"
            '"model": "test_model", '
            '"contents": [{'
            '"role": "user", '
            '"parts": [{"text": "test"}]'
            "}]"
            "}",
        ),
    ]
    assert mock_http.mock_calls == exp_calls
