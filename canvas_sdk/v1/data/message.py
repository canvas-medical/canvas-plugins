from django.db import models


class TransmissionChannel(models.TextChoices):
    """Transmission channel."""

    MANUAL = "manual", "Manual"
    TEXT_MESSAGE = "sms", "Text Message"
    EMAIL = "email", "Email"
    NOOP = "noop", "No-op"


class Message(models.Model):
    """Message."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_message_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
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


class MessageAttachment(models.Model):
    """Message attachment."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_messageattachment_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    file = models.TextField()
    content_type = models.CharField(max_length=255)
    message = models.ForeignKey(
        "v1.Message", on_delete=models.DO_NOTHING, related_name="message", null=True
    )


class MessageTransmission(models.Model):
    """Message Transmission."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_messagetransmission_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    message = models.ForeignKey(
        "v1.Message", on_delete=models.DO_NOTHING, related_name="transmissions", null=True
    )
    delivered = models.BooleanField()
    failed = models.BooleanField()

    contact_point_system = models.CharField(choices=TransmissionChannel.choices)
    contact_point_value = models.CharField(max_length=255)

    comment = models.TextField()
    delivered_by = models.ForeignKey(
        "v1.Staff",
        on_delete=models.DO_NOTHING,
        related_name="transmissions_delivered",
        null=True,
    )


__exports__ = ("TransmissionChannel", "Message", "MessageAttachment", "MessageTransmission")
