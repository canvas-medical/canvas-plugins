import json
from pathlib import Path
from types import FunctionType
from typing import cast

import pytest
import yaml

from canvas_sdk.effects import Effect
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.questionnaires import questionnaire_from_yaml, utils
from canvas_sdk.questionnaires.utils import ExtendedDraft7Validator
from plugin_runner.plugin_runner import LOADED_PLUGINS
from settings import PLUGIN_DIRECTORY


@pytest.mark.parametrize("install_test_plugin", ["test_load_questionnaire"], indirect=True)
def test_from_yaml_valid_questionnaire(install_test_plugin: Path, load_test_plugins: None) -> None:
    """Test that the from_yaml function loads a valid questionnaire."""
    plugin = LOADED_PLUGINS[
        "test_load_questionnaire:test_load_questionnaire.handlers.my_handler:ValidQuestionnaire"
    ]
    result: list[Effect] = plugin["class"](Event(EventRequest(type=EventType.UNKNOWN))).compute()

    assert (
        yaml.load(
            (
                Path(PLUGIN_DIRECTORY)
                / "test_load_questionnaire/questionnaires/example_questionnaire.yml"
            )
            .resolve()
            .read_text(),
            Loader=yaml.SafeLoader,
        ).items()
        <= json.loads(result[0].payload).items()
    )


@pytest.mark.parametrize("install_test_plugin", ["test_load_questionnaire"], indirect=True)
def test_from_yaml_invalid_questionnaire(
    install_test_plugin: Path, load_test_plugins: None
) -> None:
    """Test that the from_yaml function raises an error for invalid questionnaires."""
    plugin = LOADED_PLUGINS[
        "test_load_questionnaire:test_load_questionnaire.handlers.my_handler:InvalidQuestionnaire"
    ]
    with pytest.raises(FileNotFoundError):
        plugin["class"](Event(EventRequest(type=EventType.UNKNOWN))).compute()


@pytest.mark.parametrize("install_test_plugin", ["test_load_questionnaire"], indirect=True)
def test_from_yaml_forbidden_questionnaire(
    install_test_plugin: Path, load_test_plugins: None
) -> None:
    """Test that the from_yaml function raises an error for a questionnaire outside plugin package."""
    plugin = LOADED_PLUGINS[
        "test_load_questionnaire:test_load_questionnaire.handlers.my_handler:ForbiddenQuestionnaire"
    ]
    with pytest.raises(PermissionError):
        plugin["class"](Event(EventRequest(type=EventType.UNKNOWN))).compute()


def test_from_yaml_non_plugin_caller() -> None:
    """Test that the from_yaml function returns None when called outside a plugin."""
    with pytest.raises(RuntimeError):
        questionnaire_from_yaml("questionnaires/example_questionnaire.yml")


@pytest.mark.parametrize("install_test_plugin", ["test_load_questionnaire"], indirect=True)
def test_from_yaml_sets_default_values(install_test_plugin: Path) -> None:
    """Test that the from_yaml function sets default values for properties."""
    globals()["__is_plugin__"] = True
    globals()["__name__"] = "test_load_questionnaire"

    definition = questionnaire_from_yaml("questionnaires/example_questionnaire.yml")

    assert definition is not None
    assert definition["display_results_in_social_history_section"] is False


def test_from_yaml_requires_plugin_dir() -> None:
    """from_yaml raises ValueError when plugin_dir is missing.

    plugin_context always injects plugin_dir, so the defensive guard is exercised
    by calling the undecorated function directly (the wrapper closes over it).
    """
    wrapper = cast(FunctionType, utils.from_yaml)
    assert wrapper.__closure__ is not None
    raw_from_yaml = wrapper.__closure__[wrapper.__code__.co_freevars.index("func")].cell_contents

    with pytest.raises(ValueError, match="plugin_dir is required"):
        raw_from_yaml("questionnaires/example_questionnaire.yml")


def test_set_items_defaults_ignores_non_object_item_schema() -> None:
    """Array items whose schema has no 'properties' are validated without changes."""
    instance = ["a", "b"]

    ExtendedDraft7Validator({"type": "array", "items": {"type": "string"}}).validate(instance)

    assert instance == ["a", "b"]


def test_set_items_defaults_skips_non_dict_items() -> None:
    """Non-dict array items are skipped by the default-injection pass."""
    instance = ["untouched"]

    ExtendedDraft7Validator(
        {"type": "array", "items": {"properties": {"foo": {"type": "string"}}}}
    ).validate(instance)

    assert instance == ["untouched"]
