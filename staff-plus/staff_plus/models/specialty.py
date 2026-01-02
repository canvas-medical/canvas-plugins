from django.db.models import CASCADE, ForeignKey, Index, TextField

from canvas_sdk.v1.data.base import Model


class Specialty(Model):
    class Meta:
        db_table = "specialty"
        app_label = "staff_plus"

    name = TextField()

    def __str__(self):
        return f"{self.dbid}: {self.name}"


class StaffSpecialty(Model):
    class Meta:
        app_label = "staff_plus"
        db_table = "staff_specialties"
        indexes = [
            Index(fields=["staff_id", "specialty_id"]),
        ]

    staff = ForeignKey(
        "staff_plus.StaffProxy",
        to_field="dbid",
        on_delete=CASCADE,
        related_name="staff_specialties",
    )
    specialty = ForeignKey(
        "staff_plus.Specialty", to_field="dbid", on_delete=CASCADE, related_name="staff_specialties"
    )
