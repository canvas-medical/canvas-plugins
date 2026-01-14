from django.db.models import OneToOneField, DO_NOTHING, TextField, IntegerField

from canvas_sdk.v1.data.base import CustomModel


class Biography(CustomModel):
    """An augmented staff profile with biography and stuff"""

    class Meta:
        db_table = '"staff_plus"."biography"'
        app_label = "staff_spy"

    staff = OneToOneField(
        "StaffProxy", to_field="dbid", on_delete=DO_NOTHING, null=False, related_name="biography"
    )
    biography = TextField()
    language = TextField()
    practicing_since = IntegerField()
