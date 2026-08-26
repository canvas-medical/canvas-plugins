"""Tests for :attr:`QuestionnaireCommand.answers`.

Each answer is a question id, a response and an optional comment; the command resolves it
against that question's type and options.
"""

import json
from collections.abc import Generator
from unittest.mock import PropertyMock, patch

import pytest

from canvas_sdk.commands import PhysicalExamCommand
from canvas_sdk.commands.commands.questionnaire import Answer, QuestionnaireCommand
from canvas_sdk.commands.commands.questionnaire.question import (
    CheckboxQuestion,
    IntegerQuestion,
    RadioQuestion,
    ResponseOption,
    TextQuestion,
)

QUESTIONNAIRE_ID = "3f1a5d0e-0000-4000-8000-000000000001"

STATUS_OPTIONS = [
    ResponseOption(dbid=101, name="Never user", code="LA18978-9", value="never"),
    ResponseOption(dbid=102, name="Former user", code="LA15920-4", value="former"),
]
TYPE_OPTIONS = [
    ResponseOption(dbid=201, name="Cigarettes", code="C1", value="cigarettes"),
    ResponseOption(dbid=202, name="Cigar/Pipe", code="C2", value="cigar"),
]
#: Options named for numbers, with ids chosen to collide with those names.
COUNT_OPTIONS = [
    ResponseOption(dbid=1, name="2", code="N2", value="2"),
    ResponseOption(dbid=2, name="5", code="N5", value="5"),
]


def questions() -> list[object]:
    """One question of each type: radio, checkbox, text, number-named radio, integer."""
    return [
        RadioQuestion(
            id="9", name="question-9", label="Status", coding={}, options=list(STATUS_OPTIONS)
        ),
        CheckboxQuestion(
            id="10", name="question-10", label="Type", coding={}, options=list(TYPE_OPTIONS)
        ),
        TextQuestion(id="11", name="question-11", label="Comment", coding={}, options=[]),
        RadioQuestion(
            id="12", name="question-12", label="Days", coding={}, options=list(COUNT_OPTIONS)
        ),
        IntegerQuestion(id="13", name="question-13", label="Packs", coding={}, options=[]),
    ]


@pytest.fixture
def command() -> Generator[QuestionnaireCommand, None, None]:
    """A command whose questionnaire is the questions above."""
    cmd = QuestionnaireCommand(questionnaire_id=QUESTIONNAIRE_ID, note_uuid="note-1")
    patcher = patch.object(
        QuestionnaireCommand, "questions", new_callable=PropertyMock, return_value=questions()
    )
    patcher.start()
    yield cmd
    patcher.stop()


def test_a_choice_is_answered_by_option_id(command: QuestionnaireCommand) -> None:
    """A radio answer is an option's id, recorded as that option."""
    command.answers = [Answer(question_id=9, response=102)]

    assert command.values["questions"] == {"question-9": 102}


def test_two_answers_for_one_question_keeps_the_last(command: QuestionnaireCommand) -> None:
    """Where a question is answered twice, the last answer is the one recorded."""
    command.answers = [Answer(question_id=9, response=101), Answer(question_id=9, response=102)]

    assert command.values["questions"] == {"question-9": 102}


def test_the_caller_never_branches_on_the_question_type(command: QuestionnaireCommand) -> None:
    """One call shape answers a radio, a checkbox and a text question."""
    command.answers = [
        Answer(question_id=9, response=102),
        Answer(question_id=10, response=[201]),
        Answer(question_id=11, response="Half a pack a day"),
    ]

    answered = command.values["questions"]

    assert answered["question-9"] == 102
    assert [entry["text"] for entry in answered["question-10"]] == ["Cigarettes"]
    assert answered["question-11"] == "Half a pack a day"


def test_an_id_arriving_as_a_string_still_lands_on_its_option(
    command: QuestionnaireCommand,
) -> None:
    """A numeric string resolves to the option with that id, not the one with that name."""
    command.answers = [Answer(question_id=9, response="102"), Answer(question_id=12, response="2")]

    assert command.values["questions"] == {"question-9": 102, "question-12": 2}


def test_a_checkbox_takes_several_ids(command: QuestionnaireCommand) -> None:
    """A checkbox answer is a list of ids, recorded as one selection each."""
    command.answers = [Answer(question_id=10, response=[201, 202])]

    selected = command.values["questions"]["question-10"]

    assert [entry["value"] for entry in selected] == [201, 202]


def test_a_text_question_takes_what_was_written(command: QuestionnaireCommand) -> None:
    """A text answer is recorded as written."""
    command.answers = [Answer(question_id=11, response="Half a pack a day")]

    assert command.values["questions"] == {"question-11": "Half a pack a day"}


def test_an_integer_question_takes_a_number(command: QuestionnaireCommand) -> None:
    """An integer answer is recorded as an int, given a number or a numeric string."""
    command.answers = [Answer(question_id=13, response=3)]
    assert command.values["questions"] == {"question-13": 3}

    fresh = command.model_copy()
    fresh.answers = [Answer(question_id=13, response="4")]
    assert fresh.values["questions"] == {"question-13": 4}


def test_an_integer_question_refuses_what_is_not_a_number(command: QuestionnaireCommand) -> None:
    """An integer answer that is not a number raises."""
    command.answers = [Answer(question_id=13, response="a few")]

    with pytest.raises(ValueError, match="convertible to an integer"):
        _ = command.values


def test_a_comment_rides_on_every_selection(command: QuestionnaireCommand) -> None:
    """An answer's comment is carried onto each selection it makes."""
    command.answers = [Answer(question_id=10, response=[201, 202], comment="both")]

    selected = command.values["questions"]["question-10"]

    assert [entry["text"] for entry in selected] == ["Cigarettes", "Cigar/Pipe"]
    assert {entry["comment"] for entry in selected} == {"both"}


def test_an_option_the_question_does_not_offer_is_refused(command: QuestionnaireCommand) -> None:
    """An id the question does not offer raises, naming the question and its options."""
    command.answers = [Answer(question_id=9, response=999999)]

    with pytest.raises(ValueError, match="not an option for question 'Status'"):
        _ = command.values


def test_a_question_from_another_questionnaire_is_refused(command: QuestionnaireCommand) -> None:
    """An id that names no question in the questionnaire raises."""
    command.answers = [Answer(question_id=999, response=102)]

    with pytest.raises(ValueError, match="not a question in questionnaire"):
        _ = command.values


def test_originating_and_editing_does_not_tick_the_box_twice(
    command: QuestionnaireCommand,
) -> None:
    """Reading ``values`` twice records each checkbox selection once, not twice."""
    command.command_uuid = "9f1d3b6a-0000-4000-8000-00000000000a"
    command.answers = [Answer(question_id=10, response=201)]

    originate, edit = json.loads(command.originate().payload), json.loads(command.edit().payload)

    assert originate["data"]["questions"]["question-10"] == edit["data"]["questions"]["question-10"]
    assert len(edit["data"]["questions"]["question-10"]) == 1


def test_a_response_set_directly_on_another_question_survives(
    command: QuestionnaireCommand,
) -> None:
    """A response set directly on a question ``answers`` does not name is kept."""
    text_question = next(q for q in command.questions if q.type == "TXT")
    text_question.add_response(text="Set by hand")
    command.answers = [Answer(question_id=9, response=102)]

    answered = command.values["questions"]

    assert answered["question-11"] == "Set by hand"
    assert answered["question-9"] == 102


def test_answers_apply_to_the_commands_that_subclass_this_one(
    command: QuestionnaireCommand,
) -> None:
    """A physical exam, a review of systems and a structured assessment answer the same way."""
    exam = PhysicalExamCommand(
        note_uuid="note-1",
        questionnaire_id=QUESTIONNAIRE_ID,
        answers=[Answer(question_id=9, response=102)],
    )

    assert exam.values["questions"] == {"question-9": 102}


def test_the_effect_does_not_carry_the_answers_field(command: QuestionnaireCommand) -> None:
    """``values`` carries responses under ``questions`` and drops ``answers``."""
    command.answers = [Answer(question_id=11, response="Half a pack a day")]

    assert "answers" not in command.values


def test_a_command_with_no_answers_is_unchanged(command: QuestionnaireCommand) -> None:
    """A command with no answers carries no questions."""
    assert command.values["questions"] == {}
