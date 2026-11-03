"""A questionnaire command edited by `command_uuid` alone, reading its questionnaire from the command."""

import json

import pytest

from canvas_sdk.commands import (
    PhysicalExamCommand,
    QuestionnaireCommand,
    ReviewOfSystemsCommand,
    StructuredAssessmentCommand,
)
from canvas_sdk.commands.commands.questionnaire import Answer
from canvas_sdk.test_utils.factories import NoteFactory, PatientFactory
from canvas_sdk.v1.data import (
    Command,
    Question,
    Questionnaire,
    QuestionnaireQuestionMap,
    ResponseOption,
    ResponseOptionSet,
)


@pytest.fixture
def questionnaire(db: None) -> Questionnaire:
    """A questionnaire with one text question."""
    option_set = ResponseOptionSet.objects.create(
        status="AC", name="Text", code_system="", code="", type="TXT", use_in_shx=False
    )
    ResponseOption.objects.create(
        status="AC",
        name="",
        code="",
        code_description="",
        value="",
        response_option_set=option_set,
        ordering=0,
    )
    question = Question.objects.create(
        status="AC",
        name="How are you?",
        response_option_set=option_set,
        acknowledge_only=False,
        show_prologue=False,
        code_system="",
        code="",
    )
    questionnaire = Questionnaire.objects.create(
        status="AC",
        name="Check-in",
        expected_completion_time=0,
        can_originate_in_charting=True,
        use_case_in_charting="QUES",
        scoring_function_name="",
        scoring_code_system="",
        scoring_code="",
        code_system="",
        code="",
        search_tags="",
        use_in_shx=False,
        carry_forward="off",
    )
    QuestionnaireQuestionMap.objects.create(
        status="AC", questionnaire=questionnaire, question=question
    )
    return questionnaire


@pytest.fixture
def stored_command(questionnaire: Questionnaire) -> Command:
    """A staged command in a note, holding the questionnaire as the note UI stores it."""
    note = NoteFactory.create(patient=PatientFactory.create())
    return Command.objects.create(
        note=note,
        patient=note.patient,
        state="staged",
        schema_key="questionnaire",
        data={"questionnaire": {"value": questionnaire.dbid, "text": questionnaire.name}},
        origination_source="user",
        anchor_object_type="",
        anchor_object_dbid=0,
    )


@pytest.mark.parametrize(
    "command_class",
    [
        QuestionnaireCommand,
        ReviewOfSystemsCommand,
        PhysicalExamCommand,
        StructuredAssessmentCommand,
    ],
)
def test_answers_on_an_edit_without_the_questionnaire_reach_the_payload(
    command_class: type[QuestionnaireCommand],
    questionnaire: Questionnaire,
    stored_command: Command,
) -> None:
    """The questionnaire is read from the command, and the answers are sent against its questions."""
    question = questionnaire.questions.get()

    effect = command_class(
        command_uuid=str(stored_command.id),
        answers=[Answer(question_id=question.dbid, response="Fine")],
    ).edit()

    assert json.loads(effect.payload)["data"]["questions"] == {f"question-{question.dbid}": "Fine"}


def test_questions_read_before_answering_keep_their_responses(
    questionnaire: Questionnaire, stored_command: Command
) -> None:
    """A response added to `questions` by hand, the older way, is sent too."""
    command = QuestionnaireCommand(command_uuid=str(stored_command.id))
    question = command.questions[0]
    question.add_response(text="Fine")

    effect = command.edit()

    assert json.loads(effect.payload)["data"]["questions"] == {question.name: "Fine"}
