import json
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.base import Model, TrackableFieldsModel
from canvas_sdk.effects import Effect
from canvas_sdk.effects._field_errors import upload_key_errors
from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.v1.data import Message as MessageModel
from canvas_sdk.v1.data import Patient, Staff, Team


def _team_errors(effect: Model, team_id: UUID | None) -> list[InitErrorDetails]:
    """Return an error detail when `team_id` names a team that does not exist."""
    if team_id is None or Team.objects.filter(id=team_id).exists():
        return []
    return [
        effect._create_error_detail(
            "value",
            f"Team with id {team_id} does not exist.",
            team_id,
        )
    ]


class Message(TrackableFieldsModel):
    """
    Effect to create and/or send a message.

    Files (PNG, JPEG or PDF) are attached by passing the ``key`` of each ``StoredFilePart``
    received on a SimpleAPI route declared with ``file_uploads="stored"`` in
    ``attachment_upload_keys``. Canvas copies each file into the message, then deletes the
    upload, so a key can be attached once.
    """

    class Meta:
        effect_type = "MESSAGE"

    message_id: str | UUID | None = None
    content: str | None
    sender_id: str | UUID
    recipient_id: str | UUID
    read: datetime | None = None
    team_id: UUID | None = Field(default=None, strict=False)
    attachment_upload_keys: list[str] | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.attachment_upload_keys is not None:
            errors.extend(upload_key_errors(self, "attachment_upload_keys"))
            if method == "send" and self.attachment_upload_keys:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Attachments are added with create(), create_and_send() or edit(), "
                        "not send().",
                        self.attachment_upload_keys,
                    )
                )

        if (
            not Patient.objects.filter(id=self.sender_id).exists()
            and not Staff.objects.filter(id=self.sender_id).exists()
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
            and not Staff.objects.filter(id=self.recipient_id).exists()
        ):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Recipient with ID {self.recipient_id} does not exist.",
                    self.recipient_id,
                )
            )

        if method == "edit":
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
        elif method in (
            "create",
            "create_and_send",
        ):
            if not self.content or self.content.strip() == "":
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Message content cannot be empty.",
                        self.content,
                    )
                )

            if self.message_id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Can't set message ID when creating a message.",
                        self.message_id,
                    )
                )

            errors.extend(_team_errors(self, self.team_id))

        if method in ("edit", "send") and self.is_dirty("team_id"):
            errors.append(
                self._create_error_detail(
                    "value",
                    "Use AssignMessageTeam to change a message's team.",
                    self.team_id,
                )
            )

        return errors

    def create(self) -> Effect:
        """Originate a new command in the note body."""
        self._validate_before_effect("create")
        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps(
                {
                    "data": self.values,
                }
            ),
        )

    def create_and_send(self) -> Effect:
        """Create and send message."""
        self._validate_before_effect("create_and_send")
        return Effect(
            type="CREATE_AND_SEND_MESSAGE",
            payload=json.dumps({"data": self.values}),
        )

    def edit(self) -> Effect:
        """Edit message."""
        self._validate_before_effect("edit")
        return Effect(type="EDIT_MESSAGE", payload=json.dumps({"data": self.values}))

    def send(self) -> Effect:
        """Send message."""
        self._validate_before_effect("send")
        return Effect(
            type="SEND_MESSAGE",
            payload=json.dumps({"data": self.values}),
        )


class AssignMessageTeam(_BaseEffect):
    """Assign a message to a team, or unassign it when `team_id` is None."""

    class Meta:
        effect_type = EffectType.ASSIGN_MESSAGE_TEAM

    message_id: UUID = Field(strict=False)
    team_id: UUID | None = Field(strict=False)

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if not MessageModel.objects.filter(id=self.message_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Message with id {self.message_id} does not exist.",
                    self.message_id,
                )
            )

        errors.extend(_team_errors(self, self.team_id))

        return errors

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values to be sent in the payload."""
        return {
            "message_id": str(self.message_id),
            "team_id": str(self.team_id) if self.team_id is not None else None,
        }


__exports__ = ("AssignMessageTeam", "Message")
