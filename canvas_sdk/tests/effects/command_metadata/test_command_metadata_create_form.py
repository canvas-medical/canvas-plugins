import json

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.command_metadata import (
    CommandMetadataCreateFormEffect,
    FormField,
    InputType,
)


def test_effect_has_correct_type() -> None:
    """The effect applies with type COMMAND__FORM__CREATE_ADDITIONAL_FIELDS."""
    effect = CommandMetadataCreateFormEffect(
        command_uuid="command-uuid",
        form_fields=[FormField(key="k", label="K")],
    )
    applied = effect.apply()

    assert applied.type == EffectType.COMMAND__FORM__CREATE_ADDITIONAL_FIELDS


def test_effect_payload_contains_command_uuid_and_form() -> None:
    """The serialized payload includes the command uuid alongside the form fields."""
    field = FormField(
        key="reason",
        label="Reason",
        type=InputType.SELECT,
        options=["A", "B"],
        required=True,
    )
    effect = CommandMetadataCreateFormEffect(
        command_uuid="command-uuid",
        form_fields=[field],
    )
    applied = effect.apply()

    payload = json.loads(applied.payload)
    assert payload == {
        "data": {
            "command": "command-uuid",
            "form": [
                {
                    "key": "reason",
                    "label": "Reason",
                    "required": True,
                    "editable": True,
                    "type": "select",
                    "options": ["A", "B"],
                    "value": None,
                }
            ],
        }
    }


def test_effect_payload_supports_multiple_fields() -> None:
    """Multiple form fields serialize in order with their declared types."""
    effect = CommandMetadataCreateFormEffect(
        command_uuid="command-uuid",
        form_fields=[
            FormField(key="a", label="A"),
            FormField(key="b", label="B", type=InputType.DATE),
        ],
    )
    applied = effect.apply()
    payload = json.loads(applied.payload)

    assert payload["data"]["command"] == "command-uuid"
    assert [f["key"] for f in payload["data"]["form"]] == ["a", "b"]
    assert payload["data"]["form"][1]["type"] == "date"


def test_effect_rejects_options_on_non_select_field() -> None:
    """`options` is only valid on SELECT fields; other types raise a validation error."""
    effect = CommandMetadataCreateFormEffect(
        command_uuid="command-uuid",
        form_fields=[
            FormField(
                key="name",
                label="Name",
                type=InputType.TEXT,
                options=["not", "allowed"],
            )
        ],
    )

    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    errors = exc_info.value.errors()
    assert any("options attribute is only used" in e["msg"] for e in errors)


def test_effect_requires_command_uuid() -> None:
    """`command_uuid` is required to construct the effect."""
    with pytest.raises(ValidationError):
        CommandMetadataCreateFormEffect(form_fields=[FormField(key="k", label="K")])  # type: ignore[call-arg]


def test_effect_accepts_empty_form_fields() -> None:
    """An effect with no form fields applies and serializes to an empty form list."""
    effect = CommandMetadataCreateFormEffect(command_uuid="command-uuid", form_fields=[])
    applied = effect.apply()
    payload = json.loads(applied.payload)

    assert payload == {"data": {"command": "command-uuid", "form": []}}
