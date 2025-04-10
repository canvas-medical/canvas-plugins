from django.db import models


class CanvasUser(models.Model):
    """A class representing a Canvas User."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_auth_user_001"

    dbid = models.BigIntegerField(db_column="dbid", primary_key=True)
    email = models.CharField()
