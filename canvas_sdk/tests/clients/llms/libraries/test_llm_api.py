from http import HTTPStatus
from types import SimpleNamespace
from unittest.mock import call

import pytest
from pytest_mock import MockerFixture
from requests import exceptions

from canvas_sdk.clients.llms.constants.file_type import FileType
from canvas_sdk.clients.llms.libraries.llm_api import LlmApi
from canvas_sdk.clients.llms.structures.base_model_llm_json import BaseModelLlmJson
from canvas_sdk.clients.llms.structures.file_content import FileContent
from canvas_sdk.clients.llms.structures.llm_file_url import LlmFileUrl
from canvas_sdk.clients.llms.structures.llm_response import LlmResponse
from canvas_sdk.clients.llms.structures.llm_tokens import LlmTokens
from canvas_sdk.clients.llms.structures.llm_turn import LlmTurn
from canvas_sdk.clients.llms.structures.settings.llm_settings import LlmSettings
from canvas_sdk.utils import Http


class ImplementedLlmApi(LlmApi):
    """Subclass of LlmApi to implement the request method."""

    @classmethod
    def _api_base_url(cls) -> str:
        return "https://some.url"

    def request(self) -> LlmResponse:
        """Minimal implementation."""
        return LlmResponse(
            code=HTTPStatus.OK,
            response="something",
            tokens=LlmTokens(prompt=51, generated=23),
        )


def test_constants() -> None:
    """Test constants."""
    tested = LlmApi
    assert tested.ROLE_MODEL == "model"
    assert tested.ROLE_SYSTEM == "system"
    assert tested.ROLE_USER == "user"


def test___init__() -> None:
    """Test initialization of LlmApi."""
    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = ImplementedLlmApi(settings)

    assert tested.settings == settings
    assert tested.prompts == []
    assert isinstance(tested.http, Http)
    assert tested.http._base_url == "https://some.url"
    assert tested.file_urls == []
    assert tested.file_contents == []
    assert tested.schema is None


def test_reset_prompts() -> None:
    """Test reset_prompts clears all stored prompts."""
    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = ImplementedLlmApi(settings)

    # Add some prompts
    tested.prompts = [
        LlmTurn(role="user", text=["test"]),
        LlmTurn(role="model", text=["response"]),
    ]

    tested.reset_prompts()

    assert tested.prompts == []


def test_add_url_file() -> None:
    """Test add_url_file appends file URLs."""
    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = ImplementedLlmApi(settings)

    file_url_1 = LlmFileUrl(url="https://example.com/file1.pdf", type=FileType.PDF)
    file_url_2 = LlmFileUrl(url="https://example.com/file2.jpg", type=FileType.IMAGE)

    tested.add_url_file(file_url_1)
    tested.add_url_file(file_url_2)

    assert len(tested.file_urls) == 2
    assert tested.file_urls[0] == file_url_1
    assert tested.file_urls[1] == file_url_2


def test_add_prompt() -> None:
    """Test add_prompt routes prompts to appropriate methods based on role."""
    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = ImplementedLlmApi(settings)

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


def test_set_system_prompt() -> None:
    """Test set_system_prompt adds or replaces system prompt at beginning."""
    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = ImplementedLlmApi(settings)

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
    tested = ImplementedLlmApi(settings)

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
    tested = ImplementedLlmApi(settings)

    tested.set_model_prompt(["model1"])
    tested.set_model_prompt(["model2"])

    assert len(tested.prompts) == 2
    assert tested.prompts[0].role == "model"
    assert tested.prompts[0].text == ["model1"]
    assert tested.prompts[1].role == "model"
    assert tested.prompts[1].text == ["model2"]


@pytest.mark.parametrize(
    ("is_valid", "exp_schema"),
    [
        (False, None),
        (True, BaseModelLlmJson),
    ],
)
def test_set_schema(
    mocker: MockerFixture,
    is_valid: bool,
    exp_schema: None | BaseModelLlmJson,
) -> None:
    """Test that only BaseModelLlmJson classes are accepted as schema."""
    validate_nested_models = mocker.patch.object(BaseModelLlmJson, "validate_nested_models")

    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = ImplementedLlmApi(settings)
    assert tested.schema is None

    validate_nested_models.side_effect = [is_valid]
    tested.set_schema(BaseModelLlmJson)
    assert tested.schema is exp_schema

    exp_calls = [call()]
    assert validate_nested_models.mock_calls == exp_calls


@pytest.mark.parametrize(
    ("side_effects", "attempts", "expected", "exp_calls"),
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
    exp_calls: list,
) -> None:
    """Test attempt_requests retries until success or max attempts."""
    request = mocker.patch.object(ImplementedLlmApi, "request")
    request.side_effect = side_effects

    settings = LlmSettings(api_key="test_key", model="test_model")
    tested = ImplementedLlmApi(settings)

    result = tested.attempt_requests(attempts)
    assert result == expected
    assert request.mock_calls == exp_calls


@pytest.mark.parametrize(
    ("side_effects", "expected"),
    [
        pytest.param(
            [
                SimpleNamespace(
                    content=b"test file content", headers={"Content-Type": "theContentType"}
                )
            ],
            FileContent(
                mime_type="theContentType",
                content=b"dGVzdCBmaWxlIGNvbnRlbnQ=",
                size=17,
            ),
            id="header_defined",
        ),
        pytest.param(
            [SimpleNamespace(content=b"test file content", headers={})],
            FileContent(
                mime_type="application/octet-stream",
                content=b"dGVzdCBmaWxlIGNvbnRlbnQ=",
                size=17,
            ),
            id="no_header",
        ),
        pytest.param(
            [exceptions.RequestException("Connection error")],
            FileContent(mime_type="", content=b"", size=0),
            id="with_error",
        ),
    ],
)
def test_base64_encoded_content_of(
    mocker: MockerFixture, side_effects: list, expected: FileContent
) -> None:
    """Test base64 encoding of file content from URL."""
    mock_http = mocker.patch("canvas_sdk.clients.llms.libraries.llm_api.Http")
    mock_http.return_value.get.side_effect = side_effects

    tested = LlmApi
    file_url = LlmFileUrl(url="https://example.com/file.pdf", type=FileType.PDF)
    result = tested.base64_encoded_content_of(file_url)
    assert result == expected

    exp_calls = [
        call("https://example.com/file.pdf"),
        call().get(""),
    ]
    assert mock_http.mock_calls == exp_calls
