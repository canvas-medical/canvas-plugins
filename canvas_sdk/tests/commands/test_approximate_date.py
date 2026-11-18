"""Approximate dates: a date, or a year, month or day written as ``YYYY``, ``YYYY-MM`` or ``YYYY-MM-DD``.

Canvas records these fields as approximate dates, so a plugin that only knows the year or the
month can say so, and the partial date reaches Canvas as the string it was given.
"""

from datetime import date, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from canvas_sdk.commands import (
    AllergyCommand,
    AssessCommand,
    DiagnoseCommand,
    FollowUpCommand,
    MedicalHistoryCommand,
    PastSurgicalHistoryCommand,
)
from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.commands.commands.add_condition import AddConditionCommand
from canvas_sdk.commands.commands.immunization_statement import ImmunizationStatementCommand

#: Every command field Canvas records as an approximate date.
APPROXIMATE_FIELDS: list[tuple[type[_BaseCommand], str]] = [
    (AddConditionCommand, "approximate_date_of_onset"),
    (AllergyCommand, "approximate_date"),
    (AssessCommand, "approximate_date_of_onset"),
    (DiagnoseCommand, "approximate_date_of_onset"),
    (FollowUpCommand, "requested_date"),
    (ImmunizationStatementCommand, "approximate_date"),
    (MedicalHistoryCommand, "approximate_start_date"),
    (MedicalHistoryCommand, "approximate_end_date"),
    (PastSurgicalHistoryCommand, "approximate_date"),
]


def sent(command_class: type[_BaseCommand], field: str, value: Any) -> Any:
    """The value a command carries to Canvas for ``field`` when built with ``value``."""
    return command_class(**{field: value}).values[field]


@pytest.mark.parametrize(("command_class", "field"), APPROXIMATE_FIELDS)
@pytest.mark.parametrize("value", ["2023", "2026-09", "2026-09-14"])
def test_a_year_month_or_day_is_sent_as_written(
    command_class: type[_BaseCommand], field: str, value: str
) -> None:
    """A partial date stays partial, so Canvas records it as the approximate date it is."""
    assert sent(command_class, field, value) == value


@pytest.mark.parametrize(("command_class", "field"), APPROXIMATE_FIELDS)
def test_a_date_is_sent_as_its_iso_form(command_class: type[_BaseCommand], field: str) -> None:
    """A plugin that passes a ``date`` keeps working as it did."""
    assert sent(command_class, field, date(2026, 9, 14)) == "2026-09-14"


@pytest.mark.parametrize(("command_class", "field"), APPROXIMATE_FIELDS)
def test_a_datetime_at_midnight_is_its_date(command_class: type[_BaseCommand], field: str) -> None:
    """A midnight datetime was accepted as its date before, and still is."""
    assert sent(command_class, field, datetime(2026, 9, 14)) == "2026-09-14"


@pytest.mark.parametrize(("command_class", "field"), APPROXIMATE_FIELDS)
@pytest.mark.parametrize(
    "value",
    [
        "2026-13",
        "2026-02-30",
        "Sep 2026",
        "20260914",
        "2026/09",
        "",
        datetime(2026, 9, 14, 10, 30),
        2023,
    ],
)
def test_anything_else_is_refused(
    command_class: type[_BaseCommand], field: str, value: Any
) -> None:
    """Only real dates in the three written forms, so Canvas never stores one it can't read."""
    with pytest.raises(ValidationError):
        command_class(**{field: value})


@pytest.mark.parametrize(("command_class", "field"), APPROXIMATE_FIELDS)
def test_none_still_means_no_date(command_class: type[_BaseCommand], field: str) -> None:
    """The fields stay optional."""
    assert sent(command_class, field, None) is None
