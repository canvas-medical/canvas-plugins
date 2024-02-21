from typing import Any

from pydantic import BaseModel, ConfigDict


class _BaseCommand(BaseModel):
    model_config = ConfigDict(strict=True)

    note_id: int | None = None
    command_uuid: str | None = None
    user_id: int

    def __setattr__(self, name: str, value: Any) -> None:
        dict_to_validate = self.__dict__ | {name: value}
        self.model_validate(dict_to_validate, strict=True)
        super().__setattr__(name, value)

    @property
    def values(self) -> dict:
        return {}

    def originate(self) -> dict:
        """Originate a new command in the note body."""
        if not self.note_id:
            raise AttributeError("Note id is required to originate a command")
        return {"note_id": self.note_id, "user_id": self.user_id, "values": self.values}

    def update(self) -> dict:
        """Update the command."""
        if not self.command_uuid:
            raise AttributeError("Command uuid is required to update a command")
        return {"command_uuid": self.command_uuid, "user_id": self.user_id, "values": self.values}

    def delete(self) -> dict:
        """Delete the command."""
        if not self.command_uuid:
            raise AttributeError("Command uuid is required to delete a command")
        return {"command_uuid": self.command_uuid, "user_id": self.user_id, "delete": True}

    def commit(self) -> dict:
        """Commit the command."""
        if not self.command_uuid:
            raise AttributeError("Command uuid is required to commit a command")
        return {"command_uuid": self.command_uuid, "user_id": self.user_id, "commit": True}

    def enter_in_error(self) -> dict:
        """Enter in error the command."""
        if not self.command_uuid:
            raise AttributeError("Command uuid is required to enter in error a command")
        return {"command_uuid": self.command_uuid, "user_id": self.user_id, "enter_in_error": True}
