import functools
import json
from collections.abc import Generator
from pathlib import Path
from typing import Any, TypedDict

import yaml
from jsonschema import Draft7Validator, validators

from canvas_sdk.utils.plugins import plugin_only


class Response(TypedDict):
    """A Response of a Questionnaire."""

    name: str
    code: str
    code_description: str
    value: str


class Question(TypedDict):
    """A Question of a Questionnaire."""

    code_system: str
    code: str
    code_description: str
    content: str
    responses_code_system: str
    responses_type: str
    display_result_in_social_history_section: bool
    responses: list[Response]


class QuestionnaireConfig(TypedDict):
    """A Questionnaire configuration."""

    name: str
    form_type: str
    code_system: str
    code: str
    can_originate_in_charting: bool
    prologue: str
    display_results_in_social_history_section: bool
    questions: list[Question]


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


@plugin_only
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


@functools.cache
def json_schema() -> dict[str, Any]:
    """Reads the JSON schema for a Questionnaire Config."""
    schema = json.loads(
        (Path(__file__).resolve().parent.parent.parent / "schemas/questionnaire.json").read_text()
    )

    return schema


__exports__ = (
    "Draft7Validator",
    "ExtendedDraft7Validator",
    "from_yaml",
)
