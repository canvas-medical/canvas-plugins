from django.db.models import JSONField, TextField, UniqueConstraint

from canvas_sdk.v1.data.base import CustomModel


class NoteTypeAccessConfig(CustomModel):
    """Stores which staff members are permitted to access a given note type.

    One row per note type.  ``allowed_staff_ids`` is a list of ``Staff.id``
    values (external UUIDs).  An absent row means the note type is unrestricted.
    An empty list means no staff can access it.
    """

    note_type_id: TextField = TextField()
    allowed_staff_ids: JSONField = JSONField(default=list)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["note_type_id"],
                name="unique_note_type_access_config",
            )
        ]
