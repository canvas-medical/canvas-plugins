from django.contrib.postgres.indexes import GinIndex
from django.db.models import (
    DO_NOTHING,
    BooleanField,
    DateField,
    DateTimeField,
    DecimalField,
    Index,
    IntegerField,
    JSONField,
    OneToOneField,
    TextField,
)
from staff_plus.models.proxy import StaffProxy

from canvas_sdk.v1.data.base import CustomModel


class Biography(CustomModel):
    biography = TextField()
    practicing_since = IntegerField()
    version = DecimalField(max_digits=10, decimal_places=2, default=1.0)
    is_accepting_patients = BooleanField()
    created_date = DateField(auto_now_add=True)
    last_modified_at = DateTimeField(auto_now_add=True)
    extended_attributes = JSONField()

    class Meta:
        indexes = [
            Index(fields=["-created_date"]),
            GinIndex(fields=["extended_attributes"]),
        ]

    staff = OneToOneField(
        StaffProxy, to_field="dbid", on_delete=DO_NOTHING, related_name="biography"
    )
