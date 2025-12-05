from http import HTTPStatus
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

from requests import exceptions

from canvas_sdk.clients.llms.libraries.llm_openai import LlmOpenai
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


@patch("canvas_sdk.clients.llms.libraries.llm_openai.Http")
def test_request(http: MagicMock) -> None:
    """Test successful API request to OpenAI."""

    def reset_mocks() -> None:
        http.reset_mock()

    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmOpenai(settings)
    tested.add_prompt(LlmTurn(role="user", text=["test"]))

    # exceptions
    exception_no_response = exceptions.RequestException("Connection error")
    exception_with_response = exceptions.RequestException("Server error")
    exception_with_response.response = SimpleNamespace(status_code=404, text="not found")  # type: ignore[assignment]

    tests = [
        # success
        (
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
        ),
        # error
        (
            SimpleNamespace(
                status_code=429,
                text="Rate limit exceeded",
            ),
            LlmResponse(
                code=HTTPStatus.TOO_MANY_REQUESTS,
                response="Rate limit exceeded",
                tokens=LlmTokens(prompt=0, generated=0),
            ),
        ),
        # multiple output messages
        (
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
        ),
        # exception -- no response
        (
            exception_no_response,
            LlmResponse(
                code=HTTPStatus.BAD_REQUEST,
                response="Request failed: Connection error",
                tokens=LlmTokens(prompt=0, generated=0),
            ),
        ),
        # exception -- with response
        (
            exception_with_response,
            LlmResponse(
                code=HTTPStatus.NOT_FOUND,
                response="not found",
                tokens=LlmTokens(prompt=0, generated=0),
            ),
        ),
    ]
    for response, expected in tests:
        http.return_value.post.side_effect = [response]

        result = tested.request()
        assert result == expected

        calls = [
            call("https://us.api.openai.com/v1/responses"),
            call().post(
                "",
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
        reset_mocks()
