import datetime

from django.db.models import DO_NOTHING, Index, OneToOneField, TextField, ForeignKey, DateTimeField

from canvas_sdk.v1.data.base import CustomModel
from staff_plus.models.proxy import StaffProxy

class Language(CustomModel):

    class Meta:
        indexes = [
            Index(fields=["staff_id"]),
        ]

    staff = ForeignKey(StaffProxy, on_delete=DO_NOTHING, to_field="dbid", related_name="languages")
    name = TextField()
    code = TextField()
    created = DateTimeField(default=datetime.datetime.now)
    updated = DateTimeField(default=datetime.datetime.now)