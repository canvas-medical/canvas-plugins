"""Approximate dates: a date, or a year or month written as ``YYYY`` or ``MM/YYYY``.

Canvas records these fields as approximate dates, so a plugin that only knows the year or the
month can say so, and the partial date reaches Canvas as the string it was given. Every value a
``date`` field accepts is read the same way here.
"""

from datetime import UTC, date, datetime, timedelta, timezone
from typing import Any

import pytest
from jsonschema import Draft202012Validator
from pydantic import BaseModel, ConfigDict, ValidationError

from canvas_sdk.agents import history_tools  # noqa: F401  (registers the history tools)
from canvas_sdk.agents.standard_tools import standard_tools
from canvas_sdk.agents.tool_registry import FORMAT_CHECKER
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


class OnMain(BaseModel):
    """The field as every approximate date was typed on ``main``: a lax, optional ``date``."""

    model_config = ConfigDict(strict=False, validate_assignment=True)

    value: date | None = None


#: Values a plugin may pass today, accepted or refused on ``main``. Each must be read the same way.
VALUES_FROM_BEFORE: list[Any] = [
    None,
    date(2026, 9, 14),
    datetime(2026, 9, 14),
    datetime(2026, 9, 14, tzinfo=UTC),
    datetime(2026, 9, 14, tzinfo=timezone(timedelta(hours=-5))),
    datetime(2026, 9, 14, 10, 30),
    "2026-09-14",
    "2026-09-14T00:00:00",
    "2026-09-14T00:00:00Z",
    "2026-09-14T00:00:00+00:00",
    "2026-09-14T10:30:00",
    "2026-09-14 00:00:00",
    b"2026-09-14",
    1789344000,
    1789344000.0,
    "1789344000",
    1789344000000,
    1789344001,
    0,
    2023,
    "2026-02-30",
    "2026/09/14",
    "09/14/2026",
    "14 Sep 2026",
    "",
    " 2026-09-14",
    [2026, 9, 14],
    {"year": 2026},
]


def read_on_main(value: Any) -> tuple[str, Any]:
    """How ``main`` reads ``value``: the date it becomes, or that it is refused."""
    try:
        return ("read", OnMain(value=value).value)
    except ValidationError:
        return ("refused", None)


def read_here(command_class: type[_BaseCommand], field: str, value: Any) -> tuple[str, Any]:
    """How the command reads ``value`` for ``field`` when built with it."""
    try:
        return ("read", getattr(command_class(**{field: value}), field))
    except ValidationError:
        return ("refused", None)


def assigned_here(command_class: type[_BaseCommand], field: str, value: Any) -> tuple[str, Any]:
    """How the command reads ``value`` set on ``field`` after it is built."""
    command = command_class()
    try:
        setattr(command, field, value)
    except ValidationError:
        return ("refused", None)
    return ("read", getattr(command, field))


@pytest.mark.parametrize(("command_class", "field"), APPROXIMATE_FIELDS)
@pytest.mark.parametrize("value", VALUES_FROM_BEFORE)
def test_a_value_from_before_is_read_as_main_reads_it(
    command_class: type[_BaseCommand], field: str, value: Any
) -> None:
    """Built with it: what ``main`` took comes back as the same ``date``, and what it refused is refused."""
    assert read_here(command_class, field, value) == read_on_main(value)


@pytest.mark.parametrize(("command_class", "field"), APPROXIMATE_FIELDS)
@pytest.mark.parametrize("value", VALUES_FROM_BEFORE)
def test_a_value_from_before_is_assigned_as_main_assigns_it(
    command_class: type[_BaseCommand], field: str, value: Any
) -> None:
    """Set after the command is built, the same holds."""
    assert assigned_here(command_class, field, value) == read_on_main(value)


@pytest.mark.parametrize(("command_class", "field"), APPROXIMATE_FIELDS)
@pytest.mark.parametrize("value", [date(2026, 9, 14), "2026-09-14", 1789344000])
def test_a_value_from_before_is_sent_as_main_sent_it(
    command_class: type[_BaseCommand], field: str, value: Any
) -> None:
    """``values`` carries a full day in ISO form, as it did."""
    assert sent(command_class, field, value) == "2026-09-14"


def sent(command_class: type[_BaseCommand], field: str, value: Any) -> Any:
    """The value a command carries to Canvas for ``field`` when built with ``value``."""
    return command_class(**{field: value}).values[field]


@pytest.mark.parametrize(("command_class", "field"), APPROXIMATE_FIELDS)
@pytest.mark.parametrize("value", ["2023", "09/2026", "12/2026", "01/2026"])
def test_a_year_or_month_is_sent_as_written(
    command_class: type[_BaseCommand], field: str, value: str
) -> None:
    """A partial date stays partial, so Canvas records it as the approximate date it is."""
    command = command_class(**{field: value})

    assert getattr(command, field) == value
    assert command.values[field] == value


@pytest.mark.parametrize(("command_class", "field"), APPROXIMATE_FIELDS)
@pytest.mark.parametrize(
    "value",
    [
        "2026-09-14",
        "2026-09-14T00:00:00",
        date(2026, 9, 14),
        datetime(2026, 9, 14),
        1789344000,
        "1789344000",
    ],
)
def test_a_full_day_reads_back_as_a_date(
    command_class: type[_BaseCommand], field: str, value: Any
) -> None:
    """Whatever a ``date`` field accepts is still read as a ``date`` and sent in ISO form."""
    command = command_class(**{field: value})

    assert getattr(command, field) == date(2026, 9, 14)
    assert getattr(command, field).year == 2026
    assert command.values[field] == "2026-09-14"


@pytest.mark.parametrize(("command_class", "field"), APPROXIMATE_FIELDS)
@pytest.mark.parametrize(
    "value",
    [
        "13/2026",
        "00/2026",
        "9/2026",
        "2026-09",
        "2026-02-30",
        " 2023",
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
    """A month that does not exist, or anything a ``date`` field refuses, is refused."""
    with pytest.raises(ValidationError):
        command_class(**{field: value})


@pytest.mark.parametrize(("command_class", "field"), APPROXIMATE_FIELDS)
def test_none_still_means_no_date(command_class: type[_BaseCommand], field: str) -> None:
    """The fields stay optional."""
    assert sent(command_class, field, None) is None


@pytest.mark.parametrize(("command_class", "field"), APPROXIMATE_FIELDS)
def test_the_command_schema_still_calls_it_a_date(
    command_class: type[_BaseCommand], field: str
) -> None:
    """``command_schema`` reports these fields as ``date``, as it does for any date field."""
    schema = command_class.command_schema()
    name = command_class.model_json_schema()["properties"][field].get("commands_api_name", field)

    assert schema[name]["type"] is date


#: Every agent tool argument that fills one of those fields.
TOOL_ARGUMENTS: list[tuple[str, str]] = [
    ("originate_diagnose_condition", "approximate_date_of_onset"),
    ("originate_follow_up", "requested_date"),
    ("originate_medical_history", "approximate_start_date"),
    ("originate_medical_history", "approximate_end_date"),
    ("originate_allergy", "approximate_date"),
    ("originate_surgical_history", "approximate_date"),
    ("originate_immunization_statement", "approximate_date"),
]


def argument_errors(tool: str, argument: str, value: str) -> list[str]:
    """What the tool's argument schema says about ``value``, empty when it takes it."""
    (definition,) = (d for d in standard_tools.definitions() if d["name"] == tool)
    property_schema = definition["input_schema"]["properties"][argument]
    validator = Draft202012Validator(property_schema, format_checker=FORMAT_CHECKER)
    return [error.message for error in validator.iter_errors(value)]


@pytest.mark.parametrize(("tool", "argument"), TOOL_ARGUMENTS)
@pytest.mark.parametrize("value", ["2023", "06/2025", "2025-06-14"])
def test_an_agent_tool_takes_a_year_month_or_day(tool: str, argument: str, value: str) -> None:
    """A model that knows only the year or the month can pass it to the tool."""
    assert argument_errors(tool, argument, value) == []


@pytest.mark.parametrize(("tool", "argument"), TOOL_ARGUMENTS)
@pytest.mark.parametrize("value", ["2025-06", "June 2025", "6/2025"])
def test_an_agent_tool_refuses_other_shapes(tool: str, argument: str, value: str) -> None:
    """A shape the command would refuse is refused at the tool call."""
    assert argument_errors(tool, argument, value)
