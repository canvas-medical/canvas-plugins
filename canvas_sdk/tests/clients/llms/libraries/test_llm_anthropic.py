from http import HTTPStatus
from unittest.mock import MagicMock, patch

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
    tested.add_prompt(LlmTurn(role="system", text=["system prompt"]))
    tested.add_prompt(LlmTurn(role="user", text=["user message"]))
    tested.add_prompt(LlmTurn(role="model", text=["model response"]))

    result = tested.to_dict()

    # System and user are both mapped to "user" role and merged
    expected = {
        "model": "test_model",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "system prompt"},
                    {"type": "text", "text": "user message"},
                ],
            },
            {
                "role": "assistant",
                "content": [{"type": "text", "text": "model response"}],
            },
        ],
    }
    assert result == expected


def test_to_dict_merges_contiguous_roles() -> None:
    """Test that contiguous prompts with same role are merged."""
    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmAnthropic(settings)

    # Add two system prompts (second replaces first), then user prompts
    tested.add_prompt(LlmTurn(role="system", text=["system1"]))
    tested.add_prompt(LlmTurn(role="system", text=["system2"]))
    tested.add_prompt(LlmTurn(role="user", text=["user1"]))
    tested.add_prompt(LlmTurn(role="user", text=["user2"]))

    result = tested.to_dict()

    # System prompts replace each other, all user-role prompts are merged
    assert len(result["messages"]) == 1
    assert result["messages"][0]["role"] == "user"
    # Only system2 (replaces system1), user1, and user2 = 3 items
    assert len(result["messages"][0]["content"]) == 3


@patch("canvas_sdk.clients.llms.libraries.llm_anthropic.requests_post")
def test_request_success(mock_post: MagicMock) -> None:
    """Test successful API request to Anthropic."""

    def reset_mocks() -> None:
        mock_post.reset_mock()

    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmAnthropic(settings)
    tested.add_prompt(LlmTurn(role="user", text=["test"]))

    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '{"content": [{"text": "response text"}], "usage": {"input_tokens": 10, "output_tokens": 20}}'
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
    assert calls[0][0][0] == "https://api.anthropic.com/v1/messages"
    assert calls[0][1]["headers"]["x-api-key"] == "test_key"
    assert calls[0][1]["headers"]["anthropic-version"] == "2023-06-01"
    reset_mocks()


@patch("canvas_sdk.clients.llms.libraries.llm_anthropic.requests_post")
def test_request_error(mock_post: MagicMock) -> None:
    """Test API request error handling."""

    def reset_mocks() -> None:
        mock_post.reset_mock()

    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmAnthropic(settings)
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
