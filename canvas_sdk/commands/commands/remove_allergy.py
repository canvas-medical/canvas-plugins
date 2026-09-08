from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.commands.base import _OptionalId
from canvas_sdk.v1.data import AllergyIntolerance


class RemoveAllergyCommand(BaseCommand):
    """A class for managing a Remove Allergy command within a specific note."""

    class Meta:
        key = "removeAllergy"

    allergy_id: _OptionalId = Field(
        description="The external ID of the allergy to remove.",
        default=None,
        json_schema_extra={"commands_api_name": "allergy"},
    )
    narrative: str | None = Field(default=None, max_length=512)

    def _get_error_details(self, method: str) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.allergy_id is None:
            return errors

        allergy_patient_id = (
            AllergyIntolerance.objects.filter(id=self.allergy_id)
            .values_list("patient__id", flat=True)
            .first()
        )

        if allergy_patient_id is None or not self._is_target_patient(allergy_patient_id):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Allergy {self.allergy_id} does not belong to this command's patient",
                    self.allergy_id,
                )
            )

        return errors


__exports__ = ("RemoveAllergyCommand",)
