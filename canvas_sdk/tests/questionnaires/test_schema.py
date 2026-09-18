"""Tests for the questionnaire YAML JSON schema.

home-app downloads this schema at runtime to validate questionnaires authored via the
Questionnaire Builder, a Google sheet, or a plugin's YAML, so the accepted response types here
are the source of truth for every authoring path.
"""

from typing import Any

import pytest
from jsonschema import ValidationError

from canvas_sdk.questionnaires.utils import ExtendedDraft7Validator, json_schema


def _questionnaire(responses_type: str) -> dict[str, Any]:
    """Build a minimal valid questionnaire definition using the given response type."""
    return {
        "name": "Admission details",
        "form_type": "QUES",
        "code_system": "LOINC",
        "code": "ADMIT_DETAILS",
        "can_originate_in_charting": True,
        "questions": [
            {
                "content": "Admission date",
                "code_system": "INTERNAL",
                "code": "ADMIT_D1",
                "responses_code_system": "INTERNAL",
                "responses_type": responses_type,
                "responses": [{"name": responses_type, "code": "ADMIT_D1_A1"}],
            }
        ],
    }


@pytest.mark.parametrize("responses_type", ["SING", "MULT", "TXT", "DATE"])
def test_schema_accepts_supported_response_types(responses_type: str) -> None:
    """Every supported response type validates, including DATE."""
    ExtendedDraft7Validator(json_schema()).validate(_questionnaire(responses_type))


@pytest.mark.parametrize("responses_type", ["INT", "DEC", "DATETIME", "date", ""])
def test_schema_rejects_unsupported_response_types(responses_type: str) -> None:
    """Unsupported response types are rejected, including lowercase 'date'."""
    with pytest.raises(ValidationError):
        ExtendedDraft7Validator(json_schema()).validate(_questionnaire(responses_type))


def test_date_is_in_the_response_type_enum() -> None:
    """Guard the enum directly, since home-app depends on it to accept DATE questionnaires."""
    question_properties = json_schema()["properties"]["questions"]["items"]["properties"]

    assert "DATE" in question_properties["responses_type"]["enum"]


@pytest.mark.parametrize(
    "path,value",
    [
        (("name",), "x" * 256),
        (("code",), "x" * 101),
    ],
    ids=["name", "code"],
)
def test_schema_rejects_values_too_long_for_their_column(path: tuple[str, ...], value: str) -> None:
    """Length limits mirror the home-app columns each field is written to."""
    definition = _questionnaire("SING")
    definition[path[0]] = value

    with pytest.raises(ValidationError, match="too long"):
        ExtendedDraft7Validator(json_schema()).validate(definition)


def test_schema_rejects_an_over_long_question_content() -> None:
    """Question content is written to two 1024-character columns."""
    definition = _questionnaire("SING")
    definition["questions"][0]["content"] = "x" * 1025

    with pytest.raises(ValidationError, match="too long"):
        ExtendedDraft7Validator(json_schema()).validate(definition)


def test_schema_rejects_an_over_long_response_value() -> None:
    """Response value is written to a 1000-character column."""
    definition = _questionnaire("SING")
    definition["questions"][0]["responses"][0]["value"] = "x" * 1001

    with pytest.raises(ValidationError, match="too long"):
        ExtendedDraft7Validator(json_schema()).validate(definition)
