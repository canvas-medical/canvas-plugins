from django.db.models import ForeignKey, DO_NOTHING, TextField

from canvas_sdk.v1.data.base import CustomModel
from staff_spy.models.proxy import StaffProxy


class Language(CustomModel):

    class Meta:
        app_label = "staff_spy"
        db_table = '"staff_plus"."language"'

    staff = ForeignKey(StaffProxy, on_delete=DO_NOTHING, to_field="dbid", related_name="languages")
    name = TextField()
