"""Tests for the example read-questionnaire route."""

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from example_sdk_effect_create_questionnaire.routes.read_questionnaire import (
    ReadQuestionnaireAPI,
)

from canvas_sdk.effects.simple_api import JSONResponse
from canvas_sdk.handlers.simple_api import APIKeyCredentials

QUESTIONNAIRE_OBJECTS = (
    "example_sdk_effect_create_questionnaire.routes.read_questionnaire.Questionnaire.objects"
)
CONDITION_OBJECTS = (
    "example_sdk_effect_create_questionnaire.routes.read_questionnaire"
    ".QuestionEnablementCondition.objects"
)


class DummyEvent:
    """An event carrying only the request context the handler reads."""

    def __init__(self) -> None:
        self.context = {"method": "GET", "path": "/questionnaire"}


class DummyRequest:
    """A request whose query parameters and headers are supplied up front."""

    def __init__(
        self, query_params: dict[str, str] | None = None, headers: dict[str, str] | None = None
    ) -> None:
        self.query_params = query_params or {}
        self.headers = headers or {}


def credentials(key: str) -> APIKeyCredentials:
    """Build credentials the way the framework does, from an Authorization header."""
    return APIKeyCredentials(DummyRequest(headers={"Authorization": key}))


@pytest.fixture
def route() -> ReadQuestionnaireAPI:
    """A route instance asking for a questionnaire by name."""
    api = ReadQuestionnaireAPI(event=DummyEvent())
    api.request = DummyRequest({"name": "Depression screening"})
    api.secrets = {"api-key": "test-key"}

    return api


def body_of(responses: list[Any]) -> dict[str, Any]:
    """Return the parsed body of the route's single JSON response."""
    response = responses[0]

    assert isinstance(response, JSONResponse)

    return json.loads(response.content)


def test_authenticate_accepts_the_configured_key(route: ReadQuestionnaireAPI) -> None:
    """The route authenticates against its api-key secret."""
    assert route.authenticate(credentials("test-key")) is True


def test_authenticate_rejects_another_key(route: ReadQuestionnaireAPI) -> None:
    """A key that does not match the secret is rejected."""
    assert route.authenticate(credentials("wrong")) is False


def test_a_missing_name_is_reported(route: ReadQuestionnaireAPI) -> None:
    """Without a name there is nothing to look up, and the route says so."""
    route.request = DummyRequest({})

    assert "name" in body_of(route.get())["error"]


def test_an_unknown_name_is_reported(route: ReadQuestionnaireAPI) -> None:
    """A name with no active questionnaire is reported rather than returning an empty shape."""
    with patch(QUESTIONNAIRE_OBJECTS) as objects:
        objects.filter.return_value.first.return_value = None

        assert "Depression screening" in body_of(route.get())["error"]


def test_the_question_graph_is_returned(route: ReadQuestionnaireAPI) -> None:
    """The route reports each question with its responses and what enables it.

    This is the read side of the branching logic the CreateQuestionnaire effect writes, so a
    plugin can confirm what was persisted rather than trusting a fire-and-forget effect.
    """
    option = MagicMock(code="Q1A2", name="Several days", value="1")
    trigger = MagicMock(code="Q1")
    condition = MagicMock(
        dependent_on=trigger, operator="=", answer_option=option, answer_value=None
    )

    question = MagicMock(code="Q2", code_system="INTERNAL", enable_behavior="all")
    question.name = "How long has this been going on?"
    question.response_option_set.type = "TXT"
    question.response_option_set.use_in_shx = False
    question.response_option_set.options.order_by.return_value = []

    questionnaire = MagicMock(
        id="abc", code_system="LOINC", code="44249-1", use_case_in_charting="QUES", use_in_shx=False
    )
    questionnaire.name = "Depression screening"
    questionnaire.questions.all.return_value = [question]

    with (
        patch(QUESTIONNAIRE_OBJECTS) as objects,
        patch(CONDITION_OBJECTS) as conditions,
    ):
        objects.filter.return_value.first.return_value = questionnaire
        conditions.filter.return_value = [condition]

        body = body_of(route.get())

    assert body["name"] == "Depression screening"
    assert body["questions"][0]["code"] == "Q2"
    assert body["questions"][0]["responses_type"] == "TXT"
    assert body["questions"][0]["enabled_behavior"] == "all"
    assert body["questions"][0]["enabled_conditions"] == [
        {"depends_on": "Q1", "operator": "=", "value_code": "Q1A2", "value_string": None}
    ]


def test_only_active_questionnaires_are_returned(route: ReadQuestionnaireAPI) -> None:
    """The lookup is scoped to active questionnaires, so a superseded version is not returned."""
    with patch(QUESTIONNAIRE_OBJECTS) as objects:
        objects.filter.return_value.first.return_value = None

        route.get()

        assert objects.filter.call_args.kwargs == {
            "name": "Depression screening",
            "status": "AC",
        }
