from http import HTTPStatus
from types import SimpleNamespace
from typing import Any
from unittest.mock import call

import pytest
from pytest_mock import MockerFixture
from requests import exceptions

from canvas_sdk.clients.llms.libraries.llm_openai import LlmOpenai
from canvas_sdk.clients.llms.structures.llm_response import LlmResponse
from canvas_sdk.clients.llms.structures.llm_tokens import LlmTokens
from canvas_sdk.clients.llms.structures.llm_turn import LlmTurn
from canvas_sdk.clients.llms.structures.settings.llm_settings import LlmSettings
from canvas_sdk.utils import Http


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


def test__http() -> None:
    """Test the defined URL of the Http instance."""
    tested = LlmOpenai
    result = tested._http()
    assert isinstance(result, Http)
    assert result._base_url == "https://us.api.openai.com"


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
    http = mocker.patch("canvas_sdk.clients.llms.libraries.llm_openai.Http")
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
