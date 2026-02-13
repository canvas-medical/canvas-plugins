from django.db.models import DO_NOTHING, ForeignKey, TextField

from canvas_sdk.v1.data.base import CustomModel


class Specialty(CustomModel):
    name = TextField()


class StaffSpecialty(CustomModel):
    staff = ForeignKey(
        "StaffProxy",
        to_field="dbid",
        on_delete=DO_NOTHING,
        related_name="staff_specialties",
    )
    specialty = ForeignKey(
        "Specialty", to_field="dbid", on_delete=DO_NOTHING, related_name="staff_specialties"
    )
