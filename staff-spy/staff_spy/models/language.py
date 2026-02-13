from django.db.models import DO_NOTHING, ForeignKey, TextField
from staff_spy.models.proxy import StaffProxy

from canvas_sdk.v1.data.base import CustomModel


class Language(CustomModel):
    staff = ForeignKey(StaffProxy, on_delete=DO_NOTHING, to_field="dbid", related_name="languages")
    name = TextField()
