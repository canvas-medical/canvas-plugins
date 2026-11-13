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
    confirm_against_print,
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


def test_repairs_never_change_the_birth_date() -> None:
    """Digits in names are tried as letters; the birth date is kept as printed."""
    repairs = repair_candidates(
        {
            "first_name": "J0HN",
            "last_name": "SM1TH",
            "birth_date": "1971-03-09",
            "as_printed": {"name": "SM1TH, J0HN"},
        }
    )

    assert repairs.complete
    assert {c["birth_date"] for _, c in repairs.candidates} == {"1971-03-09"}
    assert {"SMlTH", "SMiTH"} <= {c["last_name"] for _, c in repairs.candidates}


def test_more_readings_than_the_caps_allow_are_reported_incomplete() -> None:
    """An MRN full of confusable characters has more readings than can be checked."""
    repairs = repair_candidates(
        {
            "last_name": "Smith",
            "birth_date": "1971-03-09",
            "mrn": "1050815",
            "as_printed": {"mrn": "1050815"},
        }
    )

    assert not repairs.complete
    assert len(repairs.candidates) <= MAX_CANDIDATES


def test_names_are_swapped_only_when_the_print_does_not_say_which_is_which() -> None:
    """'DOE, JOHN' puts the last name first; 'JOHN DOE' could be read either way."""
    base = {"first_name": "Doe", "last_name": "John", "birth_date": "1971-03-09"}

    with_comma = repair_candidates({**base, "as_printed": {"name": "DOE, JOHN"}}).candidates
    without = repair_candidates({**base, "as_printed": {"name": "JOHN DOE"}}).candidates

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
        as_printed={"name": "AL1, SAM", "birth_date": "03/09/1971"},
        legibility="readable_with_artifacts",
    )

    assert result["ok"] is False
    assert "More than one" in result["reason"]
    assert effects == []


@pytest.mark.django_db
def test_an_exact_match_carries_no_repair_warning() -> None:
    """A clean PDF's identifiers, read exactly as printed, match with no fix to flag."""
    patient = PatientFactory.create(first_name="John", last_name="Smith", birth_date=BIRTH)

    result, (effect,) = _run(
        "suggest_patient",
        first_name="John",
        last_name="Smith",
        birth_date="1971-03-09",
        as_printed={"name": "JOHN SMITH", "birth_date": "03/09/1971"},
        legibility="clear",
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


@pytest.mark.django_db
def test_a_match_among_cut_short_readings_is_not_taken_as_the_only_one() -> None:
    """With readings dropped by the caps, a rival chart could be among them: no one is named."""
    PatientFactory.create(last_name="Smith", birth_date=BIRTH, mrn="I050815")

    result, effects = _run(
        "suggest_patient",
        last_name="Smith",
        birth_date="1971-03-09",
        mrn="1050815",
        as_printed={"name": "SMITH", "mrn": "1050815", "birth_date": "03/09/1971"},
        legibility="readable_with_artifacts",
    )

    assert result["ok"] is False
    assert "more readings than can be checked" in result["reason"]
    assert effects == []


@pytest.mark.django_db
def test_the_models_label_never_replaces_the_repair_warning() -> None:
    """The reviewer always sees that the match needed a fix, beside whatever the model wrote."""
    PatientFactory.create(first_name="John", last_name="Smith", birth_date=BIRTH)

    _, (effect,) = _run(
        "suggest_patient",
        first_name="J0HN",
        last_name="Smith",
        birth_date="1971-03-09",
        as_printed={"name": "SMITH, J0HN", "birth_date": "03/09/1971"},
        legibility="clear",
        label="Exact match",
    )

    assert {"Matched after fax misread fix", "Exact match"} <= set(_labels(effect))


# What was printed decides -----------------------------------------------------------


@pytest.mark.parametrize(
    ("arguments", "refused"),
    [
        (
            {
                "first_name": "Ann",
                "last_name": "Smith",
                "birth_date": "1971-03-09",
                "as_printed": {"name": "ANN SMITH", "birth_date": "03/09/1971", "mrn": "B-1"},
            },
            "MRN is printed",
        ),
        (
            {
                "first_name": "Ann",
                "last_name": "Smith",
                "as_printed": {"name": "ANN SMITH", "birth_date": "03/09/1971"},
            },
            "birth date is printed",
        ),
        (
            {
                "first_name": "Ann",
                "last_name": "Smith",
                "birth_date": "1971-03-09",
                "as_printed": {"name": "ANN SMITH-JONES", "birth_date": "03/09/1971"},
            },
            "name as printed",
        ),
        (
            {
                "last_name": "Doe",
                "birth_date": "1971-03-09",
                "as_printed": {"name": "DOE, JANE", "birth_date": "03/09/1971"},
            },
            "first name is printed",
        ),
    ],
    ids=["mrn-unread", "birth-date-unread", "name-part-unread", "first-name-unread"],
)
def test_every_printed_identifier_must_be_read_and_agree(
    arguments: dict[str, Any], refused: str
) -> None:
    """A value the model left out, or read only in part, cannot quietly drop out of the match."""
    assert refused in str(check_printed(arguments))


@pytest.mark.django_db
def test_another_patients_printed_mrn_names_no_one() -> None:
    """Ann Smith matches by name and birth date, but the print carries patient B's MRN."""
    PatientFactory.create(first_name="Ann", last_name="Smith", birth_date=BIRTH, mrn="A-1")

    result, effects = _run(
        "suggest_patient",
        first_name="Ann",
        last_name="Smith",
        birth_date="1971-03-09",
        mrn="B-1",
        as_printed={"name": "ANN SMITH", "birth_date": "03/09/1971", "mrn": "MRN: B-1"},
        legibility="clear",
    )

    assert result["ok"] is False
    assert effects == []


@pytest.mark.django_db
def test_the_matched_patient_must_agree_with_the_print_in_code() -> None:
    """The patient found is compared with the print itself, not only with what was read."""
    PatientFactory.create(first_name="Ann", last_name="Smith", birth_date=BIRTH, mrn="A-1")

    result, effects = _run(
        "suggest_patient",
        last_name="Smith",
        birth_date="1971-03-09",
        mrn="A-1",
        as_printed={"name": "SMITH", "birth_date": "03/09/1971", "mrn": "MRN: A-2"},
        legibility="clear",
    )

    assert result["ok"] is False
    assert effects == []


@pytest.mark.django_db
def test_confidence_counts_the_identifiers_printed_and_confirmed() -> None:
    """Three printed identifiers the patient agrees with are high confidence; two are medium."""
    patient = PatientFactory.create(
        first_name="Ann", last_name="Smith", birth_date=BIRTH, mrn="A-1"
    )
    printed = {"name": "SMITH, ANN", "birth_date": "03/09/1971"}
    read = {"first_name": "Ann", "last_name": "Smith", "birth_date": "1971-03-09"}

    full, _ = _run("suggest_patient", **read, as_printed=printed, legibility="clear")
    # The print shows no name, so only the birth date and MRN are printed evidence.
    partial, _ = _run(
        "suggest_patient",
        birth_date="1971-03-09",
        mrn="A-1",
        as_printed={"birth_date": "03/09/1971", "mrn": "A-1"},
        legibility="clear",
    )

    assert (full["patient_id"], full["confidence"]) == (patient.id, "high")
    assert (partial["patient_id"], partial["confidence"]) == (patient.id, "medium")


@pytest.mark.django_db
def test_the_matched_patients_own_record_is_compared_with_the_print() -> None:
    """Whatever was read, the patient found must be the one the print describes."""
    patient = PatientFactory.create(
        first_name="Ann", last_name="Smith", birth_date=BIRTH, mrn="A-1"
    )
    printed = {"name": "SMITH, ANN", "birth_date": "03/09/1971", "mrn": "A-1"}

    assert confirm_against_print(patient, {"as_printed": printed}) == ("", 4)
    for other in (
        {**printed, "name": "SMITH, JANE"},
        {**printed, "birth_date": "03/10/1971"},
        {**printed, "mrn": "A-2"},
    ):
        reason, _ = confirm_against_print(patient, {"as_printed": other})
        assert "does not match the print" in reason


@pytest.mark.django_db
def test_a_repaired_reading_that_matches_several_patients_names_no_one() -> None:
    """Two John Smiths born the same day: the repair cannot say which, so it says neither."""
    for _ in range(2):
        PatientFactory.create(first_name="John", last_name="Smith", birth_date=BIRTH)

    result, effects = _run(
        "suggest_patient",
        first_name="J0HN",
        last_name="SM1TH",
        birth_date="1971-03-09",
        as_printed={"name": "SM1TH, J0HN", "birth_date": "03/09/1971"},
        legibility="readable_with_artifacts",
    )

    assert result["ok"] is False
    assert "More than one patient" in str(result)
    assert effects == []


@pytest.mark.parametrize(
    ("printed", "read"),
    [("RENÉE", "René"), ("ANDRÉA", "André"), ("ÉLISE", "Lise")],
    ids=["renee-read-as-rene", "andrea-read-as-andre", "elise-read-as-lise"],
)
@pytest.mark.django_db
def test_an_accented_print_is_not_read_as_a_shorter_name(printed: str, read: str) -> None:
    """RENÉE is printed for Renée, so the twin René born the same day is not named."""
    PatientFactory.create(first_name=read, last_name="Doe", birth_date=BIRTH)
    PatientFactory.create(
        first_name=printed.capitalize(), last_name="Doe", birth_date=date(1990, 1, 1)
    )

    result, effects = _run(
        "suggest_patient",
        first_name=read,
        last_name="Doe",
        birth_date="1971-03-09",
        as_printed={"name": f"{printed} DOE", "birth_date": "03/09/1971"},
        legibility="clear",
    )

    assert result["ok"] is False
    assert effects == []


@pytest.mark.django_db
def test_an_accented_name_read_as_printed_matches() -> None:
    """Accents fold the same way on both sides, so RENÉE DOE read as Renée names her."""
    patient = PatientFactory.create(first_name="Renée", last_name="Doe", birth_date=BIRTH)

    result, _ = _run(
        "suggest_patient",
        first_name="Renée",
        last_name="Doe",
        birth_date="1971-03-09",
        as_printed={"name": "RENÉE DOE", "birth_date": "03/09/1971"},
        legibility="clear",
    )

    assert (result["patient_id"], result["confidence"]) == (patient.id, "high")


# Middle names, suffixes, and how dates and MRNs are printed ----------------------------


@pytest.mark.parametrize(
    ("patient", "read", "printed_name"),
    [
        (
            {"first_name": "John", "last_name": "Smith", "suffix": "Jr."},
            {"first_name": "John", "last_name": "Smith", "suffix": "Jr"},
            "JOHN SMITH JR",
        ),
        (
            {"first_name": "John", "last_name": "Smith", "middle_name": "Quincy"},
            {"first_name": "John", "middle_name": "Quincy", "last_name": "Smith"},
            "JOHN QUINCY SMITH",
        ),
        (
            {"first_name": "John", "last_name": "Smith", "middle_name": "Quincy"},
            {"first_name": "John", "last_name": "Smith"},
            "SMITH, JOHN Q.",
        ),
        (
            {
                "first_name": "John",
                "last_name": "Smith",
                "middle_name": "Quincy",
                "suffix": "III",
            },
            {"first_name": "John", "middle_name": "Quincy", "last_name": "Smith", "suffix": "III"},
            "SMITH III, JOHN QUINCY",
        ),
    ],
    ids=["suffix", "middle-name", "middle-initial", "middle-name-and-suffix"],
)
@pytest.mark.django_db
def test_a_printed_middle_name_or_suffix_the_patient_has_matches(
    patient: dict[str, str], read: dict[str, str], printed_name: str
) -> None:
    """The patient's recorded middle name and suffix account for the rest of the print."""
    found = PatientFactory.create(**patient, birth_date=BIRTH)

    result, _ = _run(
        "suggest_patient",
        **read,
        birth_date="1971-03-09",
        as_printed={"name": printed_name, "birth_date": "03/09/1971"},
        legibility="clear",
    )

    assert (result.get("patient_id"), result.get("confidence")) == (found.id, "high"), result


@pytest.mark.parametrize(
    ("patient", "read", "printed_name"),
    [
        (
            {"first_name": "John", "last_name": "Smith", "suffix": "Sr."},
            {"first_name": "John", "last_name": "Smith", "suffix": "Jr"},
            "JOHN SMITH JR",
        ),
        (
            {"first_name": "John", "last_name": "Smith"},
            {"first_name": "John", "last_name": "Smith", "suffix": "Jr"},
            "JOHN SMITH JR",
        ),
        (
            {"first_name": "John", "last_name": "Smith", "middle_name": "Paul"},
            {"first_name": "John", "middle_name": "Quincy", "last_name": "Smith"},
            "JOHN QUINCY SMITH",
        ),
        (
            {"first_name": "John", "last_name": "Smith", "middle_name": "Paul"},
            {"first_name": "John", "last_name": "Smith"},
            "JOHN Q. SMITH",
        ),
        (
            {"first_name": "Ann", "last_name": "Smith"},
            {"first_name": "Ann", "middle_name": "Jones", "last_name": "Smith"},
            "ANN SMITH-JONES",
        ),
    ],
    ids=[
        "other-suffix",
        "suffix-not-recorded",
        "other-middle-name",
        "other-middle-initial",
        "unrecorded-word-read-as-middle-name",
    ],
)
@pytest.mark.django_db
def test_a_printed_middle_name_or_suffix_the_patient_lacks_names_no_one(
    patient: dict[str, str], read: dict[str, str], printed_name: str
) -> None:
    """Junior's fax never names Senior, and a word the record cannot explain names no one."""
    PatientFactory.create(**patient, birth_date=BIRTH)

    result, effects = _run(
        "suggest_patient",
        **read,
        birth_date="1971-03-09",
        as_printed={"name": printed_name, "birth_date": "03/09/1971"},
        legibility="clear",
    )

    assert result["ok"] is False, result
    assert effects == []


def test_a_middle_name_or_suffix_read_must_be_printed() -> None:
    """A middle name or suffix the print does not show is refused like any other reading."""
    printed = {"name": "JOHN SMITH", "birth_date": "03/09/1971"}
    read = {"first_name": "John", "last_name": "Smith", "birth_date": "1971-03-09"}

    assert "middle name read" in str(
        check_printed({**read, "middle_name": "Quincy", "as_printed": printed})
    )
    assert "suffix read" in str(check_printed({**read, "suffix": "Jr", "as_printed": printed}))


@pytest.mark.parametrize(
    "printed",
    ["March 9th, 1971", "09-MAR-1971", "9-Mar-1971", "Born: 03/09/1971", "Born 9 March 1971"],
)
def test_common_printed_date_formats_are_read(printed: str) -> None:
    """Ordinal days, day-month-year with a month name, and a Born label are all read."""
    assert parse_printed_date(printed) == BIRTH


@pytest.mark.django_db
def test_an_mrn_printed_beside_other_numbers_matches() -> None:
    """The MRN read is found among the numbers printed next to it."""
    patient = PatientFactory.create(
        first_name="Ann", last_name="Smith", birth_date=BIRTH, mrn="4471"
    )

    result, _ = _run(
        "suggest_patient",
        first_name="Ann",
        last_name="Smith",
        birth_date="1971-03-09",
        mrn="4471",
        as_printed={
            "name": "SMITH, ANN",
            "birth_date": "03/09/1971",
            "mrn": "MRN 4471 ACCT 99812",
        },
        legibility="clear",
    )

    assert (result.get("patient_id"), result.get("confidence")) == (patient.id, "high"), result


@pytest.mark.parametrize(
    ("read", "printed"),
    [
        ("345", "MRN 12-345"),
        ("4471", "MRN: VL-4471"),
        ("99812", "MRN 4471 ACCT 99812"),
        ("4471", "MRN 4471 5550123"),
    ],
    ids=["part-of-a-hyphenated-mrn", "part-of-a-sending-mrn", "account-number", "two-numbers"],
)
@pytest.mark.django_db
def test_only_a_whole_printed_mrn_matches(read: str, printed: str) -> None:
    """Part of an MRN, an account number, or one of two unlabeled numbers is not the MRN."""
    PatientFactory.create(first_name="Ann", last_name="Smith", birth_date=BIRTH, mrn=read)

    result, effects = _run(
        "suggest_patient",
        first_name="Ann",
        last_name="Smith",
        birth_date="1971-03-09",
        mrn=read,
        as_printed={"name": "SMITH, ANN", "birth_date": "03/09/1971", "mrn": printed},
        legibility="clear",
    )

    assert result["ok"] is False, result
    assert effects == []
