import json
import re
from enum import EnumType
from typing import Any, Literal, get_args

from pydantic import BaseModel, ConfigDict
from pydantic_core import InitErrorDetails, PydanticCustomError, ValidationError

from canvas_sdk.effects import Effect, EffectType


class _BaseCommand(BaseModel):
    model_config = ConfigDict(strict=True, revalidate_instances="always", validate_assignment=True)

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
        command_required_fields: tuple = getattr(self.Meta, f"{method}_required_fields", tuple())
        return tuple(set(base_required_fields) | set(command_required_fields))

    def _create_error_detail(self, type: str, message: str, value: Any) -> InitErrorDetails:
        return InitErrorDetails({"type": PydanticCustomError(type, message), "input": value})

    def _get_error_details(
        self, method: Literal["originate", "edit", "delete", "commit", "enter_in_error"]
    ) -> list[InitErrorDetails]:
        required_fields = self._get_effect_method_required_fields(method)
        return [
            self._create_error_detail(
                "missing", f"Field '{field}' is required to {method.replace('_', ' ')} a command", v
            )
            for field in required_fields
            if (v := getattr(self, field)) is None
        ]

    def _validate_before_effect(
        self, method: Literal["originate", "edit", "delete", "commit", "enter_in_error"]
    ) -> None:
        self.model_validate(self)
        if error_details := self._get_error_details(method):
            raise ValidationError.from_exception_data(self.__class__.__name__, error_details)

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
