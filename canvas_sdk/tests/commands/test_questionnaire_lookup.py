"""Tests for how :class:`QuestionnaireCommand` finds its questionnaire."""

import pytest

from canvas_sdk.commands.commands.questionnaire import QuestionnaireCommand
from canvas_sdk.test_utils.factories import NoteFactory
from canvas_sdk.v1.data import Command, Questionnaire


def _questionnaire() -> Questionnaire:
    return Questionnaire.objects.create(
        status="AC",
        name="Tobacco",
        expected_completion_time=1.0,
        can_originate_in_charting=True,
        use_case_in_charting="QUES",
        scoring_function_name="",
        scoring_code_system="",
        scoring_code="",
        code_system="LOINC",
        code="72166-2",
        search_tags="",
        use_in_shx=False,
        carry_forward="",
    )


def _command(data: dict) -> Command:
    note = NoteFactory.create()
    return Command.objects.create(
        note=note,
        patient=note.patient,
        state="staged",
        schema_key="questionnaire",
        data=data,
        origination_source="user",
        anchor_object_type="",
        anchor_object_dbid=0,
    )


def test_a_command_with_no_questionnaire_and_no_command_has_no_questions() -> None:
    """Nothing to look the questionnaire up by, so there are no questions."""
    command = QuestionnaireCommand(note_uuid="note-1")

    assert command._questionnaire is None
    assert command.questions == []


@pytest.mark.django_db
def test_the_questionnaire_is_read_by_its_id() -> None:
    """A given questionnaire id is looked up directly."""
    questionnaire = _questionnaire()

    command = QuestionnaireCommand(questionnaire_id=str(questionnaire.id), note_uuid="note-1")

    assert command._questionnaire == questionnaire


@pytest.mark.django_db
def test_the_questionnaire_is_read_from_the_command_when_not_given() -> None:
    """With no id given, the questionnaire picked on the command is used and remembered."""
    questionnaire = _questionnaire()
    stored = _command({"questionnaire": {"value": questionnaire.dbid}})

    command = QuestionnaireCommand(command_uuid=str(stored.id))

    assert command._questionnaire == questionnaire
    assert command.questionnaire_id == str(questionnaire.id)


@pytest.mark.django_db
def test_a_command_whose_questionnaire_is_not_picked_has_no_questions() -> None:
    """The note UI stores `questionnaire: None` until one is picked."""
    stored = _command({"questionnaire": None})

    command = QuestionnaireCommand(command_uuid=str(stored.id))

    assert command._questionnaire is None
    assert command.questions == []
