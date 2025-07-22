from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel


class TransmissionChannel(models.TextChoices):
    """Transmission channel."""

    MANUAL = "manual", "Manual"
    TEXT_MESSAGE = "sms", "Text Message"
    EMAIL = "email", "Email"
    NOOP = "noop", "No-op"


class Message(IdentifiableModel):
    """Message."""

    class Meta:
        db_table = "canvas_sdk_data_api_message_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    content = models.TextField()
    sender = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, related_name="sent_messages", null=True
    )
    recipient = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, related_name="received_messages", null=True
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="message", null=True
    )
    read = models.BooleanField()


class MessageAttachment(IdentifiableModel):
    """Message attachment."""

    class Meta:
        db_table = "canvas_sdk_data_api_messageattachment_001"

    file = models.TextField()
    content_type = models.CharField(max_length=255)
    message = models.ForeignKey(
        "v1.Message", on_delete=models.DO_NOTHING, related_name="message", null=True
    )


class MessageTransmission(IdentifiableModel):
    """Message Transmission."""

    class Meta:
        db_table = "canvas_sdk_data_api_messagetransmission_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    message = models.ForeignKey(
        "v1.Message", on_delete=models.DO_NOTHING, related_name="transmissions", null=True
    )
    delivered = models.BooleanField()
    failed = models.BooleanField()

    contact_point_system = models.CharField(choices=TransmissionChannel.choices, max_length=20)
    contact_point_value = models.CharField(max_length=255)

    comment = models.TextField()
    delivered_by = models.ForeignKey(
        "v1.Staff",
        on_delete=models.DO_NOTHING,
        related_name="transmissions_delivered",
        null=True,
    )


__exports__ = ("TransmissionChannel", "Message", "MessageAttachment", "MessageTransmission")
