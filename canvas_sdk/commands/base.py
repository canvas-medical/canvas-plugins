import json
import re
from enum import EnumType
from typing import Any, get_args

from pydantic import BaseModel, ConfigDict, ValidationError, model_validator
from typing_extensions import Self

from canvas_sdk.effects import Effect, EffectType


class _BaseCommand(BaseModel):
    model_config = ConfigDict(strict=True, revalidate_instances="always")

    class Meta:
        key = ""

    def constantized_key(self) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", self.Meta.key).upper()

    note_uuid: str | None = None
    command_uuid: str | None = None
    user_id: int

    def _verify_has_note_uuid_or_command_id(self) -> Self:
        if not self.note_uuid and not self.command_uuid:
            raise ValueError("Command should have either a note_uuid or a command_uuid.")
        return self

    def validate_all_fields(self) -> None:
        self.model_validate(self)
        self._verify_has_note_uuid_or_command_id()

    @property
    def values(self) -> dict:
        return {}

    @classmethod
    def _get_property_choices(cls, name: str, schema: dict) -> list[dict] | None:
        definition = schema.get("properties", {}).get(name, {})
        if not (choice_ref := next((a.get("$ref") for a in definition.get("anyOf", [])), None)):
            return None
        choice_key = choice_ref.split("#/$defs/")[-1]
        return schema.get("$defs", {}).get(choice_key, {}).get("enum")

    @classmethod
    def _get_property_type(cls, name: str) -> type:
        annotation = cls.model_fields[name].annotation
        if annotation_args := get_args(annotation):
            # if its a union, take the first one (which is not None)
            annotation = annotation_args[0]

        if type(annotation) is EnumType:
            return str

        return annotation

    @classmethod
    def command_schema(cls) -> dict:
        """The schema of the command."""
        base_properties = {"note_uuid", "command_uuid", "user_id"}
        schema = cls.model_json_schema()
        return {
            definition.get("commands_api_name", name): {
                "required": name in schema["required"],
                "type": cls._get_property_type(name),
                "choices": cls._get_property_choices(name, schema),
            }
            for name, definition in schema["properties"].items()
            if name not in base_properties
        }

    def originate(self) -> Effect:
        """Originate a new command in the note body."""
        self.validate_all_fields()
        if not self.note_uuid:
            raise AttributeError("Note id is required to originate a command")
        return Effect(
            type=EffectType.Value(f"ORIGINATE_{self.constantized_key()}_COMMAND"),
            payload=json.dumps(
                {
                    "user": self.user_id,
                    "note": self.note_uuid,
                    "data": self.values,
                }
            ),
        )

    def edit(self) -> Effect:
        """Edit the command."""
        self.validate_all_fields()
        if not self.command_uuid:
            raise AttributeError("Command uuid is required to edit a command")
        return {
            "type": f"EDIT_{self.constantized_key()}_COMMAND",
            "payload": {
                "user": self.user_id,
                "command": self.command_uuid,
                "data": self.values,
            },
        }

    def delete(self) -> Effect:
        """Delete the command."""
        self.validate_all_fields()
        if not self.command_uuid:
            raise AttributeError("Command uuid is required to delete a command")
        return {
            "type": f"DELETE_{self.constantized_key()}_COMMAND",
            "payload": {"command": self.command_uuid, "user": self.user_id},
        }

    def commit(self) -> Effect:
        """Commit the command."""
        self.validate_all_fields()
        if not self.command_uuid:
            raise AttributeError("Command uuid is required to commit a command")
        return {
            "type": f"COMMIT_{self.constantized_key()}_COMMAND",
            "payload": {"command": self.command_uuid, "user": self.user_id},
        }

    def enter_in_error(self) -> Effect:
        """Mark the command as entered-in-error."""
        self.validate_all_fields()
        if not self.command_uuid:
            raise AttributeError("Command uuid is required to enter in error a command")
        return {
            "type": f"ENTER_IN_ERROR_{self.constantized_key()}_COMMAND",
            "payload": {"command": self.command_uuid, "user": self.user_id},
        }
