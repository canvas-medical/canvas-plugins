"""Tests for the CreateQuestionnaire effect."""

import json
from copy import deepcopy
from typing import Any, cast

import pytest
from jsonschema.exceptions import ValidationError as SchemaValidationError
from pydantic import ValidationError

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.questionnaire import CreateQuestionnaire
from canvas_sdk.questionnaires.utils import QuestionnaireConfig


@pytest.fixture
def config() -> QuestionnaireConfig:
    """A minimal valid questionnaire with one single-select question."""
    return cast(
        QuestionnaireConfig,
        {
            "name": "Test questionnaire",
            "form_type": "QUES",
            "code_system": "INTERNAL",
            "code": "123",
            "can_originate_in_charting": True,
            "questions": [
                {
                    "content": "This is a single select question",
                    "code_system": "INTERNAL",
                    "code": "Q1",
                    "responses_code_system": "INTERNAL",
                    "responses_type": "SING",
                    "responses": [
                        {"name": "Option 1", "code": "Q1A1"},
                        {"name": "Option 2", "code": "Q1A2"},
                    ],
                }
            ],
        },
    )


def payload_of(config: QuestionnaireConfig) -> dict[str, Any]:
    """Apply the effect and return the questionnaire from inside the payload envelope."""
    effect = CreateQuestionnaire(questionnaire=config).apply()

    assert isinstance(effect, Effect)
    assert effect.type == EffectType.CREATE_QUESTIONNAIRE

    return cast(dict[str, Any], json.loads(effect.payload)["data"]["questionnaire"])


def test_payload_uses_the_data_envelope(config: QuestionnaireConfig) -> None:
    """The effect keeps the `data` wrapper every other effect uses."""
    payload = json.loads(CreateQuestionnaire(questionnaire=config).apply().payload)

    assert list(payload) == ["data"]
    assert list(payload["data"]) == ["questionnaire"]


def test_schema_defaults_are_injected(config: QuestionnaireConfig) -> None:
    """Both social-history flags default to False.

    The composer passes these straight into NOT NULL boolean columns, and a Django field default
    does not apply to an explicit None, so a missing key would fail the insert.
    """
    questionnaire = payload_of(config)

    assert questionnaire["display_results_in_social_history_section"] is False
    assert questionnaire["questions"][0]["display_result_in_social_history_section"] is False


def test_branching_logic_survives(config: QuestionnaireConfig) -> None:
    """Enablement conditions reach the payload intact."""
    config["questions"].append(
        {
            "content": "Only when Q1 is Option 1",
            "code_system": "INTERNAL",
            "code": "Q2",
            "responses_code_system": "INTERNAL",
            "responses_type": "TXT",
            "responses": [{"name": "TXT", "code": "Q2A1"}],
            "enabled_behavior": "all",
            "enabled_conditions": [{"question_code": "Q1", "operator": "=", "value_code": "Q1A1"}],
        }
    )

    questionnaire = payload_of(config)

    assert questionnaire["questions"][1]["enabled_behavior"] == "all"
    assert questionnaire["questions"][1]["enabled_conditions"] == [
        {"question_code": "Q1", "operator": "=", "value_code": "Q1A1"}
    ]


def test_questionnaire_is_required() -> None:
    """Applying without a configuration is rejected."""
    with pytest.raises(ValidationError):
        CreateQuestionnaire().apply()  # type: ignore[call-arg]


def test_missing_required_key_is_rejected(config: QuestionnaireConfig) -> None:
    """A configuration missing a required key is rejected at construction."""
    del config["code"]  # type: ignore[misc]

    with pytest.raises(ValidationError):
        CreateQuestionnaire(questionnaire=config)


def test_invalid_enum_value_is_rejected(config: QuestionnaireConfig) -> None:
    """form_type is constrained by the schema's enum when the effect is applied."""
    config["form_type"] = "BOGUS"

    with pytest.raises(SchemaValidationError, match="is not one of"):
        CreateQuestionnaire(questionnaire=config).apply()


def test_duplicate_question_coding_is_rejected(config: QuestionnaireConfig) -> None:
    """Repeated question codings are rejected, naming the coding."""
    config["questions"].append(deepcopy(config["questions"][0]))

    with pytest.raises(SchemaValidationError, match=r"INTERNAL\|Q1 is used more than once"):
        CreateQuestionnaire(questionnaire=config).apply()


def test_duplicate_response_code_is_rejected(config: QuestionnaireConfig) -> None:
    """Repeated response codes within a question are rejected, naming the code."""
    config["questions"][0]["responses"].append({"name": "Option 3", "code": "Q1A1"})

    with pytest.raises(SchemaValidationError, match="Response code Q1A1 is used more than once"):
        CreateQuestionnaire(questionnaire=config).apply()


def test_duplicate_response_code_allowed_for_placeholder_types(
    config: QuestionnaireConfig,
) -> None:
    """Free-text and date questions carry placeholder options, so their codes may repeat.

    This mirrors ResponseOptionSet.PLACEHOLDER_OPTION_TYPES in home-app, which the composer's own
    uniqueness check skips.
    """
    config["questions"][0]["responses_type"] = "TXT"
    config["questions"][0]["responses"] = [
        {"name": "TXT", "code": "SAME"},
        {"name": "TXT", "code": "SAME"},
    ]

    assert payload_of(config)["questions"][0]["responses_type"] == "TXT"


def test_condition_on_unknown_question_is_rejected(config: QuestionnaireConfig) -> None:
    """A condition referencing a question outside this questionnaire is rejected.

    The composer skips unresolvable conditions silently, which would leave the branching missing
    with no error anywhere.
    """
    config["questions"][0]["enabled_conditions"] = [
        {"question_code": "NOT_A_QUESTION", "operator": "="}
    ]

    with pytest.raises(SchemaValidationError, match="NOT_A_QUESTION"):
        CreateQuestionnaire(questionnaire=config).apply()


def test_condition_on_unknown_response_is_rejected(config: QuestionnaireConfig) -> None:
    """A condition referencing a response the target question does not have is rejected."""
    config["questions"][0]["enabled_conditions"] = [
        {"question_code": "Q1", "operator": "=", "value_code": "NOT_A_RESPONSE"}
    ]

    with pytest.raises(SchemaValidationError, match="NOT_A_RESPONSE"):
        CreateQuestionnaire(questionnaire=config).apply()


def test_condition_on_an_ambiguous_question_code_is_rejected(
    config: QuestionnaireConfig,
) -> None:
    """A condition naming a code shared by two questions cannot be resolved, so it is rejected.

    Codings are unique on (code_system, code), so two questions may legitimately share a bare
    code. A condition names only the bare code, and so does the composer when it resolves one,
    which would otherwise bind the condition to whichever question came last.
    """
    twin = deepcopy(config["questions"][0])
    twin["code_system"] = "LOINC"
    config["questions"].append(twin)
    config["questions"][1]["enabled_conditions"] = [{"question_code": "Q1", "operator": "="}]

    with pytest.raises(SchemaValidationError, match="2 questions use that code"):
        CreateQuestionnaire(questionnaire=config).apply()


def test_a_string_in_a_bool_field_is_rejected(config: QuestionnaireConfig) -> None:
    """A bool field takes a bool, not a string pydantic would otherwise coerce.

    The TypedDicts carry no config of their own, so they inherit strict from
    canvas_sdk.base.Model. Declaring any config on them would silently replace it, and "yes"
    would become True.
    """
    config["can_originate_in_charting"] = "yes"  # type: ignore[typeddict-item]

    with pytest.raises(ValidationError):
        CreateQuestionnaire(questionnaire=config)


@pytest.mark.parametrize(
    "mutate,field",
    [
        (lambda c: c.update(name="x" * 256), "name"),
        (lambda c: c.update(code="x" * 101), "code"),
        (lambda c: c["questions"][0].update(content="x" * 1025), "content"),
        (lambda c: c["questions"][0].update(code="x" * 101), "code"),
        (lambda c: c["questions"][0]["responses"][0].update(name="x" * 1025), "name"),
        (lambda c: c["questions"][0]["responses"][0].update(value="x" * 1001), "value"),
    ],
    ids=[
        "q_name",
        "q_code",
        "question_content",
        "question_code",
        "response_name",
        "response_value",
    ],
)
def test_values_too_long_for_their_column_are_rejected(
    config: QuestionnaireConfig, mutate: Any, field: str
) -> None:
    """Length limits are enforced when the effect is applied, not as a database error.

    Several of these columns are written through bulk_create, which skips full_clean, so without
    the schema's maxLength they surface as a raw Postgres DataError inside the interpreter.
    """
    mutate(config)

    with pytest.raises(SchemaValidationError, match="too long"):
        CreateQuestionnaire(questionnaire=config).apply()


def test_empty_question_code_is_rejected(config: QuestionnaireConfig) -> None:
    """An empty question code is rejected, since branching resolves by code.

    The schema requires the key but sets no minLength, and the composer skips any falsy code,
    which drops every condition naming it without an error.
    """
    config["questions"][0]["code"] = ""

    with pytest.raises(SchemaValidationError, match="empty code"):
        CreateQuestionnaire(questionnaire=config).apply()


def test_empty_response_code_is_rejected(config: QuestionnaireConfig) -> None:
    """An empty response code is rejected for the same reason."""
    config["questions"][0]["responses"][0]["code"] = ""

    with pytest.raises(SchemaValidationError, match="empty code"):
        CreateQuestionnaire(questionnaire=config).apply()


@pytest.mark.parametrize(
    "mutate,expected_path",
    [
        (lambda c: c.update(prolog="typo"), "prolog"),
        (lambda c: c["questions"][0].update(contnet="typo"), "contnet"),
        (lambda c: c["questions"][0]["responses"][0].update(cod="typo"), "cod"),
        (
            lambda c: c["questions"][0].update(
                enabled_conditions=[{"question_code": "Q1", "operator": "=", "valu_code": "Q1A1"}]
            ),
            "valu_code",
        ),
    ],
    ids=["questionnaire", "question", "response", "enabled_condition"],
)
def test_unknown_key_is_rejected(
    config: QuestionnaireConfig, mutate: Any, expected_path: str
) -> None:
    """A mistyped key is rejected rather than silently dropped.

    Pydantic strips unknown keys before the JSON schema runs, so additionalProperties never fires
    on this path. The enabled_condition case is why it matters: a typo there drops the value the
    branch compares against, producing the questionnaire-with-missing-branching that
    _validate_enabled_conditions exists to prevent.
    """
    mutate(config)

    with pytest.raises(ValidationError, match=expected_path):
        CreateQuestionnaire(questionnaire=config)


def test_a_name_leaves_room_for_the_archive_suffix(config: QuestionnaireConfig) -> None:
    """Names stop short of the column width so a superseded questionnaire can be renamed.

    Questionnaire.save() calls full_clean(), and _archive_questionnaire renames the previous row
    to "<name> (v<id>)" in the same 255-character column, so a name at the full width would
    create once and then fail every supersede.
    """
    config["name"] = "x" * 242

    with pytest.raises(SchemaValidationError, match="too long"):
        CreateQuestionnaire(questionnaire=config).apply()


def test_an_over_long_condition_value_string_is_rejected(config: QuestionnaireConfig) -> None:
    """value_string is written to answer_value, a 255-character column."""
    config["questions"].append(
        {
            "content": "Follow up",
            "code_system": "INTERNAL",
            "code": "Q2",
            "responses_code_system": "INTERNAL",
            "responses_type": "TXT",
            "responses": [{"name": "TXT", "code": "Q2A1"}],
            "enabled_conditions": [
                {"question_code": "Q1", "operator": "=", "value_string": "x" * 256}
            ],
        }
    )

    with pytest.raises(SchemaValidationError, match="too long"):
        CreateQuestionnaire(questionnaire=config).apply()
