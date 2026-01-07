from django.db.models import DO_NOTHING, Index, OneToOneField, TextField

from canvas_sdk.v1.data.base import CustomModel


class Biography(CustomModel):
    """An augmented staff profile with biography and stuff"""

    class Meta:
        db_table = "biography"
        app_label = "staff_plus"

        indexes = [
            Index(fields=["staff_id"]),
        ]

    staff = OneToOneField(
        "StaffProxy", to_field="dbid", on_delete=DO_NOTHING, null=False, related_name="biography"
    )
    biography = TextField()
