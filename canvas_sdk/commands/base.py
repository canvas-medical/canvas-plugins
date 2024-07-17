import json
import re
from enum import EnumType
from typing import Literal, get_args

from canvas_sdk.base import Model
from canvas_sdk.effects import Effect, EffectType


class _BaseCommand(Model):
    class Meta:
        key = ""
        originate_required_fields = (
            "user_id",
            "note_uuid",
        )
        edit_required_fields = (
            "user_id",
            "command_uuid",
        )
        delete_required_fields = (
            "user_id",
            "command_uuid",
        )
        commit_required_fields = (
            "user_id",
            "command_uuid",
        )
        enter_in_error_required_fields = (
            "user_id",
            "command_uuid",
        )

    def constantized_key(self) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", self.Meta.key).upper()

    note_uuid: str | None = None
    command_uuid: str | None = None
    user_id: int | None = None

    def _get_effect_method_required_fields(
        self, method: Literal["originate", "edit", "delete", "commit", "enter_in_error"]
    ) -> tuple[str]:
        base_required_fields: tuple = getattr(
            _BaseCommand.Meta, f"{method}_required_fields", tuple()
        )
        command_required_fields = super()._get_effect_method_required_fields(method)
        return tuple(set(base_required_fields) | set(command_required_fields))

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
        required_fields: tuple = getattr(cls.Meta, "originate_required_fields", tuple())
        return {
            definition.get("commands_api_name", name): {
                "required": name in required_fields,
                "type": cls._get_property_type(name),
                "choices": cls._get_property_choices(name, schema),
            }
            for name, definition in schema["properties"].items()
            if name not in base_properties
        }

    def originate(self) -> Effect:
        """Originate a new command in the note body."""
        self._validate_before_effect("originate")
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
        self._validate_before_effect("edit")
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
        self._validate_before_effect("delete")
        return {
            "type": f"DELETE_{self.constantized_key()}_COMMAND",
            "payload": {"command": self.command_uuid, "user": self.user_id},
        }

    def commit(self) -> Effect:
        """Commit the command."""
        self._validate_before_effect("commit")
        return {
            "type": f"COMMIT_{self.constantized_key()}_COMMAND",
            "payload": {"command": self.command_uuid, "user": self.user_id},
        }

    def enter_in_error(self) -> Effect:
        """Mark the command as entered-in-error."""
        self._validate_before_effect("enter_in_error")
        return {
            "type": f"ENTER_IN_ERROR_{self.constantized_key()}_COMMAND",
            "payload": {"command": self.command_uuid, "user": self.user_id},
        }
