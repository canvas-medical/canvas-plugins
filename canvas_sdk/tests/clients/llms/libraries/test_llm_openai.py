from http import HTTPStatus
from unittest.mock import MagicMock, patch

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
    tested.add_prompt(LlmTurn(role="system", text=["system prompt"]))
    tested.add_prompt(LlmTurn(role="user", text=["user message"]))
    tested.add_prompt(LlmTurn(role="model", text=["model response"]))

    result = tested.to_dict()

    expected = {
        "model": "test_model",
        "instructions": "system prompt",
        "input": [
            {
                "role": "user",
                "content": [{"type": "input_text", "text": "user message"}],
            },
            {
                "role": "assistant",
                "content": [{"type": "output_text", "text": "model response"}],
            },
        ],
    }
    assert result == expected


def test_to_dict_multiple_system_prompts() -> None:
    """Test that second system prompt replaces first in instructions."""
    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmOpenai(settings)

    # Add two system prompts (second replaces first)
    tested.add_prompt(LlmTurn(role="system", text=["system1"]))
    tested.add_prompt(LlmTurn(role="system", text=["system2"]))
    tested.add_prompt(LlmTurn(role="user", text=["user1"]))

    result = tested.to_dict()

    # Second system prompt replaces the first
    assert result["instructions"] == "system2"
    assert len(result["input"]) == 1


@patch("canvas_sdk.clients.llms.libraries.llm_openai.requests_post")
def test_request_success(mock_post: MagicMock) -> None:
    """Test successful API request to OpenAI."""

    def reset_mocks() -> None:
        mock_post.reset_mock()

    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmOpenai(settings)
    tested.add_prompt(LlmTurn(role="user", text=["test"]))

    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '{"output": [{"type": "message", "content": [{"text": "response text"}]}], "usage": {"input_tokens": 10, "output_tokens": 20}}'
    mock_post.side_effect = [mock_response]

    result = tested.request()

    expected = LlmResponse(
        code=HTTPStatus.OK,
        response="response text",
        tokens=LlmTokens(prompt=10, generated=20),
    )
    assert result == expected

    # Verify request was made correctly
    calls = mock_post.call_args_list
    assert len(calls) == 1
    assert calls[0][0][0] == "https://us.api.openai.com/v1/responses"
    assert calls[0][1]["headers"]["Authorization"] == "Bearer test_key"
    reset_mocks()


@patch("canvas_sdk.clients.llms.libraries.llm_openai.requests_post")
def test_request_error(mock_post: MagicMock) -> None:
    """Test API request error handling."""

    def reset_mocks() -> None:
        mock_post.reset_mock()

    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmOpenai(settings)
    tested.add_prompt(LlmTurn(role="user", text=["test"]))

    # Mock error response
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.text = "Rate limit exceeded"
    mock_post.side_effect = [mock_response]

    result = tested.request()

    expected = LlmResponse(
        code=HTTPStatus.TOO_MANY_REQUESTS,
        response="Rate limit exceeded",
        tokens=LlmTokens(prompt=0, generated=0),
    )
    assert result == expected
    reset_mocks()


@patch("canvas_sdk.clients.llms.libraries.llm_openai.requests_post")
def test_request_multiple_output_messages(mock_post: MagicMock) -> None:
    """Test handling multiple message outputs."""

    def reset_mocks() -> None:
        mock_post.reset_mock()

    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmOpenai(settings)
    tested.add_prompt(LlmTurn(role="user", text=["test"]))

    # Mock response with multiple outputs
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = (
        '{"output": ['
        '{"type": "message", "content": [{"text": "part1"}]}, '
        '{"type": "something", "content": [{"text": "nope"}]}, '
        '{"type": "message", "content": [{"text": "part2"}]}], '
        '"usage": {"input_tokens": 10, "output_tokens": 20}}'
    )
    mock_post.side_effect = [mock_response]

    result = tested.request()

    # Multiple message outputs should be concatenated
    expected = LlmResponse(
        code=HTTPStatus.OK,
        response="part1part2",
        tokens=LlmTokens(prompt=10, generated=20),
    )
    assert result == expected
    reset_mocks()
