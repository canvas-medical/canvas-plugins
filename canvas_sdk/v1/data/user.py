from django.db import models


class CanvasUser(models.Model):
    """A class representing a Canvas User."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_auth_user_001"

    dbid = models.BigIntegerField(db_column="dbid", primary_key=True)
    email = models.EmailField(db_column="email")
    phone_number = models.CharField(db_column="phone_number", max_length=255)


__exports__ = ("CanvasUser",)
