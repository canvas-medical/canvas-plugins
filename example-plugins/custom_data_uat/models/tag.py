from __future__ import annotations

from django.db.models import (
    CASCADE,
    DO_NOTHING,
    ForeignKey,
    IntegerField,
    TextField,
    UniqueConstraint,
)

from canvas_sdk.v1.data.base import CustomModel
from custom_data_uat.models.proxy import PatientProxy


class Tag(CustomModel):
    """A simple tag that can be applied to patients."""

    label: TextField[str, str] = TextField()
    color: TextField[str, str] = TextField(default="gray")


class PatientTag(CustomModel):
    """Through model linking Tags to Patients with a priority field."""

    tag: ForeignKey[Tag, Tag] = ForeignKey(
        Tag,
        to_field="dbid",
        on_delete=CASCADE,
        related_name="patient_tags",
    )
    patient: ForeignKey[PatientProxy, PatientProxy] = ForeignKey(
        PatientProxy,
        to_field="dbid",
        on_delete=DO_NOTHING,
        related_name="%(app_label)s_patient_tags",
    )
    priority: IntegerField[int, int] = IntegerField(default=0)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["tag", "patient"],
                name="unique_tag_patient",
            ),
        ]
