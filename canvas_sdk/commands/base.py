import json
import re
from enum import EnumType
from types import NoneType, UnionType
from typing import Any, Union, get_args, get_origin

from django.core.exceptions import ImproperlyConfigured

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.commands.constants import Coding
from canvas_sdk.effects import Effect
from canvas_sdk.effects.protocol_card import Recommendation


class _BaseCommand(TrackableFieldsModel):
    """Base class for Canvas SDK commands.
    
    Commands represent clinical actions that can be originated, edited, committed,
    and deleted within a note. This base class provides the core functionality
    for all command types.
    
    Chaining Methods with User-Set UUIDs:
        A common pattern is to originate and commit a command in a single plugin action.
        Since originate() operates asynchronously and doesn't return the command_uuid,
        you must set the command_uuid manually to enable chaining.
        
        Example:
            from uuid import uuid4
            from canvas_sdk.commands import DiagnoseCommand
            
            # Create the command
            command = DiagnoseCommand(
                note_uuid="note-123",
                icd10_code="E11.9"
            )
            
            # Set UUID manually for chaining
            command.command_uuid = str(uuid4())
            
            # Chain originate and commit
            effects = [
                command.originate(),
                command.commit()
            ]
            
        This pattern is essential when you need to both create and finalize a command
        within the same plugin action, such as in API endpoints that should complete
        the full command lifecycle.
    """
    class Meta:
        key = ""
        originate_required_fields = ("note_uuid",)
        edit_required_fields = ("command_uuid",)
        delete_required_fields = ("command_uuid",)
        commit_required_fields = ("command_uuid",)
        enter_in_error_required_fields = ("command_uuid",)

    _dirty_excluded_keys = [
        "note_uuid",
        "command_uuid",
    ]

    def __init__(self, /, **data: Any) -> None:
        """Initialize the command and mark all provided keys as dirty."""
        super().__init__(**data)

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Validate that the command has a key and required fields."""
        if not hasattr(cls.Meta, "key") or not cls.Meta.key:
            raise ImproperlyConfigured(f"Command {cls.__name__!r} must specify Meta.key.")

        if hasattr(cls.Meta, "commit_required_fields"):
            command_fields = set(cls.__pydantic_fields__.keys() | cls.__annotations__.keys())
            for field in cls.Meta.commit_required_fields:
                if field not in command_fields:
                    raise ImproperlyConfigured(f"Command {cls.__name__!r} must specify {field}.")

    @classmethod
    def constantized_key(cls) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.Meta.key).upper()

    note_uuid: str | None = None
    command_uuid: str | None = None

    def _get_effect_method_required_fields(self, method: str) -> tuple:
        base_required_fields: tuple = getattr(_BaseCommand.Meta, f"{method}_required_fields", ())
        command_required_fields = super()._get_effect_method_required_fields(method)
        return tuple(set(base_required_fields) | set(command_required_fields))

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
        """Originate a new command in the note body.
        
        Args:
            line_number: The line number where the command should be inserted in the note. 
                        Defaults to -1 (append to end).
                        
        Returns:
            Effect: An originate effect that can be applied to create the command.
            
        Note:
            This method requires note_uuid to be set on the command instance.
            
        Chaining with commit():
            To originate and commit a command in a single plugin action, you must set 
            the command_uuid manually before calling both methods, since originate() 
            operates asynchronously and doesn't return the generated command_uuid.
            
            Example:
                from uuid import uuid4
                from canvas_sdk.commands import DiagnoseCommand
                
                # Create the command with required data
                diagnose_command = DiagnoseCommand(
                    note_uuid="your-note-uuid",
                    icd10_code="E11.9"
                )
                
                # Set a UUID manually to enable chaining
                diagnose_command.command_uuid = str(uuid4())
                
                # Now you can chain originate and commit effects
                effects = [
                    diagnose_command.originate(),
                    diagnose_command.commit()
                ]
        """
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
        """Commit the command.
        
        Returns:
            Effect: A commit effect that finalizes the command.
            
        Note:
            This method requires command_uuid to be set on the command instance.
            
        Chaining with originate():
            When chaining with originate() in a single plugin action, you must set
            the command_uuid manually before calling both methods. See the originate()
            method documentation for a complete example.
        """
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


__exports__ = ("_BaseCommand",)
