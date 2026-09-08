import datetime

import pytest

from canvas_sdk.commands.commands.questionnaire import QUESTION_CLASSES
from canvas_sdk.commands.commands.questionnaire.question import (
    DateQuestion,
    ResponseOption,
)


def make_date_question() -> DateQuestion:
    """Build a DateQuestion instance for testing."""
    return DateQuestion(
        id="1",
        name="question-1",
        label="Discharge date",
        coding={"system": "LOINC", "code": "12345-6"},
        options=[],
    )


def test_date_type_registered() -> None:
    """The DATE type is dispatched to DateQuestion."""
    assert ResponseOption.TYPE_DATE == "DATE"
    assert QUESTION_CLASSES[ResponseOption.TYPE_DATE] is DateQuestion
    assert DateQuestion.type == "DATE"


def test_date_question_accepts_date() -> None:
    """A datetime.date is stored as an ISO 8601 date string."""
    question = make_date_question()
    question.add_response(datetime.date(2026, 1, 15))
    assert question.response == "2026-01-15"


def test_date_question_accepts_datetime() -> None:
    """A datetime.datetime is normalized to its date and stored as an ISO string."""
    question = make_date_question()
    question.add_response(datetime.datetime(2026, 1, 15, 9, 30, 0))
    assert question.response == "2026-01-15"


def test_date_question_accepts_iso_string() -> None:
    """A valid ISO 8601 date string is normalized and stored."""
    question = make_date_question()
    question.add_response("2026-01-15")
    assert question.response == "2026-01-15"


def test_date_question_rejects_invalid_string() -> None:
    """An unparseable date string raises a ValueError mentioning the question label."""
    question = make_date_question()
    with pytest.raises(ValueError, match="Discharge date"):
        question.add_response("not-a-date")


def test_date_question_rejects_datetime_string() -> None:
    """A string carrying a time component is rejected; a plain date is required."""
    question = make_date_question()
    with pytest.raises(ValueError, match="ISO 8601 date"):
        question.add_response("2026-01-15T09:30:00")


def test_date_question_rejects_wrong_type() -> None:
    """A value that is neither a date nor a string raises a ValueError."""
    question = make_date_question()
    with pytest.raises(ValueError, match="date or an ISO 8601 date string"):
        question.add_response(20260115)  # type: ignore[arg-type]
