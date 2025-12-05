from http import HTTPStatus
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

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


@patch("canvas_sdk.clients.llms.libraries.llm_google.Http")
def test_request(http: MagicMock) -> None:
    """Test successful API request to Google."""

    def reset_mocks() -> None:
        http.reset_mock()

    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmGoogle(settings)
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
                '"candidates": [{"content": {"parts": [{"text": "response text"}]}}], '
                '"usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 15, "thoughtsTokenCount": 5}'
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
        reset_mocks()
