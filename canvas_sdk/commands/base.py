import datetime
import json
import re
from enum import Enum, EnumType
from types import NoneType, UnionType
from typing import Any, Union, get_args, get_origin
from uuid import UUID

from canvas_sdk.base import Model
from canvas_sdk.commands.constants import Coding
from canvas_sdk.effects import Effect
from canvas_sdk.effects.protocol_card import Recommendation


class _BaseCommand(Model):
    class Meta:
        key = ""
        originate_required_fields = ("note_uuid",)
        edit_required_fields = ("command_uuid",)
        delete_required_fields = ("command_uuid",)
        commit_required_fields = ("command_uuid",)
        enter_in_error_required_fields = ("command_uuid",)

    # A set to track which fields have been modified.
    _dirty_keys: set[str] = set()

    def __init__(self, /, **data: Any) -> None:
        """Initialize the command and mark all provided keys as dirty."""
        super().__init__(**data)

        # Initialize a set to track which fields have been modified.
        self._dirty_keys = set()

        # Explicitly mark all keys provided in the constructor as dirty.
        self._dirty_keys.update(data.keys())

    def __setattr__(self, name: str, value: Any) -> None:
        """Set an attribute and mark it as dirty unless excluded."""
        if not name.startswith("_") and name not in (
            "note_uuid",
            "command_uuid",
        ):
            self._dirty_keys.add(name)
        super().__setattr__(name, value)

    def is_dirty(self, key: str) -> bool:
        """Returns True if the given property has been modified (i.e. marked as dirty), False otherwise."""
        return key in self._dirty_keys

    def constantized_key(self) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", self.Meta.key).upper()

    note_uuid: str | None = None
    command_uuid: str | None = None

    def _get_effect_method_required_fields(self, method: str) -> tuple:
        base_required_fields: tuple = getattr(_BaseCommand.Meta, f"{method}_required_fields", ())
        command_required_fields = super()._get_effect_method_required_fields(method)
        return tuple(set(base_required_fields) | set(command_required_fields))

    @property
    def values(self) -> dict:
        """Return a dictionary of modified attributes with type-specific transformations."""
        result = {}
        for key in self._dirty_keys:
            value = getattr(self, key)
            if isinstance(value, Enum):
                # If it's an enum, use its .value.
                result[key] = value.value if value else None
            elif isinstance(value, datetime.date | datetime.datetime):
                # If it's a date/datetime, use isoformat().
                result[key] = value.isoformat() if value else None
            elif isinstance(value, UUID):
                # If it's a UUID, use its string representation.
                result[key] = str(value) if value else None
            else:
                # For strings, integers, or any other type, return as is.
                result[key] = value
        return result

    @property
    def coding_filter(self) -> Coding | None:
        """The coding filter used for command insertion in protocol cards."""
        return None

    @classmethod
    def _get_property_choices(cls, name: str, schema: dict) -> list[dict] | None:
        definition = schema.get("properties", {}).get(name, {})
        if not (choice_ref := next((a.get("$ref") for a in definition.get("anyOf", [])), None)):
            return None
        choice_key = choice_ref.split("#/$defs/")[-1]
        return schema.get("$defs", {}).get(choice_key, {}).get("enum")

    @classmethod
    def _get_property_type(cls, name: str) -> type | None:
        annotation = cls.model_fields[name].annotation
        origin = get_origin(annotation)

        # Handle Union types
        if origin is UnionType or origin is Union:
            annotation_args = get_args(annotation)
            # Filter out NoneType and take the first valid type
            annotation = next(
                (arg for arg in annotation_args if arg is not NoneType), annotation_args[0]
            )

        if type(annotation) is EnumType:
            return str

        return annotation

    @classmethod
    def command_schema(cls) -> dict:
        """The schema of the command."""
        base_properties = {"note_uuid", "command_uuid"}
        schema = cls.model_json_schema()
        required_fields: tuple = getattr(cls.Meta, "commit_required_fields", ())
        return {
            definition.get("commands_api_name", name): {
                "required": name in required_fields,
                "type": cls._get_property_type(name),
                "choices": cls._get_property_choices(name, schema),
            }
            for name, definition in schema["properties"].items()
            if name not in base_properties
        }

    def originate(self, line_number: int = -1) -> Effect:
        """Originate a new command in the note body."""
        self._validate_before_effect("originate")
        return Effect(
            type=f"ORIGINATE_{self.constantized_key()}_COMMAND",
            payload=json.dumps(
                {
                    "command": self.command_uuid,
                    "note": self.note_uuid,
                    "data": self.values,
                    "line_number": line_number,
                }
            ),
        )

    def edit(self) -> Effect:
        """Edit the command."""
        self._validate_before_effect("edit")
        return Effect(
            type=f"EDIT_{self.constantized_key()}_COMMAND",
            payload=json.dumps(
                {
                    "command": self.command_uuid,
                    "data": self.values,
                }
            ),
        )

    def delete(self) -> Effect:
        """Delete the command."""
        self._validate_before_effect("delete")
        return Effect(
            type=f"DELETE_{self.constantized_key()}_COMMAND",
            payload=json.dumps({"command": self.command_uuid}),
        )

    def commit(self) -> Effect:
        """Commit the command."""
        self._validate_before_effect("commit")
        return Effect(
            type=f"COMMIT_{self.constantized_key()}_COMMAND",
            payload=json.dumps({"command": self.command_uuid}),
        )

    def enter_in_error(self) -> Effect:
        """Mark the command as entered-in-error."""
        self._validate_before_effect("enter_in_error")
        return Effect(
            type=f"ENTER_IN_ERROR_{self.constantized_key()}_COMMAND",
            payload=json.dumps({"command": self.command_uuid}),
        )

    def recommend(self, title: str = "", button: str | None = None) -> Recommendation:
        """Returns a command recommendation to be inserted via Protocol Card."""
        if button is None:
            button = self.constantized_key().lower().replace("_", " ")
        command = self.Meta.key.lower()
        return Recommendation(title=title, button=button, command=command, context=self.values)
