from django.db import models

from canvas_sdk.v1.data.base import Model


class CanvasUser(Model):
    """A class representing a Canvas User."""

    class Meta:
        db_table = "canvas_sdk_data_api_auth_user_001"

    email = models.EmailField(db_column="email")
    phone_number = models.CharField(db_column="phone_number", max_length=255)
    last_invite_date_time = models.DateTimeField()
    is_portal_registered = models.BooleanField()


__exports__ = ("CanvasUser",)
