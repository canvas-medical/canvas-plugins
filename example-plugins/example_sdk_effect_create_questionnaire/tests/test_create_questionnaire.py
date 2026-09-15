"""Tests for the example create-questionnaire route."""

import json
from typing import Any

import pytest
from example_sdk_effect_create_questionnaire.routes.create_questionnaire import (
    CreateQuestionnaireAPI,
)

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.simple_api import JSONResponse
from canvas_sdk.handlers.simple_api import APIKeyCredentials

BODY: dict[str, Any] = {
    "title": "Depression screening",
    "code": "44249-1",
    "items": [
        {
            "prompt": "Little interest or pleasure in doing things?",
            "choices": ["Not at all", "Several days", "More than half the days"],
        },
        {"prompt": "Describe anything else you would like us to know", "type": "text"},
    ],
    "follow_up": {"prompt": "How long has this been going on?", "when_answer": "Several days"},
}


class DummyEvent:
    """An event carrying only the request context the handler reads."""

    def __init__(self) -> None:
        self.context = {"method": "POST", "path": "/create-questionnaire"}


class DummyRequest:
    """A request whose JSON body and headers are supplied up front."""

    def __init__(self, body: dict[str, Any], headers: dict[str, str] | None = None) -> None:
        self._body = body
        self.headers = headers or {}

    def json(self) -> dict[str, Any]:
        """Return the body."""
        return self._body


def credentials(key: str) -> APIKeyCredentials:
    """Build credentials the way the framework does, from an Authorization header."""
    return APIKeyCredentials(DummyRequest({}, {"Authorization": key}))


@pytest.fixture
def route() -> CreateQuestionnaireAPI:
    """A route instance with a request body and a configured secret."""
    api = CreateQuestionnaireAPI(event=DummyEvent())
    api.request = DummyRequest(BODY)
    api.secrets = {"api-key": "test-key"}

    return api


def error_from(route: CreateQuestionnaireAPI) -> str:
    """Post and return the error the route answered with, asserting it rejected the body."""
    (response,) = route.post()

    assert isinstance(response, JSONResponse)
    assert response.status_code == 400

    return str(json.loads(response.content)["error"])


def questionnaire_from(route: CreateQuestionnaireAPI) -> dict[str, Any]:
    """Post and return the questionnaire carried by the effect."""
    _, effect = route.post()

    assert effect.type == EffectType.CREATE_QUESTIONNAIRE

    return json.loads(effect.payload)["data"]["questionnaire"]


def test_authenticate_accepts_the_configured_key(route: CreateQuestionnaireAPI) -> None:
    """The route authenticates against its api-key secret."""
    assert route.authenticate(credentials("test-key")) is True


def test_authenticate_rejects_another_key(route: CreateQuestionnaireAPI) -> None:
    """A key that does not match the secret is rejected."""
    assert route.authenticate(credentials("wrong")) is False


def test_response_reports_what_was_created(route: CreateQuestionnaireAPI) -> None:
    """The route answers the caller with the name and question count."""
    response, _ = route.post()

    assert isinstance(response, JSONResponse)
    assert json.loads(response.content) == {
        "created": "Depression screening",
        "questions": 3,
    }


def test_questionnaire_metadata_comes_from_the_body(route: CreateQuestionnaireAPI) -> None:
    """Title and code are taken from the caller's definition."""
    questionnaire = questionnaire_from(route)

    assert questionnaire["name"] == "Depression screening"
    assert questionnaire["code"] == "44249-1"
    assert questionnaire["code_system"] == "LOINC"


def test_choices_become_scored_responses(route: CreateQuestionnaireAPI) -> None:
    """Each choice becomes a response, coded and scored by position."""
    question = questionnaire_from(route)["questions"][0]

    assert question["responses_type"] == "SING"
    assert question["responses"] == [
        {"name": "Not at all", "code": "Q1A1", "value": "0"},
        {"name": "Several days", "code": "Q1A2", "value": "1"},
        {"name": "More than half the days", "code": "Q1A3", "value": "2"},
    ]


def test_text_item_becomes_a_free_text_question(route: CreateQuestionnaireAPI) -> None:
    """An item marked as text becomes a TXT question with a placeholder response."""
    question = questionnaire_from(route)["questions"][1]

    assert question["responses_type"] == "TXT"
    assert question["responses"] == [{"name": "TXT", "code": "Q2A1"}]


def test_follow_up_is_wired_to_the_triggering_answer(route: CreateQuestionnaireAPI) -> None:
    """The follow-up is enabled by the response whose text the caller named."""
    question = questionnaire_from(route)["questions"][2]

    assert question["enabled_behavior"] == "all"
    assert question["enabled_conditions"] == [
        {"question_code": "Q1", "operator": "=", "value_code": "Q1A2"}
    ]


def test_follow_up_on_an_unknown_answer_is_rejected(route: CreateQuestionnaireAPI) -> None:
    """A follow-up naming an answer nobody offers is reported rather than being dropped."""
    route.request = DummyRequest(
        {**BODY, "follow_up": {"prompt": "Why?", "when_answer": "Nobody offers this"}}
    )

    assert "Nobody offers this" in error_from(route)


@pytest.mark.parametrize(
    "requested,expected",
    [(None, "SING"), ("single", "SING"), ("multi", "MULT"), ("text", "TXT"), ("date", "DATE")],
    ids=["default", "single", "multi", "text", "date"],
)
def test_every_caller_type_maps_to_a_response_type(
    route: CreateQuestionnaireAPI, requested: str | None, expected: str
) -> None:
    """All four response types the schema allows are reachable through the route."""
    item: dict[str, Any] = {"prompt": "a question", "choices": ["One", "Two"]}
    if requested:
        item["type"] = requested
    route.request = DummyRequest({"title": "T", "code": "1", "items": [item]})

    question = questionnaire_from(route)["questions"][0]

    assert question["responses_type"] == expected


@pytest.mark.parametrize("requested,count", [("multi", 2), ("text", 1), ("date", 1)])
def test_typed_and_picked_answers_carry_one_placeholder(
    route: CreateQuestionnaireAPI, requested: str, count: int
) -> None:
    """Choices are carried through for MULT; TXT and DATE get a single placeholder option."""
    route.request = DummyRequest(
        {
            "title": "T",
            "code": "1",
            "items": [{"prompt": "a question", "type": requested, "choices": ["One", "Two"]}],
        }
    )

    assert len(questionnaire_from(route)["questions"][0]["responses"]) == count


def test_an_unknown_type_is_rejected_by_name(route: CreateQuestionnaireAPI) -> None:
    """An unsupported type names itself and the supported set, rather than failing obscurely."""
    route.request = DummyRequest(
        {"title": "T", "code": "1", "items": [{"prompt": "p", "type": "slider"}]}
    )

    error = error_from(route)

    assert "Unknown question type 'slider'" in error
    assert "date, multi, single, text" in error


def test_a_missing_field_is_named(route: CreateQuestionnaireAPI) -> None:
    """A body without a title is answered with the field it lacks, not an HTTP 500."""
    route.request = DummyRequest({"code": "1", "items": [{"prompt": "p", "choices": ["a"]}]})

    assert "title" in error_from(route)


def test_a_rejected_body_emits_no_effect(route: CreateQuestionnaireAPI) -> None:
    """Nothing is created when the body cannot be translated."""
    route.request = DummyRequest({"code": "1", "items": []})

    responses = route.post()

    assert len(responses) == 1
    assert isinstance(responses[0], JSONResponse)
