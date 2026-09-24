import functools
import json
from collections.abc import Generator, Iterator
from pathlib import Path
from typing import Any, NotRequired

import yaml
from jsonschema import Draft7Validator, validators
from pydantic import ConfigDict, with_config
from typing_extensions import TypedDict

from canvas_sdk.utils.plugins import plugin_context

# Unknown keys are rejected here rather than left to the schema's additionalProperties: pydantic
# strips them before validate_config runs, so a typo like "valu_code" would silently drop the
# branching value it was meant to set. strict must be restated alongside it, because supplying any
# config replaces the one inherited from canvas_sdk.base.Model.
_CONFIG = ConfigDict(extra="forbid", strict=True)


@with_config(_CONFIG)
class Response(TypedDict):
    """A Response of a Questionnaire."""

    name: str
    code: str
    code_description: NotRequired[str]
    value: NotRequired[str]


@with_config(_CONFIG)
class EnabledCondition(TypedDict):
    """A condition controlling when a Question is enabled."""

    question_code: str
    operator: str
    value_code: NotRequired[str | None]
    value_string: NotRequired[str | None]


@with_config(_CONFIG)
class Question(TypedDict):
    """A Question of a Questionnaire."""

    code_system: str
    code: str
    content: str
    responses_code_system: str
    responses_type: str
    responses: list[Response]
    code_description: NotRequired[str]
    display_result_in_social_history_section: NotRequired[bool]
    enabled_behavior: NotRequired[str]
    enabled_conditions: NotRequired[list[EnabledCondition]]


@with_config(_CONFIG)
class QuestionnaireConfig(TypedDict):
    """A Questionnaire configuration."""

    name: str
    form_type: str
    code_system: str
    code: str
    can_originate_in_charting: bool
    questions: list[Question]
    prologue: NotRequired[str]
    display_results_in_social_history_section: NotRequired[bool]


def extend_with_defaults(validator_class: type[Draft7Validator]) -> type[Draft7Validator]:
    """Extend a Draft7Validator with default values for properties."""
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(
        validator: Draft7Validator,
        properties: dict[str, Any],
        instance: dict[str, Any],
        schema: dict[str, Any],
    ) -> Generator[Any, None, None]:
        for property, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(property, subschema["default"])

        yield from validate_properties(
            validator,
            properties,
            instance,
            schema,
        )

    return validators.extend(
        validator_class,
        {"properties": set_defaults},
    )


ExtendedDraft7Validator = extend_with_defaults(Draft7Validator)


@plugin_context
def from_yaml(questionnaire_name: str, **kwargs: Any) -> QuestionnaireConfig | None:
    """Load a Questionnaire configuration from a YAML file.

    Args:
        questionnaire_name (str): The path to the questionnaire file, relative to the plugin package.
            If the path starts with a forward slash ("/"), it will be stripped during resolution.
        kwargs (Any): Additional keyword arguments.

    Returns:
        QuestionnaireConfig: The loaded Questionnaire configuration.

    Raises:
        FileNotFoundError: If the questionnaire file does not exist within the plugin's directory
            or if the resolved path is invalid.
        PermissionError: If the resolved path is outside the plugin's directory.
        ValidationError: If the questionnaire file does not conform to the JSON schema.
    """
    plugin_dir = kwargs["plugin_dir"]
    questionnaire_config_path = Path(plugin_dir / questionnaire_name.lstrip("/")).resolve()

    if not questionnaire_config_path.is_relative_to(plugin_dir):
        raise PermissionError(f"Invalid Questionnaire '{questionnaire_name}'")
    elif not questionnaire_config_path.exists():
        raise FileNotFoundError(f"Questionnaire {questionnaire_name} not found.")

    questionnaire_config = yaml.load(questionnaire_config_path.read_text(), Loader=yaml.SafeLoader)
    ExtendedDraft7Validator(json_schema()).validate(questionnaire_config)

    return questionnaire_config


# TXT and DATE carry one placeholder option, so their codes are exempt from the uniqueness rule.
# home-app's PLACEHOLDER_OPTION_TYPES also lists INT, which the schema's enum cannot produce.
PLACEHOLDER_RESPONSE_TYPES = frozenset({"TXT", "DATE"})


def config_errors(config: QuestionnaireConfig) -> Iterator[str]:
    """Yield a message for every problem in a Questionnaire configuration.

    Validating against the JSON schema also injects the `display_*_in_social_history_section`
    defaults the composer requires, so this pass fills the configuration in as well as checking it.

    Args:
        config: The configuration to check. Mutated in place with schema defaults.

    Yields:
        One message per problem, so the effect can report them all at once.
    """
    schema_errors = [
        f"{'.'.join(str(part) for part in error.absolute_path) or 'questionnaire'}: {error.message}"
        for error in ExtendedDraft7Validator(json_schema()).iter_errors(config)
    ]

    if schema_errors:
        # The checks below index into the configuration, so on one that does not match the schema
        # they would raise KeyError instead of naming the bad field.
        yield from schema_errors
        return

    yield from _coding_errors(config)
    yield from _enabled_condition_errors(config)


def _coding_errors(config: QuestionnaireConfig) -> Iterator[str]:
    """Yield a message for each missing or repeated question or response coding.

    A questionnaire whose codings repeat is rejected outright by the composer, so catching it here
    turns a server-side failure the plugin never sees into an error raised where it was written.
    """
    seen_questions: set[tuple[str, str]] = set()

    for question in config["questions"]:
        if not question["code"]:
            yield (
                f"Question {question['content']!r} has an empty code. Question codes are required "
                "to attach branching logic."
            )
            # The checks below identify the question by the code it is missing.
            continue

        coding = (question["code_system"], question["code"])
        if coding in seen_questions:
            yield (
                f"Question coding {question['code_system']}|{question['code']} is used more than "
                "once. Question codings must be unique within a questionnaire."
            )
        seen_questions.add(coding)

        if question["responses_type"] in PLACEHOLDER_RESPONSE_TYPES:
            continue

        seen_responses: set[str] = set()
        for response in question["responses"]:
            if not response["code"]:
                yield (
                    f"Response {response['name']!r} in question {question['code']} has an empty "
                    "code. Response codes are required to attach branching logic."
                )
                continue

            if response["code"] in seen_responses:
                yield (
                    f"Response code {response['code']} is used more than once in question "
                    f"{question['code']}. Response codes must be unique within a question."
                )
            seen_responses.add(response["code"])


def _enabled_condition_errors(config: QuestionnaireConfig) -> Iterator[str]:
    """Yield a message for each enablement condition that cannot be resolved.

    The composer skips unresolvable conditions silently, so without this a typo produces a
    questionnaire whose branching is quietly missing.

    A condition names its target by bare question code, with no code system, and the composer
    resolves it the same way. Two questions may legitimately share a code under different code
    systems, so a reference to a code used more than once is ambiguous rather than missing.
    """
    responses_by_code: dict[str, list[set[str]]] = {}
    for question in config["questions"]:
        responses_by_code.setdefault(question["code"], []).append(
            {response["code"] for response in question["responses"]}
        )

    for question in config["questions"]:
        for condition in question.get("enabled_conditions", []):
            referenced = condition["question_code"]
            matches = responses_by_code.get(referenced, [])

            if not matches:
                yield (
                    f"Question {question['code']} has an enablement condition on question "
                    f"{referenced}, which is not part of this questionnaire."
                )
                continue

            if len(matches) > 1:
                yield (
                    f"Question {question['code']} has an enablement condition on question "
                    f"{referenced}, but {len(matches)} questions use that code, so the condition "
                    "cannot be resolved. Question codes must be unique where branching is used."
                )
                continue

            value_code = condition.get("value_code")
            if value_code and value_code not in matches[0]:
                yield (
                    f"Question {question['code']} has an enablement condition on response "
                    f"{value_code}, which is not a response of question {referenced}."
                )


@functools.cache
def json_schema() -> dict[str, Any]:
    """Reads the JSON schema for a Questionnaire Config."""
    schema = json.loads(
        (Path(__file__).resolve().parent.parent.parent / "schemas/questionnaire.json").read_text()
    )

    return schema


__exports__ = (
    "Draft7Validator",
    "EnabledCondition",
    "ExtendedDraft7Validator",
    "from_yaml",
    "Question",
    "QuestionnaireConfig",
    "Response",
)
