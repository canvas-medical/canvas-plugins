import json
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_generated.messages.effects_pb2 import Effect
from canvas_sdk.effects.note.base import NoteOrAppointmentABC
from canvas_sdk.v1.data import Message as MessageModel
from canvas_sdk.v1.data import Patient, Staff


class Message(NoteOrAppointmentABC):
    """
    Effect to create and/or send a message.
    """

    class Meta:
        effect_type = "MESSAGE"

    message_id: str | UUID | None
    content: str
    sender_id: str | UUID
    recipient_id: str | UUID
    note_id: str | UUID | None
    read: bool = False

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if (
            not Patient.objects.filter(id=self.sender_id).exists()
            or not Staff.objects.filter(id=self.sender_id).exists()
        ):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Sender with ID {self.sender_id} does not exist.",
                    self.sender_id,
                )
            )

        if (
            not Patient.objects.filter(id=self.recipient_id).exists()
            or not Staff.objects.filter(id=self.recipient_id).exists()
        ):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Recipient with ID {self.recipient_id} does not exist.",
                    self.recipient_id,
                )
            )

        if method == "edit":
            if self.note_id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Can't update note when editing message",
                        self.note_id,
                    )
                )
            if not self.message_id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Message ID is required when editing a message.",
                        self.message_id,
                    )
                )
            else:
                if not MessageModel.objects.filter(id=self.message_id).exists():
                    errors.append(
                        self._create_error_detail(
                            "value",
                            f"Can't edit message with ID {self.message_id}: Does not exist.",
                            self.message_id,
                        )
                    )
        else:
            if self.message_id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Can't set message ID when creating/sending a message.",
                        self.message_id,
                    )
                )

        return errors

    def create_and_send(self) -> Effect:
        """Send message."""
        self._validate_before_effect("send")
        return Effect(
            type="CREATE_AND_SEND_MESSAGE",
            payload=json.dumps({"data": self.values}),
        )

    def edit(self) -> Effect:
        """Edit message."""
        self._validate_before_effect("edit")
        return Effect(type="EDIT_MESSAGE", payload=json.dumps({"data": self.values}))


__exports__ = ("Message",)
