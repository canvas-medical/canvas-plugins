from http import HTTPStatus
from types import SimpleNamespace
from typing import Any
from unittest.mock import call

import pytest
from pytest_mock import MockerFixture
from requests import exceptions

from canvas_sdk.clients.llms.libraries.llm_google import LlmGoogle
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
    http = mocker.patch("canvas_sdk.clients.llms.libraries.llm_google.Http")
    http.return_value.post.side_effect = [response]

    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmGoogle(settings)
    tested.add_prompt(LlmTurn(role="user", text=["test"]))

    result = tested.request()
    assert result == expected

    calls = [
        call(
            "https://generativelanguage.googleapis.com/"
            "v1beta/"
            "test_model:generateContent?key=test_key"
        ),
        call().post(
            "",
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
    assert http.mock_calls == calls
