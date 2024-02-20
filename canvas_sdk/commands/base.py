from typing import Any, TypedDict


class _BaseCommandAttributes(TypedDict):
    note_id: int | None
    command_uuid: str | None
    user_id: int


class _BaseCommand:
    note_id: int | None
    command_uuid: str | None
    user_id: int

    def __init__(
        self,
        user_id: int | None = None,
        note_id: int | None = None,
        command_uuid: str | None = None,
    ) -> None:
        if not user_id:
            raise AttributeError("user_id is required")
        self.user_id = user_id
        self.note_id = note_id
        self.command_uuid = command_uuid

    def __setattr__(self, name: str, value: Any) -> None:
        if name not in _BaseCommandAttributes.__annotations__:
            return super().__setattr__(name, value)

        expected_type = _BaseCommandAttributes.__annotations__[name]
        if issubclass(type(value), expected_type):
            super().__setattr__(name, value)
        else:
            raise TypeError(f"'{name}' requires a type of '{expected_type}'")

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
