from http import HTTPStatus
from unittest.mock import call

import pytest
from pytest_mock import MockerFixture
from requests import exceptions

from canvas_sdk.clients.llms.libraries.llm_base import LlmBase
from canvas_sdk.clients.llms.structures.llm_response import LlmResponse
from canvas_sdk.clients.llms.structures.llm_tokens import LlmTokens
from canvas_sdk.clients.llms.structures.llm_turn import LlmTurn
from canvas_sdk.clients.llms.structures.settings.llm_settings import LlmSettings


class TestLlmBase(LlmBase):
    """Subclass of LlmBase to implement the request method."""

    def request(self) -> LlmResponse:
        """Minimal implementation."""
        return LlmResponse(
            code=HTTPStatus.OK,
            response="something",
            tokens=LlmTokens(prompt=51, generated=23),
        )


def test___init__() -> None:
    """Test initialization of LlmBase."""
    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = TestLlmBase(settings)

    assert tested.settings == settings
    assert tested.prompts == []


def test_reset_prompts() -> None:
    """Test reset_prompts clears all stored prompts."""
    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = TestLlmBase(settings)

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
    tested = TestLlmBase(settings)

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
    tested = TestLlmBase(settings)

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
    tested = TestLlmBase(settings)

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
    tested = TestLlmBase(settings)

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


@pytest.mark.parametrize(
    "side_effects, attempts, expected, expected_calls",
    [
        pytest.param(
            [
                LlmResponse(
                    code=HTTPStatus.OK,
                    response="success",
                    tokens=LlmTokens(prompt=10, generated=20),
                )
            ],
            3,
            [
                LlmResponse(
                    code=HTTPStatus.OK,
                    response="success",
                    tokens=LlmTokens(prompt=10, generated=20),
                )
            ],
            [call()],
            id="success_first_attempt",
        ),
        pytest.param(
            [
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
            ],
            3,
            [
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
            ],
            [call(), call()],
            id="success_second_attempt",
        ),
        pytest.param(
            [
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
            ],
            2,
            [
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
            ],
            [call(), call()],
            id="all_attempts_fail",
        ),
        pytest.param(
            [
                exceptions.RequestException("There is a problem"),
                LlmResponse(
                    code=HTTPStatus.OK,
                    response="success",
                    tokens=LlmTokens(prompt=10, generated=20),
                ),
            ],
            3,
            [
                LlmResponse(
                    code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    response="Request attempt failed: There is a problem",
                    tokens=LlmTokens(prompt=0, generated=0),
                ),
                LlmResponse(
                    code=HTTPStatus.OK,
                    response="success",
                    tokens=LlmTokens(prompt=10, generated=20),
                ),
            ],
            [call(), call()],
            id="success_second_attempt_with_exception",
        ),
    ],
)
def test_attempt_requests(
    mocker: MockerFixture,
    side_effects: list,
    attempts: int,
    expected: list,
    expected_calls: list,
) -> None:
    """Test attempt_requests retries until success or max attempts."""
    request = mocker.patch.object(TestLlmBase, "request")
    request.side_effect = side_effects

    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = TestLlmBase(settings)

    result = tested.attempt_requests(attempts)
    assert result == expected
    assert request.mock_calls == expected_calls
