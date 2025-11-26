from http import HTTPStatus
from unittest.mock import MagicMock, call, patch

import pytest

from canvas_sdk.clients.llms.libraries.llm_base import LlmBase
from canvas_sdk.clients.llms.structures.llm_response import LlmResponse
from canvas_sdk.clients.llms.structures.llm_tokens import LlmTokens
from canvas_sdk.clients.llms.structures.llm_turn import LlmTurn
from canvas_sdk.clients.llms.structures.settings.llm_settings import LlmSettings


def test___init__() -> None:
    """Test initialization of LlmBase."""
    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmBase(settings)

    assert tested.settings == settings
    assert tested.prompts == []


def test_reset_prompts() -> None:
    """Test reset_prompts clears all stored prompts."""
    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmBase(settings)

    # Add some prompts
    tested.prompts = [
        LlmTurn(role="user", text=["test"]),
        LlmTurn(role="model", text=["response"]),
    ]

    tested.reset_prompts()

    assert tested.prompts == []


def test_set_system_prompt() -> None:
    """Test set_system_prompt adds or replaces system prompt at beginning."""
    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmBase(settings)

    # Add first system prompt
    tested.set_system_prompt(["system1"])
    assert len(tested.prompts) == 1
    assert tested.prompts[0].role == "system"
    assert tested.prompts[0].text == ["system1"]

    # Add user prompt
    tested.set_user_prompt(["user1"])
    assert len(tested.prompts) == 2

    # Replace system prompt
    tested.set_system_prompt(["system2"])
    assert len(tested.prompts) == 2
    assert tested.prompts[0].role == "system"
    assert tested.prompts[0].text == ["system2"]
    assert tested.prompts[1].role == "user"


def test_set_user_prompt() -> None:
    """Test set_user_prompt appends user prompts."""
    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmBase(settings)

    tested.set_user_prompt(["user1"])
    tested.set_user_prompt(["user2"])

    assert len(tested.prompts) == 2
    assert tested.prompts[0].role == "user"
    assert tested.prompts[0].text == ["user1"]
    assert tested.prompts[1].role == "user"
    assert tested.prompts[1].text == ["user2"]


def test_set_model_prompt() -> None:
    """Test set_model_prompt appends model responses."""
    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmBase(settings)

    tested.set_model_prompt(["model1"])
    tested.set_model_prompt(["model2"])

    assert len(tested.prompts) == 2
    assert tested.prompts[0].role == "model"
    assert tested.prompts[0].text == ["model1"]
    assert tested.prompts[1].role == "model"
    assert tested.prompts[1].text == ["model2"]


def test_add_prompt() -> None:
    """Test add_prompt routes prompts to appropriate methods based on role."""
    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmBase(settings)

    # Add different role prompts
    tested.add_prompt(LlmTurn(role="system", text=["sys"]))
    tested.add_prompt(LlmTurn(role="user", text=["usr"]))
    tested.add_prompt(LlmTurn(role="model", text=["mdl"]))
    tested.add_prompt(LlmTurn(role="unknown", text=["unknown"]))

    assert len(tested.prompts) == 3
    assert tested.prompts[0].role == "system"
    assert tested.prompts[0].text == ["sys"]
    assert tested.prompts[1].role == "user"
    assert tested.prompts[1].text == ["usr"]
    assert tested.prompts[2].role == "model"
    assert tested.prompts[2].text == ["mdl"]


def test_request() -> None:
    """Test request raises NotImplementedError."""
    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmBase(settings)

    with pytest.raises(NotImplementedError):
        tested.request()


@patch.object(LlmBase, "request")
def test_attempt_requests(request: MagicMock) -> None:
    """Test attempt_requests retries until success or max attempts."""

    def reset_mocks() -> None:
        request.reset_mock()

    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = LlmBase(settings)

    # Test successful on first attempt
    request.side_effect = [
        LlmResponse(
            code=HTTPStatus.OK,
            response="success",
            tokens=LlmTokens(prompt=10, generated=20),
        )
    ]

    result = tested.attempt_requests(3)
    expected = [
        LlmResponse(
            code=HTTPStatus.OK,
            response="success",
            tokens=LlmTokens(prompt=10, generated=20),
        )
    ]
    assert result == expected

    calls = [call()]
    assert request.mock_calls == calls
    reset_mocks()

    # Test successful on second attempt
    request.side_effect = [
        LlmResponse(
            code=HTTPStatus.TOO_MANY_REQUESTS,
            response="rate limit",
            tokens=LlmTokens(prompt=0, generated=0),
        ),
        LlmResponse(
            code=HTTPStatus.OK,
            response="success",
            tokens=LlmTokens(prompt=10, generated=20),
        ),
    ]

    result = tested.attempt_requests(3)
    expected = [
        LlmResponse(
            code=HTTPStatus.TOO_MANY_REQUESTS,
            response="rate limit",
            tokens=LlmTokens(prompt=0, generated=0),
        ),
        LlmResponse(
            code=HTTPStatus.OK,
            response="success",
            tokens=LlmTokens(prompt=10, generated=20),
        ),
    ]
    assert result == expected

    calls = [call(), call()]
    assert request.mock_calls == calls
    reset_mocks()

    # Test all attempts fail
    request.side_effect = [
        LlmResponse(
            code=HTTPStatus.TOO_EARLY,
            response="error1",
            tokens=LlmTokens(prompt=0, generated=0),
        ),
        LlmResponse(
            code=HTTPStatus.BAD_GATEWAY,
            response="error2",
            tokens=LlmTokens(prompt=0, generated=0),
        ),
    ]

    result = tested.attempt_requests(2)
    expected = [
        LlmResponse(
            code=HTTPStatus.TOO_EARLY,
            response="error1",
            tokens=LlmTokens(prompt=0, generated=0),
        ),
        LlmResponse(
            code=HTTPStatus.BAD_GATEWAY,
            response="error2",
            tokens=LlmTokens(prompt=0, generated=0),
        ),
        LlmResponse(
            code=HTTPStatus.TOO_MANY_REQUESTS,
            response="Http error: max attempts (2) exceeded.",
            tokens=LlmTokens(prompt=0, generated=0),
        ),
    ]
    assert result == expected

    calls = [call(), call()]
    assert request.mock_calls == calls
    reset_mocks()
