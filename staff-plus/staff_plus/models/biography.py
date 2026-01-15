from django.db.models import DO_NOTHING, Index, OneToOneField, TextField, IntegerField

from canvas_sdk.v1.data.base import CustomModel
from staff_plus.models.proxy import StaffProxy


class Biography(CustomModel):
    """An augmented staff profile with biography and stuff"""

    staff = OneToOneField(
        StaffProxy, to_field="dbid", on_delete=DO_NOTHING, null=False, related_name="biography"
    )
    biography = TextField()
    language = TextField()
    practicing_since = IntegerField()
