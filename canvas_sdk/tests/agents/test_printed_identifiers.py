"""Identifiers read off a scan, checked against the print, with fax misreads repaired in code."""

import json
from datetime import date
from typing import Any

import pytest

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.agents import standard_tools
from canvas_sdk.agents.printed_identifiers import (
    MAX_CANDIDATES,
    check_printed,
    parse_printed_date,
    repair_candidates,
)
from canvas_sdk.test_utils.factories import IntegrationTaskFactory, PatientFactory

BIRTH = date(1971, 3, 9)


def _run(tool: str, **arguments: Any) -> tuple[Any, list[Any]]:
    document = IntegrationTaskFactory.create(patient=None)
    effects: list[Any] = []
    ctx = {"document_id": str(document.id), "effects": effects}
    return standard_tools.execute(tool, arguments, ctx=ctx), effects


def _labels(effect: Any) -> list[str]:
    return [a["text"] for a in json.loads(effect.payload)["data"]["annotations"]]


# Reading the print ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("printed", "parsed"),
    [
        ("03/09/1971", BIRTH),
        ("DOB: O3/O9/l971", BIRTH),
        ("1971-03-09", BIRTH),
        ("March 9, 1971", BIRTH),
        ("9 Mar 1971", BIRTH),
        ("03/09/71", None),
        ("13/40/1971", None),
    ],
)
def test_a_printed_birth_date_is_read_month_first_and_never_guessed(
    printed: str, parsed: date | None
) -> None:
    """Fax letters in a date read as digits; a two-digit year or an impossible date is not read."""
    assert parse_printed_date(printed) == parsed


@pytest.mark.parametrize(
    ("arguments", "refused"),
    [
        ({"legibility": "illegible"}, "illegible"),
        ({"handwritten": True}, "handwritten"),
        ({"pages_disagree": True}, "different patients"),
        ({"last_name": "Smith", "as_printed": {"name": "DOE, JOHN"}}, "last name read"),
        ({"birth_date": "1971-09-03", "as_printed": {"birth_date": "03/09/1971"}}, "birth date"),
        ({"birth_date": "1971-03-09", "as_printed": {"birth_date": "03/09/71"}}, "guessing"),
        ({"mrn": "12345", "as_printed": {"mrn": "MRN: 12346"}}, "MRN read"),
    ],
)
def test_identifiers_the_print_does_not_support_are_refused(
    arguments: dict[str, Any], refused: str
) -> None:
    """A model that quietly fixed or swapped a value is caught by its own copy of the print."""
    assert refused in str(check_printed(arguments))


def test_a_reading_that_folds_a_fax_misread_still_agrees_with_the_print() -> None:
    """J0HN printed and JOHN read are the same name; 0/O and 1/l are a fax's confusions."""
    arguments = {
        "first_name": "John",
        "last_name": "Doe",
        "mrn": "A1O5",
        "birth_date": "1971-03-09",
        "as_printed": {"name": "D0E, J0HN", "mrn": "MRN A105", "birth_date": "O3/09/1971"},
    }

    assert check_printed(arguments) is None


def test_repairs_never_change_the_birth_date_and_are_capped() -> None:
    """Digits in names and confusable MRN characters are tried; the birth date is kept."""
    candidates = repair_candidates(
        {
            "first_name": "J0HN",
            "last_name": "SM1TH",
            "mrn": "1050815",
            "birth_date": "1971-03-09",
            "as_printed": {"name": "SM1TH, J0HN"},
        }
    )

    assert 0 < len(candidates) <= MAX_CANDIDATES
    assert {c["birth_date"] for _, c in candidates} == {"1971-03-09"}
    assert {"SMlTH", "SMiTH"} <= {c["last_name"] for _, c in candidates}


def test_names_are_swapped_only_when_the_print_does_not_say_which_is_which() -> None:
    """'DOE, JOHN' puts the last name first; 'JOHN DOE' could be read either way."""
    base = {"first_name": "Doe", "last_name": "John", "birth_date": "1971-03-09"}

    with_comma = repair_candidates({**base, "as_printed": {"name": "DOE, JOHN"}})
    without = repair_candidates({**base, "as_printed": {"name": "JOHN DOE"}})

    assert "name_swapped" not in {how for how, _ in with_comma}
    assert ("name_swapped", "Doe") in {(how, c["last_name"]) for how, c in without}


# Matching ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_a_fax_misread_is_repaired_and_labeled_for_the_reviewer() -> None:
    """J0HN SM1TH matches no one as read; the repair finds the one John Smith, labeled."""
    patient = PatientFactory.create(first_name="John", last_name="Smith", birth_date=BIRTH)

    result, (effect,) = _run(
        "suggest_patient",
        first_name="J0HN",
        last_name="SM1TH",
        birth_date="1971-03-09",
        as_printed={"name": "SM1TH, J0HN", "birth_date": "03/09/1971"},
        legibility="readable_with_artifacts",
    )

    assert (result["ok"], result["patient_id"], result["confidence"]) == (
        True,
        patient.id,
        "medium",
    )
    assert "fax_repair" in result["matched_on"]
    assert "Matched after fax misread fix" in _labels(effect)
    assert EffectType.Name(effect.type) == "LINK_DOCUMENT_TO_PATIENT"


@pytest.mark.django_db
def test_swapped_names_match_and_say_so() -> None:
    """A print with no comma, read the other way round, still finds the one patient."""
    patient = PatientFactory.create(first_name="Avery", last_name="Quinn", birth_date=BIRTH)

    result, (effect,) = _run(
        "suggest_patient",
        first_name="Quinn",
        last_name="Avery",
        birth_date="1971-03-09",
        as_printed={"name": "QUINN AVERY", "birth_date": "03/09/1971"},
        legibility="clear",
    )

    assert result["patient_id"] == patient.id
    assert "Matched with first/last name swapped" in _labels(effect)


@pytest.mark.django_db
def test_repairs_that_point_at_different_patients_suggest_no_one() -> None:
    """'Al1' could be All or Ali: when each reading finds a different chart, a person chooses."""
    PatientFactory.create(first_name="Sam", last_name="All", birth_date=BIRTH)
    PatientFactory.create(first_name="Sam", last_name="Ali", birth_date=BIRTH)

    result, effects = _run(
        "suggest_patient",
        first_name="Sam",
        last_name="Al1",
        birth_date="1971-03-09",
        as_printed={"name": "AL1, SAM"},
        legibility="readable_with_artifacts",
    )

    assert result["ok"] is False
    assert "More than one" in result["reason"]
    assert effects == []


@pytest.mark.django_db
def test_an_exact_match_is_unchanged_and_needs_no_print() -> None:
    """A clean PDF's identifiers match as before, without as_printed."""
    patient = PatientFactory.create(first_name="John", last_name="Smith", birth_date=BIRTH)

    result, (effect,) = _run(
        "suggest_patient", first_name="John", last_name="Smith", birth_date="1971-03-09"
    )

    assert (result["patient_id"], result["confidence"]) == (patient.id, "high")
    assert "Matched after fax misread fix" not in _labels(effect)


@pytest.mark.django_db
def test_an_illegible_fax_names_no_patient_even_when_the_values_match() -> None:
    """The model's own legibility call gates the match."""
    PatientFactory.create(first_name="John", last_name="Smith", birth_date=BIRTH)

    result, effects = _run(
        "match_patient",
        first_name="John",
        last_name="Smith",
        birth_date="1971-03-09",
        legibility="illegible",
    )

    assert result["match"] is None
    assert "illegible" in result["reason"]
