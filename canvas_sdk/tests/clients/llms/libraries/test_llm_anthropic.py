from http import HTTPStatus
from types import SimpleNamespace
from typing import Any
from unittest.mock import call

import pytest
from pytest_mock import MockerFixture
from requests import exceptions

from canvas_sdk.clients.llms.libraries.llm_anthropic import LlmAnthropic
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


def test__api_base_url() -> None:
    """Test the defined URL of the Http instance."""
    tested = LlmAnthropic
    result = tested._api_base_url()
    expected = "https://api.anthropic.com"
    assert result == expected


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        pytest.param(
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
            id="all_good",
        ),
        pytest.param(
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
    """Test successful API request to Anthropic."""
    http = mocker.patch("canvas_sdk.clients.llms.libraries.llm_api.Http")
    http.return_value.post.side_effect = [response]

    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmAnthropic(settings)
    tested.add_prompt(LlmTurn(role="user", text=["test"]))

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
    assert http.mock_calls == calls
