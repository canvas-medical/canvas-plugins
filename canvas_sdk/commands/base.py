from pydantic import BaseModel, ConfigDict, model_validator
from typing_extensions import Self

from plugin_runner.generated.messages.effects_pb2 import Effect


class _BaseCommand(BaseModel):
    model_config = ConfigDict(strict=True, validate_assignment=True)

    class Meta:
        key = ""

    # todo: update int to str as we should use external identifiers
    note_id: int | None = None
    command_uuid: str | None = None
    user_id: int

    @model_validator(mode="after")
    def _verify_has_note_id_or_command_id(self) -> Self:
        if not self.note_id and not self.command_uuid:
            raise ValueError("Command should have either a note_id or a command_uuid.")
        return self

    @property
    def values(self) -> dict:
        return {}

    def originate(self) -> Effect:
        """Originate a new command in the note body."""
        if not self.note_id:
            raise AttributeError("Note id is required to originate a command")
        return {
            "type": f"ADD_{self.Meta.key.upper()}_COMMAND",
            "payload": {
                "user": self.user_id,
                "note": self.note_id,
                "data": self.values,
            },
        }

    def edit(self) -> Effect:
        """Edit the command."""
        if not self.command_uuid:
            raise AttributeError("Command uuid is required to edit a command")
        return {
            "type": f"EDIT_{self.Meta.key.upper()}_COMMAND",
            "payload": {
                "user": self.user_id,
                "command": self.command_uuid,
                "data": self.values,
            },
        }

    def delete(self) -> Effect:
        """Delete the command."""
        if not self.command_uuid:
            raise AttributeError("Command uuid is required to delete a command")
        return {
            "type": f"DELETE_{self.Meta.key.upper()}_COMMAND",
            "payload": {"command": self.command_uuid, "user": self.user_id},
        }

    def commit(self) -> Effect:
        """Commit the command."""
        if not self.command_uuid:
            raise AttributeError("Command uuid is required to commit a command")
        return {
            "type": f"COMMIT_{self.Meta.key.upper()}_COMMAND",
            "payload": {"command": self.command_uuid, "user": self.user_id},
        }

    def enter_in_error(self) -> Effect:
        """Mark the command as entered-in-error."""
        if not self.command_uuid:
            raise AttributeError("Command uuid is required to enter in error a command")
        return {
            "type": f"ENTER_IN_ERROR_{self.Meta.key.upper()}_COMMAND",
            "payload": {"command": self.command_uuid, "user": self.user_id},
        }
