from django.db.models import DO_NOTHING, ForeignKey, Index, TextField
from staff_plus.models.proxy import StaffProxy

from canvas_sdk.v1.data.base import CustomModel


class Specialty(CustomModel):
    class Meta:
        indexes = [
            Index(fields=["name"]),
        ]

    name = TextField()

    def __str__(self):
        return f"{self.dbid}: {self.name}"


class StaffSpecialty(CustomModel):
    staff = ForeignKey(
        StaffProxy,
        to_field="dbid",
        on_delete=DO_NOTHING,
        related_name="staff_specialties",
    )
    specialty = ForeignKey(
        Specialty, to_field="dbid", on_delete=DO_NOTHING, related_name="staff_specialties"
    )
