"""The questionnaire tools: reading a charting questionnaire, and drafting it answered."""

import json
from typing import Any

import pytest

from canvas_sdk.agents import standard_tools
from canvas_sdk.test_utils.factories import (
    PatientFactory,
    QuestionFactory,
    QuestionnaireFactory,
    ResponseOptionFactory,
    ResponseOptionSetFactory,
)
from canvas_sdk.v1.data import (
    Question,
    QuestionEnablementCondition,
    Questionnaire,
    QuestionnaireQuestionMap,
    ResponseOption,
)

NOTE = "00000000-0000-0000-0000-000000000001"


def _ctx() -> dict[str, Any]:
    return {"patient_id": PatientFactory.create().id, "note_id": NOTE, "effects": []}


def _question(questionnaire: Questionnaire, response_type: str, *options: str) -> Question:
    """A question of ``response_type`` on ``questionnaire``, offering ``options``."""
    option_set = ResponseOptionSetFactory.create(type=response_type)
    for name in options:
        ResponseOptionFactory.create(response_option_set=option_set, name=name)
    question = QuestionFactory.create(response_option_set=option_set)
    QuestionnaireQuestionMap.objects.create(
        status="AC", questionnaire=questionnaire, question=question
    )
    return question


def _option(question: Question, name: str) -> ResponseOption:
    return ResponseOption.objects.get(response_option_set=question.response_option_set, name=name)


def _depends(
    question: Question,
    on: Question,
    operator: str,
    option: ResponseOption | None = None,
    value: str | None = None,
) -> None:
    QuestionEnablementCondition.objects.create(
        status="AC",
        question=question,
        dependent_on=on,
        operator=operator,
        answer_option=option,
        answer_value=value,
    )


def _sent(ctx: dict[str, Any]) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(ctx["effects"][0].payload)["data"]
    return data


@pytest.mark.django_db
def test_a_questionnaire_is_read_with_its_questions_options_and_branching() -> None:
    """Questions come in order, typed, with options in order and what each depends on."""
    questionnaire = QuestionnaireFactory.create(name="Weight intake")
    on_glp1 = _question(questionnaire, "SING", "Yes", "No")
    medication = _question(questionnaire, "TXT")
    _depends(medication, on_glp1, "=", option=_option(on_glp1, "Yes"))

    result = standard_tools.execute(
        "get_questionnaire", {"questionnaire_id": str(questionnaire.id)}, ctx=_ctx()
    )

    assert result["name"] == "Weight intake"
    first, second = result["questions"]
    assert (first["id"], first["type"], first["enabled_when"]) == (
        on_glp1.dbid,
        "single_choice",
        None,
    )
    assert [option["name"] for option in first["options"]] == ["Yes", "No"]
    assert (second["type"], second["options"]) == ("text", [])
    assert second["enabled_when"] == {
        "behavior": "all",
        "conditions": [
            {
                "question_id": on_glp1.dbid,
                "operator": "=",
                "option_id": _option(on_glp1, "Yes").dbid,
                "value": None,
            }
        ],
    }


@pytest.mark.django_db
def test_a_questionnaire_is_found_by_its_exact_name() -> None:
    """The name match ignores case."""
    questionnaire = QuestionnaireFactory.create(name="PHQ-9")

    result = standard_tools.execute("get_questionnaire", {"name": "phq-9"}, ctx=_ctx())

    assert result["id"] == str(questionnaire.id)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "hidden",
    [{"status": "IN"}, {"can_originate_in_charting": False}, {"use_case_in_charting": "ROS"}],
    ids=["inactive", "not chartable", "a review of systems"],
)
def test_only_the_questionnaires_the_chart_offers_are_read(hidden: dict[str, Any]) -> None:
    """A questionnaire the chart's command does not offer is not found."""
    questionnaire = QuestionnaireFactory.create(**hidden)

    with pytest.raises(ValueError, match="No questionnaire the chart offers"):
        standard_tools.execute(
            "get_questionnaire", {"questionnaire_id": str(questionnaire.id)}, ctx=_ctx()
        )


@pytest.mark.django_db
def test_a_question_of_a_type_no_answer_sets_is_named() -> None:
    """The model learns which question it cannot answer, instead of a partial list."""
    questionnaire = QuestionnaireFactory.create()
    _question(questionnaire, "DEC")

    with pytest.raises(ValueError, match="has type DEC"):
        standard_tools.execute(
            "get_questionnaire", {"questionnaire_id": str(questionnaire.id)}, ctx=_ctx()
        )


@pytest.mark.django_db
def test_each_question_type_is_answered_on_the_draft() -> None:
    """Every answer key lands as its question's response, uncommitted."""
    questionnaire = QuestionnaireFactory.create()
    goal = _question(questionnaire, "TXT")
    weight = _question(questionnaire, "INT")
    started = _question(questionnaire, "DATE")
    on_glp1 = _question(questionnaire, "SING", "Yes", "No")
    symptoms = _question(questionnaire, "MULT", "Nausea", "Fatigue")
    ctx = _ctx()

    result = standard_tools.execute(
        "originate_questionnaire",
        {
            "questionnaire_id": str(questionnaire.id),
            "answers": [
                {"question_id": goal.dbid, "text": "Lose 20 pounds"},
                {"question_id": weight.dbid, "integer": 210},
                {"question_id": started.dbid, "date": "2026-01-15"},
                {"question_id": on_glp1.dbid, "option_id": _option(on_glp1, "No").dbid},
                {
                    "question_id": symptoms.dbid,
                    "selections": [
                        {"option_id": _option(symptoms, "Nausea").dbid, "comment": "mornings"}
                    ],
                },
            ],
        },
        ctx=ctx,
    )

    assert (result["ok"], result["committed"], result["command"]) == (
        True,
        False,
        "questionnaire",
    )
    nausea = _option(symptoms, "Nausea")
    assert _sent(ctx)["questions"] == {
        f"question-{goal.dbid}": "Lose 20 pounds",
        f"question-{weight.dbid}": 210,
        f"question-{started.dbid}": "2026-01-15",
        f"question-{on_glp1.dbid}": _option(on_glp1, "No").dbid,
        f"question-{symptoms.dbid}": [
            {"text": "Nausea", "value": nausea.dbid, "comment": "mornings", "selected": True}
        ],
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("answer", "message"),
    [
        ({"integer": 5}, "with `text` and nothing else"),
        ({"text": "a", "integer": 5}, "with `text` and nothing else"),
        ({}, "with `text` and nothing else"),
    ],
    ids=["the wrong key", "two keys", "no key"],
)
def test_an_answer_in_the_wrong_form_stages_nothing(answer: dict[str, Any], message: str) -> None:
    """An answer must use the one key its question's type takes."""
    questionnaire = QuestionnaireFactory.create()
    question = _question(questionnaire, "TXT")
    ctx = _ctx()

    with pytest.raises(ValueError, match=message):
        standard_tools.execute(
            "originate_questionnaire",
            {
                "questionnaire_id": str(questionnaire.id),
                "answers": [{"question_id": question.dbid, **answer}],
            },
            ctx=ctx,
        )

    assert ctx["effects"] == []


@pytest.mark.django_db
def test_an_option_another_question_offers_stages_nothing() -> None:
    """The command refuses an option its question does not offer."""
    questionnaire = QuestionnaireFactory.create()
    on_glp1 = _question(questionnaire, "SING", "Yes", "No")
    other = _question(questionnaire, "SING", "Daily", "Weekly")
    ctx = _ctx()

    with pytest.raises(ValueError, match="is not an option"):
        standard_tools.execute(
            "originate_questionnaire",
            {
                "questionnaire_id": str(questionnaire.id),
                "answers": [
                    {"question_id": on_glp1.dbid, "option_id": _option(other, "Daily").dbid}
                ],
            },
            ctx=ctx,
        )

    assert ctx["effects"] == []


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("operator", "on_glp1_answer", "applies"),
    [
        ("=", "Yes", True),
        ("=", "No", False),
        ("=", None, False),
        ("!=", "No", False),
        ("!=", "Yes", True),
        ("!=", None, False),
        ("exists", "No", True),
        ("exists", None, False),
        ("not_exists", None, True),
        ("not_exists", "Yes", False),
    ],
)
def test_an_answer_to_a_question_that_does_not_apply_stages_nothing(
    operator: str, on_glp1_answer: str | None, applies: bool
) -> None:
    """A question depending on another applies only when the other's answer meets it."""
    questionnaire = QuestionnaireFactory.create()
    on_glp1 = _question(questionnaire, "SING", "Yes", "No")
    medication = _question(questionnaire, "TXT")
    condition_option = _option(on_glp1, "No") if operator == "!=" else _option(on_glp1, "Yes")
    _depends(medication, on_glp1, operator, option=condition_option)
    answers: list[dict[str, Any]] = [{"question_id": medication.dbid, "text": "Semaglutide"}]
    if on_glp1_answer:
        answers.append(
            {"question_id": on_glp1.dbid, "option_id": _option(on_glp1, on_glp1_answer).dbid}
        )
    ctx = _ctx()
    arguments = {"questionnaire_id": str(questionnaire.id), "answers": answers}

    if applies:
        standard_tools.execute("originate_questionnaire", arguments, ctx=ctx)
        assert _sent(ctx)["questions"][f"question-{medication.dbid}"] == "Semaglutide"
    else:
        with pytest.raises(ValueError, match="does not apply"):
            standard_tools.execute("originate_questionnaire", arguments, ctx=ctx)
        assert ctx["effects"] == []


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("behavior", "weight", "applies"),
    [("all", 250, False), ("any", 250, True), ("all", 300, True)],
)
def test_a_question_depending_on_several_answers_follows_its_behavior(
    behavior: str, weight: int, applies: bool
) -> None:
    """`all` needs every condition met, `any` needs one, compared as text for a value."""
    questionnaire = QuestionnaireFactory.create()
    on_glp1 = _question(questionnaire, "SING", "Yes", "No")
    current_weight = _question(questionnaire, "INT")
    reason = _question(questionnaire, "TXT")
    Question.objects.filter(dbid=reason.dbid).update(enable_behavior=behavior)
    _depends(reason, on_glp1, "=", option=_option(on_glp1, "Yes"))
    _depends(reason, current_weight, "=", value="300")
    ctx = _ctx()
    arguments = {
        "questionnaire_id": str(questionnaire.id),
        "answers": [
            {"question_id": on_glp1.dbid, "option_id": _option(on_glp1, "Yes").dbid},
            {"question_id": current_weight.dbid, "integer": weight},
            {"question_id": reason.dbid, "text": "Plateaued"},
        ],
    }

    if applies:
        standard_tools.execute("originate_questionnaire", arguments, ctx=ctx)
        assert _sent(ctx)["questions"][f"question-{reason.dbid}"] == "Plateaued"
    else:
        with pytest.raises(ValueError, match="does not apply"):
            standard_tools.execute("originate_questionnaire", arguments, ctx=ctx)


@pytest.mark.django_db
def test_a_question_answered_twice_or_not_in_the_questionnaire_stages_nothing() -> None:
    """Answers name each of the questionnaire's own questions at most once."""
    questionnaire = QuestionnaireFactory.create()
    goal = _question(questionnaire, "TXT")
    elsewhere = _question(QuestionnaireFactory.create(), "TXT")
    ctx = _ctx()

    for answers, message in [
        ([{"question_id": elsewhere.dbid, "text": "a"}], "is not a question"),
        ([{"question_id": goal.dbid, "text": "a"}] * 2, "more than once"),
    ]:
        with pytest.raises(ValueError, match=message):
            standard_tools.execute(
                "originate_questionnaire",
                {"questionnaire_id": str(questionnaire.id), "answers": answers},
                ctx=ctx,
            )

    assert ctx["effects"] == []
