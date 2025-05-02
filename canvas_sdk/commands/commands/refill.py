from typing import Literal

from django.db.models.expressions import Subquery
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.commands.prescribe import PrescribeCommand
from canvas_sdk.v1.data import Medication, Note


class RefillCommand(PrescribeCommand):
    """A class for managing a Refill command within a specific note."""

    class Meta:
        key = "refill"

    def _get_error_details(
        self, method: Literal["originate", "edit", "delete", "commit", "enter_in_error"]
    ) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.fdb_code:
            subquery = Subquery(Note.objects.filter(id=self.note_uuid).values("patient_id")[:1])
            if (
                not Medication.objects.active()
                .filter(codings__code=self.fdb_code, patient=subquery)
                .exists()
            ):
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Medication with fdb_code {self.fdb_code} does not exist.",
                        self.fdb_code,
                    )
                )

        return errors


__exports__ = ("RefillCommand",)
