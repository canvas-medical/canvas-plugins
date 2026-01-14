from django.db.models import CASCADE, ForeignKey, Index, TextField

from canvas_sdk.v1.data.base import CustomModel


class Specialty(CustomModel):
    class Meta:
        app_label = "staff_spy"
        db_table = '"staff_plus"."specialty"'

    name = TextField()

class StaffSpecialty(CustomModel):
    class Meta:
        app_label = "staff_spy"
        db_table = '"staff_plus"."staff_specialties"'

    staff = ForeignKey(
        "StaffProxy",
        to_field="dbid",
        on_delete=CASCADE,
        related_name="staff_specialties",
    )
    specialty = ForeignKey(
        "Specialty", to_field="dbid", on_delete=CASCADE, related_name="staff_specialties"
    )
