from pydantic import BaseModel, ConfigDict, model_validator
from typing_extensions import Self


class _BaseCommand(BaseModel):
    model_config = ConfigDict(strict=True, validate_assignment=True)

    # to look into: should we use external identifiers? or an sdk note class
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

    def originate(self) -> dict:
        """Originate a new command in the note body."""
        # note: this is a placeholder method until we've made some more definitive decisions about how command objects are manipulated
        if not self.note_id:
            raise AttributeError("Note id is required to originate a command")
        return {"note_id": self.note_id, "user_id": self.user_id, "values": self.values}

    def edit(self) -> dict:
        """Edit the command."""
        # note: this is a placeholder method until we've made some more definitive decisions about how command objects are manipulated
        if not self.command_uuid:
            raise AttributeError("Command uuid is required to edit a command")
        return {"command_uuid": self.command_uuid, "user_id": self.user_id, "values": self.values}

    def delete(self) -> dict:
        """Delete the command."""
        # note: this is a placeholder method until we've made some more definitive decisions about how command objects are manipulated
        if not self.command_uuid:
            raise AttributeError("Command uuid is required to delete a command")
        return {"command_uuid": self.command_uuid, "user_id": self.user_id, "delete": True}

    def commit(self) -> dict:
        """Commit the command."""
        # note: this is a placeholder method until we've made some more definitive decisions about how command objects are manipulated
        if not self.command_uuid:
            raise AttributeError("Command uuid is required to commit a command")
        return {"command_uuid": self.command_uuid, "user_id": self.user_id, "commit": True}

    def enter_in_error(self) -> dict:
        """Mark the command as entered-in-error."""
        # note: this is a placeholder method until we've made some more definitive decisions about how command objects are manipulated
        if not self.command_uuid:
            raise AttributeError("Command uuid is required to enter in error a command")
        return {"command_uuid": self.command_uuid, "user_id": self.user_id, "enter_in_error": True}
